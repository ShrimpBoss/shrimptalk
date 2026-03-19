#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理涨停数据，找出缺失和不正常的
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# 目录
DIR = Path("/home/terrence/Desktop/龙虾demo/涨停")
OUTPUT_DIR = Path("/home/terrence/.openclaw/workspace/data/limitup")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_date_from_content(content, filename):
    """从文件内容中提取日期"""
    # 获取第一行
    first_line = content.split('\n')[0]
    
    # 匹配 [1.22 星期四] 格式
    match = re.search(r'\[(\d+)\.(\d+)', first_line)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        year = 2026  # 默认 2026 年
        try:
            return datetime(year, month, day)
        except:
            return None
    return None

def parse_stats(content):
    """从内容中提取统计数据"""
    stats = {}
    
    # 涨停金额
    match = re.search(r'涨停金额[:：]?\s*(\d+)亿', content)
    if match:
        stats['涨停金额'] = int(match.group(1))
    
    # 炸板金额
    match = re.search(r'炸板金额[:：]?\s*(\d+)亿', content)
    if match:
        stats['炸板金额'] = int(match.group(1))
    
    # 涨停家数
    match = re.search(r'涨停\s*(\d+)家', content)
    if match:
        stats['涨停家数'] = int(match.group(1))
    
    # 炸板家数
    match = re.search(r'炸板\s*(\d+)家', content)
    if match:
        stats['炸板家数'] = int(match.group(1))
    
    # 跌停家数
    match = re.search(r'跌停\s*(\d+)家', content)
    if match:
        stats['跌停家数'] = int(match.group(1))
    
    # 连板家数
    match = re.search(r'连板\s*(\d+)家', content)
    if match:
        stats['连板家数'] = int(match.group(1))
    
    return stats

def main():
    # 获取所有 2026 年文件（不带 (1) 的）
    files_2026 = []
    files_2025 = []
    
    for f in DIR.glob("*.txt"):
        if "(1)" in f.name:
            files_2025.append(f)
        else:
            files_2026.append(f)
    
    print(f"2026 年文件：{len(files_2026)}个")
    print(f"2025 年文件：{len(files_2025)}个")
    
    # 解析 2026 年数据
    data_2026 = {}
    missing_files = []
    
    for i in range(1, 205):  # 1-204
        filename = f"image_{i:03d}.txt"
        filepath = DIR / filename
        
        if not filepath.exists():
            missing_files.append(i)
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        date = parse_date_from_content(content, filename)
        stats = parse_stats(content)
        
        if date:
            data_2026[date] = {
                'file': i,
                'stats': stats,
                'content': content[:500]  # 前 500 字
            }
    
    print(f"\n解析到 {len(data_2026)} 个日期")
    print(f"缺失文件编号：{missing_files}")
    
    # 检查日期连续性（1 月 22 日到 3 月 19 日）
    start_date = datetime(2026, 1, 22)
    end_date = datetime(2026, 3, 19)
    
    missing_dates = []
    abnormal_data = []
    
    current = start_date
    while current <= end_date:
        # 跳过周末
        if current.weekday() < 5:  # 周一到周五
            if current not in data_2026:
                missing_dates.append(current)
            else:
                # 检查数据是否异常
                stats = data_2026[current]['stats']
                if stats.get('涨停家数', 0) < 10:
                    abnormal_data.append((current, '涨停家数过少', stats.get('涨停家数')))
                if stats.get('涨停家数', 0) > 100:
                    abnormal_data.append((current, '涨停家数过多', stats.get('涨停家数')))
                if stats.get('炸板家数', 0) > 50:
                    abnormal_data.append((current, '炸板家数过多', stats.get('炸板家数')))
        current += timedelta(days=1)
    
    # 输出结果
    print(f"\n=== 缺失的交易日 ===")
    for d in missing_dates:
        print(f"{d.strftime('%Y-%m-%d')} ({d.strftime('%A')})")
    
    print(f"\n=== 异常数据 ===")
    for date, reason, value in abnormal_data:
        print(f"{date.strftime('%Y-%m-%d')}: {reason} ({value})")
    
    # 保存整理后的数据
    output_file = OUTPUT_DIR / "limitup_2026_summary.csv"
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        f.write("日期，文件编号，涨停金额，炸板金额，涨停家数，炸板家数，跌停家数，连板家数\n")
        for date in sorted(data_2026.keys()):
            info = data_2026[date]
            stats = info['stats']
            f.write(f"{date.strftime('%Y-%m-%d')},{info['file']},")
            f.write(f"{stats.get('涨停金额', '')},{stats.get('炸板金额', '')},")
            f.write(f"{stats.get('涨停家数', '')},{stats.get('炸板家数', '')},")
            f.write(f"{stats.get('跌停家数', '')},{stats.get('连板家数', '')}\n")
    
    print(f"\n✅ 已保存到：{output_file}")

if __name__ == "__main__":
    main()
