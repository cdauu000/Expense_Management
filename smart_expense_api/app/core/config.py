import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Thông tin dự án
    PROJECT_NAME: str = "Smart Expense API"
    API_V1_STR: str = "/api/v1"
    ALGORITHM: str = "HS256"
    # Cấu hình Database
    DATABASE_URL: str

    # --- CẤU HÌNH BẢO MẬT (MỚI) ---
    # Đây là khóa bí mật để mã hóa Token. 
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Token sống trong 30 phút
    
    class Config:
        env_file = ".env"

settings = Settings()