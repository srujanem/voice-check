@echo off
title AuthGuard — Server + Tunnel Auto-Start
color 0A
echo.
echo  ====================================================
echo   AuthGuard — Starting Server and Cloudflare Tunnel
echo  ====================================================
echo.

cd /d "D:\voice-check\voice-check"

:: ─── Step 1: Kill old instances ────────────────────────────────────────────
echo [1/4] Stopping old processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo       Done.
echo.

:: ─── Step 2: Start Flask server ────────────────────────────────────────────
echo [2/4] Starting Flask backend server...
start "" /min python run.py
timeout /t 6 /nobreak >nul
echo       Server started on http://localhost:5000
echo.

:: ─── Step 3: Start tunnel and capture URL ──────────────────────────────────
echo [3/4] Starting Cloudflare tunnel...
set LOG_FILE=%TEMP%\cf_tunnel.log

:: Start cloudflared in background, redirect output to log file
start "" /min cmd /c "cloudflared tunnel --url http://localhost:5000 --no-autoupdate > %LOG_FILE% 2>&1"

:: Wait for tunnel URL to appear in log
echo       Waiting for tunnel URL...
set TUNNEL_URL=
set /a WAIT=0
:WAIT_LOOP
timeout /t 2 /nobreak >nul
set /a WAIT+=2
findstr /C:"trycloudflare.com" %LOG_FILE% >nul 2>&1
if %errorlevel%==0 goto FOUND_URL
if %WAIT% GEQ 30 goto TIMEOUT
goto WAIT_LOOP

:FOUND_URL
for /f "tokens=*" %%a in ('findstr "trycloudflare.com" %LOG_FILE%') do set LINE=%%a
:: Extract just the URL from the line
for %%a in (%LINE%) do (
    echo %%a | findstr /C:"https://" >nul 2>&1
    if not errorlevel 1 set TUNNEL_URL=%%a
)
echo       Tunnel URL: %TUNNEL_URL%
echo.
goto UPDATE_CONFIG

:TIMEOUT
echo       WARNING: Could not get tunnel URL within 30s
echo       Server still running locally at http://localhost:5000
goto DONE

:UPDATE_CONFIG
:: ─── Step 4: Auto-update server-config.js and push to GitHub ───────────────
echo [4/4] Updating website with new tunnel URL...

:: Update server-config.js using Python
python -c "
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
url = '%TUNNEL_URL%'
path = 'D:/voice-check/voice-check/server-config.js'
content = open(path, encoding='utf-8').read()
new_content = re.sub(
    r\"const DEFAULT_URL = '[^']*'\",
    f\"const DEFAULT_URL = '{url}'\",
    content
)
open(path, 'w', encoding='utf-8').write(new_content)
print(f'Updated server-config.js with: {url}')
"

:: Push to GitHub
git add server-config.js
git commit -m "auto: update tunnel URL to %TUNNEL_URL%"
git push origin main

:: Deploy to Vercel
echo       Deploying to Vercel...
call npx -y vercel --prod --yes >nul 2>&1
echo       Vercel updated!

:DONE
echo.
echo  ====================================================
echo   AuthGuard is LIVE!
echo   Local:  http://localhost:5000
if defined TUNNEL_URL echo   Remote: %TUNNEL_URL%
echo  ====================================================
echo.
echo  This window must stay open for the server to work.
echo  Press Ctrl+C to stop everything.
echo.
pause
