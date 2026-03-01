@echo off
REM DocManager CA Desktop - Windows Startup Script
REM Double-click this file to start the application

echo ====================================================
echo   DocManager CA Desktop - Starting...
echo ====================================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

REM Check if backend directory exists
if not exist "ca_desktop\backend" (
    echo ERROR: ca_desktop\backend directory not found
    echo Please run this script from the DocManager root folder.
    pause
    exit /b 1
)

REM Check if frontend directory exists
if not exist "ca_desktop\frontend" (
    echo ERROR: ca_desktop\frontend directory not found
    echo Please run this script from the DocManager root folder.
    pause
    exit /b 1
)

REM Set PYTHONPATH to project root so 'shared' module is found
set "PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%"

REM ---- Start Backend ----
echo [1/2] Starting Backend Server...

pushd ca_desktop\backend

REM Check for virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo    Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Python not found. Please install Python 3.11+ from python.org
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    echo    Installing dependencies...
    pip install --upgrade pip setuptools wheel >nul 2>&1
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check if database exists in project root
if not exist "..\..\ca_desktop.db" (
    echo    Setting up database...
    pushd ..\..
    python scripts\setup_database.py
    popd
)

REM Start backend in background
echo    Starting backend on http://127.0.0.1:8443 ...
start /b "DocManager Backend" python -m uvicorn ca_desktop.backend.src.main:app --host 127.0.0.1 --port 8443

popd

REM Wait for backend to start
echo    Waiting for backend to be ready...
timeout /t 5 /nobreak >nul

REM ---- Start Frontend ----
echo [2/2] Starting Frontend Server...

pushd ca_desktop\frontend

if not exist "node_modules" (
    echo    Installing frontend dependencies...
    call npm install
)

echo    Starting frontend on http://127.0.0.1:5174 ...
start /b "DocManager Frontend" npm run dev

popd

echo.
echo ====================================================
echo   DocManager CA Desktop is running!
echo ====================================================
echo.
echo   CA Login:        http://localhost:5174/ca/login
echo   Client Portal:   http://localhost:5174/portal/login
echo   Public Website:  http://localhost:5174/ca-lokesh-dagdiya
echo   API Docs:        http://localhost:8443/docs
echo.
echo   Demo Credentials:
echo   CA Admin:  lokesh / lokesh
echo   Client:    9876543210 / client123
echo.
echo   Press Ctrl+C to stop all servers
echo.

REM Open browser automatically
timeout /t 3 /nobreak >nul
start http://localhost:5174/ca/login

REM Keep window open
cmd /k
