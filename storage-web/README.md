# Storage Web - File Management System

A secure file management system built with FastAPI and Streamlit that allows users to upload, manage, and download images and documents.

## ✨ Features

- 🔐 **User Authentication** - Secure registration and login
- 📤 **File Upload** - Upload images and documents
- 📁 **File Management** - View, download, and delete files
- 🏷️ **File Filtering** - Filter by file type (images/documents)
- 💾 **PostgreSQL Database** - Persistent storage
- 🖼️ **Image Preview** - View uploaded images directly
- 📊 **File Information** - See file size, upload date, and metadata

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Git (optional)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure database**
   - Make sure PostgreSQL is running
   - Create a database named `storage-web`
   - Update credentials in `database/database.py` if needed

4. **Start the application**

   **Option 1: Using batch files (Windows)**
   - Double-click `start_backend.bat` to start the API server
   - Double-click `start_frontend.bat` to start the web interface

   **Option 2: Manual start**
   
   Terminal 1 (Backend):
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```
   
   Terminal 2 (Frontend):
   ```bash
   cd frontend
   streamlit run app.py
   ```

5. **Access the application**
   - Open your browser and go to: http://localhost:8501
   - Register a new account
   - Start uploading files!

## 📖 Usage Guide

### Registration & Login
1. Open the application at http://localhost:8501
2. Click on "Register" tab
3. Fill in username, email, and password
4. Click "Register" button
5. Switch to "Login" tab and login with your credentials

### Uploading Files
1. Go to "Upload" tab
2. Click "Browse files" and select a file
3. Supported formats:
   - Images: JPG, JPEG, PNG, GIF, WEBP
   - Documents: PDF, DOC, DOCX, TXT, XLSX, CSV
4. Click "Upload" button

### Managing Files
1. Go to "All Files" tab to see all your files
2. Click ⬇️ to download a file
3. Click 🗑️ to delete a file
4. Click 🔄 to refresh the file list

### Filtering Files
1. Go to "Filter by Type" tab
2. Click "Images" to see all images with previews
3. Click "Documents" to see all documents with download options

## 🛠️ Technical Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Streamlit
- **Authentication**: JWT tokens, bcrypt password hashing
- **File Storage**: Local filesystem with database metadata

## 📁 Project Structure

```
storage-web/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── schemas.py           # Pydantic models
│   ├── uploads/             # File storage
│   │   ├── images/          # Uploaded images
│   │   └── documents/       # Uploaded documents
│   └── __init__.py
├── database/
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   └── __init__.py
├── frontend/
│   ├── app.py              # Streamlit UI
│   └── __init__.py
├── start_backend.bat        # Windows backend launcher
├── start_frontend.bat       # Windows frontend launcher
├── requirements.txt         # Python dependencies
├── QUICKSTART.md           # Quick start guide
└── README.md               # This file
```

## 🔧 Configuration

### Database
Edit `database/database.py` to configure your database:
```python
db_url = "postgresql://username:password@localhost:5432/storage-web"
```

### Security
For production, change the SECRET_KEY in `backend/main.py`:
```python
SECRET_KEY = "your-secure-secret-key-here"
```

## 🐛 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check database credentials in `database/database.py`
- Verify database "storage-web" exists:
  ```sql
  CREATE DATABASE "storage-web";
  ```

### Port Already in Use
- Backend: Change port in `start_backend.bat` or when running uvicorn
- Frontend: Change port in `start_frontend.bat` or use `--server.port` flag

### File Upload Fails
- Check upload directories exist: `backend/uploads/images` and `backend/uploads/documents`
- Verify write permissions on upload directories

### Authentication Issues
- Logout and login again
- Clear browser cache
- Check if backend server is running on port 8000

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ CORS protection
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ File type validation
- ✅ User-specific file access control

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
