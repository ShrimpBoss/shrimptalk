#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日工作日志邮件发送脚本
发送 HTML 格式的每日工作日志到指定邮箱
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# 邮件配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465  # SSL
SENDER_EMAIL = "noreply@openclaw.local"  # 发件人（模拟）
SENDER_PASSWORD = os.environ.get("SMTP_PASSWORD", "")  # 从环境变量获取密码
RECEIVER_EMAIL = "1958405595@qq.com"

# 报告文件路径
REPORT_FILE = "/home/terrence/.openclaw/workspace/daily-report-2026-03-14.html"

def read_html_report(filepath):
    """读取 HTML 报告内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def send_email():
    """发送 HTML 邮件"""
    print(f"📧 准备发送每日工作日志到 {RECEIVER_EMAIL}...")
    
    # 读取 HTML 内容
    html_content = read_html_report(REPORT_FILE)
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"📊 每日工作日志 - 2026 年 3 月 14 日（星期六）"
    msg['From'] = f"Agent 团队工作日志系统 <{SENDER_EMAIL}>"
    msg['To'] = RECEIVER_EMAIL
    
    # 添加纯文本版本（备用）
    text_content = """
尊敬的李总：

您好！以下是 2026 年 3 月 13 日的每日工作日志摘要：

【团队整体表现】
- 总任务完成：31 项
- 平均效率：94%
- 异常数量：0 起
- 客户好评率：99%
- 总体评级：⭐⭐⭐⭐⭐ (优秀)

【核心业绩指标】
- GMV: $1,456 (↑ +18.0%)
- 订单数：52 单 (↑ +15.6%)
- 净利润：$578 (↑ +18.7%)
- ROAS: 3.4 (↑ +6.3%)

【选品进展】
- 今日选品：18 款
- 待审核：1 款
- 通过率：94%

【营销投放】
- 广告花费：$178
- ROAS: 3.4 (超目标 3.0)
- 转化次数：89

【安全状态】
- 系统状态：🟢 正常
- CPU: 35% | 内存：62% | 磁盘：45%
- 安全事件：0 起

【今日重点】
1. 清空待处理订单（2 单）
2. 清空客服待回复（5 条）
3. 清空仓储待发货（3 单）
4. 完成产品审核（1 款）

详细报告请查看附件 HTML 文件。

祝工作顺利！

Agent 团队工作日志系统
2026 年 3 月 13 日 08:00
    """
    
    # 添加纯文本和 HTML 版本
    part1 = MIMEText(text_content, 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(part1)
    msg.attach(part2)
    
    # 添加 HTML 附件
    try:
        with open(REPORT_FILE, 'rb') as f:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename="每日工作日志 -2026-03-14.html"
            )
            msg.attach(attachment)
        print("✅ 附件已添加")
    except Exception as e:
        print(f"⚠️ 附件添加失败：{e}")
    
    # 尝试发送邮件
    try:
        # 检查是否有 SMTP 配置
        if not SENDER_PASSWORD:
            print("\n⚠️  SMTP 密码未配置，无法实际发送邮件")
            print("\n📋 邮件已准备就绪，配置 SMTP 后即可发送：")
            print(f"   - SMTP 服务器：{SMTP_SERVER}:{SMTP_PORT}")
            print(f"   - 发件人：{SENDER_EMAIL}")
            print(f"   - 收件人：{RECEIVER_EMAIL}")
            print(f"   - 主题：{msg['Subject']}")
            print(f"   - 报告文件：{REPORT_FILE}")
            print("\n💡 配置方法：")
            print("   1. 设置环境变量：export SMTP_PASSWORD='your_password'")
            print("   2. 或者修改脚本中的 SMTP 配置")
            print("   3. 重新运行此脚本")
            
            # 保存邮件到文件以便后续发送
            email_file = "/home/terrence/.openclaw/workspace/email-draft-2026-03-13.eml"
            with open(email_file, 'w', encoding='utf-8') as f:
                f.write(msg.as_string())
            print(f"\n💾 邮件草稿已保存到：{email_file}")
            return False
        
        # 连接 SMTP 服务器并发送
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件发送成功！")
        print(f"   收件人：{RECEIVER_EMAIL}")
        print(f"   主题：{msg['Subject']}")
        print(f"   时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP 认证失败，请检查邮箱账号和密码")
        return False
    except smtplib.SMTPConnectError:
        print(f"❌ 无法连接到 SMTP 服务器 {SMTP_SERVER}:{SMTP_PORT}")
        return False
    except Exception as e:
        print(f"❌ 发送失败：{e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📊 Agent 团队每日工作日志邮件发送系统")
    print("=" * 60)
    print()
    
    # 检查报告文件
    if not os.path.exists(REPORT_FILE):
        print(f"❌ 报告文件不存在：{REPORT_FILE}")
        exit(1)
    
    print(f"✅ 报告文件已找到：{REPORT_FILE}")
    print(f"   文件大小：{os.path.getsize(REPORT_FILE)} 字节")
    print()
    
    # 发送邮件
    success = send_email()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 邮件发送完成！")
    else:
        print("⚠️  邮件未发送（配置待完善）")
    print("=" * 60)
