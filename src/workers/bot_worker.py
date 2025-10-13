#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人工作线程模块
"""

import asyncio
import time
from PyQt5.QtCore import QThread, pyqtSignal
from src.utils import CookieManager, BrowserManager


class BotWorkerThread(QThread):
    """机器人工作线程"""
    log_signal = pyqtSignal(str, str)  # 日志信号 (message, level)
    stats_signal = pyqtSignal(dict)     # 统计信号
    status_signal = pyqtSignal(str)     # 状态信号
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.is_running = True
        self.bot = None
        self.stats = {
            'comments_sent': 0,
            'replies_sent': 0,
            'gifts_thanked': 0,
            'errors': 0,
            'start_time': None
        }
    
    def run(self):
        """运行机器人"""
        try:
            self.stats['start_time'] = time.time()
            self.status_signal.emit('运行中')
            self.log_signal.emit('🚀 机器人启动中...', 'info')
            
            # 根据选择的方法运行
            method = self.config.get('method', 'playwright')
            
            if method == 'playwright':
                self.run_playwright_bot()
            elif method == 'websocket':
                self.run_websocket_bot()
            elif method == 'selenium':
                self.run_selenium_bot()
            
        except Exception as e:
            self.log_signal.emit(f'❌ 运行出错: {str(e)}', 'error')
            self.status_signal.emit('错误')
        finally:
            self.status_signal.emit('已停止')
            self.log_signal.emit('⏹️ 机器人已停止', 'info')
    
    def run_playwright_bot(self):
        """运行Playwright方法"""
        try:
            from src.bots.live import TaobaoLivePlaywrightBot
            
            # 创建Cookie管理器
            cookie_manager = CookieManager() if self.config.get('save_cookie', True) else None
            
            # 创建浏览器管理器
            browser_manager = BrowserManager()
            
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def run_async():
                bot = TaobaoLivePlaywrightBot(
                    cookie_manager=cookie_manager,
                    browser_manager=browser_manager
                )
                
                # 获取浏览器类型
                browser_type = self.config.get('browser_type', 'chromium')
                browser_info = browser_manager.get_browser_info(browser_type)
                
                # 初始化浏览器
                self.log_signal.emit(f'📱 初始化 {browser_info["name"]} 浏览器...', 'info')
                await bot.init_browser(
                    headless=self.config.get('headless', False),
                    username=self.config.get('username'),
                    browser_type=browser_type
                )
                
                # 登录
                if self.config.get('username') and self.config.get('password'):
                    self.log_signal.emit('🔐 正在登录...', 'info')
                    login_success = await bot.login(
                        self.config['username'],
                        self.config['password'],
                        save_cookie=self.config.get('save_cookie', True)
                    )
                    
                    if not login_success:
                        self.log_signal.emit('❌ 登录失败', 'error')
                        return
                    
                    self.log_signal.emit('✅ 登录成功', 'success')
                
                # 运行机器人
                self.log_signal.emit(f'🎬 进入直播间: {self.config["live_url"]}', 'info')
                
                # 重写部分方法以发送信号
                original_send = bot.send_comment
                async def send_with_signal(content):
                    result = await original_send(content)
                    if result:
                        self.stats['comments_sent'] += 1
                        self.log_signal.emit(f'✅ 发送: {content}', 'success')
                    else:
                        self.stats['errors'] += 1
                        self.log_signal.emit(f'❌ 失败: {content}', 'error')
                    self.stats_signal.emit(self.stats)
                    return result
                
                bot.send_comment = send_with_signal
                
                await bot.run(
                    live_url=self.config['live_url'],
                    auto_comments=self.config.get('comments', []),
                    enable_auto_reply=self.config.get('auto_reply', True)
                )
            
            loop.run_until_complete(run_async())
            
        except Exception as e:
            self.log_signal.emit(f'❌ Playwright运行错误: {str(e)}', 'error')
    
    def run_websocket_bot(self):
        """运行WebSocket方法"""
        try:
            from src.bots.live import TaobaoLiveCommentBot
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def run_async():
                bot = TaobaoLiveCommentBot()
                
                # 登录
                if self.config.get('username') and self.config.get('password'):
                    self.log_signal.emit('🔐 正在登录...', 'info')
                    login_success = bot.login(
                        self.config['username'],
                        self.config['password']
                    )
                    
                    if not login_success:
                        self.log_signal.emit('❌ 登录失败', 'error')
                        return
                    
                    self.log_signal.emit('✅ 登录成功', 'success')
                
                # 运行机器人
                await bot.run(
                    live_url=self.config['live_url'],
                    auto_comments=self.config.get('comments', [])
                )
            
            loop.run_until_complete(run_async())
            
        except Exception as e:
            self.log_signal.emit(f'❌ WebSocket运行错误: {str(e)}', 'error')
    
    def run_selenium_bot(self):
        """运行Selenium方法"""
        self.log_signal.emit('ℹ️ Selenium方法需要适配直播间，暂未实现', 'warning')
    
    def stop(self):
        """停止机器人"""
        self.is_running = False
        self.terminate()

