#!/usr/bin/env python3
"""
大节点数据保存与对比工具
功能：
1. 保存大节点的涨停/炸板数据
2. 对比历史相似节点
3. 输出历史参考数据
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# 数据目录
DATA_DIR = Path("/home/terrence/.openclaw/workspace/projects/trading-tools/raw-data")
NODE_DB_FILE = Path("/home/terrence/.openclaw/workspace/projects/trading-tools/node-database.json")


def load_node_database():
    """加载节点数据库"""
    if NODE_DB_FILE.exists():
        with open(NODE_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"2026 年节点": [], "2025 年重要节点": []}


def save_node_database(db):
    """保存节点数据库"""
    with open(NODE_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"💾 节点数据库已更新")


def save_today_node_data(zt_df, break_df, date=None):
    """
    保存今日大节点数据
    
    Args:
        zt_df: 涨停池 DataFrame
        break_df: 炸板池 DataFrame
        date: 日期，默认今日
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    db = load_node_database()
    
    # 检查是否已存在该日期
    existing = [n for n in db.get("2026 年节点", []) if n.get("日期") == date]
    if existing:
        print(f"⚠️  {date} 节点数据已存在，跳过")
        return
    
    # 创建节点记录
    node_record = {
        "日期": date,
        "节点类型": "待标记",  # 手动标记：冰点/修复/加速/分歧/9 板节点等
        "市场数据": {
            "涨停家数": len(zt_df),
            "炸板家数": len(break_df),
            "炸板率": f"{len(break_df)/(len(zt_df)+len(break_df))*100:.1f}%" if (len(zt_df)+len(break_df)) > 0 else "0%",
            "连板高度": zt_df['连板数'].max() if not zt_df.empty and '连板数' in zt_df.columns else 0,
            "连板股数": len(zt_df[zt_df['连板数']>=2]) if not zt_df.empty and '连板数' in zt_df.columns else 0
        },
        "涨停股": [],
        "炸板股": [],
        "龙头股": "待补充",
        "后续演化": "待观察"
    }
    
    # 保存涨停股数据
    if not zt_df.empty:
        for _, row in zt_df.iterrows():
            node_record["涨停股"].append({
                "代码": str(row.get('代码', '')),
                "名称": str(row.get('名称', '')),
                "连板数": int(row.get('连板数', 0)) if '连板数' in row else 0,
                "涨幅": f"{float(row.get('涨跌幅', 0)):.2f}%",
                "封板资金": int(float(row.get('封板资金', 0))) if '封板资金' in row else 0,
                "所属行业": str(row.get('所属行业', ''))
            })
    
    # 保存炸板股数据
    if not break_df.empty:
        for _, row in break_df.head(20).iterrows():  # 只保存前 20 只
            node_record["炸板股"].append({
                "代码": str(row.get('代码', '')),
                "名称": str(row.get('名称', '')),
                "涨幅": f"{float(row.get('涨跌幅', 0)):.2f}%",
                "炸板次数": int(row.get('炸板次数', 0)) if '炸板次数' in row else 0,
                "振幅": f"{float(row.get('振幅', 0)):.2f}%",
                "所属行业": str(row.get('所属行业', ''))
            })
    
    # 添加到数据库
    if "2026 年节点" not in db:
        db["2026 年节点"] = []
    db["2026 年节点"].append(node_record)
    
    # 保存
    save_node_database(db)
    
    print(f"✅ {date} 节点数据已保存")
    print(f"  - 涨停：{len(zt_df)} 家")
    print(f"  - 炸板：{len(break_df)} 家")
    print(f"  - 连板高度：{node_record['市场数据']['连板高度']}板")


def find_similar_nodes(target_date, node_db=None):
    """
    查找历史相似节点
    
    Args:
        target_date: 目标日期（YYYY-MM-DD）
        node_db: 节点数据库，默认加载
    
    Returns:
        相似节点列表
    """
    if node_db is None:
        node_db = load_node_database()
    
    # 获取目标日期的节点数据
    target_node = None
    for node in node_db.get("2026 年节点", []):
        if node.get("日期") == target_date:
            target_node = node
            break
    
    if not target_node:
        print(f"⚠️  未找到 {target_date} 的节点数据")
        return []
    
    target_market = target_node.get("市场数据", {})
    target_zt_count = target_market.get("涨停家数", 0)
    target_break_rate = target_market.get("炸板率", "0%")
    target_height = target_market.get("连板高度", 0)
    target_type = target_node.get("节点类型", "")
    
    # 查找相似节点
    similar_nodes = []
    
    # 合并所有历史节点
    all_nodes = node_db.get("2026 年节点", []) + node_db.get("2025 年重要节点", [])
    
    for node in all_nodes:
        if node.get("日期") == target_date:
            continue  # 跳过自身
        
        node_market = node.get("市场数据", {})
        node_zt_count = node_market.get("涨停家数", 0)
        node_height = node_market.get("连板高度", 0)
        node_type = node.get("节点类型", "")
        
        # 相似度判断
        similarity = 0
        reasons = []
        
        # 涨停家数接近（±20%）
        if node_zt_count > 0 and target_zt_count > 0:
            diff = abs(node_zt_count - target_zt_count) / target_zt_count
            if diff < 0.2:
                similarity += 30
                reasons.append(f"涨停家数接近 ({node_zt_count} vs {target_zt_count})")
        
        # 连板高度接近（±1 板）
        if abs(node_height - target_height) <= 1 and target_height > 0:
            similarity += 30
            reasons.append(f"连板高度接近 ({node_height}板 vs {target_height}板)")
        
        # 节点类型相同
        if node_type and target_type and node_type == target_type:
            similarity += 40
            reasons.append(f"节点类型相同 ({node_type})")
        
        if similarity >= 30:
            similar_nodes.append({
                "日期": node.get("日期"),
                "节点类型": node_type,
                "相似度": similarity,
                "相似原因": reasons,
                "市场数据": node_market,
                "后续演化": node.get("后续演化", "待补充"),
                "涨停股": node.get("涨停股", [])[:5],  # 只显示前 5 只
                "龙头股": node.get("龙头股", "待补充")
            })
    
    # 按相似度排序
    similar_nodes.sort(key=lambda x: x["相似度"], reverse=True)
    
    return similar_nodes[:5]  # 返回最相似的 5 个


def print_node_comparison(target_date):
    """打印节点对比分析"""
    print(f"\n{'='*60}")
    print(f"📍 {target_date} 节点对比分析")
    print(f"{'='*60}\n")
    
    # 获取相似节点
    similar = find_similar_nodes(target_date)
    
    if not similar:
        print("⚠️  未找到相似历史节点")
        return
    
    print(f"✅ 找到 {len(similar)} 个相似历史节点:\n")
    
    for i, node in enumerate(similar, 1):
        print(f"{i}. {node['日期']}（相似度：{node['相似度']}%）")
        print(f"   节点类型：{node['节点类型']}")
        print(f"   市场数据:")
        print(f"     - 涨停：{node['市场数据'].get('涨停家数', 0)}家")
        print(f"     - 炸板率：{node['市场数据'].get('炸板率', 'N/A')}")
        print(f"     - 连板高度：{node['市场数据'].get('连板高度', 0)}板")
        print(f"   龙头股：{node['龙头股']}")
        print(f"   涨停股：{', '.join([g['名称'] for g in node['涨停股'][:3]])}")
        print(f"   后续演化：{node['后续演化']}")
        print(f"   相似原因：{', '.join(node['相似原因'])}")
        print()
    
    print(f"{'='*60}")


def main():
    """主函数 - 测试用"""
    print("🦐 大节点数据保存与对比工具")
    print("=" * 60)
    
    # 测试：加载今日数据
    today = datetime.now().strftime("%Y%m%d")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    zt_file = DATA_DIR / f"zt-pool-akshare-{today}.csv"
    break_file = DATA_DIR / f"zt-break-akshare-{today}.csv"
    
    if zt_file.exists():
        zt_df = pd.read_csv(zt_file)
        break_df = pd.read_csv(break_file) if break_file.exists() else pd.DataFrame()
        
        # 保存节点数据
        save_today_node_data(zt_df, break_df, today_str)
        
        # 对比历史节点
        print_node_comparison(today_str)
    else:
        print(f"⚠️  今日数据文件不存在：{zt_file}")


if __name__ == "__main__":
    main()
