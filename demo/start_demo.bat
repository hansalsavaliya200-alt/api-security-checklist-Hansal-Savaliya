@echo off
setlocal
cd /d "%~dp0"

set "APP_URL=http://127.0.0.1:5000/"
set "PYTHON=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON=%CD%\.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python was not found. Install Python 3.10 or newer and try again.
        pause
        exit /b 1
    )
)

powershell.exe -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing -Uri '%APP_URL%' -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
if not errorlevel 1 (
    echo The Flask demo is already running. Opening the frontend.
    start "" "%APP_URL%"
    exit /b 0
)

echo Starting the Flask API and browser frontend...
echo Open %APP_URL%
echo Press Ctrl+C in this window to stop the server.

start "" /b powershell.exe -NoProfile -WindowStyle Hidden -Command "$deadline = (Get-Date).AddSeconds(30); do { try { Invoke-WebRequest -UseBasicParsing -Uri '%APP_URL%' -TimeoutSec 1 | Out-Null; Start-Process '%APP_URL%'; exit 0 } catch { Start-Sleep -Milliseconds 500 } } while ((Get-Date) -lt $deadline)"
"%PYTHON%" app.py

endlocal
