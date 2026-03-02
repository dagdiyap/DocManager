@echo off
setlocal enabledelayedexpansion
title DocManager CA Desktop — Setup ^& Launch
color 0A

echo.
echo ================================================================
echo     DocManager CA Desktop — Full Setup ^& Launch
echo ================================================================
echo.
echo   This script will install everything needed automatically.
echo   Please keep this window open and stay connected to the internet.
echo.

:: ---------------------------------------------------------------------------
:: PATHS
:: ---------------------------------------------------------------------------
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%..\backend"
set "PROJECT_ROOT=%SCRIPT_DIR%..\.."

:: ---------------------------------------------------------------------------
:: STEP 0: Check for packaged .exe first (skip all setup if found)
:: ---------------------------------------------------------------------------
if exist "%BACKEND_DIR%\dist\DocManager\DocManager.exe" (
    echo [OK] Found packaged executable — starting directly.
    start "" "%BACKEND_DIR%\dist\DocManager\DocManager.exe"
    timeout /t 5 /nobreak >nul
    start "" http://127.0.0.1:8443
    goto :done
)
if exist "%BACKEND_DIR%\dist\DocManager.exe" (
    echo [OK] Found packaged executable — starting directly.
    start "" "%BACKEND_DIR%\dist\DocManager.exe"
    timeout /t 5 /nobreak >nul
    start "" http://127.0.0.1:8443
    goto :done
)

echo [INFO] Running from source — checking all dependencies...
echo.

:: ---------------------------------------------------------------------------
:: STEP 1: INSTALL PYTHON (if missing)
:: ---------------------------------------------------------------------------
echo [1/6] Checking Python...
where python >nul 2>&1
if !errorlevel! equ 0 goto :python_found
echo        Python not found. Installing automatically...
echo.
goto :install_python

:python_found
goto :python_ok

:install_python
:: Try winget first (built into Windows 10 1709+ and Windows 11)
where winget >nul 2>&1
if !errorlevel! neq 0 goto :install_python_manual

echo        Installing Python via winget (this may take a few minutes)...
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
if !errorlevel! neq 0 (
    echo        winget install failed. Trying alternative method...
    goto :install_python_manual
)
echo        Python installed via winget. Refreshing PATH...
call :refresh_path
where python >nul 2>&1
if !errorlevel! equ 0 goto :python_ok
echo.
echo   ERROR: Python was installed but is not in PATH yet.
echo   Please CLOSE this window and run StartDocManager.bat again.
echo   (Windows needs a restart of the terminal to detect new programs)
echo.
pause
exit /b 1

:install_python_manual
echo        Downloading Python installer...
set "PY_INSTALLER=%TEMP%\python_installer.exe"
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe' -OutFile '%PY_INSTALLER%'" 2>nul
if not exist "%PY_INSTALLER%" (
    echo.
    echo   ERROR: Could not download Python installer.
    echo   Please check your internet connection, or install Python manually:
    echo     https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo        Running Python installer (this may take a few minutes)...
echo        Python will be added to PATH automatically.
"%PY_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
if !errorlevel! neq 0 (
    echo.
    echo   ERROR: Automatic Python installation failed.
    echo   Please install Python manually:
    echo     1. Go to https://www.python.org/downloads/
    echo     2. Download Python 3.12
    echo     3. Run installer — CHECK "Add Python to PATH"
    echo     4. Run StartDocManager.bat again
    echo.
    del "%PY_INSTALLER%" 2>nul
    pause
    exit /b 1
)
del "%PY_INSTALLER%" 2>nul
echo        Python installed. Refreshing PATH...
call :refresh_path
where python >nul 2>&1
if !errorlevel! equ 0 goto :python_ok
echo.
echo   Python was installed but PATH hasn't updated yet.
echo   Please CLOSE this window and run StartDocManager.bat again.
echo.
pause
exit /b 1

:python_ok
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo        Python %PY_VER% [OK]

:: ---------------------------------------------------------------------------
:: STEP 2: INSTALL NODE.JS (if missing) — REQUIRED for WhatsApp bot
:: ---------------------------------------------------------------------------
echo [2/6] Checking Node.js...
where node >nul 2>&1
if !errorlevel! equ 0 goto :node_found
echo        Node.js not found. Installing automatically...
echo.
goto :install_node

:node_found
goto :node_ok

:install_node
:: Try winget first
where winget >nul 2>&1
if !errorlevel! neq 0 goto :install_node_manual

echo        Installing Node.js via winget (this may take a few minutes)...
winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements --silent
if !errorlevel! neq 0 (
    echo        winget install failed. Trying alternative method...
    goto :install_node_manual
)
echo        Node.js installed via winget. Refreshing PATH...
call :refresh_path
where node >nul 2>&1
if !errorlevel! equ 0 goto :node_ok
echo.
echo   Node.js was installed but is not in PATH yet.
echo   Please CLOSE this window and run StartDocManager.bat again.
echo.
pause
exit /b 1

:install_node_manual
echo        Downloading Node.js installer...
set "NODE_INSTALLER=%TEMP%\node_installer.msi"
powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.11.1/node-v20.11.1-x64.msi' -OutFile '%NODE_INSTALLER%'" 2>nul
if not exist "%NODE_INSTALLER%" (
    echo.
    echo   ERROR: Could not download Node.js installer.
    echo   Please check your internet connection, or install Node.js manually:
    echo     https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo        Running Node.js installer (this may take a few minutes)...
msiexec /i "%NODE_INSTALLER%" /quiet /norestart
if !errorlevel! neq 0 (
    echo.
    echo   ERROR: Automatic Node.js installation failed.
    echo   Please install Node.js manually:
    echo     1. Go to https://nodejs.org/
    echo     2. Download the LTS version
    echo     3. Run the installer
    echo     4. Run StartDocManager.bat again
    echo.
    del "%NODE_INSTALLER%" 2>nul
    pause
    exit /b 1
)
del "%NODE_INSTALLER%" 2>nul
echo        Node.js installed. Refreshing PATH...
call :refresh_path
where node >nul 2>&1
if !errorlevel! equ 0 goto :node_ok
echo.
echo   Node.js was installed but PATH hasn't updated yet.
echo   Please CLOSE this window and run StartDocManager.bat again.
echo.
pause
exit /b 1

:node_ok
for /f "tokens=1 delims= " %%v in ('node --version 2^>^&1') do set "NODE_VER=%%v"
echo        Node.js %NODE_VER% [OK]

:: ---------------------------------------------------------------------------
:: STEP 3: CREATE PYTHON VIRTUAL ENVIRONMENT
:: ---------------------------------------------------------------------------
echo [3/6] Checking Python environment...
if exist "%BACKEND_DIR%\venv\Scripts\activate.bat" goto :venv_exists
echo        Creating virtual environment (first run)...
python -m venv "%BACKEND_DIR%\venv"
if !errorlevel! neq 0 (
    echo   ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)
echo        Virtual environment created.

:venv_exists
call "%BACKEND_DIR%\venv\Scripts\activate.bat"
echo        Python venv [OK]

:: ---------------------------------------------------------------------------
:: STEP 4: INSTALL PYTHON DEPENDENCIES
:: ---------------------------------------------------------------------------
echo [4/6] Checking Python dependencies...
if exist "%BACKEND_DIR%\venv\.deps_installed" goto :pip_done
echo        Installing Python packages (first run, may take 1-2 minutes)...
pip install --quiet --upgrade pip
pip install --quiet -r "%BACKEND_DIR%\requirements-prod.txt"
if !errorlevel! neq 0 (
    echo.
    echo   ERROR: Failed to install Python packages.
    echo   Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
echo installed> "%BACKEND_DIR%\venv\.deps_installed"
echo        Python packages installed.

:pip_done
echo        Python dependencies [OK]

:: ---------------------------------------------------------------------------
:: STEP 5: INSTALL NODE.JS DEPENDENCIES (for WhatsApp bot)
:: ---------------------------------------------------------------------------
echo [5/6] Checking WhatsApp bot dependencies...
if exist "%BACKEND_DIR%\node_modules\whatsapp-web.js" goto :npm_done
echo        Installing WhatsApp bot packages (first run)...
pushd "%BACKEND_DIR%"
call npm install --production
if !errorlevel! neq 0 (
    popd
    echo.
    echo   ERROR: Failed to install WhatsApp bot packages.
    echo   Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
popd
echo        WhatsApp packages installed.

:npm_done
echo        Node.js dependencies [OK]

:: ---------------------------------------------------------------------------
:: STEP 6: VERIFY EVERYTHING
:: ---------------------------------------------------------------------------
echo [6/6] Final verification...

if not exist "%BACKEND_DIR%\main_prod.py" (
    echo   ERROR: main_prod.py not found. Installation may be corrupted.
    pause
    exit /b 1
)
if not exist "%BACKEND_DIR%\src\main.py" (
    echo   ERROR: src\main.py not found. Installation may be corrupted.
    pause
    exit /b 1
)
if not exist "%PROJECT_ROOT%\shared\__init__.py" (
    echo   ERROR: shared module not found. Installation may be corrupted.
    pause
    exit /b 1
)
echo        All files verified [OK]

:: ---------------------------------------------------------------------------
:: ALL DEPS READY — START THE APPLICATION
:: ---------------------------------------------------------------------------
echo.
echo ================================================================
echo     All dependencies installed successfully!
echo     Starting DocManager...
echo     (Keep this window open while using the application)
echo ================================================================
echo.

:: Set PYTHONPATH so shared module is found
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

:: Start the production server (main_prod.py handles WhatsApp subprocess)
:: Browser opens after a delay to give the server time to boot
pushd "%BACKEND_DIR%"
start "" /b cmd /c "timeout /t 6 /nobreak >nul & start http://127.0.0.1:8443"
python main_prod.py
popd

:: Server stopped
echo.
echo ================================================================
echo     DocManager has stopped.
echo ================================================================
pause
goto :done

:: ---------------------------------------------------------------------------
:: UTILITY: Refresh PATH without restarting the terminal
:: ---------------------------------------------------------------------------
:refresh_path
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USR_PATH=%%b"
set "PATH=%SYS_PATH%;%USR_PATH%"
:: Also add common Python/Node install locations
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
set "PATH=%PATH%;%PROGRAMFILES%\Python312;%PROGRAMFILES%\Python312\Scripts"
set "PATH=%PATH%;%PROGRAMFILES%\nodejs;%APPDATA%\npm"
goto :eof

:done
