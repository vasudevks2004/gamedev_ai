@echo off
setlocal enabledelayedexpansion
title Thangan - GameDev AI Companion
color 0B
cls
echo ==========================================================
echo   THANGAN // PERSONAL GAME DEV AI COMPANION
echo ==========================================================
echo Target Engine : Unreal Engine 5.4
echo Technologies  : Modern C++, Blueprints, Blender 4.x
echo ----------------------------------------------------------

:: Resolve directory where this script lives (fully portable)
set "BASE_DIR=%~dp0"
set "PYTHONPATH=%BASE_DIR%backend"
cd /d "%BASE_DIR%"

echo [1/3] Locating Python environment...

set "PYTHON_CMD="

:: 1. Try py -3.12
if not defined PYTHON_CMD (
    py -3.12 -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "PYTHON_CMD=py -3.12"
)

:: 2. Try py -3.11
if not defined PYTHON_CMD (
    py -3.11 -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "PYTHON_CMD=py -3.11"
)

:: 3. Try py -3.10
if not defined PYTHON_CMD (
    py -3.10 -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "PYTHON_CMD=py -3.10"
)

:: 4. Try generic py -3
if not defined PYTHON_CMD (
    py -3 -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "PYTHON_CMD=py -3"
)

:: 5. Try default python command if not broken
if not defined PYTHON_CMD (
    python -c "import sys" >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "PYTHON_CMD=python"
)

:: 6. Check well-known local paths
if not defined PYTHON_CMD (
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        "C:\Program Files\Python312\python.exe"
        "C:\Program Files\Python311\python.exe"
        "C:\Program Files\Python310\python.exe"
        "C:\Python312\python.exe"
        "C:\Python311\python.exe"
        "C:\Python310\python.exe"
        "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    ) do (
        if not defined PYTHON_CMD (
            if exist %%P (
                %%P -c "import sys" >nul 2>&1
                if !ERRORLEVEL! EQU 0 set "PYTHON_CMD=%%P"
            )
        )
    )
)

if not defined PYTHON_CMD (
    echo.
    echo ==========================================================
    echo [ERROR] No working Python installation was found.
    echo ==========================================================
    echo Windows reported a broken Python 3.14 path on this machine:
    echo   pythoncore-3.14-64 was not found (0x0003).
    echo.
    echo HOW TO FIX IN 1 MINUTE:
    echo   1. Run this in your terminal or Command Prompt:
    echo        py --list
    echo        py install --repair
    echo.
    echo   2. Or download a clean Python 3.12 installer from:
    echo        https://www.python.org/downloads/
    echo        *(IMPORTANT: Check "Add python.exe to PATH" during install)*
    echo ==========================================================
    echo.
    pause
    exit /b 1
)

echo [OK] Using Python: !PYTHON_CMD!

echo [2/3] Checking dependencies...
!PYTHON_CMD! -c "import fastapi, uvicorn" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo Installing required packages from requirements.txt...
    !PYTHON_CMD! -m pip install -r "%BASE_DIR%backend\requirements.txt"
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo [ERROR] Failed to install dependencies via pip.
        pause
        exit /b 1
    )
)

echo [3/3] Launching Companion Server on http://localhost:8000 ...
start "" "http://localhost:8000"
echo.
echo Server active. Press CTRL+C to stop.
echo.

!PYTHON_CMD! -m uvicorn app.main:app --app-dir "%BASE_DIR%backend" --host 127.0.0.1 --port 8000 --reload

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo [ERROR] Server terminated with an error.
    pause
)
