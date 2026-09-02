@echo off
echo ===================================================
echo   Starting AuthGuard Dual Servers
echo ===================================================
echo.

echo [1/2] Starting Python API on Port 5000...
start "AuthGuard API (Python)" cmd /k "cd /d c:\voice-check && python run.py"

echo [2/2] Starting Next.js UI on Port 3000...
start "AuthGuard UI (React)" cmd /k "cd /d c:\voice-check\frontend && npm run dev"

echo.
echo Both servers are booting up in separate windows!
echo You can now open your browser to: http://localhost:3000
echo.
pause
