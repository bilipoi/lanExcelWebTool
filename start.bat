@echo off
chcp 65001 >nul
title 局域网多人 Excel 编辑器 - 离线版
color 0A

echo ========================================
echo   局域网多人 Excel 编辑器 - 离线版
echo ========================================
echo.
echo 正在检查环境...

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python 已安装

REM 检查依赖
if not exist "venv" (
    echo.
    echo 首次运行，正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

echo [OK] 虚拟环境已准备

echo.
echo 正在安装/检查依赖（离线模式）...
call venv\Scripts\activate.bat
pip install --no-index --find-links=packages -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [警告] 部分依赖可能未完全安装，尝试在线安装...
    pip install -r requirements.txt
)

echo [OK] 依赖已就绪

echo.
echo ========================================
echo   服务启动中...
echo ========================================
echo.
echo 访问地址:
echo   - 本机: http://localhost:5000
echo   - 局域网: http://%%计算机IP%%:5000
echo.
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause