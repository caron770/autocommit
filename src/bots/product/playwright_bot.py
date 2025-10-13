#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝自动评论脚本 - Playwright版本
仅供学习研究使用，请遵守相关法律法规
"""

import asyncio
import random
import time
from playwright.async_api import async_playwright

class TaobaoCommentBot:
    def __init__(self):
        self.browser = None
        self.page = None
        self.is_logged_in = False
    
    async def init_browser(self, headless=False):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        
        # 启动浏览器，配置反检测参数
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--no-first-run',
                '--disable-default-apps'
            ]
        )
        
        # 创建新页面
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await context.new_page()
        
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
        """)
    
    async def login(self, username, password):
        """登录淘宝账号"""
        try:
            print("正在访问淘宝登录页面...")
            await self.page.goto('https://login.taobao.com/member/login.jhtml')
            
            # 等待页面加载
            await self.page.wait_for_load_state('networkidle')
            
            # 输入用户名
            await self.page.fill('#fm-login-id', username)
            await self.random_delay(1, 2)
            
            # 输入密码
            await self.page.fill('#fm-login-password', password)
            await self.random_delay(1, 2)
            
            # 点击登录按钮
            await self.page.click('#login-form button[type="submit"]')
            
            # 等待登录结果
            await self.page.wait_for_load_state('networkidle')
            
            # 检查是否需要验证码或其他验证
            if await self.page.locator('.nc_wrapper').count() > 0:
                print("检测到滑动验证码，请手动完成验证...")
                await self.page.wait_for_url('https://www.taobao.com/', timeout=60000)
            
            # 检查登录状态
            if 'login' not in self.page.url:
                self.is_logged_in = True
                print("登录成功！")
                return True
            else:
                print("登录失败，请检查账号密码")
                return False
                
        except Exception as e:
            print(f"登录过程中出现错误: {e}")
            return False
    
    async def get_orders_to_comment(self):
        """获取待评价的订单列表"""
        try:
            print("正在获取待评价订单...")
            await self.page.goto('https://trade.taobao.com/trade/itemlist/list_bought_items.htm?t=20241013')
            await self.page.wait_for_load_state('networkidle')
            
            # 点击待评价标签
            await self.page.click('a[data-tab="waitRate"]')
            await self.page.wait_for_load_state('networkidle')
            
            # 获取订单列表
            orders = await self.page.locator('.js-order-container').all()
            order_list = []
            
            for order in orders[:5]:  # 限制处理前5个订单
                try:
                    # 获取订单信息
                    order_id = await order.get_attribute('data-id')
                    product_name = await order.locator('.bought-wrapper-mod__head-info-cell___29cDO a').first.inner_text()
                    
                    # 检查是否有评价按钮
                    comment_btn = order.locator('a:has-text("评价")')
                    if await comment_btn.count() > 0:
                        comment_url = await comment_btn.get_attribute('href')
                        order_list.append({
                            'order_id': order_id,
                            'product_name': product_name,
                            'comment_url': comment_url
                        })
                except Exception as e:
                    print(f"解析订单信息时出错: {e}")
                    continue
            
            print(f"找到 {len(order_list)} 个待评价订单")
            return order_list
            
        except Exception as e:
            print(f"获取订单列表时出错: {e}")
            return []
    
    async def submit_comment(self, order_info, comment_text, rating=5):
        """提交评论"""
        try:
            print(f"正在为商品 '{order_info['product_name']}' 提交评论...")
            
            # 访问评价页面
            await self.page.goto(f"https:{order_info['comment_url']}")
            await self.page.wait_for_load_state('networkidle')
            
            # 等待评价表单加载
            await self.page.wait_for_selector('.rate-grid', timeout=10000)
            
            # 选择评分（通常是5星好评）
            star_selector = f'.rate-star:nth-child({rating})'
            if await self.page.locator(star_selector).count() > 0:
                await self.page.click(star_selector)
                await self.random_delay(0.5, 1)
            
            # 输入评论内容
            comment_textarea = self.page.locator('textarea[placeholder*="评价"]').first
            if await comment_textarea.count() > 0:
                await comment_textarea.fill(comment_text)
                await self.random_delay(1, 2)
            
            # 提交评论
            submit_btn = self.page.locator('button:has-text("发布评价")')
            if await submit_btn.count() > 0:
                await submit_btn.click()
                await self.page.wait_for_load_state('networkidle')
                
                # 检查提交结果
                if await self.page.locator(':has-text("评价成功")').count() > 0:
                    print(f"评论提交成功: {comment_text[:20]}...")
                    return True
                else:
                    print("评论提交可能失败，请检查页面状态")
                    return False
            else:
                print("未找到提交按钮")
                return False
                
        except Exception as e:
            print(f"提交评论时出错: {e}")
            return False
    
    async def random_delay(self, min_seconds=1, max_seconds=3):
        """随机延迟，模拟人工操作"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def batch_comment(self, comments_list):
        """批量评论"""
        if not self.is_logged_in:
            print("请先登录账号")
            return
        
        # 获取待评价订单
        orders = await self.get_orders_to_comment()
        if not orders:
            print("没有找到待评价的订单")
            return
        
        success_count = 0
        for i, order in enumerate(orders):
            try:
                # 随机选择评论内容
                comment = random.choice(comments_list)
                
                # 提交评论
                if await self.submit_comment(order, comment):
                    success_count += 1
                    print(f"进度: {i+1}/{len(orders)}, 成功: {success_count}")
                
                # 随机延迟，避免被检测
                await self.random_delay(3, 8)
                
            except Exception as e:
                print(f"处理订单 {order['order_id']} 时出错: {e}")
                continue
        
        print(f"批量评论完成，成功提交 {success_count} 条评论")
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()

# 使用示例
async def main():
    bot = TaobaoCommentBot()
    
    try:
        # 初始化浏览器
        await bot.init_browser(headless=False)  # 设置为True可无头运行
        
        # 登录（请替换为实际的用户名和密码）
        username = "your_username"
        password = "your_password"
        
        if await bot.login(username, password):
            # 预设评论内容
            comments = [
                "商品质量很好，物流很快，满意！",
                "包装精美，商品符合描述，好评！",
                "性价比很高，推荐购买！",
                "服务态度很好，商品质量不错！",
                "发货速度快，商品完好无损，赞！"
            ]
            
            # 开始批量评论
            await bot.batch_comment(comments)
        
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    finally:
        await bot.close()

if __name__ == "__main__":
    # 运行程序
    asyncio.run(main())
