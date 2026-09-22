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

:: Resolve directory where this script lives (fully portable)
set "BASE_DIR=%~dp0"
set "PYTHONPATH=%BASE_DIR%backend"
cd /d "%BASE_DIR%"

echo [1/3] Checking Python & Dependencies...
python -c "import fastapi, uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Dependencies not found. Installing packages from requirements.txt...
    python -m pip install -r "%BASE_DIR%backend\requirements.txt"
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo [ERROR] Failed to install dependencies. Make sure Python 3.10+ is installed and in your PATH.
        pause
        exit /b 1
    )
)

echo [2/3] Opening browser to http://localhost:8000 ...
start "" "http://localhost:8000"

echo [3/3] Launching Companion Server on port 8000 ...
echo Press CTRL+C to stop the server.
echo.

python -m uvicorn app.main:app --app-dir "%BASE_DIR%backend" --host 127.0.0.1 --port 8000 --reload

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server terminated with an error.
    pause
)
