from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

Base = declarative_base()

class Orders(Base):
    __tablename__ = "Orders"
    order_no = Column(Integer, primary_key=True, autoincrement=True)
    user_no = Column(Integer, foreignkey=True, nullable=False)
    status = Column(Integer, nullable=True)
    tot_price = Column(DECIMAL(10,2), nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)
