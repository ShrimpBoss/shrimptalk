#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据文件内容日期和文件编号推理
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

def main():
    print("=" * 70)
    print("📅 根据文件内容日期推理")
    print("=" * 70)
    
    # 获取所有文件及其日期
    files_data = []
    for f in sorted(os.listdir(DIR_2026)):
        if not f.endswith('.txt'):
            continue
        
        filepath = DIR_2026 / f
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        date = parse_date_from_content(content)
        file_num = int(re.search(r'(\d+)', f).group(1))
        
        files_data.append({
            'file': f,
            'num': file_num,
            'date': date
        })
    
    # 按日期排序
    files_by_date = sorted([f for f in files_data if f['date']], key=lambda x: x['date'])
    
    print(f"\n总文件数：{len(files_data)}个")
    print(f"有日期的文件：{len(files_by_date)}个")
    
    # 打印按日期排序的文件
    print(f"\n{'='*70}")
    print("📋 按日期排序的文件")
    print(f"{'='*70}")
    print(f"\n{'序号':<6} {'文件编号':<12} {'日期':<12} {'星期':<8} {'与前一天的间隔':<12}")
    print("-" * 70)
    
    missing_dates = []
    prev_date = None
    
    for i, data in enumerate(files_by_date, 1):
        date = data['date']
        file_num = data['num']
        file_name = data['file']
        
        # 计算与前一天的间隔
        if prev_date:
            gap = (date - prev_date).days
            if gap == 1:
                gap_str = "连续"
            elif gap <= 3:
                gap_str = f"+{gap}天"
                # 找出缺失的日期
                current = prev_date + timedelta(days=1)
                while current < date:
                    if current.weekday() < 5:  # 工作日
                        missing_dates.append(current)
                    current += timedelta(days=1)
            else:
                gap_str = f"+{gap}天 (周末/节假日)"
        else:
            gap_str = "-"
        
        print(f"{i:<6} image_{file_num:03d}.txt   {date.strftime('%Y-%m-%d')}   {date.strftime('%a'):<8} {gap_str:<12}")
        
        prev_date = date
    
    # 总结
    print(f"\n{'='*70}")
    print("📊 推理结果")
    print(f"{'='*70}")
    
    if files_by_date:
        min_date = files_by_date[0]['date']
        max_date = files_by_date[-1]['date']
        print(f"\n日期范围：{min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
        print(f"总天数：{(max_date - min_date).days + 1}天")
        print(f"有数据的天数：{len(files_by_date)}天")
    
    # 计算交易日
    trading_days = 0
    current = min_date
    while current <= max_date:
        if current.weekday() < 5:
            trading_days += 1
        current += timedelta(days=1)
    
    print(f"\n交易日总数：{trading_days}天")
    print(f"有数据的交易日：{len(files_by_date)}天")
    print(f"缺失的交易日：{trading_days - len(files_by_date)}天")
    
    if missing_dates:
        print(f"\n❌ 缺失的交易日 ({len(missing_dates)}天):")
        for d in missing_dates:
            print(f"  {d.strftime('%Y-%m-%d')} ({d.strftime('%A')})")
    
    # 文件编号与日期的关系
    print(f"\n{'='*70}")
    print("📋 文件编号与日期的对应关系")
    print(f"{'='*70}")
    
    # 按文件编号排序
    files_by_num = sorted(files_by_date, key=lambda x: x['num'])
    
    print(f"\n{'文件编号':<12} {'日期':<12} {'星期':<10} {'备注':<20}")
    print("-" * 70)
    
    for data in files_by_num:
        num = data['num']
        date = data['date']
        
        # 检查是否有异常
        remark = ""
        if num <= 10 and date.month > 2:
            remark = "⚠️ 编号小但日期晚"
        elif num >= 30 and date.month == 1:
            remark = "⚠️ 编号大但日期早"
        
        print(f"image_{num:03d}.txt   {date.strftime('%Y-%m-%d')}   {date.strftime('%a'):<10} {remark:<20}")

if __name__ == "__main__":
    main()
