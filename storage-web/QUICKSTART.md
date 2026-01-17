# Storage Web - Quick Start Guide

A modern file storage application built with FastAPI (backend) and Streamlit (frontend) using PostgreSQL database.

## 🎯 Features

✅ **User Authentication**
   - Register new users with email validation
   - Secure login with JWT tokens
   - Password hashing with bcrypt

✅ **File Management**
   - Upload images (jpg, png, gif, webp) and documents (pdf, doc, docx, txt, xlsx)
   - Full CRUD operations (Create, Read, Update, Delete)
   - File download and deletion
   - Filter files by type (images/documents)
   - View file metadata (size, upload date)

✅ **Database**
   - PostgreSQL for persistent storage
   - SQLAlchemy ORM for database operations
   - User and File models with timestamps

✅ **Web Interface**
   - Streamlit frontend with intuitive UI
   - Real-time file upload and management
   - Responsive design
   - User-friendly dashboard

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### Step 1: Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE storage_web;

# Exit
\q
```

### Step 2: Configure Environment

1. Navigate to `storage-web` folder
2. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

3. Edit `.env` with your PostgreSQL credentials:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/storage_web
SECRET_KEY=your-secret-key-keep-it-safe
```

Also update [storage-web/database/database.py](storage-web/database/database.py) line 4:
```python
db_url = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/storage_web"
```

### Step 3: Install Dependencies

```bash
cd storage-web
pip install -r requirements.txt
```

### Step 4: Run the Application

**Terminal 1 - Start Backend (FastAPI):**
```bash
cd storage-web/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- 🌐 Application: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 🔍 ReDoc: http://localhost:8000/redoc

**Terminal 2 - Start Frontend (Streamlit):**
```bash
cd storage-web/frontend
streamlit run app.py
```

Frontend will be available at: http://localhost:8501

---

## 📡 API Endpoints

### Authentication
- **POST** `/api/auth/register` - Register new user
- **POST** `/api/auth/login` - Login and get JWT token

### File Operations
- **POST** `/api/files/upload` - Upload file (requires token)
- **GET** `/api/files` - List all user files (requires token)
- **GET** `/api/files/{file_id}` - Get file info (requires token)
- **GET** `/api/files/download/{file_id}` - Download file (requires token)
- **DELETE** `/api/files/{file_id}` - Delete file (requires token)
- **GET** `/api/files/by-type/{file_type}` - Filter by type (requires token)

### Health
- **GET** `/api/health` - Health check

---

## 🗂️ Project Structure

```
storage-web/
├── backend/
│   ├── main.py              # FastAPI application with all routes
│   ├── schemas.py           # Pydantic models for validation
│   └── __init__.py
├── frontend/
│   ├── app.py              # Streamlit web interface
│   └── __init__.py
├── database/
│   ├── database.py         # PostgreSQL connection setup
│   ├── models.py           # SQLAlchemy database models
│   └── __init__.py
├── uploads/
│   ├── images/             # Uploaded images directory
│   └── documents/          # Uploaded documents directory
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

---

## 🔐 Database Schema

### Users Table
```sql
id (UUID) - Primary key
username (String) - Unique username
password (String) - Hashed password
email (String) - Unique email
created_at (DateTime) - Registration timestamp
updated_at (DateTime) - Last update timestamp
```

### Files Table
```sql
id (UUID) - Primary key
user_id (UUID) - Foreign key to users
filename (String) - Original filename
file_type (String) - 'image' or 'document'
file_size (Integer) - File size in bytes
file_path (String) - Absolute path to file
uploaded_at (DateTime) - Upload timestamp
updated_at (DateTime) - Last update timestamp
```

---

## 💡 Usage Examples

### Register a User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password"
  }'
```

Response will include `access_token` to use in subsequent requests.

### Upload a File
```bash
curl -X POST "http://localhost:8000/api/files/upload?token=YOUR_ACCESS_TOKEN" \
  -F "file=@path/to/your/file.pdf"
```

### List Files
```bash
curl "http://localhost:8000/api/files?token=YOUR_ACCESS_TOKEN"
```

---

## 🐛 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check credentials in `.env` file
- Verify database exists: `psql -U postgres -l`

### Port Already in Use
- Backend: Change port in uvicorn command to 8001, 8002, etc.
- Frontend: Streamlit will use 8502 if 8501 is busy

### File Upload Fails
- Check upload directory permissions
- Ensure uploads/images/ and uploads/documents/ exist
- Check available disk space

---

## 🔄 CRUD Operations

### Create
- **User**: Register endpoint
- **File**: Upload endpoint

### Read
- **User**: Login endpoint
- **Files**: List and get file endpoints

### Update
- Files cannot be updated, but can be deleted and re-uploaded
- User info: Can be extended with profile update endpoint

### Delete
- **File**: Delete endpoint removes file from storage and database

---

## 🚀 Future Enhancements

- [ ] Profile page with user information
- [ ] File sharing/permissions
- [ ] File versioning
- [ ] Advanced search and filtering
- [ ] File compression
- [ ] Disk usage statistics
- [ ] Admin dashboard
- [ ] Email verification
- [ ] Password reset functionality
- [ ] Two-factor authentication

---

## 📝 Notes

- All passwords are hashed using bcrypt
- JWT tokens expire after 24 hours
- Files are stored in the uploads directory
- Each user can only access their own files
- File uploads are validated by extension

---

## 📧 Support

For issues or questions, refer to the code comments or FastAPI documentation at https://fastapi.tiangolo.com/

Happy file storage! 📁✨
