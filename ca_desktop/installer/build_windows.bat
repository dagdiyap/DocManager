@echo off
setlocal enabledelayedexpansion
title DocManager - Windows Build
color 0E

echo.
echo ========================================================
echo    DocManager CA Desktop — Windows Build Script
echo ========================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%..\backend"
set "PROJECT_ROOT=%SCRIPT_DIR%..\.."

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)
echo [OK] Python found.

:: Check/create venv
if not exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo [SETUP] Creating virtual environment...
    python -m venv "%BACKEND_DIR%\venv"
)
call "%BACKEND_DIR%\venv\Scripts\activate.bat"

:: Install build dependencies
echo [BUILD] Installing dependencies...
pip install -q --upgrade pip
pip install -q -r "%BACKEND_DIR%\requirements-prod.txt"
pip install -q pyinstaller

:: Build frontend (if npm available)
where npm >nul 2>&1
if %errorlevel% equ 0 (
    if exist "%BACKEND_DIR%\..\frontend\package.json" (
        echo [BUILD] Building frontend...
        pushd "%BACKEND_DIR%\..\frontend"
        call npm install
        call npm run build
        popd
    )
)

:: Run PyInstaller
echo.
echo [BUILD] Running PyInstaller...
pushd "%BACKEND_DIR%"
pyinstaller --clean --noconfirm DocManager.spec
if %errorlevel% neq 0 (
    echo.
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)
popd

:: Copy Node.js files for WhatsApp (runs as subprocess, not bundled in .exe)
echo [BUILD] Copying WhatsApp server files...
set "DIST_DIR=%BACKEND_DIR%\dist\DocManager"
if exist "%DIST_DIR%" (
    xcopy /Y /I "%BACKEND_DIR%\package.json" "%DIST_DIR%\" >nul
    xcopy /Y /I "%BACKEND_DIR%\package-lock.json" "%DIST_DIR%\" >nul 2>&1
    xcopy /Y /I /E "%BACKEND_DIR%\src\services\whatsapp\*.js" "%DIST_DIR%\src\services\whatsapp\" >nul

    :: Copy .env.example as template
    if exist "%BACKEND_DIR%\.env.example" (
        xcopy /Y "%BACKEND_DIR%\.env.example" "%DIST_DIR%\" >nul
    )

    :: Copy launcher
    xcopy /Y "%SCRIPT_DIR%StartDocManager.bat" "%DIST_DIR%\..\installer\" >nul 2>&1
)

echo.
echo ========================================================
echo    BUILD COMPLETE
echo ========================================================
echo.
echo Distribution folder: %DIST_DIR%
echo.
echo To distribute:
echo   1. Zip the "dist\DocManager" folder
echo   2. Send to CA
echo   3. CA extracts and runs DocManager.exe
echo.
echo To test locally:
echo   cd "%DIST_DIR%"
echo   DocManager.exe
echo.
pause
