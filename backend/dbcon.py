from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Database connection string
db_url = 'mysql+mysqlconnector://root:password@localhost/bookstore'
# Create an engine
engine = create_engine(db_url, echo=True) 
# Create a configured "Session" class
Session = sessionmaker(bind=engine)

def db_con():
    db = Session()
    try:
        yield db
    finally:
        db.close()