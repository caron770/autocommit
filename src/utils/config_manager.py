#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """配置文件管理器"""
    
    @staticmethod
    def save_config(config: Dict[str, Any], filepath: str) -> bool:
        """保存配置到文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    @staticmethod
    def load_config(filepath: str) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'method': 0,
            'headless': False,
            'username': '',
            'live_url': '',
            'comments': '',
            'interval_min': 5,
            'interval_max': 12,
            'max_count': 100,
            'auto_reply': True,
            'gift_thanks': True,
            'welcome': False
        }
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> tuple[bool, str]:
        """验证配置有效性"""
        if not config.get('live_url'):
            return False, "直播间URL不能为空"
        
        if not config.get('comments'):
            return False, "评论内容不能为空"
        
        interval_min = config.get('interval_min', 0)
        interval_max = config.get('interval_max', 0)
        
        if interval_min <= 0 or interval_max <= 0:
            return False, "发送间隔必须大于0"
        
        if interval_min > interval_max:
            return False, "最小间隔不能大于最大间隔"
        
        return True, "配置有效"

