from fastapi import FastAPI,Header,Cookie
import asyncio
from user_from import Users,MessageResponse 
from typing import Annotated
app=FastAPI()

@app.get('/',response_model=MessageResponse)
async def init_page():
    return MessageResponse(message="welcome to this website")
@app.get("/users")
async def users():
    return "all users"
@app.get("/users/{name}")
async def user_det(name:str):
    return f'user name:{name}'
@app.get('/headers')
async def headers(x_token:Annotated[str,Header()]):
    return MessageResponse(message="Token:{x_token}")
@app.get('/cookie')
async def cookie(x_token:Annotated[str,Cookie()]):
    return MessageResponse(message='token:{x_token}')