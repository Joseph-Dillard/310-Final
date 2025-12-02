from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
# Define a base class for our models
Base = declarative_base()
# Define the Employee model, which corresponds to an 'employees' table
class books(Base):
    __tablename__ = 'Books'
    book_no = Column(Integer, primary_key=True, autoincrement=True)
    book_name = Column(String(50), nullable=False)
    author = Column(String(50), nullable=False)
    price_buy = Column(DECIMAL(10, 2), nullable=False)
    price_rent = Column(DECIMAL(10, 2), nullable=False)
    no_available = Column(Integer, nullable=False)