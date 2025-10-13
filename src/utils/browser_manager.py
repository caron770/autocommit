#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器管理器 - 支持多种浏览器类型
"""

import platform
from pathlib import Path
from playwright.async_api import async_playwright


class BrowserManager:
    """浏览器管理器"""
    
    # 支持的浏览器类型
    BROWSER_TYPES = {
        'chromium': {
            'name': 'Chromium',
            'description': '开源版Chrome，速度快，兼容性好（默认）',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'edge': {
            'name': 'Microsoft Edge',
            'description': '微软Edge浏览器，基于Chromium内核',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        },
        'chrome': {
            'name': 'Google Chrome',
            'description': '谷歌Chrome浏览器（需要系统已安装）',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'firefox': {
            'name': 'Mozilla Firefox',
            'description': '火狐浏览器，独立内核',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        }
    }
    
    @staticmethod
    def get_browser_list():
        """获取支持的浏览器列表"""
        return list(BrowserManager.BROWSER_TYPES.keys())
    
    @staticmethod
    def get_browser_info(browser_type):
        """获取浏览器信息"""
        return BrowserManager.BROWSER_TYPES.get(browser_type, BrowserManager.BROWSER_TYPES['chromium'])
    
    @staticmethod
    def get_edge_path():
        """获取系统Edge浏览器路径"""
        system = platform.system().lower()
        
        if system == 'windows':
            # Windows Edge路径
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Microsoft\Edge\Application\msedge.exe"
            ]
        elif system == 'darwin':  # macOS
            edge_paths = [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            ]
        else:  # Linux
            edge_paths = [
                "/usr/bin/microsoft-edge",
                "/usr/bin/microsoft-edge-stable",
                "/opt/microsoft/msedge/msedge"
            ]
        
        # 检查路径是否存在
        for path in edge_paths:
            expanded_path = Path(path.replace('%USERNAME%', Path.home().name))
            if expanded_path.exists():
                return str(expanded_path)
        
        return None
    
    @staticmethod
    def get_chrome_path():
        """获取系统Chrome浏览器路径"""
        system = platform.system().lower()
        
        if system == 'windows':
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
            ]
        elif system == 'darwin':  # macOS
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]
        else:  # Linux
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser"
            ]
        
        for path in chrome_paths:
            expanded_path = Path(path.replace('%USERNAME%', Path.home().name))
            if expanded_path.exists():
                return str(expanded_path)
        
        return None
    
    @staticmethod
    async def launch_browser(browser_type='chromium', headless=False, **kwargs):
        """启动指定类型的浏览器"""
        playwright = await async_playwright().start()
        
        # 通用的启动参数
        launch_args = [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--no-first-run',
            '--disable-default-apps',
            '--disable-web-security',
            '--allow-running-insecure-content'
        ]
        
        try:
            if browser_type == 'edge':
                # 尝试使用系统Edge
                edge_path = BrowserManager.get_edge_path()
                if edge_path:
                    print(f"✅ 使用系统Edge浏览器: {edge_path}")
                    browser = await playwright.chromium.launch(
                        executable_path=edge_path,
                        headless=headless,
                        args=launch_args,
                        **kwargs
                    )
                else:
                    print("⚠️ 系统未找到Edge，使用Chromium代替")
                    browser = await playwright.chromium.launch(
                        headless=headless,
                        args=launch_args,
                        **kwargs
                    )
            
            elif browser_type == 'chrome':
                # 尝试使用系统Chrome
                chrome_path = BrowserManager.get_chrome_path()
                if chrome_path:
                    print(f"✅ 使用系统Chrome浏览器: {chrome_path}")
                    browser = await playwright.chromium.launch(
                        executable_path=chrome_path,
                        headless=headless,
                        args=launch_args,
                        **kwargs
                    )
                else:
                    print("⚠️ 系统未找到Chrome，使用Chromium代替")
                    browser = await playwright.chromium.launch(
                        headless=headless,
                        args=launch_args,
                        **kwargs
                    )
            
            elif browser_type == 'firefox':
                print("🦊 使用Firefox浏览器")
                browser = await playwright.firefox.launch(
                    headless=headless,
                    **kwargs
                )
            
            else:  # chromium (默认)
                print("🌐 使用Chromium浏览器")
                browser = await playwright.chromium.launch(
                    headless=headless,
                    args=launch_args,
                    **kwargs
                )
            
            return browser, playwright
            
        except Exception as e:
            print(f"❌ 启动 {browser_type} 浏览器失败: {e}")
            print("🔄 回退到默认Chromium浏览器")
            browser = await playwright.chromium.launch(
                headless=headless,
                args=launch_args,
                **kwargs
            )
            return browser, playwright
    
    @staticmethod
    def get_user_agent(browser_type='chromium'):
        """获取对应浏览器的用户代理"""
        return BrowserManager.BROWSER_TYPES.get(browser_type, {}).get(
            'user_agent',
            BrowserManager.BROWSER_TYPES['chromium']['user_agent']
        )
    
    @staticmethod
    def detect_available_browsers():
        """检测系统中可用的浏览器"""
        available = ['chromium']  # Chromium总是可用的
        
        if BrowserManager.get_edge_path():
            available.append('edge')
        
        if BrowserManager.get_chrome_path():
            available.append('chrome')
        
        # Firefox通过Playwright总是可用的
        available.append('firefox')
        
        return available
