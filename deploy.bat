@echo off
color 0B
title Vercel Deployer
echo ===================================================
echo      Deploying AuthGuard Website to Vercel...
echo ===================================================
echo.
cd /d c:\voice-check

:: Run the vercel deployment
call vercel

echo.
echo ===================================================
echo   Deployment Finished! Check the Vercel link above.
echo ===================================================
echo.
pause
