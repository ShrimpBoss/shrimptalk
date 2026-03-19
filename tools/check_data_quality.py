#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查涨停数据的日期连续性和文字异常
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# 目录
DIR_2026 = Path("/home/terrence/.openclaw/workspace/data/limitup/2026")
DIR_2025 = Path("/home/terrence/.openclaw/workspace/data/limitup/2025")
OUTPUT_DIR = Path("/home/terrence/.openclaw/workspace/data/limitup")

def parse_date_from_content(content):
    """从文件内容中提取日期"""
    first_line = content.split('\n')[0]
    
    # 匹配 [1.22 星期四] 格式（简化版）
    match = re.search(r'\[(\d+)\.(\d+)', first_line)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        # 根据内容判断年份（1-3 月 = 2026，其他 = 2025）
        if month <= 3:
            year = 2026
        else:
            year = 2025
        try:
            return datetime(year, month, day)
        except:
            return None
    return None

def check_text_quality(content, filename):
    """检查文字质量"""
    issues = []
    
    # 检查是否包含常见关键字
    if '涨停' not in content:
        issues.append('缺少"涨停"关键字')
    if '连板' not in content and '市场连板' not in content:
        issues.append('缺少"连板"信息')
    
    # 检查是否有乱码
    if '\x00' in content or '' in content:
        issues.append('包含乱码')
    
    # 检查文件是否过短
    if len(content) < 500:
        issues.append(f'文件过短 ({len(content)}字)')
    
    # 检查是否有表格格式
    if '|' not in content and '代码' not in content:
        issues.append('缺少表格数据')
    
    return issues

def check_year_2026():
    """检查 2026 年数据"""
    print("=" * 60)
    print("📊 2026 年数据检查")
    print("=" * 60)
    
    files = sorted([f for f in os.listdir(DIR_2026) if f.endswith('.txt')])
    print(f"\n文件总数：{len(files)}个")
    
    # 解析日期
    data = {}
    missing_dates = []
    abnormal_files = []
    
    for f in files:
        filepath = DIR_2026 / f
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        date = parse_date_from_content(content)
        issues = check_text_quality(content, f)
        
        if date:
            data[date] = {'file': f, 'content': content}
            if issues:
                abnormal_files.append((f, date, issues))
        else:
            missing_dates.append(f)
    
    # 检查日期连续性 (1 月 22 日 - 3 月 19 日)
    start_date = datetime(2026, 1, 22)
    end_date = datetime(2026, 3, 19)
    
    missing_trading_days = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 周一到周五
            if current not in data:
                missing_trading_days.append(current)
        current += timedelta(days=1)
    
    # 输出结果
    print(f"\n解析到日期：{len(data)}个")
    print(f"无法解析日期的文件：{len(missing_dates)}个")
    for f in missing_dates[:10]:
        print(f"  - {f}")
    
    print(f"\n缺失的交易日：{len(missing_trading_days)}天")
    for d in missing_trading_days[:20]:
        print(f"  - {d.strftime('%Y-%m-%d')} ({d.strftime('%a')})")
    if len(missing_trading_days) > 20:
        print(f"  ... 还有{len(missing_trading_days)-20}天")
    
    print(f"\n文字异常文件：{len(abnormal_files)}个")
    for f, date, issues in abnormal_files:
        print(f"  - {f} ({date.strftime('%Y-%m-%d') if date else '未知日期'}): {', '.join(issues)}")
    
    return data, missing_trading_days, abnormal_files

def check_year_2025():
    """检查 2025 年数据"""
    print("\n" + "=" * 60)
    print("📊 2025 年数据检查")
    print("=" * 60)
    
    files = sorted([f for f in os.listdir(DIR_2025) if f.endswith('.txt')])
    print(f"\n文件总数：{len(files)}个")
    
    # 解析日期
    data = {}
    missing_dates = []
    abnormal_files = []
    
    for f in files:
        filepath = DIR_2025 / f
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            date = parse_date_from_content(content)
            issues = check_text_quality(content, f)
            
            if date:
                data[date] = {'file': f, 'content': content}
                if issues:
                    abnormal_files.append((f, date, issues))
            else:
                missing_dates.append(f)
        except Exception as e:
            missing_dates.append(f"❌ {f} ({e})")
    
    # 输出结果
    print(f"\n解析到日期：{len(data)}个")
    print(f"无法解析日期的文件：{len(missing_dates)}个")
    for f in missing_dates[:10]:
        print(f"  - {f}")
    if len(missing_dates) > 10:
        print(f"  ... 还有{len(missing_dates)-10}个")
    
    print(f"\n文字异常文件：{len(abnormal_files)}个")
    for f, date, issues in abnormal_files[:20]:
        print(f"  - {f} ({date.strftime('%Y-%m-%d')}): {', '.join(issues)}")
    if len(abnormal_files) > 20:
        print(f"  ... 还有{len(abnormal_files)-20}个")
    
    # 检查日期范围
    if data:
        min_date = min(data.keys())
        max_date = max(data.keys())
        print(f"\n日期范围：{min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
    
    return data, missing_dates, abnormal_files

def main():
    # 检查 2026 年
    data_2026, missing_2026, abnormal_2026 = check_year_2026()
    
    # 检查 2025 年
    data_2025, missing_2025, abnormal_2025 = check_year_2025()
    
    # 生成报告
    print("\n" + "=" * 60)
    print("📋 检查报告总结")
    print("=" * 60)
    
    report = f"""
# 🔍 涨停数据质量检查报告

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 2026 年数据

| 项目 | 数量 |
|------|------|
| 文件总数 | {len(data_2026) + len(missing_2026)}个 |
| 成功解析日期 | {len(data_2026)}个 |
| 无法解析日期 | {len(missing_2026)}个 |
| 缺失交易日 | {len(missing_2026)}天 |
| 文字异常 | {len(abnormal_2026)}个 |

---

## 📊 2025 年数据

| 项目 | 数量 |
|------|------|
| 文件总数 | {len(data_2025) + len(missing_2025)}个 |
| 成功解析日期 | {len(data_2025)}个 |
| 无法解析日期 | {len(missing_2025)}个 |
| 文字异常 | {len(abnormal_2025)}个 |

---

## ⚠️ 主要问题

### 2026 年缺失交易日
"""
    
    for d in missing_2026[:20]:
        report += f"- {d.strftime('%Y-%m-%d')} ({d.strftime('%A')})\n"
    
    report += f"""
### 2026 年文字异常
"""
    for f, date, issues in abnormal_2026[:10]:
        report += f"- {f}: {', '.join(issues)}\n"
    
    report += f"""
### 2025 年无法解析日期
"""
    for f in missing_2025[:20]:
        report += f"- {f}\n"
    if len(missing_2025) > 20:
        report += f"- ... 还有{len(missing_2025)-20}个\n"
    
    report += f"""
### 2025 年文字异常
"""
    for f, date, issues in abnormal_2025[:20]:
        report += f"- {f} ({date.strftime('%Y-%m-%d')}): {', '.join(issues)}\n"
    if len(abnormal_2025) > 20:
        report += f"- ... 还有{len(abnormal_2025)-20}个\n"
    
    # 保存报告
    report_file = OUTPUT_DIR / "数据质量检查报告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存到：{report_file}")

if __name__ == "__main__":
    main()
