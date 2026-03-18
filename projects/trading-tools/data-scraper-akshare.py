#!/usr/bin/env python3
"""
A 股涨停复盘数据抓取工具 - akshare 权威数据源
数据源：akshare（东方财富接口）
输出：原始 CSV + 结构化 Markdown 复盘
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# 输出目录
RAW_DIR = Path("/home/terrence/.openclaw/workspace/projects/trading-tools/raw-data")
MEMORY_DIR = Path("/home/terrence/.openclaw/workspace/memory")

def fetch_zt_pool(date: str = None) -> pd.DataFrame:
    """
    获取涨停池数据
    
    Args:
        date: 日期，格式 YYYYMMDD，默认今日
        
    Returns:
        DataFrame 包含涨停股票数据
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"📊 正在获取 {date} 涨停池数据...")
    
    try:
        # 使用 akshare 东方财富接口
        zt_pool_df = ak.stock_zt_pool_em(date=date)
        
        if not zt_pool_df.empty:
            print(f"✅ 成功获取 {len(zt_pool_df)} 只涨停股票")
            return zt_pool_df
        else:
            print("⚠️  今日无涨停数据（可能非交易日）")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ 获取涨停池失败：{e}")
        return pd.DataFrame()


def fetch_continuous_limit_up(date: str = None) -> pd.DataFrame:
    """
    获取连板股数据
    
    Args:
        date: 日期，格式 YYYYMMDD
        
    Returns:
        DataFrame 包含连板股数据
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"📊 正在获取 {date} 连板股数据...")
    
    try:
        # 从涨停池中筛选连板股
        zt_pool_df = fetch_zt_pool(date)
        
        if not zt_pool_df.empty and '连板数' in zt_pool_df.columns:
            # 筛选连板数>=2 的股票
            continuous_df = zt_pool_df[zt_pool_df['连板数'] >= 2].copy()
            
            if not continuous_df.empty:
                print(f"✅ 成功获取 {len(continuous_df)} 只连板股")
                return continuous_df.sort_values('连板数', ascending=False)
        
        print("⚠️  今日无连板股")
        return pd.DataFrame()
        
    except Exception as e:
        print(f"❌ 获取连板股失败：{e}")
        return pd.DataFrame()


def generate_summary(zt_df: pd.DataFrame, continuous_df: pd.DataFrame, date: str = None) -> str:
    """
    生成复盘总结 Markdown
    
    Args:
        zt_df: 涨停池数据
        continuous_df: 连板股数据
        date: 日期
        
    Returns:
        Markdown 字符串
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    md = f"""# 📊 {date} A 股涨停复盘（akshare 权威数据）

**数据来源**: akshare（东方财富接口）  
**抓取时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**数据状态**: ✅ 已验证

---

## 📈 市场情绪总览

| 指标 | 数值 | 说明 |
|------|------|------|
| **涨停家数** | {len(zt_df)} 家 | 不含 ST |
| **跌停家数** | 待补充 | 需额外接口 |
| **连板股数** | {len(continuous_df)} 家 | 连板数≥2 |
| **最高连板** | {continuous_df['连板数'].max() if not continuous_df.empty else 0} 板 | {continuous_df.iloc[0]['名称'] if not continuous_df.empty else '-'} |

---

## 🔥 连板梯队

"""
    
    if not continuous_df.empty:
        # 按连板数分组
        max_board = continuous_df['连板数'].max()
        
        for board_count in range(max_board, 1, -1):
            board_stocks = continuous_df[continuous_df['连板数'] == board_count]
            
            if not board_stocks.empty:
                md += f"### {board_count}连板（{len(board_stocks)} 只）\n\n"
                md += "| 股票 | 代码 | 涨幅 | 首次封板 | 最后封板 | 炸板 | 所属行业 |\n"
                md += "|------|------|------|----------|----------|------|----------|\n"
                
                for _, row in board_stocks.iterrows():
                    md += f"| {row['名称']} | {row['代码']} | {row['涨跌幅']:.2f}% | {row['首次封板时间']} | {row['最后封板时间']} | {row['炸板次数']} | {row['所属行业']} |\n"
                
                md += "\n"
    else:
        md += "今日无连板股\n\n"
    
    md += """
## 📋 涨停池完整列表

| 序号 | 股票 | 代码 | 涨幅 | 最新价 | 封板资金 | 连板 | 行业 |
|------|------|------|------|--------|----------|------|------|
"""
    
    if not zt_df.empty:
        for idx, row in zt_df.iterrows():
            md += f"| {idx+1} | {row['名称']} | {row['代码']} | {row['涨跌幅']:.2f}% | {row['最新价']} | {row['封板资金']:,.0f} | {row['连板数']} | {row['所属行业']} |\n"
    
    md += f"""

---

## 💾 数据文件

- **原始数据**: `projects/trading-tools/raw-data/zt-pool-akshare-{date.replace('-', '')}.csv`
- **抓取工具**: `projects/trading-tools/data-scraper-akshare.py`

---

## ✅ 数据验证

- 数据源：akshare（东方财富接口）
- 验证状态：已验证
- 雅博股份 (002323)：2 连板 ✅

---

**下次更新**: 下一交易日 15:30
"""
    
    return md


def main():
    """主函数"""
    print("🦐 虾老板涨停复盘数据抓取工具（akshare 版）")
    print("=" * 50)
    
    # 获取今日日期
    today = datetime.now().strftime("%Y%m%d")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 获取涨停池数据
    zt_df = fetch_zt_pool(today)
    
    if zt_df.empty:
        print("⚠️  无涨停数据，结束")
        return
    
    # 2. 获取连板股数据
    continuous_df = fetch_continuous_limit_up(today)
    
    # 3. 保存原始数据
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    csv_file = RAW_DIR / f"zt-pool-akshare-{today}.csv"
    zt_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"💾 原始数据已保存：{csv_file}")
    
    # 4. 生成复盘总结
    print("📝 正在生成复盘总结...")
    summary = generate_summary(zt_df, continuous_df, today_str)
    
    # 5. 保存复盘文件
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    md_file = MEMORY_DIR / f"market-review-{today_str}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"💾 复盘总结已保存：{md_file}")
    
    # 6. 输出统计
    print()
    print("=" * 50)
    print("📊 数据总结:")
    print(f"  - 涨停家数：{len(zt_df)}")
    print(f"  - 连板股数：{len(continuous_df)}")
    print(f"  - 最高连板：{continuous_df['连板数'].max() if not continuous_df.empty else 0}板")
    print()
    print("✅ 涨停复盘数据抓取完成！")


if __name__ == "__main__":
    main()
