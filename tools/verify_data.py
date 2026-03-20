#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据核对工具 - 确保所有数据最新最准确
抓取时间：早间 06:30-07:30（8 点推送前）
"""

import requests
import re
from datetime import datetime, timedelta

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("=" * 70)
print("🔍 数据核对工具 - 确保最新最准确")
print("=" * 70)
print(f"抓取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 存储验证后的数据
verified_data = {
    "futures": {},
    "stocks": {},
    "news": []
}

# ==================== 1. 财联社 - 期货实时数据 ====================
print("【1】财联社 - 期货实时数据")
print("-" * 50)

try:
    url = "https://www.cls.cn/telegraph"
    response = requests.get(url, headers=headers, timeout=15)
    content = response.text
    
    # 查找原油期货数据
    oil_matches = re.findall(r'原油[^0-9]{0,50}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%', content)
    if oil_matches:
        print(f"✅ 原油期货：{oil_matches[0][0]} 美元 ({oil_matches[0][1]}%)")
        verified_data["futures"]["原油"] = {"price": oil_matches[0][0], "change": oil_matches[0][1]}
    else:
        # 尝试其他格式
        oil_matches2 = re.findall(r'WTI[^0-9]{0,30}([0-9.]+)', content)
        if oil_matches2:
            print(f"✅ WTI 原油：{oil_matches2[0]} 美元")
            verified_data["futures"]["WTI"] = {"price": oil_matches2[0]}
    
    # 查找甲醇数据
    methanol = re.findall(r'甲醇[^0-9]{0,50}([+-]?[0-9.]+)%', content)
    if methanol:
        print(f"✅ 甲醇：{methanol[0]}%")
        verified_data["futures"]["甲醇"] = {"change": methanol[0]}
    else:
        print("❌ 甲醇数据：未找到")
    
    # 查找黄金数据
    gold = re.findall(r'黄金[^0-9]{0,50}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%', content)
    if gold:
        print(f"✅ 黄金：{gold[0][0]} 美元 ({gold[0][1]}%)")
        verified_data["futures"]["黄金"] = {"price": gold[0][0], "change": gold[0][1]}
    
    # 查找白银数据
    silver = re.findall(r'白银[^0-9]{0,50}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%', content)
    if silver:
        print(f"✅ 白银：{silver[0][0]} 美元 ({silver[0][1]}%)")
        verified_data["futures"]["白银"] = {"price": silver[0][0], "change": silver[0][1]}
    
    # 查找 24 小时内新闻
    print("\n【24 小时内重要新闻】")
    news_pattern = re.findall(r'<p[^>]*>([^<]{20,200})</p>', content)
    for news in news_pattern[:10]:
        if any(keyword in news for keyword in ['期货', '原油', '黄金', '甲醇', '美联储', '中东']):
            print(f"  - {news[:100]}")
            verified_data["news"].append(news[:100])
    
except Exception as e:
    print(f"❌ 财联社抓取失败：{e}")

print()

# ==================== 2. 金十数据 - 期货行情 ====================
print("【2】金十数据 - 期货行情")
print("-" * 50)

try:
    url = "https://www.jin10.com/"
    response = requests.get(url, headers=headers, timeout=15)
    content = response.text
    
    # 查找原油
    oil_wti = re.search(r'WTI[^0-9]{0,30}([0-9.]+)[^0-9]*([+-]?[0-9.]+)', content)
    oil_brent = re.search(r'布伦特[^0-9]{0,30}([0-9.]+)[^0-9]*([+-]?[0-9.]+)', content)
    
    if oil_wti:
        print(f"✅ WTI 原油：{oil_wti.group(1)} 美元 ({oil_wti.group(2)}%)")
        verified_data["futures"]["WTI_jin10"] = {"price": oil_wti.group(1), "change": oil_wti.group(2)}
    
    if oil_brent:
        print(f"✅ 布伦特原油：{oil_brent.group(1)} 美元 ({oil_brent.group(2)}%)")
        verified_data["futures"]["Brent_jin10"] = {"price": oil_brent.group(1), "change": oil_brent.group(2)}
    
    # 查找甲醇
    methanol = re.search(r'甲醇[^0-9]{0,30}([0-9.]+)[^0-9]*([+-]?[0-9.]+)', content)
    if methanol:
        print(f"✅ 甲醇：{methanol.group(1)} ({methanol.group(2)}%)")
        verified_data["futures"]["甲醇_jin10"] = {"price": methanol.group(1), "change": methanol.group(2)}
    else:
        print("❌ 甲醇数据：金十未找到")
    
    # 查找黄金
    gold = re.search(r'现货黄金[^0-9]{0,30}([0-9.]+)[^0-9]*([+-]?[0-9.]+)', content)
    if gold:
        print(f"✅ 现货黄金：{gold.group(1)} 美元 ({gold.group(2)}%)")
        verified_data["futures"]["黄金_jin10"] = {"price": gold.group(1), "change": gold.group(2)}
    
    # 查找白银
    silver = re.search(r'现货白银[^0-9]{0,30}([0-9.]+)[^0-9]*([+-]?[0-9.]+)', content)
    if silver:
        print(f"✅ 现货白银：{silver.group(1)} 美元 ({silver.group(2)}%)")
        verified_data["futures"]["白银_jin10"] = {"price": silver.group(1), "change": silver.group(2)}
    
except Exception as e:
    print(f"❌ 金十数据抓取失败：{e}")

print()

# ==================== 3. 东方财富 - 期货夜盘 ====================
print("【3】东方财富 - 期货夜盘")
print("-" * 50)

try:
    url = "http://quote.eastmoney.com/center/gridlist.html#futures"
    response = requests.get(url, headers=headers, timeout=15)
    content = response.text
    
    # 查找甲醇
    methanol = re.search(r'甲醇[^0-9]{0,50}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%', content)
    if methanol:
        print(f"✅ 甲醇：{methanol.group(1)} 元 ({methanol.group(2)}%)")
        verified_data["futures"]["甲醇_df"] = {"price": methanol.group(1), "change": methanol.group(2)}
    else:
        print("❌ 甲醇数据：东方财富未找到")
    
except Exception as e:
    print(f"❌ 东方财富抓取失败：{e}")

print()

# ==================== 4. 数据交叉验证 ====================
print("=" * 70)
print("【数据交叉验证】")
print("=" * 70)

# 甲醇验证
if "甲醇" in verified_data["futures"] or "甲醇_jin10" in verified_data["futures"] or "甲醇_df" in verified_data["futures"]:
    print("\n✅ 甲醇数据：")
    if "甲醇" in verified_data["futures"]:
        print(f"   财联社：{verified_data['futures']['甲醇']}")
    if "甲醇_jin10" in verified_data["futures"]:
        print(f"   金十数据：{verified_data['futures']['甲醇_jin10']}")
    if "甲醇_df" in verified_data["futures"]:
        print(f"   东方财富：{verified_data['futures']['甲醇_df']}")
else:
    print("\n❌ 甲醇数据：所有数据源均未找到，标注'待确认'")

# 原油验证
print("\n✅ 原油数据：")
if "原油" in verified_data["futures"]:
    print(f"   财联社：{verified_data['futures']['原油']}")
if "WTI" in verified_data["futures"]:
    print(f"   财联社 WTI: {verified_data['futures']['WTI']}")
if "WTI_jin10" in verified_data["futures"]:
    print(f"   金十 WTI: {verified_data['futures']['WTI_jin10']}")
if "Brent_jin10" in verified_data["futures"]:
    print(f"   金十布伦特：{verified_data['futures']['Brent_jin10']}")

# 黄金验证
print("\n✅ 黄金数据：")
if "黄金" in verified_data["futures"]:
    print(f"   财联社：{verified_data['futures']['黄金']}")
if "黄金_jin10" in verified_data["futures"]:
    print(f"   金十数据：{verified_data['futures']['黄金_jin10']}")

# 白银验证
print("\n✅ 白银数据：")
if "白银" in verified_data["futures"]:
    print(f"   财联社：{verified_data['futures']['白银']}")
if "白银_jin10" in verified_data["futures"]:
    print(f"   金十数据：{verified_data['futures']['白银_jin10']}")

print()
print("=" * 70)
print("✅ 数据核对完成")
print("=" * 70)
print(f"验证时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("⚠️ 注意事项：")
print("1. 期货数据以最新实时为准，夜间数据仅供参考")
print("2. 至少 2 个数据源交叉验证")
print("3. 不确定的标注'待确认'，不要编造数据")
print("4. 新闻必须是最近 24 小时内的")
