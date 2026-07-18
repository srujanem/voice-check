@echo off
title AI Shield - Server + Tunnel

echo ============================================
echo   AI SHIELD - Starting Server and Tunnel
echo ============================================

:: Refresh PATH so cloudflared is found
set PATH=%PATH%;C:\Program Files (x86)\cloudflared;C:\Program Files\cloudflared

:: Start the backend server in background
echo [1/2] Starting AI Shield backend on port 8000...
start "AI-Shield-Backend" cmd /k "cd /d ""%~dp0"" && python run.py"

:: Wait for server to boot
echo     Waiting for server to start...
timeout /t 5 /nobreak >nul

:: Start permanent cloudflare tunnel
echo [2/2] Starting Cloudflare Tunnel...
echo     Your permanent URL will appear below:
echo     (It looks like: https://something.trycloudflare.com)
echo.
cloudflared tunnel --url http://localhost:8000

pause
