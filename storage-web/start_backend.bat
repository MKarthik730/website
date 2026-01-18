@echo off
echo ========================================
echo Starting Storage Web Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --port 8000

pause
