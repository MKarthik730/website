# Storage Web Configuration

## Database Configuration
```
PostgreSQL Connection String:
postgresql://username:password@localhost:5432/storage_web

Steps to setup:
1. Install PostgreSQL
2. Create database: CREATE DATABASE storage_web;
3. Update database.py with your credentials
```

## Environment Variables (.env file)
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/storage_web
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Running the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Navigate to database folder
cd database

# The models will be created automatically when you run the backend
```

### 3. Start Backend (Terminal 1)
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API Docs at: http://localhost:8000/docs

### 4. Start Frontend (Terminal 2)
```bash
cd frontend
streamlit run app.py
```

Frontend will be available at: http://localhost:8501

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get access token

### Files
- `POST /api/files/upload` - Upload file (image or document)
- `GET /api/files` - Get all user files
- `GET /api/files/{file_id}` - Get file info
- `GET /api/files/download/{file_id}` - Download file
- `DELETE /api/files/{file_id}` - Delete file
- `GET /api/files/by-type/{file_type}` - Filter by type (image/document)

## Features

✅ User Registration & Login with Password Hashing
✅ JWT Token-based Authentication
✅ File Upload (Images & Documents)
✅ File Listing with Pagination
✅ File Download
✅ File Deletion
✅ Filter files by type
✅ Streamlit Web Interface
✅ RESTful API with FastAPI
✅ PostgreSQL Database

## File Types Supported

**Images:** jpg, jpeg, png, gif, webp
**Documents:** pdf, doc, docx, txt, xlsx, csv

## Project Structure

```
storage-web/
├── backend/
│   ├── main.py           # FastAPI application
│   └── schemas.py        # Pydantic models for validation
├── frontend/
│   └── app.py            # Streamlit app
├── database/
│   ├── database.py       # Database connection
│   └── models.py         # SQLAlchemy models
├── uploads/
│   ├── images/           # Uploaded images directory
│   └── documents/        # Uploaded documents directory
├── requirements.txt      # Python dependencies
└── README.md            # This file
```
