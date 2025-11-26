from fastapi import FastAPI,Depends
from fastapi import HTTPException,status
from data import users
from database import SessionLocal,engine
import databasemodels
from databasemodels import Users
from sqlalchemy.orm import Session
app=FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

databasemodels.Base.metadata.create_all(bind=engine)

def get_db():
    db_instance = SessionLocal()
    try:
        yield db_instance        
    finally:
        db_instance.close()  
@app.get("/")
def login():
    return "hello"

@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(Users).all()


@app.post("/users")
def add_user(usr: users, db: Session = Depends(get_db)):
    new_user = databasemodels.Users(
        name=usr.name,
        age=usr.age,
        number=usr.number,
        salary=usr.salary
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
@app.delete('/users/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id:int, db: Session=Depends(get_db)):
    d_user=db.query(Users).filter(Users.id==id).first()
    if d_user:
        db.delete(d_user)
        db.commit()
        return
    else:
        raise HTTPException(status_code=404, detail="not found")
   
@app.get("/users/search")
def search_user(name:str, db:Session=Depends(get_db)):
    usr_v=db.query(Users).filter(Users.name==name).first()
    if not usr_v:
        raise HTTPException(status_code=404,detail="user not found")
    else:
        return usr_v
    return None
@app.put("/users")
def update_use(name:str ,age:int,number:str , salary: int ,db:Session=Depends(get_db)):
    usr_v=db.query(Users).filter(Users.name==name).first()
    if usr_v:
        usr_v.name=name
        usr_v.age=age
        usr_v.number=number
        usr_v.salary=salary
    else:
        raise HTTPException(status_code=404,detail="user not found")
    db.add(usr_v)
    db.commit()
    db.refresh(usr_v)
    db.close()

