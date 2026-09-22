@echo off
title Thangan - GameDev AI Companion
color 0B
cls
echo ==========================================================
echo   THANGAN // PERSONAL GAME DEV AI COMPANION
echo ==========================================================
echo Target Engine : Unreal Engine 5.4
echo Technologies  : Modern C++, Blueprints, Blender 4.x
echo ----------------------------------------------------------

set "BASE_DIR=%~dp0"
set "PYTHONPATH=%BASE_DIR%backend"
cd /d "%BASE_DIR%"

echo [1/3] Locating Python environment...

set "PYTHON_EXE="

:: 1. Probe py launcher versions
py -3.13 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYTHON_EXE=py -3.13" & goto :found_python

py -3.12 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYTHON_EXE=py -3.12" & goto :found_python

py -3.11 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYTHON_EXE=py -3.11" & goto :found_python

py -3.10 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYTHON_EXE=py -3.10" & goto :found_python

py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYTHON_EXE=py -3" & goto :found_python

:: 2. Probe default python on PATH
python -c "import sys" >nul 2>&1
if not errorlevel 1 set "PYTHON_EXE=python" & goto :found_python

:: 3. Probe standard installation paths
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe" & goto :found_python
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe" & goto :found_python
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe" & goto :found_python
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe" & goto :found_python

if exist "C:\Program Files\Python313\python.exe" set "PYTHON_EXE=C:\Program Files\Python313\python.exe" & goto :found_python
if exist "C:\Program Files\Python312\python.exe" set "PYTHON_EXE=C:\Program Files\Python312\python.exe" & goto :found_python
if exist "C:\Program Files\Python311\python.exe" set "PYTHON_EXE=C:\Program Files\Python311\python.exe" & goto :found_python
if exist "C:\Program Files\Python310\python.exe" set "PYTHON_EXE=C:\Program Files\Python310\python.exe" & goto :found_python

if exist "C:\Python313\python.exe" set "PYTHON_EXE=C:\Python313\python.exe" & goto :found_python
if exist "C:\Python312\python.exe" set "PYTHON_EXE=C:\Python312\python.exe" & goto :found_python
if exist "C:\Python311\python.exe" set "PYTHON_EXE=C:\Python311\python.exe" & goto :found_python
if exist "C:\Python310\python.exe" set "PYTHON_EXE=C:\Python310\python.exe" & goto :found_python

:: No Python found
echo.
echo ==========================================================
echo [ERROR] No working Python installation was found.
echo ==========================================================
echo If you saw an error like:
echo   pythoncore-3.14-64 was not found
echo.
echo That means Windows has a broken Python registration.
echo.
echo Quick Fix:
echo 1. Download and install Python 3.12 or 3.11 from:
echo    https://www.python.org/downloads/
echo 2. IMPORTANT: Check the box "Add python.exe to PATH"
echo ==========================================================
echo.
pause
exit /b 1

:found_python
echo [OK] Using Python: %PYTHON_EXE%

echo.
echo [2/3] Checking dependencies...
%PYTHON_EXE% -c "import fastapi, uvicorn" >nul 2>&1
if not errorlevel 1 goto :deps_ok

echo Dependencies not found. Installing packages from requirements.txt...
%PYTHON_EXE% -m pip install -r "%BASE_DIR%backend\requirements.txt"
if errorlevel 1 goto :pip_failed

:deps_ok
echo.
echo [3/3] Launching Companion Server...
%PYTHON_EXE% "%BASE_DIR%backend\run_server.py"
if errorlevel 1 goto :server_error
goto :eof

:pip_failed
echo.
echo [ERROR] Failed to install dependencies via pip.
pause
exit /b 1

:server_error
echo.
echo [ERROR] Server terminated with an error code.
pause
exit /b 1
