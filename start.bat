@echo off
chcp 65001 > nul
title 智能面试模拟系统启动器

echo.
echo ========================================
echo   智能面试模拟系统 - 启动中...
echo ========================================
echo.

:: 检查Python是否安装
echo [1/5] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

:: 检查Node.js是否安装
echo.
echo [2/5] 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Node.js，请先安装Node.js 16或更高版本
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js版本: %NODE_VERSION%

:: 检查Python依赖
echo.
echo [3/5] 检查Python依赖...
cd /d "%~dp0src"
if not exist "requirements.txt" (
    echo ❌ 错误: 未找到requirements.txt文件
    pause
    exit /b 1
)
echo 正在检查依赖...
pip show opencv-python >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装Python依赖...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 错误: Python依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ Python依赖已就绪

:: 检查Node.js依赖
echo.
echo [4/5] 检查Node.js依赖...
cd /d "%~dp0app"
if not exist "package.json" (
    echo ❌ 错误: 未找到package.json文件
    pause
    exit /b 1
)
if not exist "node_modules" (
    echo 正在安装Node.js依赖...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ 错误: Node.js依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ Node.js依赖已就绪

:: 启动后端服务器
echo.
echo [5/5] 启动服务器...
cd /d "%~dp0src"
echo 正在启动后端服务器...
start "后端服务器" cmd /k "python web_server.py"

:: 等待后端启动
echo 等待后端服务器初始化...
timeout /t 5 /nobreak >nul

:: 检查后端是否启动成功
echo 检查后端服务器状态...
python -c "import requests; requests.get('http://127.0.0.1:5000/api/status', timeout=2)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 警告: 后端服务器可能未完全启动，但将继续启动前端
) else (
    echo ✅ 后端服务器启动成功
)

:: 启动前端服务器
cd /d "%~dp0app"
echo 正在启动前端服务器...
start "前端服务器" cmd /k "npm run dev"

:: 等待前端启动
echo 等待前端服务器启动...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   系统启动完成！
echo ========================================
echo.
echo 后端地址: http://127.0.0.1:5000
echo 前端地址: http://127.0.0.1:5173
echo.
echo 请在浏览器中打开前端地址开始使用
echo.
echo 如遇到问题，请查看启动指南文档
echo.
pause