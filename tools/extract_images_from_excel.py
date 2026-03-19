#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Excel 中提取所有图片并保存
"""

import openpyxl
from pathlib import Path
import io
from PIL import Image

# 输入输出
INPUT_FILE = "/home/terrence/Desktop/龙虾demo/20250428.xlsx"
OUTPUT_DIR = Path("/home/terrence/Desktop/龙虾demo/extracted_images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"🦐 开始提取图片")
print(f"输入文件：{INPUT_FILE}")
print(f"输出目录：{OUTPUT_DIR}\n")

# 打开 Excel
wb = openpyxl.load_workbook(INPUT_FILE)
ws = wb.active

print(f"工作表中的图片数量：{len(ws._images)}\n")

# 提取所有图片
for i, img_obj in enumerate(ws._images):
    try:
        # 提取图片数据
        img_data = img_obj._data()
        
        # 保存为 JPG（处理 RGBA 格式）
        img_pil = Image.open(io.BytesIO(img_data))
        
        # RGBA 转 RGB
        if img_pil.mode == 'RGBA':
            img_pil = img_pil.convert('RGB')
        
        output_file = OUTPUT_DIR / f"image_{i+1:03d}.jpg"
        img_pil.save(output_file, 'JPEG', quality=90)
        
        print(f"✅ {i+1}/{len(ws._images)} - {output_file.name} ({img_pil.size[0]}x{img_pil.size[1]})")
    
    except Exception as e:
        print(f"❌ {i+1} 失败：{e}")

print(f"\n✅ 提取完成！共 {len(list(OUTPUT_DIR.glob('*.jpg')))} 张图片")
print(f"目录：{OUTPUT_DIR}")
