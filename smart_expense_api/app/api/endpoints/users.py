from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.models.user import User 

router = APIRouter()

# --- 1. API ĐĂNG KÝ
@router.post("/register", response_model=UserOut)
def register_user(
    user_in: UserCreate, 
    db: Session = Depends(deps.get_db)
):
    # 1. Kiểm tra xem email đã có người dùng chưa
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400, 
            detail="Email này đã được đăng ký!"
        )
    
    # 2. MÃ HÓA MẬT KHẨU 
    hashed_password = security.get_password_hash(user_in.password)

    # 3. Tạo user mới và lưu vào Database
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# --- 2. API ĐĂNG NHẬP (Lấy Token) ---
@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Đăng nhập để lấy Access Token.
    form_data.username: Sẽ chứa Email người dùng nhập
    form_data.password: Sẽ chứa Mật khẩu người dùng nhập
    """
    # 1. Tìm user trong DB bằng email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Kiểm tra: User không tồn tại HOẶC Mật khẩu không khớp
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Nếu đúng, tạo Token có hạn sử dụng
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # 4. Trả về Token cho Frontend
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# --- 3. API LẤY THÔNG TIN CHÍNH MÌNH (Cần Token) ---
@router.get("/me", response_model=UserOut)
def read_users_me(
    current_user: User = Depends(deps.get_current_user)
):
    """
    API này dùng để test Token. 
    Chỉ khi header có 'Authorization: Bearer <token>' thì mới chạy được.
    """
    return current_user