from datetime import datetime, timedelta
from typing import List, Union
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm,SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import  ValidationError
from schema import ClassIn, ClassSchema, RoomIn, RoomSchema, User,Token,TokenData,UserInDB,UserIn,TodoIn,TodoSchema,CourseSchema,CourseIn,TimeTableIn,TimeTableSchema
from models import Class, Room, loginTable,Todo,Course,TimeTable
from connection import session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:3000/",
# ]

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# openssl rand -hex 32
SECRET_KEY = "af5e0fe38f983eb30e6eff86bb96d46071c7fe8bf80de8942d9e39ba9c08b193"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"basic": "Read options only", "advanced": "Read, write,add,delete"},
)

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def model_to_dict(model):
    """Convert a SQLAlchemy model object to a dictionary."""
    result = {}
    for key in model.__dict__.keys():
        if not key.startswith('_'):
            result[key] = model.__dict__[key]
    return result


def get_user(username: str):
    res = session.query(loginTable).filter(loginTable.username == username).all()
    if res:
        return UserInDB(**model_to_dict(res[0]))
    else:
        return None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user:
        if verify_password(password, user.password):
            return user
        else:
            return False
    else:
        return False


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["basic"])
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def delete_row(MyModel, row_username: str):
    row = session.query(MyModel).filter(MyModel.username == row_username).first()
    if row:
        session.delete(row)
        session.commit()
        return {"message": "Row deleted successfully."}
    else:
        return {"message": "Row not found."}
    
def delete_row_by_id(MyModel, row_id: str):
    row = session.query(MyModel).filter(MyModel.id == row_id).first()
    if row:
        session.delete(row)
        session.commit()
        return {"message": "Row deleted successfully."}
    else:
        return {"message": "Row not found."}   
    
@app.post("/token", response_model=Token,tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User,tags=["Users"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/users/add/",tags=["Users"])
async def add_user(user: UserIn, current_user: User = Security(get_current_active_user, scopes=["advanced"])):
    password = get_password_hash(user.password)
    new_user = loginTable(username=user.username,email=user.email,full_name=user.full_name,disabled=user.disabled,password=password)
    session.add(new_user)
    session.commit()
    return {"username":user.username}



@app.delete("/users/delete/",tags=["Users"])
def remove_user(user:UserIn,
    current_user: User = Security(get_current_active_user, scopes=["advanced"])
):
    res = delete_row(loginTable,user.username)
    session.commit()
    return res

@app.put("/users/update",tags=["Users"])
async def update_user(user : UserIn,current_user: User = Security(get_current_active_user, scopes=["advanced"])):
    res = session.query(loginTable).filter(loginTable.username == user.username).first()
    res.username,res.full_name,res.email,res.password,res.disabled = user.username,user.full_name,user.email,user.password,res.disabled
    session.commit()
    return model_to_dict(res)

@app.get("/users/all/",response_model=List[User],tags=["Users"])
async def fetch_all_users(
    current_user: User = Security(get_current_active_user, scopes=["advanced"])
):
    res = session.query(loginTable).filter(loginTable.disabled == False).all()
    result = [User(**model_to_dict(i)) for i in res]
    return result


@app.get("/todo/get",tags=["Todo"])
async def get_todos(current_user: User = Security(get_current_active_user,scopes=["basic"])):
    res = session.query(Todo).filter(Todo.username == current_user.username ).all()
    return [TodoSchema(**model_to_dict(i)) for i in res]

@app.post("/todo/add",tags=["Todo"])
async def post_todos(todo:TodoIn,current_user: User = Security(get_current_active_user,scopes=["basic"])):
    new_todo = Todo(username=current_user.username,todo=todo.todo,description=todo.description,status=todo.status)
    session.add(new_todo)
    session.commit()
    return {"message":"Added Successfully"}
@app.put("/todo/update",tags=["Todo"])
async def post_todos(todo:TodoSchema,current_user: User = Security(get_current_active_user,scopes=["basic"])):
    ut = session.query(Todo).filter(Todo.id == todo.id).first()
    ut.todo,ut.description,ut.status = todo.todo,todo.description,todo.status
    session.commit()
    return model_to_dict(todo)
    
@app.delete("/todo/remove",tags=["Todo"])
async def delete_todo(todo:TodoSchema,current_user: User = Security(get_current_active_user,scopes=["basic"])):
    res = session.query(Todo).filter(Todo.id == todo.id).first()
    if res:
        session.delete(res)
        session.commit()
        return {"message":"deleted Successfully"}
    else:
        return {"message":"Todo not Found"}
    

# Course
@app.get("/courses/",tags=["Courses"],response_model=List[CourseSchema])
async def get_courses():
    res = session.query(Course).all()
    return [model_to_dict(i) for i in res ]

@app.post("/courses/add",tags=["Courses"],response_model=CourseIn)
async def add_courses(course:CourseIn):
    new_course = Course(course_name = course.course_name,course_code = course.course_code,credit=course.credit)
    session.add(new_course)
    session.commit()
    return course

@app.put("/courses/update",tags=["Courses"])
async def update_course(course:CourseSchema):
    ut = session.query(Course).filter(Course.id == course.id).first()
    if ut:
        ut.course_name,ut.course_code,ut.credit = course.course_name,course.course_code,course.credit
        session.commit()
        return {"message":"Course Updated Successfully"}
    else:
        return {"message":"Row not Found"}

@app.delete("/courses/delete",tags=["Courses"])
async def delete_course(course:CourseSchema):
    res = delete_row_by_id(Course,course.id)
    return res


# Class
@app.get("/class/",tags=["Classes"],response_model=List[ClassSchema])
async def get_classes():
    res = session.query(Class).all()
    return [model_to_dict(i) for i in res ]

@app.post("/class/add",tags=["Classes"],response_model=ClassIn)
async def add_class(classes:ClassIn):
    new_class = Class(section_name = classes.section_name,department=classes.department,no_of_students=classes.no_of_students,capacity=classes.capacity)
    session.add(new_class)
    session.commit()
    return classes

    
@app.put("/class/update",tags=["Classes"])
async def update_class(classes:ClassSchema):
    ut = session.query(Class).filter(Class.id == classes.id).first()
    if ut:
        ut.section_name,ut.department,ut.no_of_students,ut.capacity = classes.section_name,classes.department,classes.no_of_students,classes.capacity
        session.commit()
        return {"message":"Classes Updated Successfully"}
    else:
        return {"message":"Row not Found"}

@app.delete("/class/delete",tags=["Classes"])
async def delete_class(classes:ClassSchema):
    res = delete_row_by_id(Course,classes.id)
    return res

#Room

@app.get("/room/",tags=["Room"],response_model=List[RoomSchema])
async def get_room():
    res = session.query(Room).all()
    return [model_to_dict(i) for i in res ]

@app.post("/room/add",tags=["Room"],response_model=RoomIn)
async def add_room(room:RoomIn):
    new_room = Room(room_name = room.room_name,capacity = room.capacity)
    session.add(new_room)
    session.commit()
    return room

@app.put("/room/update",tags=["Room"])
async def update_room(room:RoomSchema):
    ut = session.query(Room).filter(Room.id == room.id).first()
    if ut:
        ut.room_name,ut.capacity = room.room_name,room.capacity
        session.commit()
        return {"message":"room Updated Successfully"}
    else:
        return {"message":"Row not Found"}

@app.delete("/room/delete",tags=["Room"])
async def delete_room(room:RoomSchema):
    res = delete_row_by_id(Room,room.id)
    return res

# TimeTable

@app.get("/timetable/",tags=["timetable"],response_model=List[TimeTableSchema])
async def get_timetable():
    res = session.query(TimeTable).all()
    return [model_to_dict(i) for i in res ]

@app.post("/timetable/add",tags=["timetable"],response_model=TimeTableIn)
async def add_timetable(timetable:TimeTableIn):
    new_timetable = TimeTable(course_id = timetable.course_id,time = timetable.time,room_id = timetable.room_id, class_id=timetable.class_id,day = timetable.day)
    session.add(new_timetable)
    session.commit()
    return timetable

@app.put("/timetable/update",tags=["timetable"])
async def update_timetable(timetable:TimeTableSchema):
    ut = session.query(TimeTable).filter(TimeTable.id == timetable.id).first()
    if ut:
        ut.course_id, ut.time, ut.room_id, ut.class_id, ut.day = timetable.course_id,timetable.time, timetable.room_id, timetable.class_id,timetable.day
        session.commit()
        return {"message":"TimeTable Updated Successfully"}
    else:
        return {"message":"Row not Found"}

@app.delete("/timetable/delete",tags=["timetable"])
async def delete_room(timetable:TimeTableSchema):
    res = delete_row_by_id(TimeTable,timetable.id)
    return res


# Status
@app.get("/status/",tags=["Status"])
async def read_system_status():
    return {"status": "ok"}

# uncomment when using first time
# new_user = loginTable(username="admin",email="admin@admin",full_name="admin",disabled=False,password=get_password_hash("admin"))
# session.add(new_user)
# session.commit()

