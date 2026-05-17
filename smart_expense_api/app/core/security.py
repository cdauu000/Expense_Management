from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# 1. Cấu hình mã hóa mật khẩu
# Sử dụng thuật toán bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Cấu hình JWT
ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    """
    Hàm tạo ra chuỗi Token (Chìa khóa vào nhà).
    - subject: Thường là Email hoặc ID của user.
    - expires_delta: Thời gian sống của token (tùy chọn).
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Mặc định token sống 30 phút nếu không truyền tham số
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    # Tạo nội dung token (Payload)
    # 'exp': thời gian hết hạn
    # 'sub': chủ sở hữu token (subject)
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Mã hóa token bằng SECRET_KEY lấy từ file cấu hình
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu nhập vào (plain) có khớp với mật khẩu đã mã hóa (hashed) trong DB không.
    Dùng cho chức năng Đăng Nhập.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Mã hóa mật khẩu từ dạng chữ thường sang dạng băm (hash).
    Dùng cho chức năng Đăng Ký.
    """
    return pwd_context.hash(password)