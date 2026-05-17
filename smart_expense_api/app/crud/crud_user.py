from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

# 1. Hàm lấy thông tin user qua Email (Dùng cho Login/Register)
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# 2. Hàm lấy thông tin user qua ID (FIX LỖI 500: Dùng cho việc giải mã Token)
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# 3. Hàm tạo User mới (Đăng ký)
def create_user(db: Session, user: UserCreate):
    # Mã hóa mật khẩu
    hashed_password = get_password_hash(user.password)

    # Tạo đối tượng User
    db_user = User(
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 4. Hàm xác thực (Đăng nhập)
def authenticate(db: Session, email: str, password: str):
    # Tìm user theo email
    user = get_user_by_email(db, email=email)
    
    # Nếu không tìm thấy user -> Trả về None
    if not user:
        return None
        
    # Nếu tìm thấy, kiểm tra mật khẩu có khớp không
    if not verify_password(password, user.hashed_password):
        return None
        
    # Nếu khớp hết -> Trả về user
    return user