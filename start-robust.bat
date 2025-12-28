@echo off
echo Interview Coach System Startup Script
echo =============================

echo Checking Python dependencies...
cd /d %~dp0\src
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Failed to install Python dependencies
    pause
    exit /b 1
)

echo Starting backend server...
start "Backend Server" cmd /k "python web_server.py"

echo Waiting for backend server to start...
timeout /t 5 /nobreak > nul

echo Checking if backend is running...
curl -s http://127.0.0.1:5000/api/status > nul
if %ERRORLEVEL% neq 0 (
    echo Backend server may not be running properly
    echo Please check the backend server window for errors
    pause
    exit /b 1
)

echo Backend server is running!

echo Checking Node.js dependencies...
cd /d %~dp0\app
if not exist node_modules (
    echo Installing Node.js dependencies...
    npm install
    if %ERRORLEVEL% neq 0 (
        echo Failed to install Node.js dependencies
        pause
        exit /b 1
    )
)

echo Starting frontend server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo System is starting...
echo Backend server address: http://127.0.0.1:5000
echo Frontend server address: http://127.0.0.1:5173
echo.
echo Please wait a few seconds, then open your browser and visit http://127.0.0.1:5173
echo.
pause