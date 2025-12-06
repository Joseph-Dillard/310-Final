from sqlalchemy import Column, Integer, String, DECIMAL
from backend.models.base import Base

class Books(Base):
    __tablename__ = 'Books'
    book_no = Column(Integer, primary_key=True, autoincrement=True)
    book_name = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    price_buy = Column(DECIMAL(10, 2), nullable=False)
    price_rent = Column(DECIMAL(10, 2), nullable=False)
    no_available = Column(Integer, nullable=False)