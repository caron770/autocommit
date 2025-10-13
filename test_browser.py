#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器检测测试脚本
"""

from src.utils import BrowserManager

def main():
    print("🔍 检测系统中可用的浏览器...")
    print("=" * 50)
    
    # 创建浏览器管理器
    browser_manager = BrowserManager()
    
    # 检测可用浏览器
    available_browsers = browser_manager.detect_available_browsers()
    
    print(f"✅ 检测到 {len(available_browsers)} 个可用浏览器:")
    print()
    
    for i, browser_type in enumerate(available_browsers, 1):
        info = browser_manager.get_browser_info(browser_type)
        print(f"{i}. {info['name']}")
        print(f"   类型: {browser_type}")
        print(f"   描述: {info['description']}")
        
        # 显示路径（对于需要系统安装的浏览器）
        if browser_type == 'edge':
            path = browser_manager.get_edge_path()
            if path:
                print(f"   路径: {path}")
            else:
                print(f"   路径: 未找到系统Edge")
        elif browser_type == 'chrome':
            path = browser_manager.get_chrome_path()
            if path:
                print(f"   路径: {path}")
            else:
                print(f"   路径: 未找到系统Chrome")
        
        print()
    
    # 测试推荐的浏览器
    if 'edge' in available_browsers:
        print("🎉 推荐使用: Microsoft Edge (已检测到)")
        print("   Edge基于Chromium内核，兼容性和速度都很好")
    elif 'chrome' in available_browsers:
        print("🎉 推荐使用: Google Chrome (已检测到)")
        print("   Chrome速度快，兼容性好")
    else:
        print("ℹ️ 将使用: Chromium (内置)")
        print("   Chromium是Chrome的开源版本，功能完全相同")
    
    print()
    print("=" * 50)
    print("✨ 检测完成！现在你可以在UI界面中选择浏览器类型了。")

if __name__ == "__main__":
    main()
