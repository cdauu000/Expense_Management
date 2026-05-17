from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core import config, security
from app.crud import crud_user
from app.models.user import User
from app.database import SessionLocal

# Cấu hình đường dẫn để Swagger biết chỗ lấy Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Hàm này sẽ tự động chạy mỗi khi có request cần bảo mật.
    Nó giải mã Token -> Lấy ID -> Tìm User trong DB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập (Token lỗi hoặc hết hạn)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Giải mã Token
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Tìm user trong DB
    user = crud_user.get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    return user