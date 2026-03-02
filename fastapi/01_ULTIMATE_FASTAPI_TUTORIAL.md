# 🚀 ULTIMATE ADVANCED FASTAPI TUTORIAL 2026

**Complete Comprehensive Guide for Building Production-Ready FastAPI Applications**

---

## TABLE OF CONTENTS

1. [FastAPI Fundamentals](#fastapi-fundamentals)
2. [Advanced Request Handling](#advanced-request-handling)
3. [Authentication & Security](#authentication--security)
4. [Database Integration](#database-integration)
5. [Advanced Dependencies](#advanced-dependencies)
6. [WebSockets & Real-time](#websockets--real-time)
7. [Performance & Async](#performance--async)
8. [Testing & Debugging](#testing--debugging)
9. [Deployment Strategies](#deployment-strategies)
10. [Production Best Practices](#production-best-practices)

---

## FASTAPI FUNDAMENTALS

### What is FastAPI?

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python based on standard Python type hints. It's built on Starlette for the web parts and Pydantic for the data parts.

**Key Features:**
- **Fast**: High performance on par with NodeJS and Go
- **Fast to Code**: Increase development speed by 200-300%
- **Fewer Bugs**: Reduce human errors by ~40%
- **Intuitive**: Great IDE support and autocomplete
- **Easy to Learn**: Minimal documentation needed
- **Robust**: Production-ready with automatic interactive documentation
- **Standards-Based**: Built on OpenAPI and JSON Schema

### Installation

```bash
# Install with standard dependencies
pip install "fastapi[standard]"

# Or with specific packages
pip install fastapi uvicorn[standard] sqlalchemy pydantic python-dotenv
```

### Basic Hello World

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

Run with: `fastapi dev main.py`

---

## ADVANCED REQUEST HANDLING

### 1. Path Parameters with Validation

```python
from fastapi import FastAPI, Path
from typing import Annotated

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(gt=0, le=1000)],
    q: Annotated[str | None, Query(min_length=3)] = None
):
    return {"item_id": item_id, "q": q}
```

### 2. Query Parameters with Advanced Validation

```python
from fastapi import Query
from typing import Annotated

@app.get("/search/")
async def search(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    tags: Annotated[list[str] | None, Query()] = None
):
    return {"skip": skip, "limit": limit, "tags": tags}
```

### 3. Request Body with Pydantic Models

```python
from pydantic import BaseModel, Field, validator
from typing import Annotated

class Item(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    description: str | None = Field(None, max_length=500)
    price: Annotated[float, Field(gt=0)]
    tax: float | None = None
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Price must be positive')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Foo Item",
                "description": "A fantastic item",
                "price": 35.4,
                "tax": 3.2
            }
        }

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### 4. Header Parameters

```python
from fastapi import Header

@app.get("/headers/")
async def read_headers(
    user_agent: Annotated[str | None, Header()] = None,
    x_token: Annotated[str, Header()],
):
    return {"user_agent": user_agent, "x_token": x_token}
```

### 5. Cookie Parameters

```python
from fastapi import Cookie

@app.get("/cookies/")
async def read_cookies(
    session_id: Annotated[str | None, Cookie()] = None
):
    return {"session_id": session_id}
```

### 6. Form Data and File Uploads

```python
from fastapi import Form, File, UploadFile
from typing import Annotated

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    return {
        "filename": file.filename,
        "description": description,
        "content_type": file.content_type
    }

@app.post("/upload-multiple/")
async def upload_multiple(
    files: list[UploadFile] = File(...)
):
    return [{"filename": f.filename} for f in files]
```

### 7. Multiple Request Body Models

```python
from fastapi import Body

@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body()] = 0
):
    return {
        "item_id": item_id,
        "item": item,
        "user": user,
        "importance": importance
    }
```

---

## AUTHENTICATION & SECURITY

### 1. OAuth2 with Password (Hashing)

```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Annotated
import jwt

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

# Database (mock)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lm",
        "disabled": False,
    }
}

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(fake_db, username: str, password: str):
    user = fake_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = fake_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Routes
app = FastAPI()

@app.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
```

### 2. OAuth2 with Scopes

```python
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"read:items": "Read items", "write:items": "Write items"}
)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{" ".join(security_scopes.scopes)}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    # Validate token with scopes...
    return user

@app.get("/items/")
async def read_items(
    current_user: Annotated[User, Security(get_current_user, scopes=["read:items"])]
):
    return [{"item_name": "Foo"}]
```

### 3. HTTP Basic Authentication

```python
from fastapi.security import HTTPBasic, HTTPAuthorizationCredentials
import base64

security = HTTPBasic()

@app.get("/basic-auth/")
async def basic_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"username": credentials.username}
```

---

## DATABASE INTEGRATION

### 1. SQLAlchemy Setup

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Annotated
from fastapi import Depends

# Database URL (use PostgreSQL, MySQL, SQLite, etc.)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # For SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Models
class ItemDB(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Float)

Base.metadata.create_all(bind=engine)

# Schemas
class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float

class Item(ItemCreate):
    id: int
    
    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD operations
def create_item(db: Session, item: ItemCreate):
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ItemDB).offset(skip).limit(limit).all()

def get_item(db: Session, item_id: int):
    return db.query(ItemDB).filter(ItemDB.id == item_id).first()

# Routes
app = FastAPI()

@app.post("/items/", response_model=Item)
def create_item_route(
    item: ItemCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return create_item(db=db, item=item)

@app.get("/items/", response_model=list[Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Annotated[Session, Depends(get_db)] = None
):
    items = get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=Item)
def read_item(
    item_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    db_item = get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
```

### 2. Alembic Migrations

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Create initial tables"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## ADVANCED DEPENDENCIES

### 1. Dependency Injection System

```python
from fastapi import Depends

# Simple dependency
def common_parameters(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}

# Class-based dependency
class CommonQueryParams:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: Annotated[CommonQueryParams, Depends()]):
    return {"skip": commons.skip, "limit": commons.limit}

# Sub-dependencies
def get_query(commons: Annotated[CommonQueryParams, Depends()]):
    return commons.skip

@app.get("/items-sub/")
async def read_items_sub(skip: Annotated[int, Depends(get_query)]):
    return {"skip": skip}
```

### 2. Dependencies with Yield (Context Manager)

```python
async def get_db():
    print("Creating DB connection")
    # Setup
    db = "connection"
    yield db
    # Teardown
    print("Closing DB connection")

@app.get("/items/")
async def read_items(db: str = Depends(get_db)):
    return {"db": db}
```

### 3. Global Dependencies

```python
@app.get("/items/", dependencies=[Depends(verify_token)])
async def read_items():
    return [{"item": "Foo"}]
```

---

## WEBSOCKETS & REAL-TIME

### 1. Basic WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"client_id": client_id, "data": data})
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
```

### 2. Multiple WebSocket Connections (Broadcast)

```python
from typing import Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left the chat")
```

---

## PERFORMANCE & ASYNC

### 1. Async/Await Best Practices

```python
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor

# Using async
@app.get("/async-items/")
async def get_async_items():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/items")
    return response.json()

# CPU-bound tasks in thread pool
executor = ThreadPoolExecutor(max_workers=4)

@app.get("/cpu-task/")
async def cpu_task():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, heavy_computation)
    return {"result": result}

def heavy_computation():
    # Long-running CPU task
    return sum(i * i for i in range(100000000))

# Parallel requests
@app.get("/parallel-requests/")
async def parallel_requests():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            client.get("https://api.example.com/1"),
            client.get("https://api.example.com/2"),
            client.get("https://api.example.com/3"),
        )
    return [r.json() for r in results]
```

### 2. Background Tasks

```python
from fastapi import BackgroundTasks
import time

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")

@app.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(write_log, f"Notification sent to {email}")
    return {"message": "Notification sent in the background"}

# Multiple background tasks
@app.post("/send-notification-advanced/")
async def send_notification_advanced(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(write_log, f"Notification sent to {email}")
    background_tasks.add_task(send_email, email)
    background_tasks.add_task(update_analytics, email)
    return {"message": "Notification sent"}
```

---

## TESTING & DEBUGGING

### 1. Testing with pytest

```python
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)

def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["item_id"] == 1

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Foo", "price": 42.0}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Foo"

def test_invalid_item():
    response = client.get("/items/invalid")
    assert response.status_code == 422

# Async tests
@pytest.mark.asyncio
async def test_async_operation():
    response = client.get("/async-items/")
    assert response.status_code == 200
```

### 2. Error Handling

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(
            status_code=400,
            detail="Item ID must be positive"
        )
    # ... rest of implementation

# Custom exception handler
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )
```

---

## DEPLOYMENT STRATEGIES

### 1. Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db/dbname
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 2. Production Server Configuration

```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# Or use Uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Environment Variables

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    database_url: str
    secret_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()

# .env file
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
DEBUG=False
```

---

## PRODUCTION BEST PRACTICES

### 1. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Middleware

```python
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])

@app.middleware("http")
async def add_process_time_header(request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 3. Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.get("/items/")
async def read_items():
    logger.info("Reading items")
    logger.warning("Something might be wrong")
    logger.error("Something went wrong")
    return [{"item": "Foo"}]
```

### 4. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/items/", dependencies=[Depends(limiter.limit("100/minute"))])
async def read_items():
    return [{"item": "Foo"}]
```

### 5. Monitoring & Metrics

```python
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_TIME = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

@app.middleware("http")
async def add_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_TIME.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

---

## ADVANCED PATTERNS

### 1. Custom Response Classes

```python
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse

@app.get("/html/")
async def get_html():
    return HTMLResponse(content="<h1>Hello World</h1>")

@app.get("/file/")
async def download_file():
    return FileResponse("path/to/file.pdf")

@app.get("/stream/")
async def stream_data():
    async def generate():
        for i in range(10):
            yield f"data: {i}\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 2. GraphQL Integration

```python
from strawberry.fastapi import GraphQLRouter
import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello world"

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")
```

### 3. Request/Response Hooks

```python
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Before request
    print(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # After request
    print(f"Response: {response.status_code}")
    return response
```

---

## SUMMARY OF KEY CONCEPTS

| Concept | Purpose |
|---------|---------|
| **Path Parameters** | Dynamic URL segments |
| **Query Parameters** | URL query strings |
| **Request Body** | JSON data in POST/PUT |
| **Headers/Cookies** | HTTP metadata |
| **Dependencies** | Code reuse and DI |
| **Security** | Authentication & authorization |
| **Database** | Data persistence |
| **Async/Await** | Concurrent processing |
| **WebSockets** | Real-time bidirectional communication |
| **Testing** | Quality assurance |
| **Deployment** | Production readiness |

---

**Last Updated:** January 2026
**FastAPI Version:** 4.0+
**Python Version:** 3.8+
