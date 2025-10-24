#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝直播评论机器人 - PyQt图形界面
"""

import sys
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QGroupBox, QCheckBox, QProgressBar, QMessageBox, QFileDialog,
    QSplitter
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCursor

from src.workers import BotWorkerThread
from src.utils import ConfigManager, CookieManager, BrowserManager


class TaobaoLiveBotUI(QMainWindow):
    """淘宝直播评论机器人主界面"""
    
    def __init__(self):
        super().__init__()
        self.bot_thread = None
        self.config_manager = ConfigManager()
        self.cookie_manager = CookieManager()
        self.browser_manager = BrowserManager()
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('🤖 淘宝直播评论机器人 v2.0')
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #ff6600;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #ff6600;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ff8533;
            }
            QPushButton:pressed {
                background-color: #cc5200;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTextEdit {
                font-family: 'Courier New', monospace;
            }
        """)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 标题
        title_label = QLabel('🤖 淘宝直播评论机器人')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('color: #ff6600; padding: 10px;')
        main_layout.addWidget(title_label)
        
        # 分隔器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板 - 配置
        left_panel = self.create_left_panel()
        # 右侧面板 - 监控
        right_panel = self.create_right_panel()
        
        # 添加到分隔器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        
        # 底部状态栏
        self.statusBar().showMessage('就绪')
        
        # 定时器更新运行时间
        self.runtime_timer = QTimer()
        self.runtime_timer.timeout.connect(self.update_runtime)
        self.start_time = None
        
        # 添加欢迎日志
        self.add_log('🎉 欢迎使用淘宝直播评论机器人！', 'info')
        self.add_log('📖 请配置相关参数后点击"启动机器人"开始', 'info')
        self.add_log('⚠️ 仅供学习研究使用，请遵守相关法律法规', 'warning')
    
    def create_left_panel(self):
        """创建左侧配置面板"""
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # 方法选择
        method_group = QGroupBox('🔧 选择运行方法')
        method_layout = QVBoxLayout()
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            'Playwright - 推荐（可视化，稳定）',
            'WebSocket - 高级（速度快，隐蔽）',
            'Selenium - 传统（兼容性好）'
        ])
        self.method_combo.currentIndexChanged.connect(self.on_method_changed)
        method_layout.addWidget(self.method_combo)
        
        self.method_desc = QLabel('✨ 可视化操作，支持智能回复，推荐新手使用')
        self.method_desc.setWordWrap(True)
        self.method_desc.setStyleSheet('color: #666; font-size: 12px; padding: 5px;')
        method_layout.addWidget(self.method_desc)
        
        # 浏览器选择
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel('浏览器类型:'))
        self.browser_combo = QComboBox()
        
        # 获取可用浏览器
        available_browsers = self.browser_manager.detect_available_browsers()
        browser_options = []
        for browser_type in available_browsers:
            info = self.browser_manager.get_browser_info(browser_type)
            if browser_type == 'edge':
                browser_options.append(f"🔷 {info['name']} (推荐)")
            else:
                browser_options.append(f"🌐 {info['name']}")
        
        self.browser_combo.addItems(browser_options)
        
        browser_layout.addWidget(self.browser_combo)
        method_layout.addLayout(browser_layout)
        
        # 浏览器说明
        self.browser_desc = QLabel('🔷 微软Edge浏览器，基于Chromium内核')
        self.browser_desc.setWordWrap(True)
        self.browser_desc.setStyleSheet('color: #666; font-size: 11px; padding: 2px;')
        method_layout.addWidget(self.browser_desc)
        
        # 连接信号（在创建browser_desc之后）
        self.browser_combo.currentIndexChanged.connect(self.on_browser_changed)
        
        # 默认选择Edge（如果可用）
        if 'edge' in available_browsers:
            edge_index = available_browsers.index('edge')
            self.browser_combo.setCurrentIndex(edge_index)
        
        self.headless_checkbox = QCheckBox('无头模式（后台运行，不显示浏览器）')
        method_layout.addWidget(self.headless_checkbox)
        
        method_group.setLayout(method_layout)
        left_layout.addWidget(method_group)
        
        # 账号信息
        account_group = QGroupBox('👤 账号信息')
        account_layout = QVBoxLayout()
        
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel('用户名:'))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入淘宝账号')
        username_layout.addWidget(self.username_input)
        account_layout.addLayout(username_layout)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel('密码:'))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('请输入密码')
        password_layout.addWidget(self.password_input)
        account_layout.addLayout(password_layout)
        
        # Cookie选项
        cookie_layout = QHBoxLayout()
        self.save_cookie_checkbox = QCheckBox('保存Cookie（下次自动登录）')
        self.save_cookie_checkbox.setChecked(True)
        self.save_cookie_checkbox.setToolTip('保存登录状态，下次启动无需重新登录')
        cookie_layout.addWidget(self.save_cookie_checkbox)
        
        clear_cookie_btn = QPushButton('🗑️ 清除Cookie')
        clear_cookie_btn.clicked.connect(self.clear_cookies)
        clear_cookie_btn.setStyleSheet('background-color: #6c757d; font-size: 11px;')
        clear_cookie_btn.setMaximumWidth(100)
        clear_cookie_btn.setToolTip('清除当前账号的保存Cookie')
        cookie_layout.addWidget(clear_cookie_btn)
        
        account_layout.addLayout(cookie_layout)
        
        account_group.setLayout(account_layout)
        left_layout.addWidget(account_group)
        
        # 直播间设置
        live_group = QGroupBox('🎬 直播间设置')
        live_layout = QVBoxLayout()
        
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel('直播间URL:'))
        self.live_url_input = QLineEdit()
        self.live_url_input.setPlaceholderText('https://liveplatform.taobao.com/live/...')
        url_layout.addWidget(self.live_url_input)
        live_layout.addLayout(url_layout)
        
        live_group.setLayout(live_layout)
        left_layout.addWidget(live_group)
        
        # 评论设置
        comment_group = QGroupBox('💬 评论设置')
        comment_layout = QVBoxLayout()
        
        comment_layout.addWidget(QLabel('评论内容（每行一条）:'))
        self.comments_input = QTextEdit()
        self.comments_input.setPlaceholderText(
            '主播讲得真好！\n这个商品不错！\n价格很实惠！\n支持主播！\n666\n已下单！'
        )
        self.comments_input.setMaximumHeight(150)
        comment_layout.addWidget(self.comments_input)
        
        send_settings_layout = QHBoxLayout()
        send_settings_layout.addWidget(QLabel('发送间隔:'))
        self.interval_min_spin = QSpinBox()
        self.interval_min_spin.setRange(1, 60)
        self.interval_min_spin.setValue(5)
        self.interval_min_spin.setSuffix(' 秒')
        send_settings_layout.addWidget(self.interval_min_spin)
        send_settings_layout.addWidget(QLabel(' - '))
        self.interval_max_spin = QSpinBox()
        self.interval_max_spin.setRange(1, 60)
        self.interval_max_spin.setValue(12)
        self.interval_max_spin.setSuffix(' 秒')
        send_settings_layout.addWidget(self.interval_max_spin)
        comment_layout.addLayout(send_settings_layout)
        
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel('最大发送次数:'))
        self.max_count_spin = QSpinBox()
        self.max_count_spin.setRange(0, 10000)
        self.max_count_spin.setValue(100)
        self.max_count_spin.setSpecialValueText('不限制')
        count_layout.addWidget(self.max_count_spin)
        comment_layout.addLayout(count_layout)
        
        comment_group.setLayout(comment_layout)
        left_layout.addWidget(comment_group)
        
        # 高级设置
        advanced_group = QGroupBox('⚙️ 高级设置')
        advanced_layout = QVBoxLayout()
        
        self.auto_reply_checkbox = QCheckBox('启用智能回复（根据关键词自动回复）')
        self.auto_reply_checkbox.setChecked(True)
        advanced_layout.addWidget(self.auto_reply_checkbox)
        
        self.gift_thanks_checkbox = QCheckBox('启用礼物感谢（自动感谢送礼物的用户）')
        self.gift_thanks_checkbox.setChecked(True)
        advanced_layout.addWidget(self.gift_thanks_checkbox)
        
        self.welcome_checkbox = QCheckBox('启用欢迎消息（欢迎新进入的用户）')
        self.welcome_checkbox.setChecked(False)
        advanced_layout.addWidget(self.welcome_checkbox)
        
        advanced_group.setLayout(advanced_layout)
        left_layout.addWidget(advanced_group)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton('▶️ 启动机器人')
        self.start_button.clicked.connect(self.start_bot)
        self.start_button.setStyleSheet('background-color: #28a745; font-size: 14px;')
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton('⏹️ 停止机器人')
        self.stop_button.clicked.connect(self.stop_bot)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet('background-color: #dc3545; font-size: 14px;')
        control_layout.addWidget(self.stop_button)
        
        left_layout.addLayout(control_layout)
        
        # 配置保存/加载
        config_layout = QHBoxLayout()
        
        save_config_btn = QPushButton('💾 保存配置')
        save_config_btn.clicked.connect(self.save_config)
        save_config_btn.setStyleSheet('background-color: #6c757d; font-size: 12px;')
        config_layout.addWidget(save_config_btn)
        
        load_config_btn = QPushButton('📂 加载配置')
        load_config_btn.clicked.connect(self.load_config)
        load_config_btn.setStyleSheet('background-color: #6c757d; font-size: 12px;')
        config_layout.addWidget(load_config_btn)
        
        left_layout.addLayout(config_layout)
        left_layout.addStretch()
        
        return left_panel
    
    def create_right_panel(self):
        """创建右侧监控面板"""
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # 状态栏
        status_group = QGroupBox('📊 运行状态')
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel('状态: 未启动')
        self.status_label.setStyleSheet('font-size: 14px; font-weight: bold; color: #666;')
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        right_layout.addWidget(status_group)
        
        # 统计信息
        stats_group = QGroupBox('📈 统计信息')
        stats_layout = QVBoxLayout()
        
        stats_grid = QHBoxLayout()
        
        self.sent_label = QLabel('已发送: 0')
        self.sent_label.setStyleSheet('color: #28a745; font-weight: bold;')
        stats_grid.addWidget(self.sent_label)
        
        self.reply_label = QLabel('智能回复: 0')
        self.reply_label.setStyleSheet('color: #007bff; font-weight: bold;')
        stats_grid.addWidget(self.reply_label)
        
        self.gift_label = QLabel('感谢礼物: 0')
        self.gift_label.setStyleSheet('color: #ffc107; font-weight: bold;')
        stats_grid.addWidget(self.gift_label)
        
        self.error_label = QLabel('错误: 0')
        self.error_label.setStyleSheet('color: #dc3545; font-weight: bold;')
        stats_grid.addWidget(self.error_label)
        
        stats_layout.addLayout(stats_grid)
        
        self.runtime_label = QLabel('运行时间: 00:00:00')
        self.runtime_label.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.runtime_label)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        # 日志显示
        log_group = QGroupBox('📝 运行日志')
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        log_control_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton('🗑️ 清空日志')
        clear_log_btn.clicked.connect(self.clear_log)
        clear_log_btn.setStyleSheet('background-color: #6c757d;')
        log_control_layout.addWidget(clear_log_btn)
        
        export_log_btn = QPushButton('💾 导出日志')
        export_log_btn.clicked.connect(self.export_log)
        export_log_btn.setStyleSheet('background-color: #6c757d;')
        log_control_layout.addWidget(export_log_btn)
        
        log_layout.addLayout(log_control_layout)
        
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)
        
        return right_panel
    
    def on_method_changed(self, index):
        """方法选择改变"""
        descriptions = {
            0: '✨ Playwright: 可视化操作，支持智能回复，推荐新手使用。响应速度快，稳定性好。',
            1: '🚀 WebSocket: 速度最快，隐蔽性强，适合高级用户。支持毫秒级响应。',
            2: '🔧 Selenium: 传统方案，兼容性好，资料丰富。速度较慢但稳定。'
        }
        self.method_desc.setText(descriptions.get(index, ''))
        
        # Playwright方法才显示浏览器选择
        is_playwright = (index == 0)
        self.browser_combo.setVisible(is_playwright)
        self.browser_desc.setVisible(is_playwright)
        # 找到浏览器类型标签
        for i in range(self.browser_combo.parent().layout().count()):
            item = self.browser_combo.parent().layout().itemAt(i)
            if item and item.widget() and isinstance(item.widget(), QLabel):
                if item.widget().text() == '浏览器类型:':
                    item.widget().setVisible(is_playwright)
                    break
    
    def on_browser_changed(self, index):
        """浏览器选择改变"""
        # 获取可用浏览器列表
        available_browsers = self.browser_manager.detect_available_browsers()
        if index < len(available_browsers):
            browser_type = available_browsers[index]
            info = self.browser_manager.get_browser_info(browser_type)
            self.browser_desc.setText(f'🔷 {info["description"]}')
            
            # 更新日志
            self.add_log(f'🔄 已选择浏览器: {info["name"]}', 'info')
    
    def start_bot(self):
        """启动机器人"""
        # 获取选择的浏览器类型
        available_browsers = self.browser_manager.detect_available_browsers()
        browser_index = self.browser_combo.currentIndex()
        browser_type = available_browsers[browser_index] if browser_index < len(available_browsers) else 'chromium'
        
        # 准备配置
        config = {
            'method': ['playwright', 'websocket', 'selenium'][self.method_combo.currentIndex()],
            'browser_type': browser_type,
            'headless': self.headless_checkbox.isChecked(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text().strip(),
            'live_url': self.live_url_input.text().strip(),
            'comments': [c.strip() for c in self.comments_input.toPlainText().split('\n') if c.strip()],
            'interval_min': self.interval_min_spin.value(),
            'interval_max': self.interval_max_spin.value(),
            'max_count': self.max_count_spin.value(),
            'auto_reply': self.auto_reply_checkbox.isChecked(),
            'gift_thanks': self.gift_thanks_checkbox.isChecked(),
            'welcome': self.welcome_checkbox.isChecked(),
            'save_cookie': self.save_cookie_checkbox.isChecked()
        }
        
        # 验证配置
        is_valid, message = self.config_manager.validate_config(config)
        if not is_valid:
            QMessageBox.warning(self, '配置错误', message)
            return
        
        # 启动工作线程
        self.bot_thread = BotWorkerThread(config)
        self.bot_thread.log_signal.connect(self.add_log)
        self.bot_thread.stats_signal.connect(self.update_stats)
        self.bot_thread.status_signal.connect(self.update_status)
        self.bot_thread.finished.connect(self.on_bot_finished)
        
        self.bot_thread.start()
        
        # 更新UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage('机器人运行中...')
        
        # 启动运行时间计时器
        self.start_time = time.time()
        self.runtime_timer.start(1000)
        
        self.add_log('=' * 60, 'info')
        self.add_log(f'🚀 机器人启动 - 方法: {config["method"]}', 'info')
        if config["method"] == "playwright":
            browser_info = self.browser_manager.get_browser_info(config["browser_type"])
            self.add_log(f'🌐 浏览器: {browser_info["name"]}', 'info')
        self.add_log(f'🎬 直播间: {config["live_url"]}', 'info')
        self.add_log(f'💬 评论数量: {len(config["comments"])} 条', 'info')
        self.add_log(f'⏱️ 发送间隔: {config["interval_min"]}-{config["interval_max"]} 秒', 'info')
        self.add_log('=' * 60, 'info')
    
    def stop_bot(self):
        """停止机器人"""
        if self.bot_thread and self.bot_thread.isRunning():
            reply = QMessageBox.question(
                self,
                '确认停止',
                '确定要停止机器人吗？',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.add_log('⏹️ 正在停止机器人...', 'warning')
                self.bot_thread.stop()
                self.bot_thread.wait()
    
    def on_bot_finished(self):
        """机器人停止后的处理"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage('就绪')
        self.runtime_timer.stop()
    
    def add_log(self, message, level='info'):
        """添加日志"""
        # 检查log_text是否已经创建，如果没有则直接返回
        if not hasattr(self, 'log_text') or self.log_text is None:
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        colors = {
            'info': '#d4d4d4',
            'success': '#4ec9b0',
            'warning': '#dcdcaa',
            'error': '#f48771'
        }
        
        color = colors.get(level, '#d4d4d4')
        
        formatted_message = f'<span style="color: #808080;">[{timestamp}]</span> ' \
                          f'<span style="color: {color};">{message}</span>'
        
        self.log_text.append(formatted_message)
        
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def update_stats(self, stats):
        """更新统计信息"""
        self.sent_label.setText(f'已发送: {stats.get("comments_sent", 0)}')
        self.reply_label.setText(f'智能回复: {stats.get("replies_sent", 0)}')
        self.gift_label.setText(f'感谢礼物: {stats.get("gifts_thanked", 0)}')
        self.error_label.setText(f'错误: {stats.get("errors", 0)}')
    
    def update_status(self, status):
        """更新状态"""
        status_colors = {
            '运行中': '#28a745',
            '已停止': '#6c757d',
            '错误': '#dc3545'
        }
        
        color = status_colors.get(status, '#6c757d')
        self.status_label.setText(f'状态: {status}')
        self.status_label.setStyleSheet(f'font-size: 14px; font-weight: bold; color: {color};')
    
    def update_runtime(self):
        """更新运行时间"""
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.runtime_label.setText(f'运行时间: {hours:02d}:{minutes:02d}:{seconds:02d}')
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.add_log('📝 日志已清空', 'info')
    
    def clear_cookies(self):
        """清除Cookie"""
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, '提示', '请先输入用户名')
            return
        
        reply = QMessageBox.question(
            self,
            '确认清除',
            f'确定要清除账号 "{username}" 的Cookie吗？\n清除后下次需要重新登录。',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.cookie_manager.delete_cookies(username):
                QMessageBox.information(self, '成功', 'Cookie已清除！')
                self.add_log(f'🗑️ 已清除账号 {username} 的Cookie', 'info')
            else:
                QMessageBox.information(self, '提示', '该账号没有保存的Cookie')
                self.add_log(f'ℹ️ 账号 {username} 没有保存的Cookie', 'info')
    
    def export_log(self):
        """导出日志"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            '导出日志',
            f'log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            'Text Files (*.txt)'
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, '成功', f'日志已导出到: {filename}')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'导出失败: {str(e)}')
    
    def save_config(self):
        """保存配置"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            '保存配置',
            'config.json',
            'JSON Files (*.json)'
        )
        
        if filename:
            # 获取选择的浏览器类型
            available_browsers = self.browser_manager.detect_available_browsers()
            browser_index = self.browser_combo.currentIndex()
            browser_type = available_browsers[browser_index] if browser_index < len(available_browsers) else 'chromium'
            
            config = {
                'method': self.method_combo.currentIndex(),
                'browser_type': browser_type,
                'headless': self.headless_checkbox.isChecked(),
                'username': self.username_input.text(),
                'live_url': self.live_url_input.text(),
                'comments': self.comments_input.toPlainText(),
                'interval_min': self.interval_min_spin.value(),
                'interval_max': self.interval_max_spin.value(),
                'max_count': self.max_count_spin.value(),
                'auto_reply': self.auto_reply_checkbox.isChecked(),
                'gift_thanks': self.gift_thanks_checkbox.isChecked(),
                'welcome': self.welcome_checkbox.isChecked(),
                'save_cookie': self.save_cookie_checkbox.isChecked()
            }
            
            if self.config_manager.save_config(config, filename):
                QMessageBox.information(self, '成功', '配置已保存！')
            else:
                QMessageBox.critical(self, '错误', '保存配置失败！')
    
    def load_config(self):
        """加载配置"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            '加载配置',
            '',
            'JSON Files (*.json)'
        )
        
        if filename:
            config = self.config_manager.load_config(filename)
            
            if config:
                self.method_combo.setCurrentIndex(config.get('method', 0))
                
                # 加载浏览器配置
                browser_type = config.get('browser_type', 'chromium')
                available_browsers = self.browser_manager.detect_available_browsers()
                if browser_type in available_browsers:
                    browser_index = available_browsers.index(browser_type)
                    self.browser_combo.setCurrentIndex(browser_index)
                
                self.headless_checkbox.setChecked(config.get('headless', False))
                self.username_input.setText(config.get('username', ''))
                self.live_url_input.setText(config.get('live_url', ''))
                self.comments_input.setPlainText(config.get('comments', ''))
                self.interval_min_spin.setValue(config.get('interval_min', 5))
                self.interval_max_spin.setValue(config.get('interval_max', 12))
                self.max_count_spin.setValue(config.get('max_count', 100))
                self.auto_reply_checkbox.setChecked(config.get('auto_reply', True))
                self.gift_thanks_checkbox.setChecked(config.get('gift_thanks', True))
                self.welcome_checkbox.setChecked(config.get('welcome', False))
                self.save_cookie_checkbox.setChecked(config.get('save_cookie', True))
                
                QMessageBox.information(self, '成功', '配置已加载！')
                self.add_log('📂 配置已从文件加载', 'success')
            else:
                QMessageBox.critical(self, '错误', '加载配置失败！')

