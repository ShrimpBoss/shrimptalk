#!/usr/bin/env python3
"""
节点题材强度分析工具
功能：
1. 分析节点最强题材
2. 统计题材梯队
3. 计算题材强度
"""

import pandas as pd
from collections import Counter
from pathlib import Path

# 数据目录
DATA_DIR = Path("/home/terrence/.openclaw/workspace/projects/trading-tools/raw-data")


def analyze_industry_strength(zt_df):
    """
    分析题材强度
    
    Args:
        zt_df: 涨停池 DataFrame
    
    Returns:
        题材分析字典
    """
    if zt_df.empty or '所属行业' not in zt_df.columns:
        return {}
    
    # 统计各题材涨停家数
    industry_count = Counter(zt_df['所属行业'])
    
    # 计算题材强度
    total = len(zt_df)
    industry_data = []
    
    for industry, count in industry_count.most_common(10):  # 前 10 大题材
        strength = count / total * 100
        
        # 找出该题材的代表股（连板数最高的 3 只）
        industry_stocks = zt_df[zt_df['所属行业'] == industry]
        if '连板数' in industry_stocks.columns:
            top_stocks = industry_stocks.sort_values('连板数', ascending=False).head(3)
            reps = []
            for _, row in top_stocks.iterrows():
                if row['连板数'] >= 2:
                    reps.append(f"{row['名称']}({row['连板数']}板)")
                else:
                    reps.append(row['名称'])
            rep_str = '、'.join(reps)
        else:
            rep_str = '、'.join(industry_stocks['名称'].head(3).tolist())
        
        industry_data.append({
            "题材": industry,
            "涨停家数": count,
            "题材强度": f"{strength:.1f}%",
            "代表股": rep_str
        })
    
    # 确定最强题材
    strongest = industry_data[0] if industry_data else {}
    
    return {
        "最强题材": strongest.get("题材", ""),
        "题材强度": f"{strongest.get('涨停家数', 0)}/{total}={strongest.get('题材强度', '0%')}",
        "题材梯队": industry_data,
        "题材持续性": "待观察"
    }


def print_industry_analysis(zt_df):
    """打印题材分析"""
    print("\n" + "="*60)
    print("🏭 题材强度分析")
    print("="*60 + "\n")
    
    analysis = analyze_industry_strength(zt_df)
    
    if not analysis:
        print("⚠️  无题材数据")
        return
    
    print(f"🔥 最强题材：{analysis['最强题材']}")
    print(f"📊 题材强度：{analysis['题材强度']}")
    print()
    print("题材梯队:")
    print("-" * 60)
    print(f"{'题材':<15} {'涨停家数':<10} {'题材强度':<10} {'代表股':<20}")
    print("-" * 60)
    
    for item in analysis['题材梯队']:
        print(f"{item['题材']:<15} {item['涨停家数']:<10} {item['题材强度']:<10} {item['代表股']:<20}")
    
    print("-" * 60)
    print()
    
    # 判断题材集中度
    if analysis['题材梯队']:
        top_strength = float(analysis['题材梯队'][0]['题材强度'].replace('%', ''))
        
        if top_strength >= 30:
            print("✅ 题材集中度高（>30%），主线清晰")
        elif top_strength >= 20:
            print("🟡 题材集中度中等（20-30%），多主线竞争")
        else:
            print("⚠️  题材集中度低（<20%），快速轮动")
    
    print()


def compare_industry_continuity(current_analysis, history_analysis):
    """
    对比题材持续性
    
    Args:
        current_analysis: 当前题材分析
        history_analysis: 历史题材分析列表
    
    Returns:
        持续性分析结果
    """
    current_strongest = current_analysis.get('最强题材', '')
    
    # 查找历史相似题材
    similar_history = []
    for hist in history_analysis:
        if hist.get('最强题材') == current_strongest:
            similar_history.append(hist)
    
    if similar_history:
        print(f"\n📈 {current_strongest} 题材历史持续性统计:")
        print(f"  历史出现 {len(similar_history)} 次")
        
        # 统计后续表现
        positive = sum(1 for h in similar_history if '上涨' in h.get('后续演化', ''))
        negative = sum(1 for h in similar_history if '下跌' in h.get('后续演化', ''))
        
        if positive > negative:
            print(f"  后续上涨概率：{positive/len(similar_history)*100:.0f}% ✅")
        elif negative > positive:
            print(f"  后续下跌概率：{negative/len(similar_history)*100:.0f}% ⚠️")
        else:
            print("  后续走势分化 🟡")
    else:
        print(f"\n⚠️  {current_strongest} 题材无历史参考")


def main():
    """主函数"""
    print("🦐 节点题材强度分析工具")
    print("=" * 60)
    
    # 加载今日数据
    today = pd.Timestamp.now().strftime("%Y%m%d")
    zt_file = DATA_DIR / f"zt-pool-akshare-{today}.csv"
    
    if zt_file.exists():
        zt_df = pd.read_csv(zt_file)
        
        # 题材分析
        print_industry_analysis(zt_df)
        
        # 保存题材分析到节点数据库（手动调用）
        print("💡 提示：题材分析结果已显示，可手动录入节点数据库")
    else:
        print(f"⚠️  今日数据文件不存在：{zt_file}")


if __name__ == "__main__":
    main()
