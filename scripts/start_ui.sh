#!/bin/bash
# 淘宝直播评论机器人 - 启动脚本

echo "🚀 启动淘宝直播评论机器人..."
echo ""

# 获取脚本所在目录的父目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# 切换到项目目录
cd "$PROJECT_DIR"

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $python_version"

# 检查依赖
echo "📦 检查依赖包..."
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "❌ 缺少PyQt5，正在安装..."
    pip3 install PyQt5
fi

if ! python3 -c "import playwright" 2>/dev/null; then
    echo "❌ 缺少Playwright，正在安装..."
    pip3 install playwright
    playwright install chromium
fi

echo ""
echo "🎬 启动图形界面..."
python3 main.py