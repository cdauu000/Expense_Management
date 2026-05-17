import sys
import os


sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Category, User

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def get_hash(password): return pwd_context.hash(password)
except ImportError:
    
    def get_hash(password): return password 

db = SessionLocal()

vietnamese_categories = [
    "Tiền lương",  "Tiền ăn", "Tiền nhà", 
    "Tiền sinh hoạt", "Tiền đi lại", "Tiền học", "Tiền giải trí"
]

def init_categories():
    print("========================================")
    print("      KIỂM TRA & TẠO DỮ LIỆU")
    print("========================================")

    # 1. KIỂM TRA XEM CÓ USER NÀO CHƯA
    users = db.query(User).all()
    
    selected_user = None

    if not users:
        print("Database hiện tại TRỐNG RỖNG (Chưa có user nào).")
        create_now = input(" Bạn có muốn tạo user 'admin' (pass: 123456) ngay bây giờ không? (y/n): ")
        
        if create_now.lower() == 'y':
            # Tạo user Admin ngay lập tức
            hashed_pw = get_hash("123456")
            new_admin = User(username="admin", email="admin@example.com", password=hashed_pw)
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            selected_user = new_admin
            print(f"✅ Đã tạo User: admin (ID: {selected_user.id})")
        else:
            print("Đã hủy. Hãy đăng ký tài khoản trên Web trước.")
            return
    else:
        # Nếu đã có User, in ra cho bạn chọn
        print("🔍 Danh sách User tìm thấy trong Database:")
        for u in users:
            print(f"   - ID: {u.id} | Username: {u.username}")
        
        target_name = input("👉 Nhập chính xác username bạn muốn thêm danh mục: ").strip()
        selected_user = db.query(User).filter(User.username == target_name).first()

    # 2. BẮT ĐẦU THÊM DANH MỤC
    if not selected_user:
        print(f" Lỗi: Không tìm thấy user '{target_name}'!")
        return

    print("----------------------------------------")
    print(f"Đang thêm danh mục cho: {selected_user.username}...")
    
    count = 0
    for name in vietnamese_categories:
        exists = db.query(Category).filter(
            Category.name == name, 
            Category.owner_id == selected_user.id
        ).first()
        
        if not exists:
            new_cat = Category(name=name, owner_id=selected_user.id)
            db.add(new_cat)
            print(f"[+] Thêm mới: {name}")
            count += 1
        else:
            print(f"[-] Đã có: {name}")
    
    db.commit()
    print("----------------------------------------")
    print(f" HOÀN TẤT! Đã thêm {count} danh mục.")

if __name__ == "__main__":
    init_categories()