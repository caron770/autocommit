# 淘宝自动评论脚本使用指南

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器（推荐方案）
playwright install chromium

# 或者下载ChromeDriver（Selenium方案）
# 从 https://chromedriver.chromium.org/ 下载对应版本
```

### 2. 配置账号信息

创建 `.env` 文件：
```env
TAOBAO_USERNAME=your_username
TAOBAO_PASSWORD=your_password
```

### 3. 运行脚本

#### 方案一：Playwright（推荐）
```bash
python taobao_comment_playwright.py
```

#### 方案二：Selenium
```bash
python taobao_comment_selenium.py
```

## ⚙️ 高级配置

### 自定义评论内容

编辑脚本中的 `comments` 列表：
```python
comments = [
    "商品质量很好，物流很快，满意！",
    "包装精美，商品符合描述，好评！",
    "性价比很高，推荐购买！",
    # 添加更多评论...
]
```

### 调整运行参数

```python
# 设置无头模式（后台运行）
await bot.init_browser(headless=True)

# 调整延迟时间（秒）
await bot.random_delay(5, 10)  # 5-10秒随机延迟
```

## 🛡️ 安全建议

1. **测试环境**：先在测试账号上验证功能
2. **频率控制**：避免高频操作，建议每次间隔5-10秒
3. **内容多样化**：准备多样化的评论内容
4. **监控日志**：关注控制台输出，及时发现异常

## 📊 性能优化

### 提升速度的方法：

1. **使用HTTP请求**：直接调用API，速度最快
2. **无头模式**：减少界面渲染开销
3. **并发处理**：同时处理多个订单（需谨慎）
4. **缓存机制**：缓存登录状态和页面数据

### 示例：并发评论（高级用法）

```python
import asyncio

async def concurrent_comment(bot, orders, comments):
    """并发处理多个评论"""
    tasks = []
    for order in orders:
        comment = random.choice(comments)
        task = bot.submit_comment(order, comment)
        tasks.append(task)
        
        # 控制并发数量，避免过载
        if len(tasks) >= 3:
            await asyncio.gather(*tasks)
            tasks = []
            await asyncio.sleep(random.uniform(10, 20))
    
    # 处理剩余任务
    if tasks:
        await asyncio.gather(*tasks)
```

## 🚨 注意事项

- 本脚本仅供学习研究使用
- 请遵守淘宝平台使用规则
- 不要用于商业用途或恶意刷评
- 建议在虚拟环境中运行
- 定期更新脚本以适应页面变化

## 🔧 故障排除

### 常见问题：

1. **登录失败**：检查用户名密码，可能需要手动验证
2. **找不到元素**：页面结构可能已更新，需要调整选择器
3. **请求被拦截**：增加延迟时间，使用代理IP
4. **评论提交失败**：检查评论内容是否符合平台规范

### 调试技巧：

```python
# 开启详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 截图调试
await page.screenshot(path='debug.png')

# 保存页面HTML
html = await page.content()
with open('debug.html', 'w', encoding='utf-8') as f:
    f.write(html)
```
