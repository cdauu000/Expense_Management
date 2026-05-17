from sqlalchemy import Column, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    month = Column(Integer)
    year = Column(Integer)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Quan hệ
    owner = relationship("User", back_populates="budgets")