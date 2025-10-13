// 淘宝直播评论机器人 - 浏览器插件版本
// 仅供学习研究使用，请遵守相关法律法规

class TaobaoLiveBotExtension {
    constructor() {
        this.isRunning = false;
        this.commentQueue = [];
        this.autoComments = [
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
        ];
        
        this.replyRules = {
            '价格': ['价格很实惠哦！', '性价比超高！', '现在有优惠活动！'],
            '多少钱': ['价格很实惠哦！', '性价比超高！', '现在有优惠活动！'],
            '质量': ['质量绝对保证！', '用料很好的！', '品质没问题！'],
            '怎么样': ['质量绝对保证！', '用料很好的！', '品质没问题！'],
            '发货': ['发货很快的！', '包邮哦！', '今天下单明天发货！'],
            '快递': ['发货很快的！', '包邮哦！', '今天下单明天发货！'],
            '尺寸': ['有详细尺寸表的！', '可以看商品详情！', '客服会帮您推荐！'],
            '大小': ['有详细尺寸表的！', '可以看商品详情！', '客服会帮您推荐！'],
            '颜色': ['有多种颜色可选！', '都很好看的！', '可以看直播展示！'],
            '优惠': ['现在有活动！', '直播间有专属优惠！', '限时特价！'],
            '便宜': ['现在有活动！', '直播间有专属优惠！', '限时特价！'],
            '好看': ['谢谢夸奖！', '确实很好看！', '您眼光真好！'],
            '漂亮': ['谢谢夸奖！', '确实很好看！', '您眼光真好！']
        };
        
        this.init();
    }
    
    init() {
        console.log('🤖 淘宝直播评论机器人已加载');
        this.createControlPanel();
        this.startMonitoring();
    }
    
    createControlPanel() {
        // 创建控制面板
        const panel = document.createElement('div');
        panel.id = 'live-bot-panel';
        panel.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 300px;
            background: #fff;
            border: 2px solid #ff6600;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            font-family: Arial, sans-serif;
            font-size: 14px;
        `;
        
        panel.innerHTML = `
            <div style="text-align: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #ff6600;">🤖 直播评论机器人</h3>
            </div>
            
            <div style="margin-bottom: 10px;">
                <label>
                    <input type="checkbox" id="auto-comment-toggle"> 自动评论
                </label>
                <span style="margin-left: 10px;">间隔: 
                    <input type="number" id="comment-interval" value="8" min="3" max="30" style="width: 50px;">秒
                </span>
            </div>
            
            <div style="margin-bottom: 10px;">
                <label>
                    <input type="checkbox" id="auto-reply-toggle" checked> 智能回复
                </label>
            </div>
            
            <div style="margin-bottom: 10px;">
                <label>
                    <input type="checkbox" id="gift-thanks-toggle" checked> 礼物感谢
                </label>
            </div>
            
            <div style="margin-bottom: 15px;">
                <textarea id="custom-comments" placeholder="自定义评论内容，每行一条" 
                    style="width: 100%; height: 80px; resize: vertical;">${this.autoComments.join('\n')}</textarea>
            </div>
            
            <div style="text-align: center;">
                <button id="start-bot" style="background: #ff6600; color: white; border: none; padding: 8px 20px; border-radius: 5px; cursor: pointer;">启动机器人</button>
                <button id="stop-bot" style="background: #ccc; color: white; border: none; padding: 8px 20px; border-radius: 5px; cursor: pointer; margin-left: 10px;" disabled>停止机器人</button>
            </div>
            
            <div id="bot-status" style="margin-top: 10px; padding: 8px; background: #f0f0f0; border-radius: 5px; text-align: center;">
                状态: 未启动
            </div>
            
            <div style="margin-top: 10px; font-size: 12px; color: #666; text-align: center;">
                仅供学习研究使用
            </div>
        `;
        
        document.body.appendChild(panel);
        
        // 绑定事件
        document.getElementById('start-bot').onclick = () => this.startBot();
        document.getElementById('stop-bot').onclick = () => this.stopBot();
        
        // 拖拽功能
        this.makeDraggable(panel);
    }
    
    makeDraggable(element) {
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        element.onmousedown = dragMouseDown;
        
        function dragMouseDown(e) {
            e = e || window.event;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
        }
        
        function elementDrag(e) {
            e = e || window.event;
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            element.style.top = (element.offsetTop - pos2) + "px";
            element.style.left = (element.offsetLeft - pos1) + "px";
        }
        
        function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
        }
    }
    
    startBot() {
        this.isRunning = true;
        
        // 更新UI
        document.getElementById('start-bot').disabled = true;
        document.getElementById('stop-bot').disabled = false;
        document.getElementById('bot-status').innerHTML = '状态: <span style="color: green;">运行中</span>';
        
        // 获取设置
        const autoComment = document.getElementById('auto-comment-toggle').checked;
        const autoReply = document.getElementById('auto-reply-toggle').checked;
        const giftThanks = document.getElementById('gift-thanks-toggle').checked;
        const interval = parseInt(document.getElementById('comment-interval').value) * 1000;
        
        // 更新自定义评论
        const customComments = document.getElementById('custom-comments').value.split('\n').filter(c => c.trim());
        if (customComments.length > 0) {
            this.autoComments = customComments;
        }
        
        console.log('🚀 机器人已启动');
        
        // 启动自动评论
        if (autoComment) {
            this.startAutoComment(interval);
        }
        
        // 启动评论发送器
        this.startCommentSender();
    }
    
    stopBot() {
        this.isRunning = false;
        
        // 更新UI
        document.getElementById('start-bot').disabled = false;
        document.getElementById('stop-bot').disabled = true;
        document.getElementById('bot-status').innerHTML = '状态: <span style="color: red;">已停止</span>';
        
        console.log('⏹️ 机器人已停止');
    }
    
    startMonitoring() {
        // 监听页面上的新评论
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) {
                            this.handleNewNode(node);
                        }
                    });
                }
            });
        });
        
        // 观察评论区
        const commentSelectors = [
            '.comment-list',
            '.live-comment-list', 
            '.message-list',
            '.chat-list',
            '.danmu-list'
        ];
        
        commentSelectors.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                observer.observe(element, { childList: true, subtree: true });
                console.log(`📡 开始监控: ${selector}`);
            }
        });
        
        // 如果没找到评论区，监控整个body
        if (!commentSelectors.some(s => document.querySelector(s))) {
            observer.observe(document.body, { childList: true, subtree: true });
            console.log('📡 开始监控整个页面');
        }
    }
    
    handleNewNode(node) {
        if (!this.isRunning) return;
        
        // 检查是否是评论节点
        const commentText = this.extractCommentText(node);
        if (commentText) {
            console.log(`[新评论] ${commentText}`);
            this.handleComment(commentText);
        }
        
        // 检查是否是礼物节点
        const giftInfo = this.extractGiftInfo(node);
        if (giftInfo) {
            console.log(`[礼物] ${giftInfo.username} 送出了 ${giftInfo.giftName}`);
            this.handleGift(giftInfo);
        }
    }
    
    extractCommentText(node) {
        // 尝试从不同的结构中提取评论文本
        const selectors = [
            '.comment-content',
            '.message-content',
            '.chat-content',
            '.danmu-content'
        ];
        
        for (let selector of selectors) {
            const element = node.querySelector ? node.querySelector(selector) : null;
            if (element && element.textContent) {
                return element.textContent.trim();
            }
        }
        
        // 如果没有找到特定选择器，检查节点本身
        if (node.textContent && node.textContent.length > 0 && node.textContent.length < 200) {
            // 过滤掉一些明显不是评论的内容
            const text = node.textContent.trim();
            if (!text.includes('http') && !text.includes('www') && text.length > 2) {
                return text;
            }
        }
        
        return null;
    }
    
    extractGiftInfo(node) {
        // 尝试提取礼物信息
        const text = node.textContent || '';
        
        // 匹配礼物相关的文本模式
        const giftPatterns = [
            /(.+?)送出了(.+)/,
            /(.+?)打赏了(.+)/,
            /(.+?)赠送(.+)/
        ];
        
        for (let pattern of giftPatterns) {
            const match = text.match(pattern);
            if (match) {
                return {
                    username: match[1].trim(),
                    giftName: match[2].trim()
                };
            }
        }
        
        return null;
    }
    
    handleComment(commentText) {
        if (!document.getElementById('auto-reply-toggle').checked) return;
        
        // 根据关键词自动回复
        for (let keyword in this.replyRules) {
            if (commentText.includes(keyword)) {
                const replies = this.replyRules[keyword];
                const reply = replies[Math.floor(Math.random() * replies.length)];
                this.addCommentToQueue(reply);
                break;
            }
        }
    }
    
    handleGift(giftInfo) {
        if (!document.getElementById('gift-thanks-toggle').checked) return;
        
        const thankMessages = [
            `感谢${giftInfo.username}的${giftInfo.giftName}！`,
            `谢谢${giftInfo.username}！`,
            `${giftInfo.username}太棒了！`,
            '感谢支持！'
        ];
        
        const message = thankMessages[Math.floor(Math.random() * thankMessages.length)];
        this.addCommentToQueue(message);
    }
    
    addCommentToQueue(comment) {
        this.commentQueue.push(comment);
        console.log(`📝 添加到队列: ${comment}`);
    }
    
    startAutoComment(interval) {
        if (!this.isRunning) return;
        
        const sendRandomComment = () => {
            if (!this.isRunning) return;
            
            const comment = this.autoComments[Math.floor(Math.random() * this.autoComments.length)];
            this.addCommentToQueue(comment);
            
            // 随机间隔 (±20%)
            const randomInterval = interval + (Math.random() - 0.5) * interval * 0.4;
            setTimeout(sendRandomComment, randomInterval);
        };
        
        // 延迟开始，避免立即发送
        setTimeout(sendRandomComment, Math.random() * interval);
    }
    
    startCommentSender() {
        const sendComment = () => {
            if (!this.isRunning) {
                setTimeout(sendComment, 1000);
                return;
            }
            
            if (this.commentQueue.length > 0) {
                const comment = this.commentQueue.shift();
                this.sendCommentToLiveRoom(comment);
            }
            
            // 每2-5秒检查一次队列
            const delay = 2000 + Math.random() * 3000;
            setTimeout(sendComment, delay);
        };
        
        sendComment();
    }
    
    sendCommentToLiveRoom(comment) {
        // 查找评论输入框
        const inputSelectors = [
            '.comment-input input',
            'input[placeholder*="说点什么"]',
            'textarea[placeholder*="说点什么"]',
            '.live-comment-input input',
            '.comment-box input',
            '#comment-input',
            'input[type="text"]'
        ];
        
        let inputElement = null;
        for (let selector of inputSelectors) {
            inputElement = document.querySelector(selector);
            if (inputElement) break;
        }
        
        if (!inputElement) {
            console.log('❌ 未找到评论输入框');
            return false;
        }
        
        // 模拟人工输入
        inputElement.focus();
        inputElement.value = '';
        
        // 逐字输入，模拟打字效果
        let i = 0;
        const typeChar = () => {
            if (i < comment.length) {
                inputElement.value += comment[i];
                inputElement.dispatchEvent(new Event('input', { bubbles: true }));
                i++;
                setTimeout(typeChar, 50 + Math.random() * 100);
            } else {
                // 输入完成，发送评论
                setTimeout(() => {
                    this.submitComment(inputElement);
                }, 200 + Math.random() * 300);
            }
        };
        
        typeChar();
    }
    
    submitComment(inputElement) {
        // 查找发送按钮
        const sendSelectors = [
            '.comment-send',
            'button:contains("发送")',
            'button:contains("发表")',
            '.send-btn',
            '.comment-submit',
            'button[type="submit"]'
        ];
        
        let sendButton = null;
        for (let selector of sendSelectors) {
            if (selector.includes('contains')) {
                // 处理包含文本的选择器
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.includes('发送') || btn.textContent.includes('发表')) {
                        sendButton = btn;
                        break;
                    }
                }
            } else {
                sendButton = document.querySelector(selector);
            }
            if (sendButton) break;
        }
        
        if (sendButton) {
            sendButton.click();
            console.log(`✅ 发送评论: ${inputElement.value}`);
        } else {
            // 如果没找到发送按钮，尝试按回车
            inputElement.dispatchEvent(new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                bubbles: true
            }));
            console.log(`✅ 发送评论(回车): ${inputElement.value}`);
        }
    }
}

// 检查是否在淘宝直播页面
if (window.location.hostname.includes('taobao.com') || 
    window.location.hostname.includes('tmall.com') ||
    window.location.href.includes('live')) {
    
    // 等待页面加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new TaobaoLiveBotExtension();
        });
    } else {
        new TaobaoLiveBotExtension();
    }
}

// 导出给其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TaobaoLiveBotExtension;
}
