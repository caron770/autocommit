# 📁 项目结构说明

## 目录结构

```
autocommit/
├── src/                          # 源代码目录
│   ├── __init__.py              # 包初始化文件
│   ├── ui/                      # UI界面模块
│   │   ├── __init__.py
│   │   └── main_window.py       # PyQt主窗口实现
│   ├── bots/                    # 机器人实现模块
│   │   ├── __init__.py
│   │   ├── live/               # 直播评论机器人
│   │   │   ├── __init__.py
│   │   │   ├── playwright_bot.py    # Playwright实现
│   │   │   └── websocket_bot.py     # WebSocket实现
│   │   └── product/            # 商品评价机器人
│   │       ├── __init__.py
│   │       ├── playwright_bot.py    # Playwright实现
│   │       └── selenium_bot.py      # Selenium实现
│   ├── utils/                  # 工具函数模块
│   │   ├── __init__.py
│   │   └── config_manager.py   # 配置管理器
│   └── workers/                # 工作线程模块
│       ├── __init__.py
│       └── bot_worker.py       # 机器人工作线程
├── config/                     # 配置文件目录
│   └── example_config.json     # 示例配置文件
├── docs/                       # 文档目录
│   ├── UI使用说明.md           # UI使用说明
│   ├── live_comment_guide.md  # 技术详解
│   └── setup_guide.md         # 安装指南
├── scripts/                    # 脚本目录
│   ├── start_ui.sh            # Mac/Linux启动脚本
│   └── start_ui.bat           # Windows启动脚本
├── extensions/                 # 浏览器扩展
│   └── taobao_live_extension.js   # 浏览器插件
├── main.py                    # 主入口文件
├── requirements.txt           # Python依赖列表
├── .gitignore                # Git忽略文件
├── README.md                 # 项目说明
└── STRUCTURE.md             # 本文件

```

## 模块说明

### 1. src/ - 源代码目录

所有Python源代码都在这个目录下，采用模块化设计。

#### src/ui/ - 界面模块
- `main_window.py`: PyQt5主窗口实现
  - TaobaoLiveBotUI类：主界面类
  - 包含所有UI组件和交互逻辑

#### src/bots/ - 机器人实现

**src/bots/live/** - 直播评论机器人
- `playwright_bot.py`: 基于Playwright的直播评论实现
  - TaobaoLivePlaywrightBot类
  - 支持智能回复、礼物感谢等功能
- `websocket_bot.py`: 基于WebSocket的高性能实现
  - TaobaoLiveCommentBot类
  - 毫秒级响应速度

**src/bots/product/** - 商品评价机器人
- `playwright_bot.py`: 基于Playwright的商品评价
- `selenium_bot.py`: 基于Selenium的传统实现

#### src/utils/ - 工具模块
- `config_manager.py`: 配置管理器
  - ConfigManager类
  - 支持配置的保存、加载、验证

#### src/workers/ - 工作线程
- `bot_worker.py`: 机器人工作线程
  - BotWorkerThread类
  - 处理机器人运行逻辑
  - 通过信号与UI通信

### 2. config/ - 配置目录

存放配置文件：
- `example_config.json`: 示例配置，可作为模板

### 3. docs/ - 文档目录

所有文档集中存放：
- `UI使用说明.md`: 详细的图形界面使用教程
- `live_comment_guide.md`: 技术实现和优化指南
- `setup_guide.md`: 安装和配置指南

### 4. scripts/ - 脚本目录

启动脚本：
- `start_ui.sh`: Mac/Linux启动脚本
- `start_ui.bat`: Windows启动脚本

### 5. extensions/ - 浏览器扩展

- `taobao_live_extension.js`: 浏览器插件版本的实现

## 导入路径

### 主程序导入
```python
# main.py
from src.ui import TaobaoLiveBotUI
```

### UI模块导入
```python
# src/ui/main_window.py
from src.workers import BotWorkerThread
from src.utils import ConfigManager
```

### Worker模块导入
```python
# src/workers/bot_worker.py
from src.bots.live import TaobaoLivePlaywrightBot, TaobaoLiveCommentBot
```

## 运行方式

### 1. 使用启动脚本（推荐）
```bash
# Mac/Linux
./scripts/start_ui.sh

# Windows
scripts\start_ui.bat
```

### 2. 直接运行主程序
```bash
python main.py
```

## 开发指南

### 添加新功能

1. **添加新的机器人实现**
   - 在 `src/bots/live/` 或 `src/bots/product/` 添加新文件
   - 更新对应的 `__init__.py`
   - 在 `src/workers/bot_worker.py` 添加调用逻辑

2. **添加新的UI组件**
   - 在 `src/ui/` 添加新的UI文件
   - 在 `main_window.py` 中导入使用

3. **添加新的工具函数**
   - 在 `src/utils/` 添加新的工具模块
   - 更新 `__init__.py`

### 代码规范

- 使用 UTF-8 编码
- 遵循 PEP 8 代码规范
- 添加必要的类型注解
- 编写清晰的文档字符串

## 版本历史

### v2.0 (2024-10-13)
- ✨ 重构项目结构
- 📦 模块化设计
- 🎨 优化代码组织
- 📁 规范目录布局

### v1.0 (2024-10-12)
- 🎉 首次发布
- 💬 基础功能实现

## 维护说明

### 定期维护任务

1. **更新依赖**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **清理缓存**
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} +
   find . -type f -name "*.pyc" -delete
   ```

3. **代码检查**
   ```bash
   flake8 src/
   pylint src/
   ```

## 注意事项

- 所有Python模块都放在 `src/` 目录下
- 配置文件放在 `config/` 目录
- 文档放在 `docs/` 目录
- 不要将敏感信息提交到版本控制
- 遵守 `.gitignore` 规则

---

**更新日期：2024-10-13**
