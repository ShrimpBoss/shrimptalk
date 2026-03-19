#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量识别 Excel 中的所有涨停/炸板图片
"""

import openpyxl
import requests
import base64
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import io
from PIL import Image

# API 配置
API_KEY = "sk-561f772674114910bbf9702d77c8cae1"
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen-vl-plus"

# 输入输出
INPUT_FILE = "/home/terrence/Desktop/龙虾demo/20250428.xlsx"
OUTPUT_DIR = Path("/home/terrence/.openclaw/workspace/data/emotion")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT = """
请识别这张股票涨停数据图片，提取以下信息：
- 股票名称
- 股票代码（6 位数字）
- 连板高度（数字）
- 涨停时间
- 涨停原因

返回 JSON 数组格式：
[{"name":"股票名","code":"000001","lianban":3,"time":"09:25","reason":"概念"}]
只返回 JSON，不要其他文字。
"""

def image_to_base64(img):
    """PIL Image 转 base64"""
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return base64.b64encode(buffer.getvalue()).decode()

def call_api(img_pil):
    """调用通义千问 VL 识别"""
    img_base64 = image_to_base64(img_pil)
    
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
                {"type": "text", "text": PROMPT}
            ]
        }],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # 清理 JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        
        return json.loads(content)
    except Exception as e:
        print(f"识别失败：{e}")
        return []

def main():
    print(f"🦐 批量识别工具启动")
    print(f"输入文件：{INPUT_FILE}")
    print(f"输出目录：{OUTPUT_DIR}\n")
    
    # 打开 Excel
    wb = openpyxl.load_workbook(INPUT_FILE)
    ws = wb.active
    
    print(f"工作表中的图片数量：{len(ws._images)}\n")
    
    all_stocks = []
    
    # 批量处理所有图片
    for i, img_obj in enumerate(ws._images):
        if (i + 1) % 10 == 0:
            print(f"已处理 {i+1}/{len(ws._images)} 张...")
        
        try:
            # 提取图片数据
            img_data = img_obj._data()
            img_pil = Image.open(io.BytesIO(img_data))
            
            # 识别
            stocks = call_api(img_pil)
            
            # 添加到结果
            for stock in stocks:
                if isinstance(stock, dict) and stock.get('name'):
                    stock['source_img'] = i + 1
                    all_stocks.append(stock)
        
        except Exception as e:
            print(f"图片{i+1}处理失败：{e}")
    
    print(f"\n=== 识别完成 ===")
    print(f"共识别 {len(all_stocks)} 只股票")
    
    # 保存结果
    if all_stocks:
        df = pd.DataFrame(all_stocks)
        df.insert(0, '识别日期', '2025-04-28')
        
        # 保存
        output_file = OUTPUT_DIR / "2025-04-28-allstocks.xlsx"
        df.to_excel(output_file, index=False)
        print(f"✅ 已保存：{output_file}")
        
        # 统计
        print(f"\n=== 连板统计 ===")
        if 'lianban' in df.columns:
            for h in sorted(df['lianban'].unique(), reverse=True):
                count = len(df[df['lianban']==h])
                if count > 0:
                    print(f"  {h}板：{count}只")
        
        print(f"\n=== 涨停原因 TOP10 ===")
        if 'reason' in df.columns:
            for reason, count in df['reason'].value_counts().head(10).items():
                print(f"  {reason}: {count}只")

if __name__ == "__main__":
    main()
