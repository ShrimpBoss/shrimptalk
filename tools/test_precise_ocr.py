#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确识别涨停连板表（第一段）
"""

import requests
import base64
import json

API_KEY = "sk-561f772674114910bbf9702d77c8cae1"
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
MODEL = "qwen-vl-plus"

image_path = "/home/terrence/Desktop/龙虾demo/segment_0.jpg"

# 读取图片
with open(image_path, "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

# 更精确的 prompt
prompt = """
请精确识别这张涨停连板表格图片。

【表格结构】
这是一个股票涨停数据表格，包含以下列（从左到右）：
1. 连板高度（如 4 板、3 板、2 板）
2. 股票名称
3. 股票代码（6 位数字）
4. 涨停时间（如 09:25）
5. 涨停原因/概念

【要求】
1. 严格按照表格中的视觉位置识别，不要推测
2. 股票代码必须是 6 位数字
3. 连板高度是数字（1-10）
4. 如果某列看不清，写"未知"

【返回格式】
只返回 JSON 数组，格式如下：
[
  {"lianban": "4", "name": "东贝集团", "code": "601956", "time": "09:25", "reason": "机器人"},
  {"lianban": "3", "name": "华银电力", "code": "600744", "time": "09:25", "reason": "绿色电力"}
]
"""

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

print("正在识别 segment_0.jpg（涨停连板表）...")
response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
result = response.json()

content = result["choices"][0]["message"]["content"]
print(f"\nAI 回复:\n{content}")

# 解析 JSON
if "```json" in content:
    json_str = content.split("```json")[1].split("```")[0]
else:
    json_str = content

data = json.loads(json_str)
print(f"\n识别结果：{len(data)} 只股票")
for stock in data:
    print(f"{stock.get('lianban','?')}板 | {stock.get('name','?'):<10} {stock.get('code','?'):<8} {stock.get('time','?'):<8} {stock.get('reason','?')}")
