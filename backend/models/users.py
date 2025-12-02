from sqlalchemy import create_engine, Column, Integer, String, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
# Define a base class for our models
Base = declarative_base()
# Define the Employee model, which corresponds to an 'employees' table
class users(Base):
    __tablename__ = 'users'
    user_no = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(Integer, nullable=False)  # 0 for customer, 1 for admin