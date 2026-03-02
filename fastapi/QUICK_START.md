# 🚀 FASTAPI QUICK START GUIDE

**Get up and running in 5 minutes**

---

## INSTALLATION

```bash
# 1. Create project directory
mkdir my_fastapi_app
cd my_fastapi_app

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install FastAPI
pip install "fastapi[standard]"
```

---

## BASIC APP (main.py)

```python
from fastapi import FastAPI

app = FastAPI(title="My API")

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

**Run:**
```bash
fastapi dev main.py
```

**Visit:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## WITH DATABASE (main.py)

```python
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# Database
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model
class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(float)

Base.metadata.create_all(bind=engine)

# Schema
class Item(BaseModel):
    name: str
    price: float

# App
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/items/")
async def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemDB(name=item.name, price=item.price)
    db.add(db_item)
    db.commit()
    return db_item

@app.get("/items/")
async def read_items(db: Session = Depends(get_db)):
    return db.query(ItemDB).all()
```

---

## WITH AUTHENTICATION (main.py)

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Annotated

# Config
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class User(BaseModel):
    username: str
    email: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str

# Database (mock)
fake_users = {
    "user1": {
        "username": "user1",
        "email": "user1@example.com",
        "hashed_password": pwd_context.hash("password123")
    }
}

# Functions
def authenticate_user(username: str, password: str):
    user = fake_users.get(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user

def create_access_token(username: str):
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

# App
app = FastAPI()

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(username: str = Depends(get_current_user)):
    return {"username": username}
```

---

## WITH WEBSOCKET (main.py)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## TESTING (test_main.py)

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["Hello"] == "World"

def test_read_item():
    response = client.get("/items/1?q=test")
    assert response.status_code == 200
    assert response.json()["item_id"] == 1

def test_create_item():
    response = client.post("/items/", json={"name": "Test", "price": 99.99})
    assert response.status_code == 200
```

**Run Tests:**
```bash
pip install pytest
pytest test_main.py -v
```

---

## DOCKER (Dockerfile)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
pytest==7.4.3
```

**Build & Run:**
```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

---

## ENVIRONMENT VARIABLES (.env)

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./test.db
DEBUG=False
```

**Use in Code:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## COMMON ENDPOINTS PATTERN

```python
# CREATE
@app.post("/items/", status_code=201)
async def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    return db_item

# READ ALL
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ItemDB).offset(skip).limit(limit).all()

# READ ONE
@app.get("/items/{item_id}")
async def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

# UPDATE
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, db: Session = Depends(get_db)):
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    db_item.name = item.name
    db_item.price = item.price
    db.commit()
    return db_item

# DELETE
@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_item)
    db.commit()
```

---

## VALIDATION

```python
from pydantic import BaseModel, Field, validator
from typing import Annotated

class Item(BaseModel):
    # Field validation
    name: Annotated[str, Field(min_length=1, max_length=100)]
    price: Annotated[float, Field(gt=0, decimal_places=2)]
    description: str | None = Field(None, max_length=500)
    
    # Custom validation
    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.isalpha():
            raise ValueError('Name must contain only letters')
        return v

# Query validation
@app.get("/items/")
async def read_items(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 10
):
    return {"skip": skip, "limit": limit}

# Path validation
@app.get("/items/{item_id}")
async def read_item(item_id: Annotated[int, Path(gt=0)] = 0):
    return {"item_id": item_id}
```

---

## DEPLOYMENT CHECKLIST

- [ ] Install all dependencies
- [ ] Set environment variables
- [ ] Create database
- [ ] Run migrations
- [ ] Run tests
- [ ] Build Docker image
- [ ] Test Docker image
- [ ] Push to registry
- [ ] Deploy to server
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up HTTPS
- [ ] Monitor logs
- [ ] Set up health checks
- [ ] Configure backups

---

## USEFUL COMMANDS

```bash
# Create requirements.txt
pip freeze > requirements.txt

# Run with auto-reload
fastapi dev main.py

# Run tests with coverage
pytest --cov=.

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Docker build
docker build -t app .

# Docker run
docker run -p 8000:8000 app
```

---

## 📚 NEXT STEPS

1. ✅ Run a basic app
2. ✅ Add database
3. ✅ Add authentication
4. ✅ Add WebSocket
5. ✅ Write tests
6. ✅ Deploy with Docker
7. 📖 Read full tutorial: `01_ULTIMATE_FASTAPI_TUTORIAL.md`
8. 🔍 Review production code: `02_ADVANCED_PRODUCTION_APP.py`
9. 🧪 Study tests: `03_COMPREHENSIVE_TESTS.py`
10. 🚀 Deploy to production: `04_DEPLOYMENT_GUIDE.md`

---

## 💡 PRO TIPS

1. **Use Async** - Always use `async def` for I/O operations
2. **Type Hints** - FastAPI validates based on type hints
3. **Depends** - Use dependency injection for cleaner code
4. **Validate** - Use Pydantic models for automatic validation
5. **Document** - Add docstrings to endpoints
6. **Test** - Write tests as you code
7. **Secure** - Use authentication and HTTPS
8. **Monitor** - Log and monitor production apps
9. **Version** - Use semantic versioning
10. **Backup** - Always backup your database

---

**You're ready to build amazing APIs! 🎉**
