from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate

# 1. Lấy danh sách danh mục (của riêng user đó)
def get_categories(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Category).filter(Category.owner_id == user_id).offset(skip).limit(limit).all()

# 2. Tạo danh mục mới
def create_category(db: Session, category: CategoryCreate, user_id: int):
    # Convert Schema -> Model
    db_category = Category(name=category.name, owner_id=user_id)
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category) # Lấy lại ID vừa tạo
    return db_category