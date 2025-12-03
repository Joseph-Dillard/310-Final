from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
# Define a base class for our models
Base = declarative_base()
# Define the Employee model, which corresponds to an 'employees' table
class order_details(Base):
    __tablename__ = 'Order_details'
    item_no = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(Integer, foreign_key=True, nullable=False)
    book_no = Column(Integer, foreign_key=True, nullable=False)
    purchase_type = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)