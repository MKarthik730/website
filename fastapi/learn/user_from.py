from pydantic import BaseModel,Field,field_validator
class Users(BaseModel):
    name:str=Field(...,description="name of user")
    age:int=Field(...,description="age of use")
    balance:float=Field(..., description="balance of user")

    @field_validator('age')
    @classmethod
    def validate_age(cls,v):
        if(v<18):
            raise ValueError("age should be greater than 18")
        return v
    @field_validator('balance')
    @classmethod
    def validate_balance(cls,v):
        if v<0:
            raise ValueError("very low balance")
        return v
class MessageResponse(BaseModel):
    """Simple message response"""
    message: str