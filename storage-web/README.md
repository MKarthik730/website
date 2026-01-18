# Storage Web - File Management System

A secure file management system built with FastAPI and Streamlit that allows users to upload, manage, and download images and documents.

## Features

- **User Authentication** - Secure registration and login system
- **File Upload** - Upload images and documents with validation
- **File Management** - View, download, and delete files
- **File Filtering** - Filter files by type (images/documents)
- **PostgreSQL Database** - Persistent data storage
- **Image Preview** - View uploaded images directly in the interface
- **File Information** - Display file size, upload date, and metadata

## Quick Start

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
   - Ensure PostgreSQL is running
   - Create a database named `storage-web`
   - Update database credentials in `database/database.py` if needed

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
   - Open your browser and navigate to: http://localhost:8501
   - Register a new account
   - Start uploading files

## Usage Guide

### Registration & Login

1. Open the application at http://localhost:8501
2. Navigate to the "Register" tab
3. Enter username, email, and password
4. Click the "Register" button
5. Switch to the "Login" tab and login with your credentials

### Uploading Files

1. Navigate to the "Upload" tab
2. Click "Browse files" and select a file
3. Supported formats:
   - Images: JPG, JPEG, PNG, GIF, WEBP
   - Documents: PDF, DOC, DOCX, TXT, XLSX, CSV
4. Click the "Upload" button

### Managing Files

1. Navigate to the "All Files" tab to view all your files
2. Use the download button to download a file
3. Use the delete button to remove a file
4. Use the refresh button to reload the file list

### Filtering Files

1. Navigate to the "Filter by Type" tab
2. Select "Images" to view all images with previews
3. Select "Documents" to view all documents with download options

## Technical Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Streamlit
- **Authentication**: JWT tokens, bcrypt password hashing
- **File Storage**: Local filesystem with database metadata

## Project Structure

```
storage-web/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── schemas.py           # Pydantic models
│   ├── uploads/            # File storage
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
└── README.md                # This file
```

## Configuration

### Database

Edit `database/database.py` to configure your database connection:
```python
db_url = "postgresql://username:password@localhost:5432/storage-web"
```

### Security

For production deployments, update the SECRET_KEY in `backend/main.py`:
```python
SECRET_KEY = "your-secure-secret-key-here"
```

## Troubleshooting

### Database Connection Error

- Ensure PostgreSQL service is running
- Verify database credentials in `database/database.py`
- Confirm the database "storage-web" exists:
  ```sql
  CREATE DATABASE "storage-web";
  ```

### Port Already in Use

- Backend: Modify the port in `start_backend.bat` or specify a different port when running uvicorn
- Frontend: Modify the port in `start_frontend.bat` or use the `--server.port` flag

### File Upload Fails

- Verify upload directories exist: `backend/uploads/images` and `backend/uploads/documents`
- Check write permissions on upload directories

### Authentication Issues

- Logout and login again
- Clear browser cache and cookies
- Verify the backend server is running on port 8000

## Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- CORS protection
- SQL injection protection via SQLAlchemy ORM
- File type validation
- User-specific file access control

## API Documentation

Once the backend server is running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

Contributions are welcome. Please feel free to submit issues, fork the repository, and create pull requests.

## License

This project is open source and available under the MIT License.

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/)
