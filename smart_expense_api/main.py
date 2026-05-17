from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel 
from typing import Optional

from app.database import engine, Base, get_db, SessionLocal
from app import models
from app.schemas import UserCreate

from app.core.security import create_access_token, verify_password, get_password_hash


from app.api.endpoints import expenses, categories, budgets

# --- 1. KHỞI TẠO DATABASE ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Expense API")

# --- 2. CẤU HÌNH CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi nguồn (Frontend)
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép GET, POST, PUT, DELETE
    allow_headers=["*"],
)

# --- 3. CẤU HÌNH BẢO MẬT ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# =================================================================

class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    date: Optional[str] = None

# =================================================================

from jose import JWTError, jwt
from app.core.config import settings 

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Giải mã token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# --- 4. API ĐĂNG KÝ ---
@app.post("/users/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")
    
    hashed_password = get_password_hash(user.password)
    
    new_user = models.User(
        username=user.username, 
        password=hashed_password, 
        email=user.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Tạo tài khoản thành công", "username": new_user.username}

# --- 5. API ĐĂNG NHẬP ---
@app.post("/users/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tài khoản hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

# =================================================================
#  PHẦN MỚI THÊM: API SỬA GIAO DỊCH (PUT)

@app.put("/expenses/{transaction_id}")
def update_transaction(
    transaction_id: int, 
    item: TransactionUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) 
):
    # 1. Tìm giao dịch trong DB 
    db_transaction = db.query(models.Expense).filter(
        models.Expense.id == transaction_id,
        models.Expense.owner_id == current_user.id
    ).first()

    if not db_transaction:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch hoặc bạn không có quyền sửa")

    # 2. Cập nhật dữ liệu mới
    if item.title is not None:
        db_transaction.title = item.title
    if item.amount is not None:
        db_transaction.amount = item.amount
    if item.category is not None:
        db_transaction.category = item.category
    if item.date is not None:
        
        db_transaction.date = item.date 

    # 3. Lưu vào MySQL
    db.commit()
    db.refresh(db_transaction)
    
    return {"message": "Cập nhật thành công", "data": db_transaction}

# --- 6. ĐĂNG KÝ CÁC ROUTER ---

app.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])

# --- 7. TỰ ĐỘNG TẠO DATA MẪU
@app.on_event("startup")
def init_data_automatic():
    print("--- ĐANG KIỂM TRA DỮ LIỆU MẪU ---")
    db = SessionLocal()
    try:
        # A. Tạo User Admin
        first_user = db.query(models.User).filter(models.User.id == 1).first()
        if not first_user:
            hashed_pw = get_password_hash("123456") 
            default_user = models.User(
                username="admin", 
                email="admin@gmail.com", 
                password=hashed_pw 
            )
            db.add(default_user)
            db.commit()
            print(">>> Đã tạo Admin mặc định.")
        
        # B. Tạo Danh mục Tiếng Việt
        vietnamese_categories = [
            "Tiền ăn", "Tiền nhà", "Tiền sinh hoạt", 
            "Tiền đi lại", "Tiền học", "Tiền giải trí", "Lương"
        ]
        user_id = 1 
        for name in vietnamese_categories:
            exists = db.query(models.Category).filter(models.Category.name == name).first()
            if not exists:
                try:
                    new_cat = models.Category(name=name, owner_id=user_id)
                except:
                    new_cat = models.Category(name=name)
                db.add(new_cat)
        db.commit()
        print(">>> Kiểm tra danh mục hoàn tất.")

    except Exception as e:
        print(f"Lỗi khởi tạo: {e}")
    finally:
        db.close()

# --- 8. MOUNT STATIC FILES (GIAO DIỆN) ---
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")