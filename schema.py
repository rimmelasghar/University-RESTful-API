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