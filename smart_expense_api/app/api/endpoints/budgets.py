from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api import deps
from app.models.user import User
from app.schemas import budget as budget_schema
from app.crud import crud_budget

router = APIRouter()

# API 1: Đặt hạn mức (Ví dụ: Tháng 1, Ăn uống giới hạn 2 triệu)
@router.post("/", response_model=dict)
def set_budget(
    budget_in: budget_schema.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    crud_budget.create_or_update_budget(db, budget_in, user_id=current_user.id)
    return {"message": "Đã cập nhật hạn mức thành công!"}

# API 2: Xem tình hình chi tiêu (So sánh Thực tế vs Hạn mức)
@router.get("/status", response_model=List[budget_schema.BudgetOut])
def check_budget_status(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    return crud_budget.get_budget_status(db, user_id=current_user.id, month=month, year=year)