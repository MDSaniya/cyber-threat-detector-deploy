@echo off
REM Quick setup script for Windows - activates VENV and runs the app
REM Usage: Run this file to start the development server

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║      CyberFedDefender - Quick Start Script (Windows)          ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ⚠️  Virtual environment not found. Creating...
    python -m venv venv
    echo ✓ Virtual environment created
)

REM Activate venv
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ VENV activated

REM Check if requirements are installed
echo.
echo Checking dependencies...
python -m pip -q show flask > nul
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    echo ✓ Dependencies installed
) else (
    echo ✓ Dependencies already installed
)

REM Start the app
echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║  Starting Flask development server...                          ║
echo ║  Open browser to: http://localhost:5000                        ║
echo ║  Press Ctrl+C to stop the server                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

python app.py
pause
