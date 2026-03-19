#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 驱动的涨停表格 OCR 工具
========================
使用通义千问 VL（多模态大模型）识别涨停/炸板表格图片
输出结构化 Excel/CSV 数据

作者：虾老板
日期：2026-03-19

支持识别：
- 涨停池表格（连板股、首板股）
- 炸板池表格
- 任意格式的涨停统计图片
- 公众号/网站/APP 截图

输出：
- 标准 Excel 文件（可直接追加到宝哥的情绪监控表）
- CSV 文件
- 连板梯队文本
"""

import os
import json
import base64
import requests
from datetime import datetime
from pathlib import Path

# ==================== 配置区 ====================

# 输出目录（独立存储，不污染原始数据）
OUTPUT_DIR = Path("/home/terrence/.openclaw/workspace/data/emotion")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 通义千问 VL API 配置
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")  # 需要配置
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
MODEL = "qwen-vl-max"  # 通义千问 VL 最强模型

# ==================== 工具函数 ====================

def image_to_base64(image_path: str) -> str:
    """将图片转换为 base64 编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def call_qwen_vl(image_path: str, prompt: str) -> dict:
    """调用通义千问 VL API 识别图片"""
    if not API_KEY:
        raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")
    
    image_base64 = image_to_base64(image_path)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:image/png;base64,{image_base64}"},
                        {"text": prompt}
                    ]
                }
            ]
        },
        "parameters": {
            "response_format": "json"  # 强制 JSON 输出
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    return result

# ==================== 核心识别功能 ====================

PROMPT_ZT_TABLE = """
请识别这张涨停股票表格图片，提取每只股票的以下信息：

【必填字段】
- 股票名称（如"三房巷"）
- 股票代码（如"600370"）
- 连板高度（如"5 板"，如果是首板写"1"）
- 涨停时间（如"09:25:00"）
- 涨停原因/所属板块（如"化学纤维"）
- 封单金额（如"1.2 亿"，如果没有写 null）
- 开板次数（如"9 次"，如果是一字板写"0"）

【要求】
1. 以 JSON 格式返回，不要有任何多余文字
2. 不要遗漏任何一行数据
3. 如果某个字段无法识别，写 null
4. 股票代码保持 6 位数字格式

【返回格式示例】
{
    "date": "2026-03-19",
    "stocks": [
        {
            "name": "三房巷",
            "code": "600370",
            "continuous_limit": 5,
            "limit_time": "09:25:00",
            "reason": "化学纤维",
            "order_amount": "1.2 亿",
            "open_count": 9
        }
    ]
}
"""

PROMPT_ZB_TABLE = """
请识别这张炸板股票表格图片，提取每只股票的以下信息：

【必填字段】
- 股票名称（如"泸天化"）
- 股票代码（如"000912"）
- 最高涨幅（如"+10%"，涨停价）
- 收盘涨幅（如"-10.05%"，如果跌停写"-10%"）
- 炸板时间（如"10:30"）
- 所属板块（如"化肥"）

【要求】
1. 以 JSON 格式返回，不要有任何多余文字
2. 不要遗漏任何一行数据
3. 如果某个字段无法识别，写 null

【返回格式示例】
{
    "date": "2026-03-19",
    "stocks": [
        {
            "name": "泸天化",
            "code": "000912",
            "max_change": "+10%",
            "close_change": "-10.05%",
            "broken_time": "10:30",
            "sector": "化肥"
        }
    ]
}
"""

def recognize_limit_up_table(image_path: str) -> dict:
    """识别涨停表格"""
    print(f"🔍 识别涨停表格：{image_path}")
    result = call_qwen_vl(image_path, PROMPT_ZT_TABLE)
    return result

def recognize_broken_table(image_path: str) -> dict:
    """识别炸板表格"""
    print(f"🔍 识别炸板表格：{image_path}")
    result = call_qwen_vl(image_path, PROMPT_ZB_TABLE)
    return result

# ==================== 数据导出 ====================

def export_to_excel(data: dict, output_path: str):
    """导出为 Excel 文件"""
    import pandas as pd
    
    df = pd.DataFrame(data.get("stocks", []))
    df.insert(0, "识别日期", data.get("date", datetime.now().strftime("%Y-%m-%d")))
    
    # 保存
    df.to_excel(output_path, index=False)
    print(f"✅ 已保存到：{output_path}")
    return df

def export_to_csv(data: dict, output_path: str):
    """导出为 CSV 文件"""
    import pandas as pd
    
    df = pd.DataFrame(data.get("stocks", []))
    df.insert(0, "识别日期", data.get("date", datetime.now().strftime("%Y-%m-%d")))
    
    # 保存
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ 已保存到：{output_path}")
    return df

# ==================== 主流程 ====================

def process_image(image_path: str, table_type: str = "limit_up"):
    """
    处理单张图片
    
    Args:
        image_path: 图片路径
        table_type: "limit_up" 涨停表 / "broken" 炸板表
    """
    print(f"\n{'='*50}")
    print(f"🦐 虾老板 AI-OCR 涨停表格识别工具")
    print(f"{'='*50}\n")
    
    # 选择 prompt
    if table_type == "limit_up":
        result = recognize_limit_up_table(image_path)
    else:
        result = recognize_broken_table(image_path)
    
    # 解析结果
    try:
        # 从 API 响应中提取 JSON
        content = result["output"]["choices"][0]["message"]["content"]
        # 尝试解析 JSON
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        else:
            json_str = content
        data = json.loads(json_str)
    except Exception as e:
        print(f"❌ 解析失败：{e}")
        print(f"原始响应：{content}")
        return None
    
    # 导出
    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    base_name = f"zt-{date_str}" if table_type == "limit_up" else f"zb-{date_str}"
    
    export_to_excel(data, OUTPUT_DIR / f"{base_name}.xlsx")
    export_to_csv(data, OUTPUT_DIR / f"{base_name}.csv")
    
    # 打印统计
    stock_count = len(data.get("stocks", []))
    print(f"\n📊 识别结果：共 {stock_count} 只股票")
    
    return data

# ==================== CLI 入口 ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python ai_ocr_zt_table.py <图片路径> [limit_up|broken]")
        print("示例：python ai_ocr_zt_table.py /path/to/zt_table.png limit_up")
        sys.exit(1)
    
    image_path = sys.argv[1]
    table_type = sys.argv[2] if len(sys.argv) > 2 else "limit_up"
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在：{image_path}")
        sys.exit(1)
    
    process_image(image_path, table_type)
