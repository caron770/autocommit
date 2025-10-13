@echo off
chcp 65001 >nul
echo 🚀 启动淘宝直播评论机器人...
echo.

REM 获取脚本所在目录的父目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%.."

REM 检查Python版本
python --version
echo.

REM 检查依赖
echo 📦 检查依赖包...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo ❌ 缺少PyQt5，正在安装...
    pip install PyQt5
)

python -c "import playwright" 2>nul
if errorlevel 1 (
    echo ❌ 缺少Playwright，正在安装...
    pip install playwright
    playwright install chromium
)

echo.
echo 🎬 启动图形界面...
python main.py

pause