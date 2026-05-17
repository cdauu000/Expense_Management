# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# 1. Load biến môi trường
load_dotenv()

# 2. Lấy giá trị từ biến môi trường
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# --- DEBUG & FALLBACK ---
print("--------------------------------------------------")
if SQLALCHEMY_DATABASE_URL:
    print(f" Đã đọc được DATABASE_URL từ .env")
else:
    print(f" CẢNH BÁO: Không tìm thấy file .env hoặc biến DATABASE_URL.")
   
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:050611@localhost:3306/smartexpense_db"
print("--------------------------------------------------")

# 3. Tạo Engine kết nối

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 4. Tạo SessionLocal (Phiên làm việc với DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Tạo Base (Lớp cha cho các Models)
Base = declarative_base()

# 6. Hàm Dependency Injection 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()