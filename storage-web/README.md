# Storage Web

A simple file management system built with FastAPI and Streamlit for uploading and managing images and documents.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1C1C1C?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)

## What it does

- Upload images (JPG, PNG, GIF, WEBP) and documents (PDF, DOC, DOCX, TXT, XLSX, CSV)
- View and download your uploaded files
- Filter files by type (images or documents)
- User authentication with registration and login
- Preview images directly in the interface

## Tech Stack

**Backend:**
- ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) FastAPI
- ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) Python 3.8+

**Frontend:**
- ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) Streamlit

**Database:**
- ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white) PostgreSQL
- ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1C1C1C?style=flat&logo=sqlalchemy&logoColor=white) SQLAlchemy

**Authentication:**
- ![JWT](https://img.shields.io/badge/JWT-000000?style=flat&logo=JSON%20web%20tokens&logoColor=white) JWT Tokens
- ![Bcrypt](https://img.shields.io/badge/Bcrypt-2A2F3D?style=flat&logo=bcrypt&logoColor=white) Bcrypt

## Setup

### Requirements

- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository
```bash
git clone https://github.com/MKarthik730/website.git
cd storage-web
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Setup database
   - Make sure PostgreSQL is running
   - Create a database named `storage-web`
   - Update connection string in `database/database.py` if needed

4. Run the application

   Windows - use batch files:
   - Double-click `start_backend.bat` (runs on port 8000)
   - Double-click `start_frontend.bat` (runs on port 8501)

   Or run manually:

   Terminal 1:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```
   
   Terminal 2:
   ```bash
   cd frontend
   streamlit run app.py
   ```

5. Open http://localhost:8501 in your browser

## Project Structure

```
storage-web/
├── backend/
│   ├── main.py
│   ├── uploads/
│   │   ├── images/
│   │   └── documents/
├── database/
│   ├── database.py
│   └── models.py
├── frontend/
│   └── app.py
├── start_backend.bat
├── start_frontend.bat
└── requirements.txt
```

## API Docs

Once backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

Database connection in `database/database.py`:
```python
db_url = "postgresql://username:password@localhost:5432/storage-web"
```

For production, change SECRET_KEY in `backend/main.py`

## Troubleshooting

**Database connection error**
- Check if PostgreSQL is running
- Verify database exists and credentials are correct

**Port already in use**
- Backend: Change port in batch file or uvicorn command
- Frontend: Change port in batch file or use `--server.port` flag

**Upload fails**
- Make sure `backend/uploads/images` and `backend/uploads/documents` directories exist

## License

MIT License
