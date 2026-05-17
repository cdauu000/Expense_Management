from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.budget import Budget
from app.models.expense import Expense
from app.models.category import Category
from app.schemas.budget import BudgetCreate

def create_or_update_budget(db: Session, budget_in: BudgetCreate, user_id: int):
    # Kiểm tra xem đã có hạn mức cho danh mục này trong tháng này chưa
    existing_budget = db.query(Budget).filter(
        Budget.owner_id == user_id,
        Budget.category_id == budget_in.category_id,
        Budget.month == budget_in.month,
        Budget.year == budget_in.year
    ).first()

    if existing_budget:
        # Nếu có rồi thì cập nhật số tiền mới
        existing_budget.amount = budget_in.amount
        db.commit()
        db.refresh(existing_budget)
        return existing_budget
    else:
        # Nếu chưa có thì tạo mới
        new_budget = Budget(**budget_in.dict(), owner_id=user_id)
        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)
        return new_budget

def get_budget_status(db: Session, user_id: int, month: int, year: int):
    # 1. Lấy tất cả các hạn mức (Budget) user đã đặt trong tháng
    budgets = db.query(Budget).filter(
        Budget.owner_id == user_id, Budget.month == month, Budget.year == year
    ).all()

    result = []
    for b in budgets:
        # 2. Tính tổng tiền ĐÃ TIÊU cho danh mục này
        spent = db.query(func.sum(Expense.amount)).filter(
            Expense.owner_id == user_id,
            Expense.category_id == b.category_id,
            func.extract('month', Expense.date_added) == month,
            func.extract('year', Expense.date_added) == year
        ).scalar() or 0 # Nếu chưa tiêu gì thì là 0

        # 3. Tính toán cảnh báo
        remaining = b.amount - spent
        warning_msg = "OK"
        if remaining < 0:
            warning_msg = "VƯỢT QUÁ HẠN MỨC!"
        elif remaining < (b.amount * 0.2): # Còn dưới 20%
            warning_msg = "Sắp hết hạn mức!"

        # 4. Gom dữ liệu trả về
        result.append({
            "id": b.id,
            "category_name": b.category.name,
            "limit_amount": b.amount,
            "spent_amount": spent,
            "remaining": remaining,
            "warning": warning_msg
        })
    
    return result