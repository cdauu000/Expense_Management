from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.core import security
from datetime import timedelta

router = APIRouter()

@router.post("/login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # 1. Tìm user trong Database theo username
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # 2. Kiểm tra:
    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tài khoản hoặc mật khẩu", 
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Nếu đúng hết, tạo Token
    access_token_expires = timedelta(minutes=30)
    access_token = security.create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )

    # 4. Trả về Token cho Frontend
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}