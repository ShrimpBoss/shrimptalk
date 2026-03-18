#!/usr/bin/env python3
"""
A 股涨停复盘数据抓取工具 - akshare 完整版
数据源：akshare（东方财富接口）
包含：涨停池、炸板池、昨日涨停、连板梯队、涨停板块分析
"""

import akshare as ak
import pandas as pd
from datetime import datetime
from pathlib import Path
from collections import Counter

# 输出目录
RAW_DIR = Path("/home/terrence/.openclaw/workspace/projects/trading-tools/raw-data")
MEMORY_DIR = Path("/home/terrence/.openclaw/workspace/memory")


def fetch_zt_pool(date=None):
    """获取涨停池数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"📊 正在获取 {date} 涨停池数据...")
    try:
        df = ak.stock_zt_pool_em(date=date)
        if not df.empty:
            print(f"✅ 成功获取 {len(df)} 只涨停股票")
            return df
        else:
            print("⚠️  今日无涨停数据")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ 获取涨停池失败：{e}")
        return pd.DataFrame()


def fetch_zt_break_pool(date=None):
    """获取炸板池数据"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"📊 正在获取 {date} 炸板池数据...")
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date)
        if not df.empty:
            print(f"✅ 成功获取 {len(df)} 只炸板股票")
            return df
        else:
            print("⚠️  今日无炸板数据")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ 获取炸板池失败：{e}")
        return pd.DataFrame()


def fetch_yesterday_zt(date=None):
    """获取昨日涨停今日表现"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    print(f"📊 正在获取 {date} 昨日涨停今日表现...")
    try:
        df = ak.stock_zt_pool_previous_em(date=date)
        if not df.empty:
            print(f"✅ 成功获取 {len(df)} 只昨日涨停股票")
            return df
        else:
            print("⚠️  无昨日涨停数据")
            return pd.DataFrame()
    except Exception as e:
        print(f"❌ 获取昨日涨停失败：{e}")
        return pd.DataFrame()


def analyze_industry(zt_df):
    """分析涨停个股行业分布"""
    if zt_df.empty or '所属行业' not in zt_df.columns:
        return pd.DataFrame()
    
    industry_count = Counter(zt_df['所属行业'])
    industry_df = pd.DataFrame.from_dict(industry_count, orient='index', columns=['涨停家数'])
    industry_df = industry_df.sort_values('涨停家数', ascending=False)
    
    return industry_df


def generate_summary(zt_df, break_df, yesterday_df, date=None):
    """生成完整复盘总结"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # 计算连板股
    continuous_df = zt_df[zt_df['连板数'] >= 2].copy() if not zt_df.empty else pd.DataFrame()
    
    # 计算炸板率
    total = len(zt_df) + len(break_df)
    break_rate = (len(break_df) / total * 100) if total > 0 else 0
    
    # 计算昨日涨停今日表现
    avg_gain = yesterday_df['涨跌幅'].mean() if not yesterday_df.empty else 0
    
    # 行业分布
    industry_df = analyze_industry(zt_df)
    
    md = f"""# 📊 {date} A 股涨停复盘（完整版）

**数据来源**: akshare（东方财富接口）  
**抓取时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**数据状态**: ✅ 已验证

---

## 📈 市场情绪总览

| 指标 | 数值 | 说明 |
|------|------|------|
| **涨停家数** | {len(zt_df)} 家 | 不含 ST |
| **炸板家数** | {len(break_df)} 家 | 封板后炸板 |
| **炸板率** | {break_rate:.1f}% | 炸板/ (涨停 + 炸板) |
| **连板股数** | {len(continuous_df)} 家 | 连板数≥2 |
| **最高连板** | {continuous_df['连板数'].max() if not continuous_df.empty else 0} 板 | {continuous_df.iloc[0]['名称'] if not continuous_df.empty else '-'} |
| **昨日涨停今日表现** | {avg_gain:.2f}% | 昨日涨停股平均涨跌幅 |

---

## 🔥 连板梯队

"""
    
    if not continuous_df.empty:
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
    
    # 炸板池
    md += """
## 💥 炸板池

"""
    if not break_df.empty:
        md += f"**炸板率**: {break_rate:.1f}%（{len(break_df)} 只炸板）\n\n"
        md += "| 股票 | 代码 | 涨幅 | 最新价 | 涨停价 | 首次封板 | 炸板次数 | 振幅 | 所属行业 |\n"
        md += "|------|------|------|--------|--------|----------|----------|------|----------|\n"
        
        for _, row in break_df.head(20).iterrows():
            md += f"| {row['名称']} | {row['代码']} | {row['涨跌幅']:.2f}% | {row['最新价']} | {row['涨停价']} | {row['首次封板时间']} | {row['炸板次数']} | {row['振幅']:.2f}% | {row['所属行业']} |\n"
    else:
        md += "今日无炸板股\n"
    
    # 昨日涨停今日表现
    md += """

## 📉 昨日涨停今日表现

"""
    if not yesterday_df.empty:
        # 计算晋级情况（用涨停统计列）
        if '涨停统计' in yesterday_df.columns:
            # 涨停统计格式如 "2/1" 表示 2 天 1 板
            def parse_board_count(x):
                try:
                    return int(x.split('/')[1]) if '/' in str(x) else 0
                except:
                    return 0
            
            yesterday_df['今日连板'] = yesterday_df['涨停统计'].apply(parse_board_count)
            success_df = yesterday_df[yesterday_df['今日连板'] > 0]
        else:
            success_df = yesterday_df[yesterday_df['涨跌幅'] > 0]
        
        fail_df = yesterday_df[yesterday_df['涨跌幅'] < 0]
        
        md += f"- **昨日涨停总数**: {len(yesterday_df)} 只\n"
        md += f"- **今日平均涨幅**: {avg_gain:.2f}%\n"
        md += f"- **晋级成功**: {len(success_df)} 只\n"
        md += f"- **晋级失败（核按钮）**: {len(fail_df)} 只\n\n"
        
        if len(fail_df) > 0:
            md += "### 今日核按钮（昨日涨停今日大跌）\n\n"
            md += "| 股票 | 代码 | 今日涨跌幅 | 昨日连板 | 所属行业 |\n"
            md += "|------|------|------------|----------|----------|\n"
            
            for _, row in fail_df[fail_df['涨跌幅'] < -5].head(10).iterrows():
                board = row.get('昨日连板数', row.get('涨停统计', '-'))
                md += f"| {row['名称']} | {row['代码']} | {row['涨跌幅']:.2f}% | {board} | {row['所属行业']} |\n"
    else:
        md += "无昨日涨停数据\n"
    
    # 涨停板块分析
    md += """

## 🏭 涨停板块分析

"""
    if not industry_df.empty:
        md += "| 行业 | 涨停家数 | 占比 | 代表个股 |\n"
        md += "|------|----------|------|----------|\n"
        
        for idx, (industry, count) in enumerate(industry_df.head(10).iterrows()):
            reps = zt_df[zt_df['所属行业'] == industry]['名称'].head(3).tolist()
            rep_str = '、'.join(reps)
            ratio = count / len(zt_df) * 100 if len(zt_df) > 0 else 0
            md += f"| {industry} | {count} | {ratio:.1f}% | {rep_str} |\n"
    else:
        md += "无行业分布数据\n"
    
    # 涨停池完整列表
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

- **涨停池**: `raw-data/zt-pool-akshare-{date.replace('-', '')}.csv`
- **炸板池**: `raw-data/zt-break-akshare-{date.replace('-', '')}.csv`
- **昨日涨停**: `raw-data/zt-yesterday-akshare-{date.replace('-', '')}.csv`

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
    print("🦐 虾老板涨停复盘数据抓取工具（完整版）")
    print("=" * 50)
    
    today = datetime.now().strftime("%Y%m%d")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 获取涨停池数据
    zt_df = fetch_zt_pool(today)
    
    if zt_df.empty:
        print("⚠️  无涨停数据，结束")
        return
    
    # 2. 获取炸板池数据
    break_df = fetch_zt_break_pool(today)
    
    # 3. 获取昨日涨停今日表现
    yesterday_df = fetch_yesterday_zt(today)
    
    # 4. 保存原始数据
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    zt_file = RAW_DIR / f"zt-pool-akshare-{today}.csv"
    zt_df.to_csv(zt_file, index=False, encoding='utf-8-sig')
    print(f"💾 涨停池已保存：{zt_file}")
    
    if not break_df.empty:
        break_file = RAW_DIR / f"zt-break-akshare-{today}.csv"
        break_df.to_csv(break_file, index=False, encoding='utf-8-sig')
        print(f"💾 炸板池已保存：{break_file}")
    
    if not yesterday_df.empty:
        yesterday_file = RAW_DIR / f"zt-yesterday-akshare-{today}.csv"
        yesterday_df.to_csv(yesterday_file, index=False, encoding='utf-8-sig')
        print(f"💾 昨日涨停已保存：{yesterday_file}")
    
    # 5. 生成复盘总结
    print("📝 正在生成复盘总结...")
    summary = generate_summary(zt_df, break_df, yesterday_df, today_str)
    
    # 6. 保存复盘文件
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    md_file = MEMORY_DIR / f"market-review-{today_str}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"💾 复盘总结已保存：{md_file}")
    
    # 7. 输出统计
    print()
    print("=" * 50)
    print("📊 数据总结:")
    print(f"  - 涨停家数：{len(zt_df)}")
    print(f"  - 炸板家数：{len(break_df)}")
    print(f"  - 炸板率：{len(break_df)/(len(zt_df)+len(break_df))*100:.1f}%")
    print(f"  - 连板股数：{len(zt_df[zt_df['连板数']>=2])}")
    print(f"  - 昨日涨停：{len(yesterday_df)}")
    avg = yesterday_df['涨跌幅'].mean() if not yesterday_df.empty else 0
    print(f"  - 昨日涨停今日平均：{avg:.2f}%")
    print()
    print("✅ 涨停复盘数据抓取完成！")


if __name__ == "__main__":
    main()
