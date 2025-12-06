from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from backend.models.base import Base

class Order_details(Base):
    __tablename__ = 'Order_details'
    item_no = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(Integer, nullable=False)
    book_no = Column(Integer, nullable=False)
    purchase_type = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)