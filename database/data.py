from pydantic import BaseModel
class users(BaseModel):
    name:str
    age:int
    number:str
    salary:int
class usersupdate(BaseModel):
    name:str
    age:int
    number:str
    salary:int


