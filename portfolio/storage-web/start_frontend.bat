@echo off
echo ========================================
echo Starting Storage Web Frontend
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Starting Streamlit app on http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
