from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Local imports
import sys
sys.path.append('../database')
sys.path.append('../')

from database.database import SessionLocal, engine, Base
from database.models import User, File as FileModel
from .schemas import UserRegister, UserLogin, UserResponse, FileResponse, FileListResponse

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Storage Web API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Upload directories
UPLOAD_DIR = Path("./uploads")
IMAGES_DIR = UPLOAD_DIR / "images"
DOCUMENTS_DIR = UPLOAD_DIR / "documents"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


# ==================== Utility Functions ====================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = None, db: Session = Depends(get_db)) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = decode_token(token)
    username = payload.get("sub")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ==================== Auth Routes ====================

@app.post("/api/auth/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.post("/api/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }


# ==================== File Routes ====================

@app.post("/api/files/upload")
def upload_file(
    file: UploadFile = File(...),
    token: str = None,
    db: Session = Depends(get_db)
):
    """Upload a file (image or document)"""
    current_user = get_current_user(token, db)
    
    # Determine file type and save directory
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        file_type = 'image'
        save_dir = IMAGES_DIR
    elif file_ext in ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'csv']:
        file_type = 'document'
        save_dir = DOCUMENTS_DIR
    else:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Generate unique filename
    file_id = str(__import__('uuid').uuid4())
    file_name = f"{file_id}_{file.filename}"
    file_path = save_dir / file_name
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Save to database
        db_file = FileModel(
            user_id=current_user.id,
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            file_path=str(file_path)
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return {
            "id": db_file.id,
            "filename": db_file.filename,
            "file_type": db_file.file_type,
            "file_size": db_file.file_size,
            "uploaded_at": db_file.uploaded_at
        }
    
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/files", response_model=FileListResponse)
def list_files(token: str = None, db: Session = Depends(get_db)):
    """List all files for current user"""
    current_user = get_current_user(token, db)
    
    files = db.query(FileModel).filter(FileModel.user_id == current_user.id).order_by(desc(FileModel.uploaded_at)).all()
    
    return {
        "total_files": len(files),
        "files": files
    }


@app.get("/api/files/{file_id}", response_model=FileResponse)
def get_file_info(file_id: str, token: str = None, db: Session = Depends(get_db)):
    """Get file information"""
    current_user = get_current_user(token, db)
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file


@app.get("/api/files/download/{file_id}")
def download_file(file_id: str, token: str = None, db: Session = Depends(get_db)):
    """Download a file"""
    current_user = get_current_user(token, db)
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file or not Path(file.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file.file_path,
        filename=file.filename,
        media_type='application/octet-stream'
    )


@app.delete("/api/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: str, token: str = None, db: Session = Depends(get_db)):
    """Delete a file"""
    current_user = get_current_user(token, db)
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete from filesystem
    file_path = Path(file.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database
    db.delete(file)
    db.commit()


@app.get("/api/files/by-type/{file_type}")
def get_files_by_type(file_type: str, token: str = None, db: Session = Depends(get_db)):
    """Get files filtered by type (image or document)"""
    current_user = get_current_user(token, db)
    
    if file_type not in ['image', 'document']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    files = db.query(FileModel).filter(
        FileModel.user_id == current_user.id,
        FileModel.file_type == file_type
    ).order_by(desc(FileModel.uploaded_at)).all()
    
    return {
        "total_files": len(files),
        "files": files
    }


# ==================== Health Check ====================

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
