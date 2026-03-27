@echo off
REM Run script for Dating App Backend on Windows

echo Starting Dating App Backend...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.

REM Create uploads directory if it doesn't exist
if not exist "uploads" mkdir uploads

REM Run the application
echo Starting server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
