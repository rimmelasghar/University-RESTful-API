import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, Integer, String,Boolean,UniqueConstraint
# from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class loginTable(Base):
    __tablename__ = 'login'

    id = Column(Integer, primary_key=True)
    username = Column(String(50),unique=True)
    full_name = Column(String(50))
    email = Column(String(50))
    password = Column(String(255))
    disabled = Column(Boolean, default=False)

    __table_args__ = (UniqueConstraint('username'),)

class Todo(Base):
    __tablename__ = "todo"
    
    id = Column(Integer,primary_key=True)
    username = Column(String(50))
    todo = Column(String(50))
    description = Column(String(255))
    status = Column(Boolean,default=False)
    
    
