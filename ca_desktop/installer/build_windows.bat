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

:: ---------------------------------------------------------------------------
:: CHECK ALL REQUIRED TOOLS
:: ---------------------------------------------------------------------------
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.10+ first.
    pause
    exit /b 1
)
echo [OK] Python found.

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Install Node.js LTS from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found.

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm not found. Reinstall Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] npm found.

:: ---------------------------------------------------------------------------
:: PYTHON SETUP
:: ---------------------------------------------------------------------------
if not exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo [SETUP] Creating virtual environment...
    python -m venv "%BACKEND_DIR%\venv"
)
call "%BACKEND_DIR%\venv\Scripts\activate.bat"

echo [BUILD] Installing Python dependencies...
pip install -q --upgrade pip
pip install -q -r "%BACKEND_DIR%\requirements-prod.txt"
pip install -q pyinstaller

:: ---------------------------------------------------------------------------
:: NODE.JS SETUP
:: ---------------------------------------------------------------------------
echo [BUILD] Installing Node.js dependencies...
pushd "%BACKEND_DIR%"
call npm install --production
if %errorlevel% neq 0 (
    echo ERROR: npm install failed. Check your internet connection.
    popd
    pause
    exit /b 1
)
popd
echo [OK] Node.js dependencies installed.

:: ---------------------------------------------------------------------------
:: BUILD FRONTEND
:: ---------------------------------------------------------------------------
if exist "%BACKEND_DIR%\..\frontend\package.json" (
    echo [BUILD] Building frontend...
    pushd "%BACKEND_DIR%\..\frontend"
    call npm install
    call npm run build
    if %errorlevel% neq 0 (
        echo WARNING: Frontend build failed. Continuing without frontend.
    )
    popd
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

:: ---------------------------------------------------------------------------
:: COPY FILES TO DIST
:: ---------------------------------------------------------------------------
echo [BUILD] Copying WhatsApp server files to dist...
set "DIST_DIR=%BACKEND_DIR%\dist\DocManager"
if not exist "%DIST_DIR%" (
    echo ERROR: dist folder not found. PyInstaller may have failed.
    pause
    exit /b 1
)

:: WhatsApp JS files
xcopy /Y /I "%BACKEND_DIR%\package.json" "%DIST_DIR%\" >nul
xcopy /Y /I "%BACKEND_DIR%\package-lock.json" "%DIST_DIR%\" >nul 2>&1
mkdir "%DIST_DIR%\src\services\whatsapp" 2>nul
xcopy /Y /I "%BACKEND_DIR%\src\services\whatsapp\*.js" "%DIST_DIR%\src\services\whatsapp\" >nul

:: .env template
if exist "%BACKEND_DIR%\.env.example" (
    xcopy /Y "%BACKEND_DIR%\.env.example" "%DIST_DIR%\" >nul
)

:: Launcher
mkdir "%DIST_DIR%\..\installer" 2>nul
xcopy /Y "%SCRIPT_DIR%StartDocManager.bat" "%DIST_DIR%\..\installer\" >nul 2>&1
xcopy /Y "%SCRIPT_DIR%README_INSTALL.md" "%DIST_DIR%\..\installer\" >nul 2>&1

:: ---------------------------------------------------------------------------
:: INSTALL NODE DEPS INSIDE DIST (so .exe can start WhatsApp subprocess)
:: ---------------------------------------------------------------------------
echo [BUILD] Installing Node.js dependencies in dist folder...
pushd "%DIST_DIR%"
call npm install --production
if %errorlevel% neq 0 (
    echo ERROR: npm install in dist folder failed.
    popd
    pause
    exit /b 1
)
popd
echo [OK] Node.js dependencies installed in dist.

:: ---------------------------------------------------------------------------
:: VERIFY BUILD
:: ---------------------------------------------------------------------------
echo.
echo [BUILD] Verifying build output...
set BUILD_OK=1
if not exist "%DIST_DIR%\DocManager.exe" (
    echo   MISSING: DocManager.exe
    set BUILD_OK=0
)
if not exist "%DIST_DIR%\src\services\whatsapp\server.js" (
    echo   MISSING: src\services\whatsapp\server.js
    set BUILD_OK=0
)
if not exist "%DIST_DIR%\node_modules\whatsapp-web.js" (
    echo   MISSING: node_modules\whatsapp-web.js
    set BUILD_OK=0
)
if not exist "%DIST_DIR%\package.json" (
    echo   MISSING: package.json
    set BUILD_OK=0
)

if "%BUILD_OK%"=="0" (
    echo.
    echo   WARNING: Some files are missing from the build.
    echo   The distribution may not work correctly.
) else (
    echo   All required files present [OK]
)

echo.
echo ================================================================
echo    BUILD COMPLETE
echo ================================================================
echo.
echo   Distribution folder: %DIST_DIR%
echo.
echo   To distribute to CA:
echo     1. Zip the entire "dist\DocManager" folder
echo     2. Send the zip to the CA
echo     3. CA extracts and double-clicks DocManager.exe
echo.
echo   To test locally:
echo     cd "%DIST_DIR%"
echo     DocManager.exe
echo.
pause
