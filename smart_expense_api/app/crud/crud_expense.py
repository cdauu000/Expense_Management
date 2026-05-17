from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate

from sqlalchemy import func
from datetime import datetime

def create_expense(db: Session, expense: ExpenseCreate, user_id: int):
    db_expense = Expense(**expense.dict(), owner_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_multi_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(Expense)\
             .filter(Expense.owner_id == owner_id)\
             .offset(skip)\
             .limit(limit)\
             .all()
             
def get_monthly_total(db: Session, user_id: int, month: int, year: int):
    # Tính tổng tiền (amount) của user trong tháng/năm cụ thể
    result = db.query(func.sum(Expense.amount))\
               .filter(Expense.owner_id == user_id)\
               .filter(func.extract('month', Expense.date_added) == month)\
               .filter(func.extract('year', Expense.date_added) == year)\
               .scalar()
    # Nếu chưa tiêu gì thì trả về 0, ngược lại trả về số tiền
    return result if result else 0