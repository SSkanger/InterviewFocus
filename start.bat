@echo off
echo Interview Coach System Startup Script
echo =============================

echo Starting backend server...
start cmd /k "cd /d %~dp0\src && python web_server.py"

echo Waiting for backend server to start...
timeout /t 3 /nobreak > nul

echo Starting frontend server...
start cmd /k "cd /d %~dp0\app && npm run dev"

echo.
echo System is starting...
echo Backend server address: http://localhost:5000
echo Frontend server address: http://localhost:5173
echo.
echo Please wait a few seconds, then open your browser and visit http://localhost:5173
echo.
pause