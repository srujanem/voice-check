@echo off
echo.
echo ============================================
echo   STOPPING AI SHIELD SERVER
echo ============================================
echo.
echo Finding Python processes running uvicorn...
taskkill /F /FI "WINDOWTITLE eq AI-Shield-Backend*" >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
echo.
echo Server successfully stopped!
