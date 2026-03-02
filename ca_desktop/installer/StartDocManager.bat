@echo off
setlocal enabledelayedexpansion
title DocManager CA Desktop
color 0A

echo.
echo ========================================================
echo    DocManager CA Desktop - Starting...
echo ========================================================
echo.

:: Find our directory (where this .bat lives)
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%..\backend"

:: -----------------------------------------------------------
:: Option 1: PyInstaller .exe exists -> use it
:: -----------------------------------------------------------
if exist "%BACKEND_DIR%\dist\DocManager\DocManager.exe" (
    echo [OK] Found packaged executable.
    echo Starting DocManager...
    start "" "%BACKEND_DIR%\dist\DocManager\DocManager.exe"
    timeout /t 5 /nobreak >nul
    start "" http://127.0.0.1:8443
    goto :eof
)

if exist "%BACKEND_DIR%\dist\DocManager.exe" (
    echo [OK] Found packaged executable.
    echo Starting DocManager...
    start "" "%BACKEND_DIR%\dist\DocManager.exe"
    timeout /t 5 /nobreak >nul
    start "" http://127.0.0.1:8443
    goto :eof
)

:: -----------------------------------------------------------
:: Option 2: Portable mode - run from source with Python
:: -----------------------------------------------------------
echo [INFO] No packaged .exe found — running from source.
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] Python %PY_VER% found.

:: Check/create virtual environment
if not exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo [SETUP] Creating virtual environment (first run)...
    python -m venv "%BACKEND_DIR%\venv"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)

:: Activate venv
call "%BACKEND_DIR%\venv\Scripts\activate.bat"

:: Install/update dependencies
if not exist "%BACKEND_DIR%\venv\.deps_installed" (
    echo [SETUP] Installing Python dependencies (first run, may take a minute)...
    pip install -q --upgrade pip
    pip install -q -r "%BACKEND_DIR%\requirements-prod.txt"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies.
        echo Try running: pip install -r requirements-prod.txt
        pause
        exit /b 1
    )
    echo. > "%BACKEND_DIR%\venv\.deps_installed"
    echo [OK] Dependencies installed.
)

:: Check Node.js for WhatsApp (optional)
where node >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js found — WhatsApp bot will be available.
    if not exist "%BACKEND_DIR%\node_modules\whatsapp-web.js" (
        echo [SETUP] Installing WhatsApp bot dependencies...
        pushd "%BACKEND_DIR%"
        call npm install --production >nul 2>&1
        popd
        echo [OK] WhatsApp dependencies installed.
    )
) else (
    echo [INFO] Node.js not found — WhatsApp bot will be disabled.
    echo        Install from https://nodejs.org/ to enable it.
)

echo.
echo ========================================================
echo    Starting DocManager Server...
echo    (Keep this window open while using the application)
echo ========================================================
echo.

:: Set PYTHONPATH so shared module is found
set "PYTHONPATH=%BACKEND_DIR%\..\..;%PYTHONPATH%"

:: Start the production server
pushd "%BACKEND_DIR%"
start "" http://127.0.0.1:8443
python main_prod.py
popd

:: If we get here, server stopped
echo.
echo DocManager has stopped.
pause
