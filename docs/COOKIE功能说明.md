# 🍪 Cookie保存功能说明

## 📋 功能概述

Cookie保存功能让你无需每次都输入账号密码登录，大大提升使用体验！

### ✨ 主要特性

- 🔐 **自动登录**：保存登录状态，下次启动自动登录
- 💾 **安全存储**：Cookie加密存储在本地
- 🗑️ **一键清除**：随时清除保存的Cookie
- 👥 **多账号支持**：支持保存多个账号的Cookie
- ⏰ **过期检测**：自动检测过期Cookie（30天）

## 🚀 使用方法

### 1. 保存Cookie

#### 步骤一：勾选保存选项
在UI界面的"账号信息"区域，勾选 **"保存Cookie（下次自动登录）"** 选项。

```
┌─────────────────────────────┐
│ 👤 账号信息                  │
├─────────────────────────────┤
│ 用户名: [your_username]     │
│ 密码:   [**********]        │
│ ☑ 保存Cookie（下次自动登录）│
│         [🗑️ 清除Cookie]     │
└─────────────────────────────┘
```

#### 步骤二：正常登录
- 点击"启动机器人"
- 输入账号密码登录
- 登录成功后，Cookie会自动保存

#### 日志提示
```
[10:30:15] ✅ 登录成功
[10:30:15] 💾 Cookie已保存，下次可自动登录
```

### 2. 使用Cookie自动登录

下次启动时：

1. **勾选** "保存Cookie（下次自动登录）"
2. **输入用户名**（用于识别Cookie）
3. **点击**"启动机器人"
4. 系统会自动加载Cookie并尝试登录

#### 成功提示
```
[10:35:20] 📱 初始化浏览器...
[10:35:21] ✅ 已加载保存的Cookie，可能无需登录
[10:35:22] 🔐 正在登录...
[10:35:23] ✅ 使用Cookie自动登录成功！
```

### 3. 清除Cookie

当你想重新登录或切换账号时：

1. **输入用户名**
2. **点击** "🗑️ 清除Cookie" 按钮
3. **确认**清除操作

系统会删除该账号的所有Cookie，下次需要重新登录。

## 🔧 高级功能

### 多账号管理

Cookie按用户名区分，可以保存多个账号：

```python
config/cookies/
├── user1_cookies.json      # 账号1的Cookie
├── user2_cookies.json      # 账号2的Cookie
└── user3_cookies.json      # 账号3的Cookie
```

### 自动清理过期Cookie

程序会自动检测Cookie年龄：
- **< 30天**：正常使用 ✅
- **> 30天**：可能过期，提示重新登录 ⚠️

你也可以手动清理所有过期Cookie：

```python
from src.utils import CookieManager

cookie_manager = CookieManager()
# 清理超过30天的Cookie
cookie_manager.clean_expired_cookies(days=30)
```

## 📁 存储位置

Cookie文件存储在：
```
config/cookies/{username}_cookies.json
```

### Cookie文件格式

```json
{
  "username": "your_username",
  "saved_at": "2024-10-13T10:30:15.123456",
  "cookies": [
    {
      "name": "cookie_name",
      "value": "cookie_value",
      "domain": ".taobao.com",
      "path": "/",
      "expires": 1234567890,
      "httpOnly": true,
      "secure": true
    }
    // ... 更多Cookie
  ]
}
```

## 🔒 安全说明

### Cookie安全性

1. **本地存储**
   - Cookie仅存储在本地计算机
   - 不会上传到任何服务器
   - 文件存储在项目目录下

2. **访问权限**
   - Cookie文件仅当前用户可访问
   - 使用文件系统权限保护

3. **敏感信息**
   - Cookie包含登录状态信息
   - **不要**分享Cookie文件给他人
   - **不要**将Cookie文件提交到版本控制

### 安全建议

✅ **推荐做法：**
- 定期清除不用的Cookie
- 使用测试账号进行开发
- 不在公共电脑上保存Cookie
- 定期更换密码

❌ **避免做法：**
- 不要分享Cookie文件
- 不要在多台电脑间复制Cookie
- 不要长期不清理Cookie
- 不要保存重要账号的Cookie

## ⚙️ 配置选项

### 在配置文件中设置

`config.json`:
```json
{
  "save_cookie": true,  // 是否保存Cookie
  "username": "your_username",
  // ... 其他配置
}
```

### 在代码中使用

```python
from src.utils import CookieManager

# 创建Cookie管理器
cookie_manager = CookieManager()

# 保存Cookie
cookies = await context.cookies()  # Playwright获取Cookie
cookie_manager.save_cookies(cookies, username="user1")

# 加载Cookie
cookies = cookie_manager.load_cookies(username="user1")
if cookies:
    await context.add_cookies(cookies)

# 删除Cookie
cookie_manager.delete_cookies(username="user1")

# 列出所有保存的Cookie
all_cookies = cookie_manager.list_saved_cookies()

# 清理过期Cookie
cleaned = cookie_manager.clean_expired_cookies(days=30)
```

## ❓ 常见问题

### Q1: Cookie保存在哪里？
**A:** Cookie保存在 `config/cookies/` 目录下，以 `{username}_cookies.json` 命名。

### Q2: Cookie会过期吗？
**A:** 会的。Cookie一般有效期为30天左右，过期后需要重新登录。

### Q3: 可以手动编辑Cookie文件吗？
**A:** 可以，但不推荐。Cookie格式复杂，手动编辑可能导致登录失败。

### Q4: Cookie安全吗？
**A:** Cookie存储在本地，相对安全。但不要分享给他人，也不要提交到代码仓库。

### Q5: 自动登录失败怎么办？
**A:** 可能是Cookie过期，点击"清除Cookie"按钮，然后重新登录。

### Q6: 可以保存多个账号吗？
**A:** 可以！系统会根据用户名自动区分不同账号的Cookie。

### Q7: Cookie会被上传吗？
**A:** 不会！Cookie仅存储在你的本地电脑，绝不上传。

### Q8: 如何彻底删除所有Cookie？
**A:** 删除 `config/cookies/` 目录下的所有文件即可。

## 🔍 故障排除

### 问题1: 自动登录失败

**症状**：勾选了保存Cookie，但每次还是要登录

**解决方案：**
1. 检查Cookie文件是否存在：`config/cookies/{username}_cookies.json`
2. 检查用户名是否输入正确
3. 尝试清除Cookie重新登录
4. 查看日志中的错误信息

### 问题2: Cookie文件找不到

**症状**：提示"Cookie文件不存在"

**解决方案：**
1. 确认之前已经成功登录过
2. 确认勾选了"保存Cookie"选项
3. 检查 `config/cookies/` 目录是否存在
4. 确认用户名拼写正确

### 问题3: Cookie加载失败

**症状**：加载Cookie后仍需登录

**解决方案：**
1. Cookie可能已过期，清除后重新登录
2. 网站可能更新了Cookie策略
3. 检查网络连接是否正常

## 📝 更新日志

### v2.0 (2024-10-13)
- ✨ 新增Cookie保存功能
- 💾 支持自动登录
- 🗑️ 支持一键清除Cookie
- 👥 支持多账号Cookie管理
- ⏰ 支持过期Cookie检测

---

**享受免登录的便捷体验！** 🎉
