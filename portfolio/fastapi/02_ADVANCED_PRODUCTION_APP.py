# Advanced FastAPI Examples - Complete Production App

import asyncio
from datetime import datetime, timedelta
from typing import Annotated, Optional
from enum import Enum

from fastapi import (
    FastAPI, Depends, HTTPException, status, Query, Path, 
    Body, Form, File, UploadFile, BackgroundTasks, WebSocket, 
    WebSocketDisconnect, Security, Request
)
from fastapi.security import (
    OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasic, 
    HTTPAuthorizationCredentials, SecurityScopes
)
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, validator, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt
from passlib.context import CryptContext
import logging
import httpx

# ===========================
# CONFIGURATION
# ===========================

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ===========================
# DATABASE SETUP
# ===========================

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1)

Base.metadata.create_all(bind=engine)

# ===========================
# PYDANTIC MODELS
# ===========================

class ItemBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    description: Optional[str] = Field(None, max_length=500)
    price: Annotated[float, Field(gt=0)]

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

# ===========================
# SECURITY
# ===========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"read:items": "Read items", "write:items": "Write items"}
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{" ".join(security_scopes.scopes)}"'
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
    except jwt.PyJWTError:
        raise credentials_exception
    
    if token_data.username is None:
        raise credentials_exception
    
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    
    return User(id=1, username=token_data.username, email="user@example.com", is_active=True)

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ===========================
# DATABASE DEPENDENCIES
# ===========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===========================
# LOGGING
# ===========================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===========================
# FASTAPI APP
# ===========================

app = FastAPI(
    title="Advanced FastAPI Application",
    description="Production-ready FastAPI with auth, DB, WebSocket",
    version="1.0.0"
)

# ===========================
# MIDDLEWARE
# ===========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# ===========================
# ROUTES - AUTHENTICATION
# ===========================

@app.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token endpoint.
    """
    user = User(id=1, username=form_data.username, email="user@example.com", is_active=True)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": ["read:items", "write:items"]},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Get current user information."""
    return current_user

# ===========================
# ROUTES - ITEMS
# ===========================

@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    current_user: Annotated[User, Security(get_current_active_user, scopes=["write:items"])],
    db: Annotated[Session, Depends(get_db)]
) -> Item:
    """Create a new item."""
    logger.info(f"User {current_user.username} creating item: {item.name}")
    
    db_item = ItemDB(
        name=item.name,
        description=item.description,
        price=item.price
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return Item(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        created_at=db_item.created_at
    )

@app.get("/items/", response_model=list[Item])
async def read_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["read:items"])],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    db: Annotated[Session, Depends(get_db)] = None
) -> list[Item]:
    """Read items with pagination."""
    logger.info(f"User {current_user.username} reading items")
    
    items = db.query(ItemDB).offset(skip).limit(limit).all()
    return [
        Item(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            created_at=item.created_at
        )
        for item in items
    ]

@app.get("/items/{item_id}", response_model=Item)
async def read_item(
    item_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
) -> Item:
    """Read a specific item."""
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return Item(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        created_at=db_item.created_at
    )

@app.put("/items/{item_id}", response_model=Item)
async def update_item(
    item_id: Annotated[int, Path(gt=0)],
    item: ItemCreate,
    current_user: Annotated[User, Security(get_current_active_user, scopes=["write:items"])],
    db: Annotated[Session, Depends(get_db)]
) -> Item:
    """Update an item."""
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    
    db.commit()
    db.refresh(db_item)
    
    return Item(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        created_at=db_item.created_at
    )

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Security(get_current_active_user, scopes=["write:items"])],
    db: Annotated[Session, Depends(get_db)]
) -> None:
    """Delete an item."""
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()

# ===========================
# ROUTES - FILE HANDLING
# ===========================

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    description: Annotated[str, Form()] = "",
    current_user: Annotated[User, Depends(get_current_active_user)] = None
) -> dict:
    """Upload a file."""
    logger.info(f"User {current_user.username} uploading file: {file.filename}")
    
    contents = await file.read()
    return {
        "filename": file.filename,
        "size": len(contents),
        "description": description,
        "content_type": file.content_type
    }

@app.post("/upload-multiple/")
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    current_user: Annotated[User, Depends(get_current_active_user)] = None
) -> dict:
    """Upload multiple files."""
    return {
        "files": [
            {
                "filename": file.filename,
                "content_type": file.content_type
            }
            for file in files
        ]
    }

# ===========================
# ROUTES - BACKGROUND TASKS
# ===========================

def send_email_task(email: str, message: str):
    """Simulate sending email."""
    logger.info(f"Sending email to {email}: {message}")

@app.post("/send-email/")
async def send_email(
    email: Annotated[str, Body()],
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)] = None
) -> dict:
    """Send email in background."""
    background_tasks.add_task(send_email_task, email, f"Hello from {current_user.username}")
    return {"message": "Email scheduled"}

# ===========================
# ROUTES - WEBSOCKET
# ===========================

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left the chat")

# ===========================
# ROUTES - HEALTH CHECK
# ===========================

@app.get("/health/")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}

# ===========================
# ERROR HANDLERS
# ===========================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
