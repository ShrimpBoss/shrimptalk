#!/bin/bash
# 飞书机器人自动配置脚本
# 使用：./setup-feishu.sh

set -e

echo "🤖 飞书机器人配置脚本"
echo "===================="
echo ""

# 创建目录
BOT_DIR="$HOME/.openclaw/workspace/feishu-bot"
mkdir -p "$BOT_DIR"

echo "📁 工作目录：$BOT_DIR"
echo ""

# 提示用户输入 Webhook
echo "请输入飞书机器人 Webhook 地址："
echo "（在飞书群组 → 设置 → 群机器人 → 自定义机器人 → 获取）"
read -p "Webhook URL: " WEBHOOK_URL

# 提示是否启用签名
echo ""
echo "是否启用签名校验？（推荐）"
echo "1) 是，启用签名校验"
echo "2) 否，暂不启用"
read -p "选择 [1/2]: " ENABLE_SIGN

SECRET=""
if [ "$ENABLE_SIGN" = "1" ]; then
    echo ""
    echo "请输入签名 Secret（在机器人配置页面复制）："
    read -p "Secret: " SECRET
fi

# 创建 .env 文件
echo ""
echo "📝 创建配置文件..."

cat > "$BOT_DIR/.env" << EOF
# 飞书机器人配置
# ⚠️ 不要提交到 Git！

FEISHU_WEBHOOK_URL=$WEBHOOK_URL
EOF

if [ -n "$SECRET" ]; then
    echo "FEISHU_SECRET=$SECRET" >> "$BOT_DIR/.env"
    echo "✅ 签名已配置"
fi

# 设置文件权限
chmod 600 "$BOT_DIR/.env"
echo "✅ 配置文件权限已设置（仅所有者可读写）"

# 创建测试脚本
echo ""
echo "📝 创建测试脚本..."

cat > "$BOT_DIR/test_feishu.py" << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import hashlib
import hmac
import base64
import time
import json
import requests
from dotenv import load_dotenv
import os
from pathlib import Path

# 加载环境变量
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

WEBHOOK_URL = os.getenv('FEISHU_WEBHOOK_URL')
SECRET = os.getenv('FEISHU_SECRET')

def gen_sign(timestamp, secret):
    """生成签名"""
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign

def send_message(text, sign=False):
    """发送消息到飞书"""
    timestamp = str(int(time.time()))
    
    data = {
        'msg_type': 'text',
        'content': {
            'text': text
        }
    }
    
    if sign and SECRET:
        data['timestamp'] = timestamp
        data['sign'] = gen_sign(timestamp, SECRET)
    
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        result = response.json()
        
        if result.get('code') == 0 or result.get('StatusCode') == 0 or result.get('msg') == 'success':
            print('✅ 发送成功！')
            return True
        else:
            print(f'❌ 发送失败：{json.dumps(result, ensure_ascii=False)}')
            return False
    except Exception as e:
        print(f'❌ 请求错误：{e}')
        return False

if __name__ == '__main__':
    print('🧪 测试飞书机器人...')
    print('')
    
    # 测试 1：简单消息
    print('测试 1: 发送简单消息...')
    send_message('🤖 Dashboard 测试消息', sign=bool(SECRET))
    print('')
    
    # 测试 2：带格式消息
    print('测试 2: 发送格式化消息...')
    test_msg = '''📊 Dashboard 测试报告

✅ 系统状态：正常
📈 今日数据：
  - GMV: $1,234
  - 订单：45 单
  - 利润：$487

时间：''' + time.strftime('%Y-%m-%d %H:%M:%S')
    
    send_message(test_msg, sign=bool(SECRET))
    print('')
    
    print('✅ 测试完成！请查看飞书群组消息。')
PYTHON_SCRIPT

chmod +x "$BOT_DIR/test_feishu.py"
echo "✅ 测试脚本已创建"

# 创建 Python 依赖文件
cat > "$BOT_DIR/requirements.txt" << EOF
requests>=2.28.0
python-dotenv>=1.0.0
EOF

echo "✅ 依赖文件已创建"

# 安装依赖
echo ""
echo "📦 安装 Python 依赖..."
if command -v pip3 &> /dev/null; then
    pip3 install -r "$BOT_DIR/requirements.txt"
    echo "✅ 依赖已安装"
else
    echo "⚠️ 未找到 pip3，请手动安装依赖："
    echo "   pip3 install requests python-dotenv"
fi

# 创建 Dashboard 集成代码
echo ""
echo "📝 创建 Dashboard 集成代码..."

cat > "$BOT_DIR/feishu_integration.js" << 'JS_CODE'
/**
 * 飞书通知集成模块
 * 用于 Dashboard 后端
 */

const crypto = require('crypto');

class FeishuNotifier {
  constructor() {
    this.webhookUrl = process.env.FEISHU_WEBHOOK_URL;
    this.secret = process.env.FEISHU_SECRET;
  }

  /**
   * 生成签名
   */
  genSign(timestamp, secret) {
    const stringToSign = `${timestamp}\n${secret}`;
    const hmac = crypto.createHmac('sha256', stringToSign);
    hmac.update('');
    return hmac.digest('base64');
  }

  /**
   * 发送消息
   */
  async send(message, options = {}) {
    if (!this.webhookUrl) {
      console.error('❌ 未配置 FEISHU_WEBHOOK_URL');
      return false;
    }

    const timestamp = String(Math.floor(Date.now() / 1000));
    
    const data = {
      msg_type: options.msgType || 'text',
      content: options.content || { text: message }
    };

    // 添加签名
    if (this.secret) {
      data.timestamp = timestamp;
      data.sign = this.genSign(timestamp, this.secret);
    }

    try {
      const response = await fetch(this.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const result = await response.json();
      
      if (result.code === 0 || result.StatusCode === 0 || result.msg === 'success') {
        console.log('✅ 飞书通知已发送');
        return true;
      } else {
        console.error('❌ 飞书通知失败:', result);
        return false;
      }
    } catch (error) {
      console.error('❌ 飞书通知异常:', error);
      return false;
    }
  }

  /**
   * 发送文本消息
   */
  async sendText(text) {
    return this.send(text, { msgType: 'text', content: { text } });
  }

  /**
   * 发送富文本消息
   */
  async sendPost(title, content) {
    return this.send(null, {
      msgType: 'post',
      content: {
        post: {
          zh_cn: {
            title,
            content
          }
        }
      }
    });
  }

  /**
   * 发送建议完成通知
   */
  async notifySuggestionCompleted(suggestion) {
    const text = `✅ 建议已完成

标题：${suggestion.title}
负责人：${suggestion.assignee}
反馈：${suggestion.feedback || '无'}`;

    return this.sendText(text);
  }

  /**
   * 发送日报
   */
  async sendDailyReport(metrics) {
    return this.sendPost('📊 Dashboard 日报', [
      [
        { tag: 'text', text: `日期：${new Date().toLocaleDateString('zh-CN')}\n` },
        { tag: 'text', text: `GMV: $${metrics.gmv}\n` },
        { tag: 'text', text: `订单：${metrics.orders}单\n` },
        { tag: 'text', text: `利润：$${metrics.profit}\n` },
        { tag: 'text', text: `ROAS: ${metrics.roas}` }
      ]
    ]);
  }

  /**
   * 发送告警
   */
  async sendAlert(title, message) {
    const text = `🚨 ${title}\n\n${message}\n\n<at user_id="all"></at>`;
    return this.sendText(text);
  }
}

module.exports = FeishuNotifier;
JS_CODE

echo "✅ Dashboard 集成代码已创建"

# 创建使用说明
cat > "$BOT_DIR/README.md" << EOF
# 飞书机器人集成

## 快速开始

### 1. 测试飞书机器人
\`\`\`bash
cd $BOT_DIR
python3 test_feishu.py
\`\`\`

### 2. 集成到 Dashboard

在 \`dashboard-website/backend/server.js\` 中引入：

\`\`\`javascript
const FeishuNotifier = require('../feishu-bot/feishu_integration');
const notifier = new FeishuNotifier();

// 使用示例
await notifier.sendText('测试消息');
await notifier.notifySuggestionCompleted(suggestion);
\`\`\`

## 配置文件

\`.env\` 文件包含敏感信息，请勿提交到 Git！

## 消息类型

- 文本消息：\`sendText(text)\`
- 富文本消息：\`sendPost(title, content)\`
- 建议完成：\`notifySuggestionCompleted(suggestion)\`
- 日报：\`sendDailyReport(metrics)\`
- 告警：\`sendAlert(title, message)\`
EOF

echo "✅ 使用说明已创建"

# 完成
echo ""
echo "===================="
echo "✅ 配置完成！"
echo ""
echo "📁 文件位置：$BOT_DIR"
echo "   - .env (配置文件)"
echo "   - test_feishu.py (测试脚本)"
echo "   - feishu_integration.js (Dashboard 集成)"
echo "   - requirements.txt (Python 依赖)"
echo "   - README.md (使用说明)"
echo ""
echo "🧪 下一步：运行测试"
echo "   cd $BOT_DIR"
echo "   python3 test_feishu.py"
echo ""
echo "📚 查看详细说明："
echo "   cat $BOT_DIR/README.md"
echo ""
