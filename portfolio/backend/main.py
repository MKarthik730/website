from fastapi import FastAPI,Depends
from fastapi import HTTPException,status
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.data import users, usersupdate
from database.database import SessionLocal,engine
from database import databasemodels
from database.databasemodels import Users
from sqlalchemy.orm import Session
app=FastAPI()
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"," https://stupid-dancers-end.loca.lt"], 
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
def update_use(update:usersupdate,db:Session=Depends(get_db)):
    usr_v=db.query(Users).filter(Users.name==update.name).first()
    if usr_v:
        usr_v.name=update.name
        usr_v.age=update.age
        usr_v.number=update.number
        usr_v.salary=update.salary
    else:
        raise HTTPException(status_code=404,detail="user not found")
    db.add(usr_v)
    db.commit()
    db.refresh(usr_v)
    return usr_v

