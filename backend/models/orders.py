from sqlalchemy import Column, Integer, DECIMAL, ForeignKey
from backend.models.base import Base

class Orders(Base):
    __tablename__ = "Orders"
    order_no = Column(Integer, primary_key=True, autoincrement=True)
    user_no = Column(Integer, nullable=False)
    status = Column(Integer, nullable=True)  # 0 for curr cart, 1 for completed order
    tot_price = Column(DECIMAL(10, 2), nullable=True)
    payment_status = Column(Integer, nullable=True)  # 1 for pending, 2 for paid