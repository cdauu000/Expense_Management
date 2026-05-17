from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from sqlalchemy import func

from app import models, schemas
from app.database import get_db 
from app.schemas import expense as expense_schema
from app.crud import crud_expense

from app.models import Category, Expense

from app.database import SessionLocal 
from app.api import deps
from app.models.expense import Expense
from app.models.user import User

from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate 

router = APIRouter()
@router.get("/stats/monthly")
def get_monthly_stats(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    total = crud_expense.get_monthly_total(db, user_id=current_user.id, month=month, year=year)
    return {"month": month, "year": year, "total_spent": total}

# 1. API THÊM KHOẢN CHI

@router.post("/", response_model=ExpenseOut)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    
    new_expense = models.Expense(
        amount=expense_in.amount,
        description=expense_in.description,  
        category_id=expense_in.category_id,
        date=expense_in.date,
        owner_id=current_user.id
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

# 2. API XEM DANH SÁCH (Của mình)
@router.get("/", response_model=List[ExpenseOut])
def read_my_expenses(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    return db.query(Expense).filter(Expense.owner_id == current_user.id).all()

# 3. API SỬA CHI TIÊU
@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Không tìm thấy khoản chi tiêu này")
    
    if expense.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa khoản chi này")
    
    # Cập nhật thông minh: Chỉ sửa field nào user gửi lên
    if expense_in.title is not None:
        expense.title = expense_in.title
    if expense_in.amount is not None:
        expense.amount = expense_in.amount
    if expense_in.description is not None:
        expense.description = expense_in.description

    db.commit()
    db.refresh(expense)
    return expense

# 4. API XÓA CHI TIÊU
@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Không tìm thấy khoản chi tiêu này")
    
    if expense.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa khoản chi này")
    
    db.delete(expense)
    db.commit()
    
    return {"message": "Đã xóa thành công"}
@router.get("/stats")
def get_expense_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Truy vấn: Nhóm theo danh mục và tính tổng tiền
    
    
    stats = db.query(
        Category.name,
        func.sum(Expense.amount).label("total_amount")
    ).join(Expense, Category.id == Expense.category_id)\
     .filter(Expense.owner_id == current_user.id)\
     .group_by(Category.name).all()

    # Chuyển đổi dữ liệu về dạng JSON đơn giản cho Frontend
    data = [{"category": name, "total": total} for name, total in stats]
    return data