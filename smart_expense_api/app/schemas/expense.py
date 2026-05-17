from pydantic import BaseModel
from typing import Optional
from datetime import date
from .category import Category 

# --- 1. Base Schema 
class ExpenseBase(BaseModel):
    amount: float
    category_id: int
    description: Optional[str] = None
    date: date
   
# --- 2. Schema Create 
class ExpenseCreate(ExpenseBase):
    pass

# --- 3. Schema Update 

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    date: Optional[date] = None

# --- 4. Schema Out 

class ExpenseOut(ExpenseBase):
    id: int
    owner_id: int
    category: Optional[Category] = None 

    class Config:
        from_attributes = True

Expense = ExpenseOut