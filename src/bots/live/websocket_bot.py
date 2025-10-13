#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝直播评论机器人 - WebSocket + HTTP方案
实现高频率实时评论发送
仅供学习研究使用，请遵守相关法律法规
"""

import asyncio
import json
import random
import time
import websockets
import requests
from urllib.parse import urlparse, parse_qs
import re

class TaobaoLiveCommentBot:
    def __init__(self):
        self.session = requests.Session()
        self.websocket = None
        self.live_id = None
        self.user_id = None
        self.is_connected = False
        self.comment_queue = asyncio.Queue()
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://liveplatform.taobao.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8'
        }
    
    def login(self, username, password):
        """登录淘宝账号"""
        try:
            print("正在登录淘宝账号...")
            
            # 获取登录页面
            login_url = "https://login.taobao.com/member/login.jhtml"
            response = self.session.get(login_url, headers=self.headers)
            
            # 提取登录所需的token等参数
            # 这里需要根据实际页面结构解析
            
            login_data = {
                'loginId': username,
                'password': password,
                # 其他必要参数...
            }
            
            # 发送登录请求
            login_response = self.session.post(
                "https://login.taobao.com/member/login.jhtml",
                data=login_data,
                headers=self.headers
            )
            
            if login_response.status_code == 200:
                # 检查登录状态
                if 'login' not in login_response.url:
                    print("登录成功！")
                    return True
            
            print("登录失败，请检查账号密码")
            return False
            
        except Exception as e:
            print(f"登录过程出错: {e}")
            return False
    
    def extract_live_info(self, live_url):
        """从直播链接提取直播间信息"""
        try:
            # 访问直播页面
            response = self.session.get(live_url, headers=self.headers)
            html_content = response.text
            
            # 提取直播间ID
            live_id_match = re.search(r'liveId["\']?\s*[:=]\s*["\']?(\d+)', html_content)
            if live_id_match:
                self.live_id = live_id_match.group(1)
                print(f"提取到直播间ID: {self.live_id}")
            
            # 提取用户ID
            user_id_match = re.search(r'userId["\']?\s*[:=]\s*["\']?(\d+)', html_content)
            if user_id_match:
                self.user_id = user_id_match.group(1)
                print(f"提取到用户ID: {self.user_id}")
            
            # 提取WebSocket连接地址
            ws_match = re.search(r'wss?://[^"\']+', html_content)
            if ws_match:
                self.ws_url = ws_match.group(0)
                print(f"提取到WebSocket地址: {self.ws_url}")
                return True
            
            return False
            
        except Exception as e:
            print(f"提取直播信息出错: {e}")
            return False
    
    async def connect_websocket(self):
        """连接WebSocket获取实时消息"""
        try:
            print("正在连接WebSocket...")
            
            # 构建WebSocket连接参数
            ws_headers = {
                'User-Agent': self.headers['User-Agent'],
                'Origin': 'https://liveplatform.taobao.com'
            }
            
            self.websocket = await websockets.connect(
                self.ws_url,
                extra_headers=ws_headers,
                ping_interval=30,
                ping_timeout=10
            )
            
            self.is_connected = True
            print("WebSocket连接成功！")
            
            # 发送认证消息
            auth_message = {
                'type': 'auth',
                'liveId': self.live_id,
                'userId': self.user_id,
                'timestamp': int(time.time() * 1000)
            }
            
            await self.websocket.send(json.dumps(auth_message))
            return True
            
        except Exception as e:
            print(f"WebSocket连接失败: {e}")
            return False
    
    async def listen_messages(self):
        """监听WebSocket消息"""
        try:
            while self.is_connected:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                # 处理不同类型的消息
                if data.get('type') == 'comment':
                    await self.handle_comment(data)
                elif data.get('type') == 'gift':
                    await self.handle_gift(data)
                elif data.get('type') == 'enter':
                    await self.handle_enter(data)
                
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已断开")
            self.is_connected = False
        except Exception as e:
            print(f"监听消息出错: {e}")
    
    async def handle_comment(self, data):
        """处理评论消息"""
        username = data.get('username', '未知用户')
        content = data.get('content', '')
        print(f"[评论] {username}: {content}")
        
        # 根据评论内容触发自动回复
        await self.auto_reply(content)
    
    async def handle_gift(self, data):
        """处理礼物消息"""
        username = data.get('username', '未知用户')
        gift_name = data.get('giftName', '未知礼物')
        print(f"[礼物] {username} 送出了 {gift_name}")
        
        # 感谢礼物
        thank_messages = [
            f"感谢{username}的{gift_name}！",
            f"谢谢{username}！",
            f"{username}太棒了！"
        ]
        await self.add_comment_to_queue(random.choice(thank_messages))
    
    async def handle_enter(self, data):
        """处理进入直播间消息"""
        username = data.get('username', '未知用户')
        print(f"[进入] {username} 进入了直播间")
        
        # 欢迎消息
        welcome_messages = [
            f"欢迎{username}！",
            f"{username}来了！",
            "欢迎新朋友！"
        ]
        
        # 随机发送欢迎消息（30%概率）
        if random.random() < 0.3:
            await self.add_comment_to_queue(random.choice(welcome_messages))
    
    async def auto_reply(self, comment_content):
        """根据评论内容自动回复"""
        # 关键词回复规则
        reply_rules = {
            '价格': ['价格很实惠哦！', '性价比超高！', '现在有优惠活动！'],
            '质量': ['质量绝对保证！', '用料很好的！', '品质没问题！'],
            '发货': ['发货很快的！', '包邮哦！', '今天下单明天发货！'],
            '尺寸': ['有详细尺寸表的！', '可以看商品详情！', '客服会帮您推荐！'],
            '颜色': ['有多种颜色可选！', '都很好看的！', '可以看直播展示！'],
            '优惠': ['现在有活动！', '直播间有专属优惠！', '限时特价！']
        }
        
        for keyword, replies in reply_rules.items():
            if keyword in comment_content:
                reply = random.choice(replies)
                await self.add_comment_to_queue(reply)
                break
    
    async def add_comment_to_queue(self, comment):
        """添加评论到发送队列"""
        await self.comment_queue.put(comment)
    
    async def send_comment_worker(self):
        """评论发送工作线程"""
        while True:
            try:
                # 从队列获取评论
                comment = await self.comment_queue.get()
                
                # 发送评论
                success = await self.send_comment(comment)
                if success:
                    print(f"✅ 发送成功: {comment}")
                else:
                    print(f"❌ 发送失败: {comment}")
                
                # 标记任务完成
                self.comment_queue.task_done()
                
                # 随机延迟，避免频率过高
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"发送评论出错: {e}")
                await asyncio.sleep(1)
    
    async def send_comment(self, content):
        """发送评论到直播间"""
        try:
            # 构建评论数据
            comment_data = {
                'liveId': self.live_id,
                'content': content,
                'timestamp': int(time.time() * 1000),
                'userId': self.user_id
            }
            
            # 发送HTTP请求
            response = self.session.post(
                'https://liveplatform.taobao.com/api/live/comment',
                json=comment_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            
            return False
            
        except Exception as e:
            print(f"发送评论API调用失败: {e}")
            return False
    
    async def start_auto_comment(self, comments_list, interval_range=(3, 8)):
        """开始自动评论"""
        while True:
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
    
    async def run(self, live_url, auto_comments=None):
        """运行机器人"""
        try:
            # 提取直播间信息
            if not self.extract_live_info(live_url):
                print("无法提取直播间信息")
                return
            
            # 连接WebSocket
            if not await self.connect_websocket():
                print("WebSocket连接失败")
                return
            
            # 启动任务
            tasks = [
                asyncio.create_task(self.listen_messages()),
                asyncio.create_task(self.send_comment_worker())
            ]
            
            # 如果提供了自动评论列表，启动自动评论
            if auto_comments:
                tasks.append(
                    asyncio.create_task(self.start_auto_comment(auto_comments))
                )
            
            print("🤖 机器人已启动，开始监听直播间...")
            
            # 等待所有任务完成
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print("\n正在停止机器人...")
        except Exception as e:
            print(f"运行出错: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()

# 使用示例
async def main():
    bot = TaobaoLiveCommentBot()
    
    # 登录账号
    username = "your_username"
    password = "your_password"
    
    if bot.login(username, password):
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
            "颜色好看！"
        ]
        
        # 启动机器人
        await bot.run(live_url, auto_comments)

if __name__ == "__main__":
    asyncio.run(main())
