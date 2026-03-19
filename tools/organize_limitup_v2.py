#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新整理涨停数据 - 正确区分 2025 和 2026 年
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# 目录
DIR = Path("/mnt/shared/龙虾 demo/涨停")
OUTPUT_DIR = Path("/home/terrence/.openclaw/workspace/data/limitup")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def parse_date_from_content(content, filename):
    """从文件内容中提取日期"""
    first_line = content.split('\n')[0]
    
    # 匹配 [1.22 星期四] 格式
    match = re.search(r'\[(\d+)\.(\d+)', first_line)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        
        # 根据文件名判断年份
        # 1-40 号 = 2026 年，41 号以上 = 2025 年
        file_num = int(re.search(r'(\d+)', filename).group(1))
        year = 2026 if file_num <= 40 else 2025
        
        try:
            return datetime(year, month, day)
        except:
            return None
    return None

def parse_stats(content):
    """从内容中提取统计数据"""
    stats = {}
    
    # 涨停金额
    match = re.search(r'涨停金额 [:：]?\s*(\d+)亿', content)
    if match:
        stats['涨停金额'] = int(match.group(1))
    
    # 炸板金额
    match = re.search(r'炸板金额 [:：]?\s*(\d+)亿', content)
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
    # 分类文件
    files_2026 = []  # 1-40 号
    files_2025 = []  # 41 号以上 + 带 (1) 的
    
    for f in DIR.glob("*.txt"):
        if "(1)" in f.name:
            files_2025.append(f)
        else:
            # 提取文件编号
            match = re.search(r'(\d+)', f.name)
            if match:
                num = int(match.group(1))
                if num <= 40:
                    files_2026.append(f)
                else:
                    files_2025.append(f)
    
    print(f"2026 年文件：{len(files_2026)}个 (1-40 号)")
    print(f"2025 年文件：{len(files_2025)}个 (41 号以上 + 带 (1) 的)")
    
    # 解析 2026 年数据
    data_2026 = {}
    missing_2026 = []
    
    for i in range(1, 41):
        filename = f"image_{i:03d}.txt"
        filepath = DIR / filename
        
        if not filepath.exists():
            missing_2026.append(i)
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        date = parse_date_from_content(content, filename)
        stats = parse_stats(content)
        
        if date:
            data_2026[date] = {
                'file': i,
                'stats': stats,
                'content': content[:500]
            }
    
    print(f"\n2026 年解析到 {len(data_2026)} 个日期")
    print(f"2026 年缺失文件编号：{missing_2026}")
    
    # 检查 2026 年日期连续性 (1 月 22 日 - 3 月 19 日)
    start_date = datetime(2026, 1, 22)
    end_date = datetime(2026, 3, 19)
    
    missing_dates_2026 = []
    abnormal_2026 = []
    
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 周一到周五
            if current not in data_2026:
                missing_dates_2026.append(current)
            else:
                stats = data_2026[current]['stats']
                if stats.get('涨停家数', 0) < 20:
                    abnormal_2026.append((current, '涨停家数过少', stats.get('涨停家数')))
                if stats.get('涨停家数', 0) > 100:
                    abnormal_2026.append((current, '涨停家数过多', stats.get('涨停家数')))
                if stats.get('炸板家数', 0) > 50:
                    abnormal_2026.append((current, '炸板家数过多', stats.get('炸板家数')))
        current += timedelta(days=1)
    
    # 输出 2026 年结果
    print(f"\n{'='*50}")
    print("📊 2026 年数据整理结果")
    print(f"{'='*50}")
    print(f"\n缺失的交易日 ({len(missing_dates_2026)}天):")
    for d in missing_dates_2026[:20]:
        print(f"  {d.strftime('%Y-%m-%d')} ({d.strftime('%a')})")
    if len(missing_dates_2026) > 20:
        print(f"  ... 还有{len(missing_dates_2026)-20}天")
    
    print(f"\n异常数据 ({len(abnormal_2026)}条):")
    for date, reason, value in abnormal_2026:
        print(f"  {date.strftime('%Y-%m-%d')}: {reason} ({value})")
    
    # 保存 2026 年数据
    output_2026 = OUTPUT_DIR / "limitup_2026.csv"
    with open(output_2026, 'w', encoding='utf-8-sig') as f:
        f.write("日期，文件编号，涨停金额，炸板金额，涨停家数，炸板家数，跌停家数，连板家数\n")
        for date in sorted(data_2026.keys()):
            info = data_2026[date]
            stats = info['stats']
            f.write(f"{date.strftime('%Y-%m-%d')},{info['file']},")
            f.write(f"{stats.get('涨停金额', '')},{stats.get('炸板金额', '')},")
            f.write(f"{stats.get('涨停家数', '')},{stats.get('炸板家数', '')},")
            f.write(f"{stats.get('跌停家数', '')},{stats.get('连板家数', '')}\n")
    
    print(f"\n✅ 2026 年数据已保存到：{output_2026}")
    
    # 简单统计 2025 年
    data_2025_count = 0
    for f in files_2025:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        date = parse_date_from_content(content, f.name)
        if date and date.year == 2025:
            data_2025_count += 1
    
    print(f"\n2025 年文件解析到 {data_2025_count} 个有效日期")

if __name__ == "__main__":
    main()
