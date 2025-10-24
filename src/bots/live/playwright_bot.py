#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝直播评论机器人 - Playwright版本
适合快速部署和测试
仅供学习研究使用，请遵守相关法律法规
"""

import asyncio
import random
import time
import json
from playwright.async_api import async_playwright
from pathlib import Path

class TaobaoLivePlaywrightBot:
    def __init__(self, cookie_manager=None, browser_manager=None):
        self.browser = None
        self.page = None
        self.context = None
        self.playwright = None
        self.is_running = False
        self.comment_queue = asyncio.Queue()
        self.live_url = None
        self.cookie_manager = cookie_manager
        self.browser_manager = browser_manager
        self.current_username = None
    
    async def init_browser(self, headless=False, username=None, browser_type='chromium'):
        """初始化浏览器"""
        if self.browser_manager:
            # 使用浏览器管理器启动浏览器
            self.browser, self.playwright = await self.browser_manager.launch_browser(
                browser_type=browser_type,
                headless=headless
            )
            user_agent = self.browser_manager.get_user_agent(browser_type)
        else:
            # 回退到默认Chromium
            playwright = await async_playwright().start()
            self.playwright = playwright
            self.browser = await playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-web-security',
                    '--allow-running-insecure-content'
                ]
            )
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        # 创建新页面
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent
        )
        
        # 如果有Cookie管理器和用户名，尝试加载Cookie
        if self.cookie_manager and username:
            cookies = self.cookie_manager.load_cookies(username)
            if cookies:
                await self.context.add_cookies(cookies)
                print("✅ 已加载保存的Cookie，可能无需登录")
        
        self.page = await self.context.new_page()
        
        # 注入反检测脚本
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            window.chrome = {
                runtime: {},
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // 覆盖检测函数
            window.navigator.webdriver = undefined;
        """)
    
    async def login(self, username, password, save_cookie=True):
        """登录淘宝账号"""
        try:
            self.current_username = username
            
            # 先检查是否已经登录（通过Cookie）
            print("🔍 检查登录状态...")
            await self.page.goto('https://www.taobao.com/', timeout=30000)
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            
            # 检查登录状态
            if await self.check_login_status():
                print("✅ 使用Cookie自动登录成功！")
                return True
            
            print("📝 Cookie登录失败，开始账号密码登录...")
            print("正在访问淘宝登录页面...")
            await self.page.goto('https://login.taobao.com/member/login.jhtml', timeout=30000)
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            
            # 等待登录表单加载
            await self.page.wait_for_selector('#fm-login-id', timeout=10000)
            
            # 输入用户名
            await self.page.fill('#fm-login-id', username)
            await self.random_delay(0.5, 1)
            
            # 输入密码
            await self.page.fill('#fm-login-password', password)
            await self.random_delay(0.5, 1)
            
            # 点击登录按钮
            await self.page.click('#login-form button[type="submit"]')
            print("⏳ 等待登录响应...")
            await self.random_delay(2, 3)
            
            # 检查是否需要验证码（滑块/拼图等）
            max_wait = 60  # 最多等待60秒
            waited = 0
            while waited < max_wait:
                # 检查是否有验证码
                has_slider = await self.page.locator('.nc_wrapper').count() > 0
                has_captcha = await self.page.locator('#nocaptcha').count() > 0
                
                if has_slider or has_captcha:
                    if waited == 0:
                        print("🔐 检测到验证码，请在浏览器中手动完成验证...")
                    await asyncio.sleep(1)
                    waited += 1
                else:
                    # 没有验证码了，检查登录状态
                    break
            
            # 等待页面跳转或登录完成
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # 检查登录状态
            is_logged_in = await self.check_login_status()
            if is_logged_in or 'login' not in self.page.url.lower():
                print("✅ 登录成功！")
                
                # 保存Cookie
                if save_cookie and self.cookie_manager:
                    cookies = await self.context.cookies()
                    self.cookie_manager.save_cookies(cookies, username)
                    print("💾 Cookie已保存，下次可自动登录")
                
                return True
            else:
                print("❌ 登录失败，请检查账号密码或重试")
                return False
                
        except asyncio.TimeoutError:
            print("❌ 登录超时，请检查网络连接")
            return False
        except Exception as e:
            print(f"❌ 登录过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def check_login_status(self):
        """检查登录状态"""
        try:
            # 查找登录标识元素
            # 淘宝登录后通常会有用户昵称或头像
            login_indicators = [
                '.site-nav-user',  # 用户信息区域
                '.site-nav-sign',  # 登录后的标识
                'a[href*="member.taobao.com"]',  # 会员中心链接
                '.J_MyTaobao',  # 我的淘宝
                '.site-nav-bd .site-nav-user',  # 用户区域
            ]
            
            for indicator in login_indicators:
                try:
                    count = await self.page.locator(indicator).count()
                    if count > 0:
                        # 进一步检查元素是否可见
                        element = self.page.locator(indicator).first
                        if await element.is_visible():
                            return True
                except:
                    continue
            
            # 额外检查：如果当前URL不包含login，大概率已登录
            current_url = self.page.url
            if current_url and 'login' not in current_url.lower() and 'taobao.com' in current_url:
                # 检查页面是否有"请登录"字样
                login_text = await self.page.locator('text=请登录').count()
                if login_text == 0:
                    return True
            
            return False
        except Exception as e:
            print(f"⚠️ 检查登录状态出错: {e}")
            return False
    
    async def enter_live_room(self, live_url):
        """进入直播间"""
        try:
            print(f"🎬 正在进入直播间: {live_url}")
            self.live_url = live_url
            
            # 访问直播间
            await self.page.goto(live_url, timeout=30000)
            print("⏳ 等待直播间页面加载...")
            await self.page.wait_for_load_state('networkidle', timeout=20000)
            
            # 等待直播间关键元素加载完成（评论输入框、直播画面等）
            input_selectors = [
                '.comment-input',
                'input[placeholder*="说点什么"]',
                'textarea[placeholder*="说点什么"]',
                'input[placeholder*="发个评论"]',
                '.live-comment-input',
                '.live-input',
                '.chat-input'
            ]
            
            # 尝试找到任意一个输入框
            found = False
            for selector in input_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    found = True
                    print(f"✅ 找到评论输入框: {selector}")
                    break
                except:
                    continue
            
            if not found:
                print("⚠️ 未找到评论输入框，但将继续尝试运行...")
                # 不直接返回False，给后续操作机会
            
            # 等待一下确保页面完全加载
            await asyncio.sleep(2)
            
            print("✅ 成功进入直播间！")
            return True
            
        except asyncio.TimeoutError:
            print(f"❌ 进入直播间超时: {live_url}")
            return False
        except Exception as e:
            print(f"❌ 进入直播间失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def send_comment(self, content):
        """发送评论"""
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                # 查找评论输入框（多种可能的选择器）
                input_selectors = [
                    '.comment-input input',
                    'input[placeholder*="说点什么"]',
                    'textarea[placeholder*="说点什么"]',
                    '.live-comment-input input',
                    '.comment-box input',
                    '#comment-input',
                    'input[placeholder*="发个评论"]',
                    'textarea[placeholder*="发个评论"]',
                    '.live-input input',
                    '.chat-input input',
                    'input[type="text"]'
                ]
                
                input_element = None
                for selector in input_selectors:
                    try:
                        count = await self.page.locator(selector).count()
                        if count > 0:
                            elem = self.page.locator(selector).first
                            # 检查元素是否可见和可用
                            if await elem.is_visible() and await elem.is_enabled():
                                input_element = elem
                                break
                    except:
                        continue
                
                if not input_element:
                    print("❌ 未找到可用的评论输入框")
                    if retry_count < max_retries - 1:
                        print(f"⏳ {retry_count + 1}秒后重试...")
                        await asyncio.sleep(1)
                        retry_count += 1
                        continue
                    return False
                
                # 聚焦输入框
                await input_element.focus()
                await self.random_delay(0.1, 0.3)
                
                # 清空输入框并输入评论
                await input_element.fill('')
                await self.random_delay(0.1, 0.2)
                
                # 模拟人工逐字输入（可选，更真实但慢）
                # await input_element.type(content, delay=random.randint(50, 150))
                await input_element.fill(content)
                await self.random_delay(0.3, 0.6)
                
                # 查找发送按钮
                send_selectors = [
                    'button:has-text("发送")',
                    'button:has-text("发表")',
                    '.comment-send',
                    '.send-btn',
                    '.comment-submit',
                    'button[type="submit"]',
                    '.submit-btn'
                ]
                
                send_button = None
                for selector in send_selectors:
                    try:
                        count = await self.page.locator(selector).count()
                        if count > 0:
                            btn = self.page.locator(selector).first
                            if await btn.is_visible() and await btn.is_enabled():
                                send_button = btn
                                break
                    except:
                        continue
                
                # 如果找到发送按钮就点击，否则按回车
                if send_button:
                    await send_button.click()
                else:
                    await input_element.press('Enter')
                
                await self.random_delay(0.3, 0.5)
                print(f"✅ 发送评论: {content}")
                return True
                
            except Exception as e:
                print(f"⚠️ 发送评论出错（尝试 {retry_count + 1}/{max_retries}）: {e}")
                if retry_count < max_retries - 1:
                    await asyncio.sleep(1)
                    retry_count += 1
                else:
                    print(f"❌ 发送评论最终失败: {content}")
                    return False
        
        return False
    
    async def monitor_live_room(self):
        """监控直播间消息"""
        try:
            print("🔍 开始监控直播间消息...")
            
            # 监听网络请求，获取实时消息
            async def handle_response(response):
                try:
                    if 'comment' in response.url or 'message' in response.url:
                        if response.status == 200:
                            data = await response.json()
                            await self.handle_live_message(data)
                except:
                    pass
            
            self.page.on('response', handle_response)
            
            # 也可以通过DOM监听新评论
            await self.monitor_dom_changes()
            
        except Exception as e:
            print(f"监控直播间出错: {e}")
    
    async def monitor_dom_changes(self):
        """监控DOM变化获取新评论"""
        try:
            # 监听评论区的变化
            await self.page.evaluate("""
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList') {
                            mutation.addedNodes.forEach((node) => {
                                if (node.nodeType === 1) {
                                    // 检查是否是新评论
                                    const commentText = node.textContent || '';
                                    if (commentText && commentText.length > 0) {
                                        window.newComment = commentText;
                                    }
                                }
                            });
                        }
                    });
                });
                
                // 观察评论区
                const commentArea = document.querySelector('.comment-list, .live-comment-list, .message-list');
                if (commentArea) {
                    observer.observe(commentArea, { childList: true, subtree: true });
                }
            """)
            
            # 定期检查新评论
            while self.is_running:
                try:
                    new_comment = await self.page.evaluate('window.newComment')
                    if new_comment:
                        await self.handle_new_comment(new_comment)
                        await self.page.evaluate('window.newComment = null')
                except:
                    pass
                
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"DOM监控出错: {e}")
    
    async def handle_live_message(self, data):
        """处理直播间消息"""
        try:
            # 根据消息类型处理
            if isinstance(data, dict):
                msg_type = data.get('type', '')
                content = data.get('content', '')
                username = data.get('username', '')
                
                if msg_type == 'comment' and content:
                    print(f"[评论] {username}: {content}")
                    await self.auto_reply_to_comment(content)
                elif msg_type == 'gift':
                    gift_name = data.get('giftName', '')
                    print(f"[礼物] {username} 送出了 {gift_name}")
                    await self.thank_for_gift(username, gift_name)
                    
        except Exception as e:
            print(f"处理消息出错: {e}")
    
    async def handle_new_comment(self, comment_text):
        """处理新评论"""
        try:
            print(f"[新评论] {comment_text}")
            await self.auto_reply_to_comment(comment_text)
        except Exception as e:
            print(f"处理新评论出错: {e}")
    
    async def auto_reply_to_comment(self, comment_content):
        """根据评论内容自动回复"""
        # 关键词回复规则
        reply_rules = {
            '价格': ['价格很实惠哦！', '性价比超高！', '现在有优惠活动！'],
            '多少钱': ['价格很实惠哦！', '性价比超高！', '现在有优惠活动！'],
            '质量': ['质量绝对保证！', '用料很好的！', '品质没问题！'],
            '怎么样': ['质量绝对保证！', '用料很好的！', '品质没问题！'],
            '发货': ['发货很快的！', '包邮哦！', '今天下单明天发货！'],
            '快递': ['发货很快的！', '包邮哦！', '今天下单明天发货！'],
            '尺寸': ['有详细尺寸表的！', '可以看商品详情！', '客服会帮您推荐！'],
            '大小': ['有详细尺寸表的！', '可以看商品详情！', '客服会帮您推荐！'],
            '颜色': ['有多种颜色可选！', '都很好看的！', '可以看直播展示！'],
            '优惠': ['现在有活动！', '直播间有专属优惠！', '限时特价！'],
            '便宜': ['现在有活动！', '直播间有专属优惠！', '限时特价！'],
            '好看': ['谢谢夸奖！', '确实很好看！', '您眼光真好！'],
            '漂亮': ['谢谢夸奖！', '确实很好看！', '您眼光真好！']
        }
        
        for keyword, replies in reply_rules.items():
            if keyword in comment_content:
                reply = random.choice(replies)
                await self.add_comment_to_queue(reply)
                break
    
    async def thank_for_gift(self, username, gift_name):
        """感谢礼物"""
        thank_messages = [
            f"感谢{username}的{gift_name}！",
            f"谢谢{username}！",
            f"{username}太棒了！",
            f"感谢支持！"
        ]
        await self.add_comment_to_queue(random.choice(thank_messages))
    
    async def add_comment_to_queue(self, comment):
        """添加评论到发送队列"""
        await self.comment_queue.put(comment)
    
    async def comment_sender_worker(self):
        """评论发送工作线程"""
        while self.is_running:
            try:
                # 从队列获取评论
                comment = await asyncio.wait_for(
                    self.comment_queue.get(), 
                    timeout=1.0
                )
                
                # 发送评论
                await self.send_comment(comment)
                
                # 标记任务完成
                self.comment_queue.task_done()
                
                # 随机延迟，避免频率过高
                await self.random_delay(2, 5)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"发送评论出错: {e}")
                await asyncio.sleep(1)
    
    async def auto_comment_worker(self, comments_list, interval_range=(5, 15)):
        """自动评论工作线程"""
        while self.is_running:
            try:
                # 随机选择评论内容
                comment = random.choice(comments_list)
                
                # 添加到发送队列
                await self.add_comment_to_queue(comment)
                
                # 随机间隔
                interval = random.uniform(*interval_range)
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"自动评论出错: {e}")
                await asyncio.sleep(5)
    
    async def random_delay(self, min_seconds=1, max_seconds=3):
        """随机延迟，模拟人工操作"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def run(self, live_url, auto_comments=None, enable_auto_reply=True):
        """运行机器人"""
        try:
            self.is_running = True
            
            # 进入直播间
            if not await self.enter_live_room(live_url):
                return
            
            # 启动任务
            tasks = [
                asyncio.create_task(self.comment_sender_worker())
            ]
            
            # 启动监控（如果启用自动回复）
            if enable_auto_reply:
                tasks.append(
                    asyncio.create_task(self.monitor_live_room())
                )
            
            # 启动自动评论（如果提供了评论列表）
            if auto_comments:
                tasks.append(
                    asyncio.create_task(self.auto_comment_worker(auto_comments))
                )
            
            print("🤖 直播间机器人已启动！")
            print("📝 功能：")
            if auto_comments:
                print("  - ✅ 自动发送评论")
            if enable_auto_reply:
                print("  - ✅ 智能回复评论")
            print("  - ✅ 礼物感谢")
            print("\n按 Ctrl+C 停止机器人...")
            
            # 等待所有任务完成
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print("\n正在停止机器人...")
        except Exception as e:
            print(f"运行出错: {e}")
        finally:
            self.is_running = False
            if self.browser:
                await self.browser.close()

# 使用示例
async def main():
    bot = TaobaoLivePlaywrightBot()
    
    try:
        # 初始化浏览器
        await bot.init_browser(headless=False)  # 设置为True可无头运行
        
        # 登录账号
        username = "your_username"
        password = "your_password"
        
        if await bot.login(username, password):
            # 直播间链接
            live_url = "https://liveplatform.taobao.com/live/12345678"
            
            # 自动评论内容
            auto_comments = [
                "主播讲得真好！",
                "这个商品不错！",
                "价格很实惠！",
                "支持主播！",
                "666",
                "已下单！",
                "质量怎么样？",
                "有优惠吗？",
                "什么时候发货？",
                "颜色好看！",
                "主播辛苦了！",
                "产品很棒！",
                "性价比高！",
                "推荐购买！"
            ]
            
            # 启动机器人
            await bot.run(
                live_url=live_url,
                auto_comments=auto_comments,
                enable_auto_reply=True
            )
    
    except Exception as e:
        print(f"程序执行出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())
