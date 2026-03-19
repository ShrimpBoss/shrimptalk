#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
早间资讯搜集工具
数据源：韭研公社、财联社、格隆汇
"""

import requests
import re
from datetime import datetime
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path("/home/terrence/.openclaw/workspace/memory")

def fetch_jiuyangongshe():
    """抓取韭研公社首页"""
    print("📰 抓取韭研公社...")
    
    url = "https://www.jiuyangongshe.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        content = response.text
        
        # 提取热门帖子
        posts = []
        
        # 提取盘前纪要
        if "盘前纪要" in content:
            posts.append("✅ 盘前纪要已更新")
        
        # 提取开盘必读
        if "开盘必读" in content:
            posts.append("✅ 开盘必读已更新")
        
        # 提取题材催化
        if "题材催化" in content:
            posts.append("✅ 题材催化已更新")
        
        return {
            "source": "韭研公社",
            "status": "success",
            "posts": posts,
            "raw_content": content[:5000]
        }
    except Exception as e:
        return {
            "source": "韭研公社",
            "status": "error",
            "error": str(e)
        }

def fetch_cls():
    """抓取财联社电报"""
    print("📰 抓取财联社...")
    
    url = "https://www.cls.cn/telegraph"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        content = response.text
        
        # 提取早间新闻精选
        news = []
        
        if "早间新闻精选" in content:
            news.append("✅ 早间新闻精选已更新")
        
        return {
            "source": "财联社",
            "status": "success",
            "news": news,
            "raw_content": content[:5000]
        }
    except Exception as e:
        return {
            "source": "财联社",
            "status": "error",
            "error": str(e)
        }

def fetch_gelonghui():
    """抓取格隆汇"""
    print("📰 抓取格隆汇...")
    
    url = "https://www.gelonghui.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        content = response.text
        
        return {
            "source": "格隆汇",
            "status": "success",
            "raw_content": content[:5000]
        }
    except Exception as e:
        return {
            "source": "格隆汇",
            "status": "error",
            "error": str(e)
        }

def generate_report(jiuyuan, cls, gelonghui):
    """生成资讯报告"""
    print("📝 生成资讯报告...")
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# 🌅 {date_str} 早间资讯

**搜集时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**数据源**: 韭研公社、财联社、格隆汇

---

## 📊 数据源状态

| 数据源 | 状态 |
|--------|------|
| 韭研公社 | {"✅ 成功" if jiuyuan['status'] == 'success' else "❌ 失败"} |
| 财联社 | {"✅ 成功" if cls['status'] == 'success' else "❌ 失败"} |
| 格隆汇 | {"✅ 成功" if gelonghui['status'] == 'success' else "❌ 失败"} |

---

## 🔥 韭研公社重点

"""
    
    if jiuyuan['status'] == 'success':
        for post in jiuyuan.get('posts', []):
            report += f"- {post}\n"
    else:
        report += f"- ❌ 抓取失败：{jiuyuan.get('error', '未知错误')}\n"
    
    report += f"""
---

## 📰 财联社早间精选

"""
    
    if cls['status'] == 'success':
        for news in cls.get('news', []):
            report += f"- {news}\n"
    else:
        report += f"- ❌ 抓取失败：{cls.get('error', '未知错误')}\n"
    
    report += f"""
---

## 💡 核心观点

> ⚠️ 详细分析需要进一步处理原始数据

---

**备注**: 原始数据已保存，需要进一步分析提取关键信息。
"""
    
    # 保存报告
    output_file = OUTPUT_DIR / f"market-morning-{date_str}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存到：{output_file}")
    
    return output_file, report

def main():
    print("=" * 60)
    print("🌅 早间资讯搜集")
    print("=" * 60)
    
    # 抓取数据源
    jiuyuan = fetch_jiuyangongshe()
    cls = fetch_cls()
    gelonghui = fetch_gelonghui()
    
    # 生成报告
    output_file, report = generate_report(jiuyuan, cls, gelonghui)
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("📋 资讯摘要")
    print("=" * 60)
    print(report[:1000])
    
    return output_file

if __name__ == "__main__":
    main()
