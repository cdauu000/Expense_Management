from pydantic import BaseModel
from typing import Optional

# --- 1. Base Schema
class BudgetBase(BaseModel):
    amount: float
    month: int
    year: int
    category_id: Optional[int] = None

# --- 2. Schema Create
class BudgetCreate(BudgetBase):
    pass

# --- 3. Schema Update

class BudgetUpdate(BaseModel):
    amount: Optional[float] = None
    month: Optional[int] = None
    year: Optional[int] = None
    category_id: Optional[int] = None

# --- 4. Schema Out 

class BudgetOut(BudgetBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


Budget = BudgetOut