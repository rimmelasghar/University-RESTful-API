from pydantic import BaseModel, ValidationError
from typing import List, Union


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserIn(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    password: str

class UserInDB(User):
    password: str
    
class TodoSchema(BaseModel):
    id : int
    username: str
    todo : str
    description: Union[str,None] = None
    status: Union[bool, None] = None
    
class TodoIn(BaseModel):
    todo : str
    description: Union[str,None] = None
    status: Union[bool, None] = None

class CourseSchema(BaseModel):
    id : int
    course_name : str
    course_code : str
    credit : int

class CourseIn(BaseModel):
    course_name : str
    course_code : str
    credit : int

class ClassSchema(BaseModel):
    id : int
    section_name : str
    department : str
    no_of_students : int
    capacity : int

class ClassIn(BaseModel):
    section_name : str
    department : str
    no_of_students : int
    capacity : int

class RoomSchema(BaseModel):
    id : int
    room_name : str
    capacity : int

class RoomIn(BaseModel):
    room_name : str
    capacity : int