# Personal AI Game Development Assistant Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  THANGAN // PERSONAL GAME DEV AI COMPANION               " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Target Engine : Unreal Engine 5.4" -ForegroundColor Green
Write-Host "Technologies  : Modern C++, Blueprints, Blender 4.x" -ForegroundColor Green
Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray

$BASE_DIR = $PSScriptRoot
$env:PYTHONPATH = "$BASE_DIR\backend"

Write-Host "[1/2] Opening browser to http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process "http://localhost:8000"

Write-Host "[2/2] Launching Companion Server on http://localhost:8000 ..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the companion." -ForegroundColor DarkGray
python -m uvicorn app.main:app --app-dir "$BASE_DIR\backend" --host 127.0.0.1 --port 8000 --reload
