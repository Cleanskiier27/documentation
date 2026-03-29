@echo off
title NetworkBuster Auto-Start
cd /d "C:\Users\ceans\OneDrive\Documents\GitHub\networkbuster.net"

echo Starting NetworkBuster Services...
echo.

:: Start servers in background
start "NetworkBuster Servers" /min cmd /c "node start-servers.js"

:: Wait a moment
timeout /t 5 /nobreak > nul

echo NetworkBuster services started!
echo.
echo Close this window or it will close in 10 seconds...
timeout /t 10
