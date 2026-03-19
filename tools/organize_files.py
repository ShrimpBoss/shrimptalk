#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理涨停数据文件 - 按年份分类
"""

import os
import re
import shutil
from pathlib import Path

# 源目录
SRC_DIR = "/home/terrence/Desktop/涨停"
# 目标目录
BASE_DIR = Path("/home/terrence/.openclaw/workspace/data/limitup")
DIR_2026 = BASE_DIR / "2026"
DIR_2025 = BASE_DIR / "2025"

# 创建目录
DIR_2026.mkdir(parents=True, exist_ok=True)
DIR_2025.mkdir(parents=True, exist_ok=True)

def get_file_number(filename):
    """从文件名中提取编号"""
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def main():
    # 获取所有 txt 文件
    files = [f for f in os.listdir(SRC_DIR) if f.endswith('.txt')]
    print(f"找到 {len(files)} 个 txt 文件")
    
    # 分类
    files_2026 = []
    files_2025 = []
    
    for f in files:
        num = get_file_number(f)
        if num is None:
            files_2025.append(f)
        elif num <= 40:
            files_2026.append(f)
        else:
            files_2025.append(f)
    
    print(f"2026 年文件：{len(files_2026)}个")
    print(f"2025 年文件：{len(files_2025)}个")
    
    # 复制 2026 年文件
    print(f"\n复制 2026 年文件到 {DIR_2026}...")
    for f in sorted(files_2026, key=lambda x: get_file_number(x) or 0):
        src = os.path.join(SRC_DIR, f)
        dst = DIR_2026 / f
        shutil.copy2(src, dst)
    print(f"✅ 已复制 {len(files_2026)} 个文件")
    
    # 复制 2025 年文件
    print(f"\n复制 2025 年文件到 {DIR_2025}...")
    for f in sorted(files_2025, key=lambda x: get_file_number(x) or 0):
        src = os.path.join(SRC_DIR, f)
        dst = DIR_2025 / f
        shutil.copy2(src, dst)
    print(f"✅ 已复制 {len(files_2025)} 个文件")
    
    # 生成文件清单
    print(f"\n生成文件清单...")
    
    # 2026 年清单
    with open(BASE_DIR / "2026_文件清单.txt", 'w', encoding='utf-8') as f:
        f.write("2026 年涨停数据文件清单 (1-40 号)\n")
        f.write("=" * 50 + "\n\n")
        for i, file in enumerate(sorted(files_2026, key=lambda x: get_file_number(x) or 0), 1):
            num = get_file_number(file)
            f.write(f"{i:3d}. {file} (编号{num})\n")
    
    # 2025 年清单
    with open(BASE_DIR / "2025_文件清单.txt", 'w', encoding='utf-8') as f:
        f.write("2025 年涨停数据文件清单 (41 号以上 + 带 (1) 的)\n")
        f.write("=" * 50 + "\n\n")
        for i, file in enumerate(sorted(files_2025, key=lambda x: get_file_number(x) or 0), 1):
            num = get_file_number(file)
            f.write(f"{i:3d}. {file} (编号{num})\n")
    
    print(f"✅ 已生成文件清单")
    
    # 统计
    print(f"\n{'='*50}")
    print("📊 整理完成统计")
    print(f"{'='*50}")
    print(f"2026 年目录：{DIR_2026}")
    print(f"  - 文件数：{len(files_2026)}个")
    print(f"  - 编号范围：1-40")
    print(f"\n2025 年目录：{DIR_2025}")
    print(f"  - 文件数：{len(files_2025)}个")
    print(f"  - 编号范围：41-204 + 带 (1) 的")
    print(f"\n文件清单：")
    print(f"  - {BASE_DIR / '2026_文件清单.txt'}")
    print(f"  - {BASE_DIR / '2025_文件清单.txt'}")

if __name__ == "__main__":
    main()
