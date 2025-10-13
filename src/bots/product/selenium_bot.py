#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝自动评论脚本 - Selenium版本
仅供学习研究使用，请遵守相关法律法规
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TaobaoCommentSelenium:
    def __init__(self, headless=False):
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        self.init_driver(headless)
    
    def init_driver(self, headless=False):
        """初始化Chrome驱动"""
        chrome_options = Options()
        
        # 反检测配置
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置用户代理
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # 启动驱动
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # 执行反检测脚本
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def login(self, username, password):
        """登录淘宝"""
        try:
            print("正在访问淘宝登录页面...")
            self.driver.get('https://login.taobao.com/member/login.jhtml')
            
            # 输入用户名
            username_input = self.wait.until(EC.presence_of_element_located((By.ID, 'fm-login-id')))
            username_input.clear()
            username_input.send_keys(username)
            self.random_delay(1, 2)
            
            # 输入密码
            password_input = self.driver.find_element(By.ID, 'fm-login-password')
            password_input.clear()
            password_input.send_keys(password)
            self.random_delay(1, 2)
            
            # 点击登录
            login_btn = self.driver.find_element(By.CSS_SELECTOR, '#login-form button[type="submit"]')
            login_btn.click()
            
            # 等待登录结果
            time.sleep(3)
            
            # 检查是否需要验证
            if self.driver.current_url.find('login') == -1:
                self.is_logged_in = True
                print("登录成功！")
                return True
            else:
                print("登录失败或需要验证，请手动处理")
                input("完成验证后按回车继续...")
                if self.driver.current_url.find('login') == -1:
                    self.is_logged_in = True
                    return True
                return False
                
        except Exception as e:
            print(f"登录过程出错: {e}")
            return False
    
    def get_comment_orders(self):
        """获取待评价订单"""
        try:
            print("正在获取待评价订单...")
            self.driver.get('https://trade.taobao.com/trade/itemlist/list_bought_items.htm')
            time.sleep(3)
            
            # 点击待评价标签
            wait_rate_tab = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-tab="waitRate"]')))
            wait_rate_tab.click()
            time.sleep(2)
            
            # 获取评价链接
            comment_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="rate.taobao.com"]')
            
            orders = []
            for link in comment_links[:5]:  # 限制前5个
                href = link.get_attribute('href')
                text = link.text
                if '评价' in text:
                    orders.append(href)
            
            print(f"找到 {len(orders)} 个待评价订单")
            return orders
            
        except Exception as e:
            print(f"获取订单列表出错: {e}")
            return []
    
    def submit_single_comment(self, comment_url, comment_text, rating=5):
        """提交单个评论"""
        try:
            print(f"正在处理评论: {comment_text[:20]}...")
            self.driver.get(comment_url)
            time.sleep(2)
            
            # 选择星级评分
            try:
                stars = self.driver.find_elements(By.CSS_SELECTOR, '.rate-star')
                if len(stars) >= rating:
                    stars[rating-1].click()
                    self.random_delay(0.5, 1)
            except:
                print("未找到评分选项")
            
            # 输入评论内容
            try:
                comment_textarea = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea')))
                comment_textarea.clear()
                comment_textarea.send_keys(comment_text)
                self.random_delay(1, 2)
            except:
                print("未找到评论输入框")
                return False
            
            # 提交评论
            try:
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button:contains("发布"), input[value*="发布"]')
                submit_btn.click()
                time.sleep(2)
                
                # 检查是否成功
                if "成功" in self.driver.page_source or "感谢" in self.driver.page_source:
                    print("评论提交成功")
                    return True
                else:
                    print("评论提交状态未知")
                    return False
                    
            except Exception as e:
                print(f"提交评论时出错: {e}")
                return False
                
        except Exception as e:
            print(f"处理评论出错: {e}")
            return False
    
    def batch_comment(self, comments_list):
        """批量评论"""
        if not self.is_logged_in:
            print("请先登录")
            return
        
        # 获取待评价订单
        orders = self.get_comment_orders()
        if not orders:
            print("没有待评价订单")
            return
        
        success_count = 0
        for i, order_url in enumerate(orders):
            try:
                # 随机选择评论
                comment = random.choice(comments_list)
                
                # 提交评论
                if self.submit_single_comment(order_url, comment):
                    success_count += 1
                
                print(f"进度: {i+1}/{len(orders)}, 成功: {success_count}")
                
                # 随机延迟
                self.random_delay(5, 10)
                
            except Exception as e:
                print(f"处理订单时出错: {e}")
                continue
        
        print(f"批量评论完成，成功 {success_count} 条")
    
    def random_delay(self, min_sec=1, max_sec=3):
        """随机延迟"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

# 使用示例
def main():
    bot = TaobaoCommentSelenium(headless=False)
    
    try:
        # 登录
        username = "your_username"
        password = "your_password"
        
        if bot.login(username, password):
            # 评论内容
            comments = [
                "商品质量很好，物流很快，满意！",
                "包装精美，商品符合描述，好评！",
                "性价比很高，推荐购买！",
                "服务态度很好，商品质量不错！",
                "发货速度快，商品完好无损，赞！"
            ]
            
            # 开始批量评论
            bot.batch_comment(comments)
    
    except Exception as e:
        print(f"程序出错: {e}")
    
    finally:
        bot.close()

if __name__ == "__main__":
    main()
