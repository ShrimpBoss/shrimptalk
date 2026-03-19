#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量识别涨停表格图片（所有 segment）
"""

import os
import json
import base64
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# API 配置
API_KEY = "sk-561f772674114910bbf9702d77c8cae1"
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen-vl-plus"

# 输出目录
OUTPUT_DIR = Path("/home/terrence/.openclaw/workspace/data/emotion")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_ZT = """
请识别这张涨停股票表格图片，提取每只股票的以下信息：

【必填字段】
- 股票名称（如"三房巷"）
- 股票代码（如"600370"）
- 连板高度（数字，如 5 表示 5 板，首板写 1）
- 涨停时间（如"09:25:00"）
- 涨停原因/所属板块（如"化学纤维"）

【要求】
1. 以 JSON 格式返回
2. 不要遗漏任何一行数据
3. 如果某个字段无法识别，写 null

【返回格式】
{
    "date": "2025-04-28",
    "stocks": [
        {"name": "东贝集团", "code": "601956", "continuous_limit": 4, "limit_time": "09:25", "reason": "机器人"}
    ]
}
"""

PROMPT_ZB = """
请识别这张炸板股票表格图片，提取每只股票的以下信息：

【必填字段】
- 股票名称
- 股票代码
- 最高涨幅（如"+10%"）
- 收盘涨幅（如"-10.05%"）
- 所属板块

【要求】
1. 以 JSON 格式返回
2. 不要遗漏任何一行数据

【返回格式】
{
    "date": "2025-04-28",
    "stocks": [
        {"name": "泸天化", "code": "000912", "max_change": "+10%", "close_change": "-10.05%", "sector": "化肥"}
    ]
}
"""

def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def call_api(image_path, prompt):
    img_base64 = image_to_base64(image_path)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}},
                {"type": "text", "text": prompt}
            ]
        }],
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    
    # 解析 JSON
    if "```json" in content:
        json_str = content.split("```json")[1].split("```")[0]
    else:
        json_str = content
    
    return json.loads(json_str)

def process_all_segments():
    img_dir = Path("/home/terrence/Desktop/龙虾demo")
    
    all_stocks_zt = []
    all_stocks_zb = []
    detected_date = None
    
    # 处理涨停 segment
    print("=== 识别涨停数据 ===")
    for i in range(5):
        seg_file = img_dir / f"segment_{i}.jpg"
        if not seg_file.exists():
            print(f"跳过：{seg_file} 不存在")
            continue
        
        print(f"处理 segment_{i}.jpg ...", end=" ", flush=True)
        try:
            data = call_api(seg_file, PROMPT_ZT)
            stocks = data.get("stocks", [])
            all_stocks_zt.extend(stocks)
            if data.get("date") and not detected_date:
                detected_date = data["date"]
            print(f"识别 {len(stocks)} 只")
        except Exception as e:
            print(f"失败：{e}")
    
    # 处理炸板 segment（如果有的话）
    print("\n=== 识别炸板数据 ===")
    for i in range(5):
        seg_file = img_dir / f"segment_zb_{i}.jpg"
        if not seg_file.exists():
            continue
        
        print(f"处理 segment_zb_{i}.jpg ...", end=" ", flush=True)
        try:
            data = call_api(seg_file, PROMPT_ZB)
            stocks = data.get("stocks", [])
            all_stocks_zb.extend(stocks)
            print(f"识别 {len(stocks)} 只")
        except Exception as e:
            print(f"失败：{e}")
    
    # 保存结果
    if not detected_date:
        detected_date = "2025-04-28"  # 默认
    
    print(f"\n=== 保存结果 ===")
    print(f"涨停股：{len(all_stocks_zt)} 只")
    print(f"炸板股：{len(all_stocks_zb)} 只")
    
    # 保存涨停数据
    if all_stocks_zt:
        df_zt = pd.DataFrame(all_stocks_zt)
        df_zt.insert(0, "识别日期", detected_date)
        df_zt.to_excel(OUTPUT_DIR / f"zt-{detected_date}-full.xlsx", index=False)
        df_zt.to_csv(OUTPUT_DIR / f"zt-{detected_date}-full.csv", index=False, encoding="utf-8-sig")
        print(f"✅ 涨停数据已保存：zt-{detected_date}-full.xlsx")
    
    # 保存炸板数据
    if all_stocks_zb:
        df_zb = pd.DataFrame(all_stocks_zb)
        df_zb.insert(0, "识别日期", detected_date)
        df_zb.to_excel(OUTPUT_DIR / f"zb-{detected_date}.xlsx", index=False)
        df_zb.to_csv(OUTPUT_DIR / f"zb-{detected_date}.csv", index=False, encoding="utf-8-sig")
        print(f"✅ 炸板数据已保存：zb-{detected_date}.xlsx")
    
    # 打印统计
    if all_stocks_zt:
        print(f"\n=== 涨停统计 ===")
        print(f"连板高度分布:")
        for h in sorted(df_zt['continuous_limit'].unique(), reverse=True):
            count = len(df_zt[df_zt['continuous_limit']==h])
            print(f"  {h}板：{count}只")
        
        print(f"\n涨停原因 TOP5:")
        for reason, count in df_zt['reason'].value_counts().head(5).items():
            print(f"  {reason}: {count}只")

if __name__ == "__main__":
    process_all_segments()
