from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
from models import Base

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:03322593149@127.0.0.1:3306/testdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

# Define a SQLAlchemy model
session = SessionLocal()
Base.metadata.create_all(engine)