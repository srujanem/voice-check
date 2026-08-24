@echo off
color 0B
title AuthGuard Master Server
echo ===================================================
echo     Starting AuthGuard AI Server
echo ===================================================
echo.

echo [1/2] Starting Python AI Server (Port 5000)...
start "Python Backend (Port 5000)" /min cmd /c "cd /d c:\voice-check && python run.py"

echo [2/2] Starting Website Server (Port 8000)...
start "AuthGuard Website (Port 8000)" /min cmd /c "cd /d c:\voice-check && python -m http.server 8000"

timeout /t 3 /nobreak >nul

echo.
echo ===================================================
echo   SUCCESS! Opening your website now...
echo ===================================================
start http://localhost:8000
echo.
pause
