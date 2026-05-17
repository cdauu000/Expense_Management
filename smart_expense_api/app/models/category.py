from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")