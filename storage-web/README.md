# Storage Web

*A Modern File Management System for Secure Document and Image Storage*

## Quick Access

**API Documentation**: [Swagger UI](http://localhost:8000/docs) | [ReDoc](http://localhost:8000/redoc)  
**Frontend Application**: [Local Server](http://localhost:8501)  
**Project Repository**: [GitHub](https://github.com/MKarthik730/website)

## Mission

The digital world is flooded with files and documents. Organizations and individuals struggle to manage, organize, and secure their digital assets effectively.

That gap is what we address with Storage Web.

Storage Web is a comprehensive file management system designed for secure, efficient, and user-friendly document and image storage. Our mission is to provide a robust solution that combines modern web technologies with enterprise-grade security, enabling users to seamlessly upload, organize, filter, and manage their digital files with complete control and confidence.

The future of digital asset management depends on systems that prioritize both usability and security. Storage Web represents our commitment to building reliable, scalable file management solutions that work in the real world.

## Features

**Core Capabilities**

- **Secure Authentication** - User registration and login with JWT token-based authentication and bcrypt password hashing
- **File Upload** - Upload images (JPG, JPEG, PNG, GIF, WEBP) and documents (PDF, DOC, DOCX, TXT, XLSX, CSV) with automatic type validation
- **File Management** - View, download, and delete files with user-specific access control
- **Advanced Filtering** - Filter files by type with separate views for images and documents
- **Image Preview** - Direct image preview functionality within the interface
- **File Metadata** - Display file size, upload date, and detailed file information
- **PostgreSQL Integration** - Robust database backend for persistent data storage

## Technical Architecture

**Technology Stack**

- **Backend Framework**: FastAPI - High-performance, modern Python web framework
- **Frontend Framework**: Streamlit - Interactive web interface for rapid development
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Security**: CORS protection, SQL injection prevention, file type validation

## Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database server
- Git (optional, for cloning the repository)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/MKarthik730/website.git
   cd storage-web
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure PostgreSQL database**
   - Ensure PostgreSQL service is running
   - Create a database named `storage-web`
   - Update database credentials in `database/database.py` if needed:
     ```python
     db_url = "postgresql://username:password@localhost:5432/storage-web"
     ```

4. **Start the application**

   **Windows (Batch Files)**:
   - Double-click `start_backend.bat` to start the API server (port 8000)
   - Double-click `start_frontend.bat` to start the web interface (port 8501)

   **Manual Start**:
   
   Terminal 1 - Backend Server:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```
   
   Terminal 2 - Frontend Interface:
   ```bash
   cd frontend
   streamlit run app.py
   ```

5. **Access the application**
   - Open your browser and navigate to: http://localhost:8501
   - Register a new account
   - Begin uploading and managing your files

## Usage Guide

### Getting Started

1. **Registration & Login**
   - Navigate to http://localhost:8501
   - Click on the "Register" tab
   - Enter your username, email, and password
   - Complete registration and switch to the "Login" tab
   - Log in with your credentials

2. **Uploading Files**
   - Navigate to the "Upload" tab
   - Click "Browse files" and select your file
   - Supported formats are automatically validated
   - Click "Upload" to complete the process

3. **Managing Files**
   - View all files in the "All Files" tab
   - Download files using the download button
   - Delete files using the delete button
   - Refresh the file list as needed

4. **Filtering Files**
   - Use the "Filter by Type" tab
   - Select "Images" to view all uploaded images with previews
   - Select "Documents" to view all documents with download options

## Project Structure

```
storage-web/
├── backend/
│   ├── main.py              # FastAPI application and API endpoints
│   ├── schemas.py           # Pydantic models for data validation
│   ├── uploads/             # File storage directory
│   │   ├── images/          # Uploaded image files
│   │   └── documents/       # Uploaded document files
│   └── __init__.py
├── database/
│   ├── database.py          # Database configuration and connection
│   ├── models.py            # SQLAlchemy ORM models
│   └── __init__.py
├── frontend/
│   ├── app.py              # Streamlit user interface
│   └── __init__.py
├── start_backend.bat        # Windows backend launcher script
├── start_frontend.bat       # Windows frontend launcher script
├── npm_tunnel_backend.bat   # Backend tunnel configuration
├── npm_tunnel_frontend.bat  # Frontend tunnel configuration
├── requirements.txt         # Python package dependencies
└── README.md                # This file
```

## Configuration

### Database Configuration

Edit `database/database.py` to configure your database connection:
```python
db_url = "postgresql://username:password@localhost:5432/storage-web"
```

### Security Configuration

For production deployments, update the SECRET_KEY in `backend/main.py`:
```python
SECRET_KEY = "your-secure-secret-key-here"
```

### Port Configuration

Modify port settings in the batch files or use command-line flags:
- Backend: Change port 8000 in `start_backend.bat` or uvicorn command
- Frontend: Change port 8501 in `start_frontend.bat` or use `streamlit run app.py --server.port 8502`

## Security Features

- **Password Security**: bcrypt hashing with salt for secure password storage
- **Authentication**: JWT token-based authentication system
- **CORS Protection**: Cross-origin resource sharing protection enabled
- **SQL Injection Prevention**: SQLAlchemy ORM protects against injection attacks
- **File Type Validation**: Automatic validation of uploaded file types
- **User Access Control**: User-specific file access with session management

## API Documentation

Once the backend server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs - Interactive API explorer and testing interface
- **ReDoc**: http://localhost:8000/redoc - Alternative API documentation interface

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL service is running
- Check database credentials in `database/database.py`
- Confirm the database exists:
  ```sql
  CREATE DATABASE "storage-web";
  ```

### Port Conflicts

- **Backend**: Modify the port in `start_backend.bat` or specify a different port:
  ```bash
  python -m uvicorn main:app --reload --port 8001
  ```

- **Frontend**: Modify the port in `start_frontend.bat` or use:
  ```bash
  streamlit run app.py --server.port 8502
  ```

### File Upload Issues

- Verify upload directories exist: `backend/uploads/images` and `backend/uploads/documents`
- Check file system write permissions on upload directories
- Ensure sufficient disk space is available

### Authentication Problems

- Logout and login again to refresh tokens
- Clear browser cache and cookies
- Verify backend server is running on port 8000
- Check JWT token expiration settings

## Contributing

Contributions are welcome and encouraged. Please feel free to:

- Submit issues for bugs or feature requests
- Fork the repository and create feature branches
- Submit pull requests with improvements or fixes
- Provide feedback and suggestions

## License

This project is open source and available under the MIT License.

## Acknowledgments

Storage Web is built with the following technologies and frameworks:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [Streamlit](https://streamlit.io/) - Rapid web application development framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit and ORM
- [PostgreSQL](https://www.postgresql.org/) - Advanced open-source relational database

---

*Storage Web - Secure File Management for the Modern Web*
