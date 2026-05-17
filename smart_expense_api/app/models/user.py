from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    username = Column(String(255), unique=True, index=True) 
    email = Column(String(255), unique=True, index=True)    
    password = Column(String(255))                          
    is_active = Column(Boolean, default=True)

    items = relationship("Expense", back_populates="owner")
    categories = relationship("Category", back_populates="owner")
    budgets = relationship("Budget", back_populates="owner")