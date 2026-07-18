@echo off
echo.
echo ============================================
echo   STARTING CLIENT WEBSITE on Port 5000
echo ============================================
echo.
echo This will run your frontend website. 
echo It will connect to the AI Shield Backend at port 8000.
echo.
cd /d "%~dp0client_website"
echo Starting server...
echo Open your browser to: http://127.0.0.1:5000
echo.
python -m http.server 5000
pause
