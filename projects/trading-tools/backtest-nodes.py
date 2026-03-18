#!/usr/bin/env python3
"""
历史节点数据回测工具
功能：
1. 批量获取 2025-2026 年关键节点的涨停/炸板数据
2. 保存到节点数据库
3. 建立完整的历史参考库
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

# 关键节点日期列表（从宝哥 Excel 和记忆中提取）
KEY_NODES_2025_2026 = [
    # 2026 年节点
    "20260318",  # 冰点修复
    "20260316",  # 冰点
    "20260311",  # 冰点
    "20260304",  # 节点
    "20260303",  # 节点
    "20260226",  # 节点
    "20260224",  # 节点
    "20260212",  # 节点
    "20260202",  # 节点
    "20260130",  # 节点
    "20260128",  # 节点
    "20260126",  # 节点
    "20260123",  # 节点
    "20260116",  # 节点
    "20260113",  # 节点
    "20260107",  # 节点
    
    # 2025 年重要节点
    "20251229",  # 节点
    "20251017",  # 大冰点
    "20251016",  # 大冰点
    "20251015",  # 大冰点
    "20250919",  # 首开 6+5 断板
    "20250905",  # 大冰点/天普 9 板断板
    "20250904",  # 大冰点/天普 9 板断板
    "20250828",  # 节点
    "20250811",  # 指数突破/连板冰点
    "20250801",  # 西藏旅游 9 板断板
    "20250731",  # 西藏旅游 9 板断板
    "20250721",  # 兰生 6 板压制
    "20250707",  # 指数破 N 年新高
]


def fetch_zt_pool(date):
    """获取指定日期的涨停池数据"""
    try:
        df = ak.stock_zt_pool_em(date=date)
        if not df.empty:
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ {date} 涨停池获取失败：{e}")
        return pd.DataFrame()


def fetch_zt_break_pool(date):
    """获取指定日期的炸板池数据"""
    try:
        df = ak.stock_zt_pool_zbgc_em(date=date)
        if not df.empty:
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ {date} 炸板池获取失败：{e}")
        return pd.DataFrame()


def analyze_node_data(date, zt_df, break_df):
    """分析节点数据"""
    if zt_df.empty:
        return None
    
    # 计算市场数据
    total = len(zt_df) + len(break_df)
    break_rate = len(break_df) / total * 100 if total > 0 else 0
    
    # 连板统计
    continuous_df = zt_df[zt_df['连板数'] >= 2] if '连板数' in zt_df.columns else pd.DataFrame()
    max_board = int(zt_df['连板数'].max()) if '连板数' in zt_df.columns and not zt_df.empty else 0
    
    # 题材统计
    industry_count = {}
    if '所属行业' in zt_df.columns:
        industry_count = zt_df['所属行业'].value_counts().head(5).to_dict()
    
    # 最强题材
    strongest_industry = list(industry_count.keys())[0] if industry_count else ""
    
    # 龙头股
    leader = ""
    if not continuous_df.empty and '名称' in continuous_df.columns:
        leader_row = continuous_df.loc[continuous_df['连板数'].idxmax()]
        leader = f"{leader_row['名称']}({int(leader_row['连板数'])}板)"
    
    return {
        "日期": f"{date[:4]}-{date[4:6]}-{date[6:]}",
        "市场数据": {
            "涨停家数": len(zt_df),
            "炸板家数": len(break_df),
            "炸板率": f"{break_rate:.1f}%",
            "连板高度": max_board,
            "连板股数": len(continuous_df)
        },
        "题材分析": {
            "最强题材": strongest_industry,
            "题材梯队": [{"题材": k, "涨停家数": int(v)} for k, v in industry_count.items()]
        },
        "涨停股": [],
        "炸板股": [],
        "龙头股": leader,
        "节点类型": "待标记",
        "后续演化": "待观察"
    }


def save_node_to_database(node_data, db_file):
    """保存节点数据到数据库"""
    # 加载数据库
    if db_file.exists():
        with open(db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)
    else:
        db = {"2026 年节点": [], "2025 年重要节点": []}
    
    # 检查是否已存在
    all_nodes = db.get("2026 年节点", []) + db.get("2025 年重要节点", [])
    existing_dates = [n.get("日期") for n in all_nodes]
    
    if node_data["日期"] in existing_dates:
        print(f"⚠️  {node_data['日期']} 已存在，跳过")
        return False
    
    # 添加到对应年份
    year = "2026 年节点" if node_data["日期"].startswith("2026") else "2025 年重要节点"
    if year not in db:
        db[year] = []
    
    # 简化涨停股数据（只保存前 10 只）
    if node_data.get("涨停股"):
        node_data["涨停股"] = node_data["涨停股"][:10]
    
    db[year].append(node_data)
    
    # 保存
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    return True


def backtest_all_nodes():
    """回测所有关键节点"""
    print("🦐 历史节点数据回测工具")
    print("=" * 60)
    print(f"📅 待回测节点：{len(KEY_NODES_2025_2026)} 个")
    print()
    
    db_file = Path("/home/terrence/.openclaw/workspace/projects/trading-tools/node-database.json")
    
    success_count = 0
    for i, date in enumerate(KEY_NODES_2025_2026, 1):
        print(f"[{i}/{len(KEY_NODES_2025_2026)}] 处理 {date}...")
        
        # 获取涨停/炸板数据
        zt_df = fetch_zt_pool(date)
        break_df = fetch_zt_break_pool(date)
        
        if zt_df.empty:
            print(f"  ⚠️  无涨停数据，跳过")
            continue
        
        # 分析节点数据
        node_data = analyze_node_data(date, zt_df, break_df)
        
        if node_data:
            # 保存涨停股数据（简化版）
            for _, row in zt_df.head(20).iterrows():
                node_data["涨停股"].append({
                    "代码": str(row.get('代码', '')),
                    "名称": str(row.get('名称', '')),
                    "连板数": int(row.get('连板数', 0)) if '连板数' in row else 0,
                    "涨幅": f"{float(row.get('涨跌幅', 0)):.2f}%",
                    "所属行业": str(row.get('所属行业', ''))
                })
            
            # 保存炸板股数据（简化版）
            for _, row in break_df.head(10).iterrows():
                node_data["炸板股"].append({
                    "代码": str(row.get('代码', '')),
                    "名称": str(row.get('名称', '')),
                    "涨幅": f"{float(row.get('涨跌幅', 0)):.2f}%",
                    "所属行业": str(row.get('所属行业', ''))
                })
            
            # 保存到数据库
            if save_node_to_database(node_data, db_file):
                print(f"  ✅ 保存成功：{node_data['日期']} - {node_data['市场数据']['涨停家数']}家涨停，{node_data['市场数据']['连板高度']}板")
                success_count += 1
            else:
                print(f"  ⚠️  已存在")
        else:
            print(f"  ❌ 分析失败")
        
        # 避免请求过快
        if i % 5 == 0:
            print("  ⏳ 休息 2 秒...")
            import time
            time.sleep(2)
    
    print()
    print("=" * 60)
    print(f"✅ 回测完成！成功保存 {success_count}/{len(KEY_NODES_2025_2026)} 个节点")
    print(f"💾 数据库：{db_file}")


if __name__ == "__main__":
    backtest_all_nodes()
