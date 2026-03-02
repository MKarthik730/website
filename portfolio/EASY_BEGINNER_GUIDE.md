# 🎓 FASTAPI FOR BEGINNERS - EASY UNDERSTANDING GUIDE

## What is FastAPI? 🤔

Think of FastAPI like a **restaurant ordering system**:
- **Customer (You)** → Sends request to API
- **API (FastAPI)** → Receives order and processes it
- **Database** → Stores the data (like a receipt)
- **Response** → Gives back the result

---

## Installation - Step by Step ⚙️

### Step 1: Install Python
Download from: https://www.python.org/

### Step 2: Create a Folder
```bash
mkdir my_first_api
cd my_first_api
```

### Step 3: Create Virtual Environment (Isolated Python)
Think of this as a **separate workspace** so your project doesn't mess with other Python projects.

```bash
python -m venv env
```

**On Windows:**
```bash
env\Scripts\activate
```

**On Mac/Linux:**
```bash
source env/bin/activate
```

You should see `(env)` at the start of your terminal line.

### Step 4: Install FastAPI and Server
```bash
pip install fastapi uvicorn[standard]
```

This installs:
- **FastAPI**: The framework for building APIs
- **Uvicorn**: The server that runs your API

---

## Your First API - Super Simple! 🚀

Create a file called `main.py`:

```python
from fastapi import FastAPI

# Create an API
app = FastAPI()

# Create an endpoint (a way to access your API)
@app.get("/")
async def hello():
    return {"message": "Hello World!"}
```

### Run it:
```bash
fastapi dev main.py
```

### Open in browser:
```
http://localhost:8000
```

**You should see:**
```json
{"message": "Hello World!"}
```

---

## Understanding the Code 📖

```python
from fastapi import FastAPI
# This imports FastAPI - like importing a tool from a toolbox

app = FastAPI()
# This creates your API - like creating a new app

@app.get("/")
# This is a "decorator" - it says "this function handles GET requests to /"
# GET = asking for data (like visiting a website)

async def hello():
# "async" = can handle multiple requests at the same time
# "def hello()" = your function name

    return {"message": "Hello World!"}
# Returns JSON data (key-value pairs)
```

---

## Interactive Documentation 📚

FastAPI automatically creates documentation for you!

**Visit these URLs:**
- `http://localhost:8000/docs` → Interactive docs (Swagger UI)
- `http://localhost:8000/redoc` → Alternative docs (ReDoc)

You can **test your API directly from the browser!**

---

## API Endpoints Explained 🔗

Think of endpoints like **different routes in a restaurant:**
- **GET** `/menu` → Get the menu (retrieve data)
- **POST** `/order` → Place an order (create data)
- **PUT** `/order/1` → Modify your order (update data)
- **DELETE** `/order/1` → Cancel your order (delete data)

---

## Example 1: Getting Data

```python
from fastapi import FastAPI

app = FastAPI()

# Sample data
users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]

# Get all users
@app.get("/users")
async def get_users():
    return users

# Get one specific user
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Find the user with this ID
    for user in users:
        if user["id"] == user_id:
            return user
    # If not found
    return {"error": "User not found"}
```

### Test it:
```
http://localhost:8000/users
http://localhost:8000/users/1
http://localhost:8000/users/2
```

---

## Example 2: Creating Data (POST)

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define what a user should look like
class User(BaseModel):
    name: str
    email: str
    age: int

users = []

# Create a new user
@app.post("/users")
async def create_user(user: User):
    # Add new user to the list
    users.append({
        "id": len(users) + 1,
        "name": user.name,
        "email": user.email,
        "age": user.age
    })
    return {"message": "User created!", "user": users[-1]}
```

### How to test with documentation:
1. Go to `http://localhost:8000/docs`
2. Click on `/users POST` endpoint
3. Click "Try it out"
4. Enter data like:
```json
{
  "name": "David",
  "email": "david@example.com",
  "age": 25
}
```
5. Click "Execute"

---

## Example 3: Using a Database 🗄️

First, install:
```bash
pip install sqlalchemy sqlite3
```

```python
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# Database setup
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model (what data looks like in database)
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

# API model (what data looks like when you send/receive)
class UserSchema(BaseModel):
    name: str
    email: str

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API
app = FastAPI()

# Create user in database
@app.post("/users")
async def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = UserDB(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get all users from database
@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    return users

# Get one user
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user is None:
        return {"error": "User not found"}
    return user

# Update user
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        return {"error": "User not found"}
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    return db_user

# Delete user
@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if db_user is None:
        return {"error": "User not found"}
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
```

**This is CRUD:**
- **C**reate (POST)
- **R**ead (GET)
- **U**pdate (PUT)
- **D**elete (DELETE)

---

## Example 4: Authentication (Login) 🔐

```python
from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"

app = FastAPI()

# Hash passwords securely
pwd_context = CryptContext(schemes=["bcrypt"])

# OAuth2 login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Fake user database
fake_users = {
    "testuser": {
        "username": "testuser",
        "password_hashed": pwd_context.hash("password123")
    }
}

# Login endpoint
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users.get(form_data.username)
    
    # Check if user exists and password is correct
    if not user or not pwd_context.verify(form_data.password, user["password_hashed"]):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    
    # Create a token (like a ticket)
    token = jwt.encode(
        {"sub": form_data.username},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {"access_token": token, "token_type": "bearer"}

# Protect an endpoint with login
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

@app.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello {current_user}"}
```

### How it works:
1. User logs in with username and password
2. API gives back a **token** (like a ticket)
3. User uses token to access protected endpoints
4. API checks if token is valid

---

## Understanding Key Concepts 🎯

### 1. `@app.get()` - GET Request
```python
@app.get("/hello")
async def hello():
    return {"message": "Hello"}
```
Used to **retrieve data**. Like asking for information.

### 2. `@app.post()` - POST Request
```python
@app.post("/users")
async def create_user(user: User):
    return {"status": "created"}
```
Used to **create new data**. Like submitting a form.

### 3. `@app.put()` - PUT Request
```python
@app.put("/users/{user_id}")
async def update_user(user_id: int):
    return {"status": "updated"}
```
Used to **update existing data**. Like editing a form.

### 4. `@app.delete()` - DELETE Request
```python
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return {"status": "deleted"}
```
Used to **delete data**. Like removing something.

---

## Path Parameters vs Query Parameters 🔀

### Path Parameter (in the URL path)
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

# URL: /users/5
# user_id = 5
```

### Query Parameter (at the end with `?`)
```python
@app.get("/users")
async def get_users(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# URL: /users?skip=0&limit=10
# skip = 0, limit = 10
```

---

## Validation - Making Sure Data is Correct ✓

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    # name must be 1-50 characters
    
    age: int = Field(ge=0, le=150)
    # age must be 0-150
    
    email: str
    # email must be a valid email
```

FastAPI automatically checks this!

---

## Testing Your API 🧪

Create `test_main.py`:

```python
from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

# Test GET request
def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test POST request
def test_create_user():
    response = client.post("/users", json={
        "name": "Test User",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
```

### Run tests:
```bash
pip install pytest
pytest test_main.py -v
```

---

## Deploying Your API 🚀

### Using Docker (Container)

Create `Dockerfile`:
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

Create `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
passlib[bcrypt]==1.7.4
```

### Run Docker:
```bash
docker build -t my_api .
docker run -p 8000:8000 my_api
```

---

## Common Problems & Solutions 🐛

### Problem 1: "Module not found"
**Solution:** Install it with pip
```bash
pip install fastapi
```

### Problem 2: "Port 8000 already in use"
**Solution:** Use different port
```bash
uvicorn main:app --port 8001
```

### Problem 3: "Database locked"
**Solution:** Close other connections or restart

### Problem 4: "CORS error"
**Solution:** Add CORS middleware
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## File Structure for Your Project 📁

```
my_api/
├── env/                    # Virtual environment
├── main.py                 # Your API code
├── database.py             # Database setup
├── models.py               # Database models
├── schemas.py              # Pydantic models
├── requirements.txt        # Dependencies
├── Dockerfile              # For Docker
├── test_main.py            # Tests
└── .env                    # Secret keys (don't share!)
```

---

## Step-by-Step Project Tutorial 📝

### Project: Simple Blog API

**Step 1: Create folders and files**
```bash
mkdir blog_api
cd blog_api
python -m venv env
env\Scripts\activate  # Windows
mkdir models
touch main.py database.py requirements.txt
```

**Step 2: Install dependencies**
```bash
pip install fastapi uvicorn sqlalchemy sqlite3 pydantic
pip freeze > requirements.txt
```

**Step 3: Create database models** (`database.py`)
```python
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    content = Column(Text)

Base.metadata.create_all(bind=engine)
```

**Step 4: Create API** (`main.py`)
```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Post
from pydantic import BaseModel

app = FastAPI(title="Blog API")

class PostSchema(BaseModel):
    title: str
    content: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create post
@app.post("/posts")
async def create_post(post: PostSchema, db: Session = Depends(get_db)):
    db_post = Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    return db_post

# Get all posts
@app.get("/posts")
async def get_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()

# Get one post
@app.get("/posts/{post_id}")
async def get_post(post_id: int, db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.id == post_id).first()
```

**Step 5: Run it**
```bash
fastapi dev main.py
```

**Step 6: Test it**
Visit: `http://localhost:8000/docs`

---

## What You Should Practice 💪

1. **Create a Todo API**
   - Create todo
   - List todos
   - Update todo
   - Delete todo
   - Mark as done

2. **Create a Notes API**
   - Create note
   - View note
   - Edit note
   - Delete note
   - Search notes

3. **Create a Student API**
   - Add student
   - View students
   - Update grades
   - Delete student
   - Get students by class

---

## Important Concepts Summary 📋

| Concept | Meaning | Example |
|---------|---------|---------|
| **Endpoint** | A URL path | `/users`, `/posts` |
| **Request** | Data sent TO the API | POST with user info |
| **Response** | Data sent FROM the API | JSON with user data |
| **Status Code** | Success/Error indicator | 200 (OK), 404 (Not Found) |
| **Parameter** | Data passed to function | user_id, skip, limit |
| **Schema** | Data structure definition | UserSchema with fields |
| **Database** | Where data is stored | SQLite, PostgreSQL |
| **Token** | Authentication ticket | JWT token |
| **CORS** | Allow cross-origin requests | Enable frontend to access |

---

## Resources to Learn More 📚

1. **Official Docs:** https://fastapi.tiangolo.com
2. **YouTube:** Search "FastAPI Tutorial"
3. **Practice:** Build small projects
4. **Community:** FastAPI Discord server
5. **Read Code:** Look at GitHub projects

---

## Next Steps 🎯

1. ✅ Understand this guide
2. ✅ Create your first API
3. ✅ Build a simple project (Todo app)
4. ✅ Add database integration
5. ✅ Add authentication
6. ✅ Write tests
7. ✅ Deploy with Docker
8. 📖 Read advanced guides

---

**Congratulations! You now understand FastAPI basics!** 🎉

**Start building amazing APIs today!** 🚀
