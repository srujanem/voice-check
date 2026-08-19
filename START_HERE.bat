@echo off
title AuthGuard — Start Server
color 0A
echo.
echo  =====================================================
echo   AuthGuard — Starting Backend Server
echo  =====================================================
echo.
cd /d "D:\voice-check\voice-check"
echo [1/2] Stopping any old Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo       Done.
echo.
echo [2/2] Starting Flask backend on http://localhost:5000 ...
start "" /min python run.py
timeout /t 5 /nobreak >nul
echo.
echo  =====================================================
echo   Server is RUNNING at http://localhost:5000
echo   Open your browser and go to your frontend!
echo  =====================================================
echo.
echo  Press any key to close this window (server keeps running)
pause >nul
