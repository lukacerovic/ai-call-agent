@echo off
REM AI Call Agent - Windows Setup Script
REM This script sets up the project on Windows

echo.
echo ========================================
echo AI Call Agent - Windows Setup
echo ========================================
echo.

REM Check Python version
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10 or 3.11
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Python version is 3.10 or 3.11
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

echo.
echo ========================================
echo Setting up Backend...
echo ========================================
echo.

cd backend
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Checking for .env file...
echo ========================================
echo.

if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo NOTE: Please edit backend\.env and add your API keys:
    echo   1. OPENAI_API_KEY - Get from https://platform.openai.com/api-keys
    echo   2. GROQ_API_KEY (optional) - Get from https://groq.com/
    echo.
    pause
) else (
    echo .env file already exists
)

cd ..

echo.
echo ========================================
echo Setting up Frontend...
echo ========================================
echo.

cd frontend

echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo Installing npm dependencies...
call npm install

if %errorlevel% neq 0 (
    echo ERROR: Failed to install npm dependencies
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Edit your API keys:
echo    backend\.env
echo.
echo 2. Start Backend (Terminal 1):
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn main:app --reload
echo.
echo 3. Start Frontend (Terminal 2):
echo    cd frontend
echo    npm start
echo.
echo 4. Open browser:
echo    http://localhost:3000
echo.
echo For more help, see: SETUP.md
echo.
pause
