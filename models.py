import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, Integer, String,Boolean,UniqueConstraint,Time,ForeignKeyConstraint, Enum
import enum
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
    
class Room(Base):
    __tablename__ = "room"
    
    id = Column(Integer,primary_key = True)
    room_name = Column(String(255))
    capacity = Column(Integer)

class Course(Base):
    __tablename__ = "course"
    
    id = Column(Integer,primary_key = True)
    course_name = Column(String(255))
    course_code = Column(String(255))
    credit = Column(Integer)
   
class Class(Base):
    __tablename__ = "class"
    
    id = Column(Integer,primary_key = True)
    section_name = Column(String(255))
    department = Column(String(255))
    no_of_students = Column(Integer)
    capacity = Column(Integer)


class MyChoiceDay(enum.Enum):
    MONDAY  = 'MONDAY'  
    TUESDAY  = 'TUESDAY' 
    WEDNESDAY = 'WEDNESDAY'   
    THURSDAY = 'THURSDAY'            
    FRIDAY   = 'FRIDAY'  

class TimeTable(Base):
    __tablename__ = "timetable"
    
    id = Column(Integer,primary_key = True)
    course_id = Column(Integer)
    time = Column(Time)
    room_id = Column(Integer)
    class_id = Column(Integer)
    day = Column(Enum(MyChoiceDay))
    
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['course.id']),
        ForeignKeyConstraint(['class_id'], ['class.id']),
        ForeignKeyConstraint(['room_id'], ['room.id']),
    )    