from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import category as category_schema
from app.crud import crud_category
from app.models.user import User
from app.api import deps 

router = APIRouter()

# API 1: Xem danh sách danh mục
@router.get("/", response_model=List[category_schema.Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user) # Bắt buộc phải đăng nhập
):
    categories = crud_category.get_categories(db, user_id=current_user.id, skip=skip, limit=limit)
    return categories

# API 2: Tạo danh mục mới
@router.post("/", response_model=category_schema.Category)
def create_category(
    category_in: category_schema.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user) # Bắt buộc phải đăng nhập
):
    return crud_category.create_category(db=db, category=category_in, user_id=current_user.id)