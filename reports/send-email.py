#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日工作日志邮件发送脚本
发送 HTML 报告到李总邮箱
"""

import smtplib
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# 配置
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.qq.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RECIPIENT_EMAIL = '1958405595@qq.com'

# 报告文件
REPORT_DATE = '2026-03-11'
REPORT_HTML_PATH = f'/home/terrence/.openclaw/workspace/reports/daily-report-email-{REPORT_DATE}.html'

def send_email():
    """发送 HTML 邮件"""
    
    # 检查 SMTP 配置
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ 错误：SMTP 配置缺失")
        print("\n需要配置以下环境变量:")
        print("  export SENDER_EMAIL=your-qq-number@qq.com")
        print("  export SENDER_PASSWORD=your-authorization-code")
        print("\nQQ 邮箱授权码获取方法:")
        print("  1. 登录 QQ 邮箱网页版")
        print("  2. 设置 → 账户")
        print("  3. 开启 POP3/SMTP 服务")
        print("  4. 生成授权码（不是登录密码）")
        return False
    
    # 检查报告文件
    if not os.path.exists(REPORT_HTML_PATH):
        print(f"❌ 错误：报告文件不存在 {REPORT_HTML_PATH}")
        return False
    
    try:
        # 读取 HTML 内容
        with open(REPORT_HTML_PATH, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'📊 每日工作日志 - {REPORT_DATE}'
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        
        # 添加 HTML 内容
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # 发送邮件
        print(f"📧 正在发送邮件到 {RECIPIENT_EMAIL}...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(0)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        
        print("✅ 邮件发送成功！")
        print(f"   收件人：{RECIPIENT_EMAIL}")
        print(f"   主题：📊 每日工作日志 - {REPORT_DATE}")
        print(f"   发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ 错误：SMTP 认证失败")
        print("   请检查 SENDER_EMAIL 和 SENDER_PASSWORD 是否正确")
        print("   QQ 邮箱需要使用授权码，不是登录密码")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ 错误：SMTP 错误 - {e}")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    success = send_email()
    sys.exit(0 if success else 1)
