#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据文件序号和交易日推理缺失的日期
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

DIR_2026 = Path("/home/terrence/.openclaw/workspace/data/limitup/2026")

def parse_date_from_content(content):
    """从文件内容中提取日期"""
    first_line = content.split('\n')[0]
    match = re.search(r'\[(\d+)\.(\d+)', first_line)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        if month <= 3:
            year = 2026
        else:
            year = 2025
        try:
            return datetime(year, month, day)
        except:
            return None
    return None

def get_trading_days(start, end):
    """获取交易日（排除周末）"""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:  # 周一到周五
            days.append(current)
        current += timedelta(days=1)
    return days

def main():
    print("=" * 70)
    print("📅 根据文件序号推理交易日")
    print("=" * 70)
    
    # 获取所有文件
    files = sorted([f for f in os.listdir(DIR_2026) if f.endswith('.txt')])
    
    # 解析已知日期
    known_dates = {}
    for f in files:
        filepath = DIR_2026 / f
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        date = parse_date_from_content(content)
        if date:
            # 提取文件编号
            match = re.search(r'(\d+)', f)
            if match:
                num = int(match.group(1))
                known_dates[num] = date
    
    print(f"\n已知日期的文件：{len(known_dates)}个")
    for num in sorted(known_dates.keys())[:10]:
        print(f"  image_{num:03d}.txt -> {known_dates[num].strftime('%Y-%m-%d')} ({known_dates[num].strftime('%a')})")
    
    # 推理起始日期
    # image_001.txt = 2026-01-22 (周四)
    start_date = datetime(2026, 1, 22)
    
    # 生成交易日序列
    trading_days = get_trading_days(start_date, datetime(2026, 3, 19))
    
    print(f"\n从 2026-01-22 到 2026-03-19 共有 {len(trading_days)} 个交易日")
    
    # 推理每个文件编号对应的日期
    print(f"\n{'='*70}")
    print("📋 文件编号与交易日对应关系")
    print(f"{'='*70}")
    print(f"\n{'序号':<6} {'推理日期':<12} {'实际日期':<12} {'状态':<10}")
    print("-" * 70)
    
    missing_files = []
    date_mismatch = []
    
    for i, trading_day in enumerate(trading_days, 1):
        file_num = i
        inferred_date = trading_day
        
        # 检查是否有实际日期
        if file_num in known_dates:
            actual_date = known_dates[file_num]
            if inferred_date == actual_date:
                status = "✅ 匹配"
            else:
                status = f"⚠️ 不匹配"
                date_mismatch.append((file_num, inferred_date, actual_date))
        else:
            actual_date = None
            status = "❌ 缺失"
            missing_files.append((file_num, inferred_date))
        
        if actual_date:
            print(f"{file_num:<6} {inferred_date.strftime('%Y-%m-%d'):<12} {actual_date.strftime('%Y-%m-%d'):<12} {status:<10}")
        else:
            print(f"{file_num:<6} {inferred_date.strftime('%Y-%m-%d'):<12} {'-':<12} {status:<10}")
    
    # 总结
    print(f"\n{'='*70}")
    print("📊 推理结果总结")
    print(f"{'='*70}")
    print(f"\n交易日总数：{len(trading_days)}天")
    print(f"匹配的文件：{len(known_dates)}个")
    print(f"缺失的文件：{len(missing_files)}个")
    print(f"日期不匹配：{len(date_mismatch)}个")
    
    if missing_files:
        print(f"\n❌ 缺失的文件:")
        for num, date in missing_files[:20]:
            print(f"  image_{num:03d}.txt -> {date.strftime('%Y-%m-%d')} ({date.strftime('%a')})")
    
    if date_mismatch:
        print(f"\n⚠️ 日期不匹配的文件:")
        for num, inferred, actual in date_mismatch:
            print(f"  image_{num:03d}.txt: 推理{inferred.strftime('%Y-%m-%d')}, 实际{actual.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()
