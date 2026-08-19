@echo off
echo Starting AuthGuard Backend Servers...

echo [1/3] Starting Flask ML Backend (Port 5000)...
start /B "Flask" cmd /c "cd /d D:\voice-check\voice-check && python run.py"

echo [2/3] Starting Node API Gateway (Port 8000)...
start /B "Node" cmd /c "cd /d D:\Server\ai-training-panel\node_server && node server.js"

echo [3/3] Starting Permanent Ngrok Tunnel...
start "Ngrok Tunnel" cmd /c "cd /d D:\voice-check\voice-check && ngrok http 8000"

echo.
echo All systems go! Your permanent URL is: https://blitz-untimed-yiddish.ngrok-free.dev
echo You can close this window, but leave the Ngrok window open.
pause
