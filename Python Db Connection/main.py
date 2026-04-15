
from fastapi import FastAPI,Depends,HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session,select,text

app = FastAPI()

class User(SQLModel, table=True): # user
    id:int | None = Field(default=None,primary_key=True)
    name:str
    age:int
    email:str
    password:str

# Db setup

engine = create_engine("sqlite:///database.db")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Dependency (session)
def get_session():
    with Session(engine) as session:
        yield session

# CRUD APIs

# Create User
@app.post('/users')
def create_user(user:User,session:Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Get All Users
@app.get('/users')
def get_users(session:Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

# Update User
@app.put('/users/{user_id}')
def update_user(user_id:int,updated_user:User,session:Session=Depends(get_session)):
    user = session.get(User,user_id)

    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    
    user.name = updated_user.name
    user.age = updated_user.age
    user.email = updated_user.email
    user.password = updated_user.password

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@app.get('/users/{user_id}')
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    statement = text("SELECT * FROM user WHERE id = :id")
    result = session.execute(statement,{"id":user_id}).mappings().first()

    if not result:
        raise HTTPException(status_code=404,detail="User not found")
    return result
    

@app.delete('/users/{user_id}')
def delete_user(user_id:int,session:Session=Depends(get_session)):
    user = session.get(User,user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    session.delete(user)
    session.commit()

    return {"message":"user deleted successfully"}
