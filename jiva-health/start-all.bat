@echo off
setlocal enabledelayedexpansion

:: Jīva Health - Main Startup Script (Windows)
echo ============================================
echo      Jiva Health - Development Mode
echo  AI-Powered Health Record Management
echo ============================================
echo.

:: Check prerequisites
echo [*] Checking prerequisites...

where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed
    exit /b 1
)

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed
    exit /b 1
)

echo [OK] All prerequisites satisfied
echo.

:: Check environment files
echo [*] Checking environment files...

if not exist "backend\.env" (
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env"
        echo [WARNING] Created backend\.env from example
    ) else (
        echo [ERROR] backend\.env.example not found
        exit /b 1
    )
)

if not exist "mobile-app\.env" (
    if exist "mobile-app\.env.example" (
        copy "mobile-app\.env.example" "mobile-app\.env"
        echo [WARNING] Created mobile-app\.env from example
    ) else (
        echo [ERROR] mobile-app\.env.example not found
        exit /b 1
    )
)

echo [OK] Environment files checked
echo.

:: Create logs directory
if not exist "logs" mkdir logs

:: Start Backend
echo [*] Starting Backend Server...

if not exist "backend\venv" (
    echo [*] Creating Python virtual environment...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    cd ..
    echo [OK] Virtual environment created
)

cd backend
call venv\Scripts\activate
start /B cmd /c "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ..\logs\backend.log 2>&1"
cd ..

echo [OK] Backend starting on http://localhost:8000
timeout /t 3 /nobreak >nul

:: Start Mobile App
echo.
echo [*] Starting Mobile App...

if not exist "mobile-app\node_modules" (
    echo [*] Installing npm dependencies...
    cd mobile-app
    call npm install
    cd ..
    echo [OK] Dependencies installed
)

cd mobile-app
start /B cmd /c "npm start > ..\logs\mobile.log 2>&1"
cd ..

echo [OK] Expo starting on http://localhost:19006
echo.
echo ============================================
echo   Jiva Health is now running!
echo ============================================
echo.
echo Backend API:     http://localhost:8000
echo API Docs:        http://localhost:8000/docs
echo Mobile App:      http://localhost:19006
echo.
echo Press Ctrl+C to stop all services...
echo.

pause
