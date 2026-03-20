# FastAPI Advanced Reference & Cheat Sheet

## QUICK START

```python
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Run: fastapi dev main.py
```

---

## ROUTING & HTTP METHODS

```python
# GET - Retrieve data
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# POST - Create data
@app.post("/items/")
async def create_item(item: Item):
    return item

# PUT - Update entire resource
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return item

# PATCH - Partial update
@app.patch("/items/{item_id}")
async def patch_item(item_id: int, item: ItemUpdate):
    return item

# DELETE - Remove resource
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"deleted": True}

# HEAD - Like GET but no body
@app.head("/items/{item_id}")
async def read_item_head(item_id: int):
    return

# OPTIONS - Describe communication options
@app.options("/items/")
async def options_items():
    return
```

---

## PATH PARAMETERS

```python
from fastapi import Path
from typing import Annotated

# Basic path parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# With validation
@app.get("/items/{item_id}")
async def read_item(item_id: Annotated[int, Path(gt=0, le=1000)]):
    return {"item_id": item_id}

# Multiple path parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: int):
    return {"user_id": user_id, "item_id": item_id}

# String path with options
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

# Enum path parameter
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    return {"model_name": model_name}
```

---

## QUERY PARAMETERS

```python
from fastapi import Query

# Basic query parameter
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# With validation
@app.get("/items/")
async def read_items(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 10
):
    return {"skip": skip, "limit": limit}

# Required query parameter
@app.get("/items/")
async def read_items(required_param: Annotated[str, Query(...)]):
    return {"required_param": required_param}

# List query parameters
@app.get("/items/")
async def read_items(tags: Annotated[list[str], Query()] = []):
    return {"tags": tags}

# Query: /items/?tags=foo&tags=bar

# Regex validation
@app.get("/items/")
async def read_items(
    q: Annotated[str, Query(regex="^[a-z]+$")] = None
):
    return {"q": q}
```

---

## REQUEST BODY

```python
from pydantic import BaseModel, Field, validator

# Simple model
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item

# Nested models
class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    address: Address

@app.post("/users/")
async def create_user(user: User):
    return user

# With validation
class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, decimal_places=2)
    
    @validator('name')
    def name_must_not_contain_numbers(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError('Name must not contain numbers')
        return v

# Multiple body parameters
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body()] = 0
):
    return {"item_id": item_id, "item": item, "user": user, "importance": importance}
```

---

## HEADERS & COOKIES

```python
from fastapi import Header, Cookie

# Header parameter
@app.get("/headers/")
async def read_header(
    user_agent: Annotated[str | None, Header()] = None
):
    return {"User-Agent": user_agent}

# Required header
@app.get("/headers/")
async def read_header(
    x_token: Annotated[str, Header()]
):
    return {"X-Token": x_token}

# Cookie parameter
@app.get("/cookies/")
async def read_cookie(
    session_id: Annotated[str | None, Cookie()] = None
):
    return {"session_id": session_id}

# Set cookie in response
from fastapi.responses import JSONResponse

@app.post("/login/")
async def login():
    response = JSONResponse({"login": True})
    response.set_cookie(key="session_id", value="some_value")
    return response
```

---

## FORM DATA & FILES

```python
from fastapi import Form, File, UploadFile

# Form data
@app.post("/login/")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    return {"username": username}

# File upload
@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...)
):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents)}

# Multiple files
@app.post("/upload-multiple/")
async def upload_multiple(
    files: list[UploadFile] = File(...)
):
    return [{"filename": f.filename} for f in files]

# File + form data
@app.post("/upload-with-metadata/")
async def upload_with_metadata(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    return {"filename": file.filename, "description": description}
```

---

## RESPONSE MODELS

```python
# Basic response model
@app.get("/items/", response_model=list[Item])
async def read_items():
    return items

# Exclude fields in response
@app.get("/items/", response_model=Item, response_model_exclude={"password"})
async def read_item():
    return item

# Include only specific fields
@app.get("/items/", response_model=Item, response_model_include={"name", "price"})
async def read_item():
    return item

# Custom response
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse

@app.get("/html/")
async def get_html():
    return HTMLResponse("<h1>Hello</h1>")

@app.get("/file/")
async def download_file():
    return FileResponse("path/to/file.pdf")

# Streaming response
@app.get("/stream/")
async def stream():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## STATUS CODES

```python
from fastapi import status

# Explicit status code
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item

# Common status codes
200 - OK (default for GET)
201 - Created (default for POST with response_model)
202 - Accepted
204 - No Content (default for DELETE)
301 - Moved Permanently
304 - Not Modified
400 - Bad Request
401 - Unauthorized
403 - Forbidden
404 - Not Found
405 - Method Not Allowed
409 - Conflict
422 - Unprocessable Entity (validation error)
500 - Internal Server Error
503 - Service Unavailable
```

---

## ERROR HANDLING

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Raise HTTPException
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(
            status_code=400,
            detail="Item ID must be positive"
        )
    return {"item_id": item_id}

# Custom exception handler
class CustomException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": f"Error: {exc.name}"}
    )

# Validation error handler
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )
```

---

## DEPENDENCIES

```python
from fastapi import Depends

# Function dependency
def common_params(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(params: dict = Depends(common_params)):
    return params

# Class dependency
class CommonParams:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonParams = Depends()):
    return {"skip": commons.skip, "limit": commons.limit}

# Dependency with yield (setup/teardown)
async def get_db():
    db = "connection"
    try:
        yield db
    finally:
        print("Closing connection")

# Sub-dependencies
def get_skip():
    return 0

def get_limit(skip: int = Depends(get_skip)):
    return 100 - skip

# Global dependencies
@app.get("/items/", dependencies=[Depends(verify_token)])
async def read_items():
    return []
```

---

## SECURITY & AUTHENTICATION

```python
from fastapi.security import (
    OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasic
)
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

# OAuth2 with Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

@app.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}

# JWT token creation
def create_access_token(username: str, expires_delta: timedelta | None = None):
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

## MIDDLEWARE

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])

# Custom middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response

# GZip compression
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

---

## WEBSOCKETS

```python
from fastapi import WebSocket, WebSocketDisconnect

# Simple WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

# Broadcasting
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
    
    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)
    
    async def broadcast(self, message: str):
        for connection in self.active:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(ws: WebSocket, client_id: int):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(ws)
```

---

## BACKGROUND TASKS

```python
from fastapi import BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")

@app.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(write_log, f"Sent to {email}")
    return {"message": "Sent"}
```

---

## ENVIRONMENT VARIABLES

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI"
    debug: bool = False
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## TESTING

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_create_item():
    response = client.post("/items/", json={"name": "Test", "price": 10})
    assert response.status_code == 201
```

---

## COMMON PATTERNS

### Search with Filters
```python
@app.get("/items/")
async def search_items(
    q: str | None = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "name"
):
    # Implement search logic
    return []
```

### Pagination
```python
@app.get("/items/")
async def read_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * page_size
    return items[offset:offset + page_size]
```

### Soft Delete
```python
@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    item.is_deleted = True
    db.commit()
```

### Bulk Operations
```python
@app.post("/items/bulk/")
async def create_items_bulk(items: list[ItemCreate]):
    created = [create_item(item) for item in items]
    return created
```

### Export Data
```python
@app.get("/export/")
async def export_data():
    import csv
    from fastapi.responses import StreamingResponse
    
    def generate():
        yield "id,name,price\n"
        for item in items:
            yield f"{item.id},{item.name},{item.price}\n"
    
    return StreamingResponse(generate(), media_type="text/csv")
```

---

## USEFUL DECORATORS

```python
# Include in OpenAPI
@app.get("/items/", include_in_schema=True)

# Exclude from OpenAPI
@app.get("/internal/", include_in_schema=False)

# Tags for documentation
@app.get("/items/", tags=["items"])

# Summary and description
@app.get("/items/", summary="List items", description="Get all items")

# Deprecated
@app.get("/old-endpoint/", deprecated=True)

# Response description
@app.get("/items/", responses={404: {"description": "Item not found"}})
```

---

**FastAPI Version:** 4.0+
**Python:** 3.8+
**Last Updated:** January 2026
