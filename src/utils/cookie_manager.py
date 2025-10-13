#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookie管理器 - 保存和加载Cookie，避免重复登录
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class CookieManager:
    """Cookie管理器"""
    
    def __init__(self, cookies_dir: str = "config/cookies"):
        """
        初始化Cookie管理器
        
        Args:
            cookies_dir: Cookie存储目录
        """
        self.cookies_dir = Path(cookies_dir)
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
    
    def save_cookies(self, cookies: List[Dict[str, Any]], username: str) -> bool:
        """
        保存Cookie到文件
        
        Args:
            cookies: Cookie列表
            username: 用户名（用于区分不同账号）
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 使用用户名作为文件名（安全处理）
            safe_username = "".join(c for c in username if c.isalnum() or c in ('_', '-'))
            cookie_file = self.cookies_dir / f"{safe_username}_cookies.json"
            
            # 添加保存时间
            cookie_data = {
                'username': username,
                'saved_at': datetime.now().isoformat(),
                'cookies': cookies
            }
            
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Cookie已保存: {cookie_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存Cookie失败: {e}")
            return False
    
    def load_cookies(self, username: str) -> List[Dict[str, Any]]:
        """
        从文件加载Cookie
        
        Args:
            username: 用户名
            
        Returns:
            List[Dict]: Cookie列表，如果不存在返回空列表
        """
        try:
            safe_username = "".join(c for c in username if c.isalnum() or c in ('_', '-'))
            cookie_file = self.cookies_dir / f"{safe_username}_cookies.json"
            
            if not cookie_file.exists():
                print(f"ℹ️ Cookie文件不存在: {cookie_file}")
                return []
            
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            # 检查Cookie是否过期（可选：根据saved_at判断）
            saved_at = datetime.fromisoformat(cookie_data.get('saved_at', ''))
            days_old = (datetime.now() - saved_at).days
            
            if days_old > 30:  # Cookie超过30天，可能已过期
                print(f"⚠️ Cookie已超过30天，可能已过期")
                return []
            
            print(f"✅ 成功加载Cookie (保存于 {days_old} 天前)")
            return cookie_data.get('cookies', [])
            
        except Exception as e:
            print(f"❌ 加载Cookie失败: {e}")
            return []
    
    def delete_cookies(self, username: str) -> bool:
        """
        删除指定用户的Cookie
        
        Args:
            username: 用户名
            
        Returns:
            bool: 是否删除成功
        """
        try:
            safe_username = "".join(c for c in username if c.isalnum() or c in ('_', '-'))
            cookie_file = self.cookies_dir / f"{safe_username}_cookies.json"
            
            if cookie_file.exists():
                cookie_file.unlink()
                print(f"✅ Cookie已删除: {cookie_file}")
                return True
            else:
                print(f"ℹ️ Cookie文件不存在")
                return False
                
        except Exception as e:
            print(f"❌ 删除Cookie失败: {e}")
            return False
    
    def list_saved_cookies(self) -> List[Dict[str, str]]:
        """
        列出所有已保存的Cookie信息
        
        Returns:
            List[Dict]: Cookie信息列表
        """
        try:
            cookie_files = list(self.cookies_dir.glob("*_cookies.json"))
            cookies_info = []
            
            for cookie_file in cookie_files:
                try:
                    with open(cookie_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    cookies_info.append({
                        'username': data.get('username', 'Unknown'),
                        'saved_at': data.get('saved_at', 'Unknown'),
                        'file': str(cookie_file)
                    })
                except:
                    continue
            
            return cookies_info
            
        except Exception as e:
            print(f"❌ 列出Cookie失败: {e}")
            return []
    
    def clean_expired_cookies(self, days: int = 30) -> int:
        """
        清理过期的Cookie
        
        Args:
            days: 超过多少天算过期
            
        Returns:
            int: 清理的Cookie数量
        """
        try:
            cleaned = 0
            cookie_files = list(self.cookies_dir.glob("*_cookies.json"))
            
            for cookie_file in cookie_files:
                try:
                    with open(cookie_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    saved_at = datetime.fromisoformat(data.get('saved_at', ''))
                    days_old = (datetime.now() - saved_at).days
                    
                    if days_old > days:
                        cookie_file.unlink()
                        cleaned += 1
                        print(f"🗑️ 清理过期Cookie: {cookie_file.name} ({days_old}天前)")
                except:
                    continue
            
            print(f"✅ 共清理 {cleaned} 个过期Cookie")
            return cleaned
            
        except Exception as e:
            print(f"❌ 清理Cookie失败: {e}")
            return 0

