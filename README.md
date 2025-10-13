# 🤖 淘宝直播评论机器人

一个功能强大的淘宝直播间评论自动化工具，支持多种运行方式，配备完整的图形化界面。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 主要特性

### 🎨 图形化界面
- 💻 **现代化UI设计**：基于PyQt5的美观界面
- 🎛️ **实时控制面板**：可视化配置所有参数
- 📊 **数据统计展示**：实时显示运行状态和统计信息
- 📝 **彩色日志输出**：分级显示运行日志

### 🚀 多种运行方式
| 方式 | 速度 | 稳定性 | 隐蔽性 | 难度 | 推荐度 |
|------|------|--------|--------|------|--------|
| **Playwright** | 🚀🚀🚀🚀 | ⭐⭐⭐⭐⭐ | 🛡️🛡️🛡️🛡️ | 🔧🔧 | ⭐⭐⭐⭐⭐ |
| **WebSocket** | 🚀🚀🚀🚀🚀 | ⭐⭐⭐⭐ | 🛡️🛡️🛡️🛡️🛡️ | 🔧🔧🔧🔧 | ⭐⭐⭐⭐ |
| **Selenium** | 🚀🚀 | ⭐⭐⭐ | 🛡️🛡️ | 🔧🔧 | ⭐⭐⭐ |

### 🤖 智能功能
- 💬 **自动评论**：预设内容定时发送
- 🧠 **智能回复**：关键词触发自动回复
- 🎁 **礼物感谢**：自动感谢送礼物的用户
- 👋 **欢迎消息**：新用户进入时自动欢迎
- 🍪 **Cookie保存**：自动保存登录状态，无需重复登录

## 📁 项目结构

```
autocommit/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── ui/                       # UI界面模块
│   │   ├── __init__.py
│   │   └── main_window.py       # PyQt主窗口
│   ├── bots/                     # 机器人实现模块
│   │   ├── __init__.py
│   │   ├── live/                # 直播评论
│   │   │   ├── __init__.py
│   │   │   ├── playwright_bot.py
│   │   │   └── websocket_bot.py
│   │   └── product/             # 商品评价
│   │       ├── __init__.py
│   │       ├── playwright_bot.py
│   │       └── selenium_bot.py
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── config_manager.py   # 配置管理器
│   │   └── cookie_manager.py   # Cookie管理器
│   └── workers/                 # 工作线程
│       ├── __init__.py
│       └── bot_worker.py
├── config/                      # 配置文件目录
│   ├── cookies/                # Cookie存储目录
│   └── example_config.json
├── docs/                        # 文档目录
│   ├── README.md
│   ├── UI使用说明.md
│   ├── live_comment_guide.md
│   ├── setup_guide.md
│   └── COOKIE功能说明.md      # Cookie功能说明
├── scripts/                     # 脚本目录
│   ├── start_ui.sh
│   └── start_ui.bat
├── extensions/                  # 浏览器扩展
│   └── taobao_live_extension.js
├── main.py                     # 主入口文件
├── requirements.txt            # 依赖列表
├── .gitignore                 # Git忽略文件
└── README.md                  # 项目说明
```

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

#### Windows
```bash
双击运行 scripts\start_ui.bat
```

#### Mac/Linux
```bash
./scripts/start_ui.sh
```

### 方式二：手动安装

#### 1. 安装依赖
```bash
# 安装Python包
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

#### 2. 启动程序
```bash
python main.py
```

## 📖 使用教程

### 基础使用
1. 打开程序
2. 选择运行方式（推荐Playwright）
3. 输入直播间URL
4. 填写评论内容（每行一条）
5. 设置发送间隔
6. 点击"启动机器人"

### 高级功能
- **智能回复**：勾选后会根据用户评论关键词自动回复
- **配置保存**：可保存当前配置，下次直接加载
- **日志导出**：可将运行日志导出为文件
- **无头模式**：后台运行，不显示浏览器窗口
- **Cookie保存**：自动保存登录状态，下次无需重复登录

详细教程请查看：
- [docs/UI使用说明.md](docs/UI使用说明.md) - UI使用教程
- [docs/COOKIE功能说明.md](docs/COOKIE功能说明.md) - Cookie功能详解

## 🎯 功能对比

### 直播评论 vs 商品评价

| 特性 | 直播评论 | 商品评价 |
|------|---------|---------|
| **实时性** | 要求高，毫秒级 | 要求低，分钟级 |
| **频率** | 可高频（秒级） | 低频（订单级） |
| **交互** | 支持智能回复 | 单向评价 |
| **复杂度** | 较高 | 较低 |
| **应用场景** | 直播互动 | 订单评价 |

## ⚠️ 注意事项

### 频率建议
```python
SAFE_FREQUENCIES = {
    '新手练习': (10, 20),   # 10-20秒一次
    '日常使用': (5, 12),    # 5-12秒一次
    '高频模式': (3, 8),     # 3-8秒一次（需谨慎）
}
```

### 安全建议
- ✅ 使用测试账号，避免主账号风险
- ✅ 控制发送频率，避免被检测
- ✅ 内容多样化，避免重复
- ✅ 分时段运行，避免长时间不间断
- ❌ 不要用于商业用途
- ❌ 不要恶意刷评论
- ❌ 不要违反平台规则

## 🛡️ 反检测策略

1. **行为模拟**
   - 随机延迟时间
   - 模拟打字速度
   - 真实用户代理

2. **内容多样化**
   - 动态生成评论
   - 轮换评论内容
   - 关键词替换

3. **频率控制**
   - 自适应调整
   - 智能退避
   - 分时段运行

## 📊 性能指标

| 指标 | Playwright | WebSocket | Selenium |
|------|-----------|-----------|----------|
| **响应速度** | < 2秒 | < 100ms | < 5秒 |
| **发送频率** | 20-40条/小时 | 40-60条/小时 | 10-20条/小时 |
| **成功率** | 95%+ | 98%+ | 85%+ |
| **资源占用** | 中 | 低 | 高 |

## 🔧 故障排除

### 常见问题

**Q: 启动后提示缺少模块？**
```bash
pip install -r requirements.txt
playwright install chromium
```

**Q: 评论发送失败？**
- 检查登录状态
- 降低发送频率
- 更换评论内容

**Q: 程序卡住不动？**
- 重启程序
- 检查网络连接
- 使用无头模式

更多问题请查看 [docs/UI使用说明.md](docs/UI使用说明.md#常见问题)

## 📝 更新日志

### v2.0 (2024-10-13)
- ✨ 重构项目结构，模块化设计
- 🚀 优化代码组织，提高可维护性
- 📦 添加配置管理器
- 🎨 改进UI代码结构
- 📁 规范目录布局

### v1.0 (2024-10-12)
- 🎉 首次发布
- 💬 基础评论功能
- 📝 命令行版本

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目仅供学习研究使用，请勿用于商业用途。

## ⚠️ 免责声明

**重要提醒：**
- 本工具仅供学习研究使用
- 请遵守相关法律法规和平台规则
- 使用本工具产生的一切后果由使用者自行承担
- 不得用于商业用途或恶意刷评
- 建议仅在测试环境使用

## 📞 支持

如有问题，请：
1. 查看 [docs/UI使用说明.md](docs/UI使用说明.md)
2. 查看 [docs/live_comment_guide.md](docs/live_comment_guide.md)
3. 检查运行日志
4. 提交 Issue

---

**享受使用，祝你学习愉快！** 🎉

Made with ❤️ for learning purposes only.