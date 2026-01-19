@echo off
REM Build script for creating EXE file

echo ========================================
echo  Universal File Converter - Build Script
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo Building EXE with PyInstaller...
pyinstaller FileConverter.spec --clean

echo.
if exist "dist\FileConverter.exe" (
    echo ========================================
    echo  Build Successful!
    echo ========================================
    echo.
    echo EXE file location: dist\FileConverter.exe
    echo.
    echo You can now distribute the FileConverter.exe file.
    echo The EXE is standalone and doesn't require Python installation.
) else (
    echo ========================================
    echo  Build Failed!
    echo ========================================
    echo Please check the error messages above.
)

echo.
pause
