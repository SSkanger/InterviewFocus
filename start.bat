@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title 智能面试模拟系统启动器

echo.
echo ========================================
echo   智能面试模拟系统 - 启动中...
echo ========================================
echo.

:: 检查Python是否安装
echo [1/5] 检查Python环境...

:: 使用项目文件夹下的虚拟环境Python解释器
set "PYTHON_EXE=%~dp0p_envs\python.exe"
echo 🐍 使用项目虚拟环境Python解释器: %PYTHON_EXE%

:: 检查指定的Python是否存在
if not exist "%PYTHON_EXE%" (
    echo ❌ 错误: 未找到指定的Python解释器: %PYTHON_EXE%
    echo ❌ 请检查路径是否正确，或修改start.bat文件中的PYTHON_EXE变量
    pause
    exit /b 1
)

:: 验证Python解释器是否可运行
echo 正在验证Python解释器...
"%PYTHON_EXE%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 无法运行Python解释器: %PYTHON_EXE%
    echo ❌ 请检查Python环境是否正确安装
    pause
    exit /b 1
)

:: 获取Python版本
for /f "tokens=2" %%i in ('"%PYTHON_EXE%" --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

:: 检查Python版本是否在兼容范围内
:: 提取主版本号和次版本号
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

:: 检查主版本是否为3
if not "%PYTHON_MAJOR%" == "3" (
    echo ⚠️ 警告: 项目建议使用Python 3.8-3.11版本
)

:: 检查次版本是否在8-11之间
set "is_compatible=false"
for %%i in (8 9 10 11) do (
    if "%PYTHON_MINOR%" == "%%i" (
        set "is_compatible=true"
        goto :break_loop
    )
)
:break_loop

if not "%is_compatible%" == "true" (
    echo ⚠️ 警告: 您当前使用的是Python %PYTHON_VERSION%
    echo ⚠️ 项目建议使用Python 3.8-3.11版本，当前版本可能与某些依赖不兼容
    echo ⚠️ 建议安装Python 3.10或3.11版本以获得最佳兼容性
    pause
)

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
echo [3/5] 检查Python依赖...
cd /d "%~dp0src"
if not exist "requirements.txt" (
    echo ❌ 错误: 未找到requirements.txt文件
    pause
    exit /b 1
)
echo 正在检查依赖...
"%PYTHON_EXE%" -m pip show opencv-python >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装Python依赖...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
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
cd /d "%~dp0src"
echo 正在启动后端服务器...

:: 正常启动模式
start "后端服务器" "%PYTHON_EXE%" web_server.py

:: 等待后端启动
echo 等待后端服务器初始化...
timeout /t 10 /nobreak >nul

:: 检查后端是否启动成功
echo 检查后端服务器状态...
set "backend_started=false"
for /L %%i in (1,1,10) do (
    echo 第 %%i 次尝试连接后端...
    :: 使用curl.exe检查后端是否可用，而不是python
    curl.exe -s -o nul -w "%%{http_code}" http://127.0.0.1:5000/api/status > temp_status.txt
    set /p STATUS_CODE=<temp_status.txt
    del temp_status.txt
    if "!STATUS_CODE!" == "200" (
        echo ✅ 后端服务器启动成功
        set "backend_started=true"
        goto :backend_ready
    )
    echo ⚠️ 后端未就绪，等待2秒后重试...
    timeout /t 2 /nobreak >nul
)
:backend_ready
if not "%backend_started%" == "true" (
    echo ⚠️ 警告: 后端服务器可能未完全启动，前端可能无法正常工作
    echo 请手动检查后端服务器是否正常运行
    echo 您可以在任务管理器中查看是否有python进程在运行
    echo 或者手动在终端中运行: "%PYTHON_EXE%" src/web_server.py
    timeout /t 5 /nobreak >nul
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
echo 正在自动打开浏览器...
start "" http://127.0.0.1:5173
echo.
echo 浏览器已自动打开，请开始使用智能面试模拟系统
echo.
echo 如遇到问题，请查看启动指南文档
echo.
pause