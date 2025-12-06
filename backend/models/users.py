from sqlalchemy import Column, Integer, String, DECIMAL
from backend.models.base import Base

class Users(Base):
    __tablename__ = 'users'
    user_no = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Integer, nullable=False, default=0)  # 0 for customer, 1 for admin