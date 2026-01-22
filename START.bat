@echo off
echo ============================================================
echo Document Converter - Quick Start
echo ============================================================
echo.

echo Checking Python...
python --version
if %errorlevel% neq 0 (
    echo Error: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo.
echo Starting server...
echo.
echo Server will start at: http://localhost:5000
echo Press Ctrl+C to stop
echo.

python start_server.py

pause
