#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝直播评论机器人 - 主入口
"""

import sys
from PyQt5.QtWidgets import QApplication

from src.ui import TaobaoLiveBotUI


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用图标和样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = TaobaoLiveBotUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

