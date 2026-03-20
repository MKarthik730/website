from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()
class Users(Base):
    __tablename__="database"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String)
    age=Column(Integer)
    number=Column(String(15))
    salary=Column(Integer)