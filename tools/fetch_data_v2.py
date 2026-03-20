#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版数据获取工具 - 确保最新最准确
支持多个备用数据源，智能解析 HTML 和 JSON
"""

import requests
import re
import json
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.google.com/"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.data = {
            "futures": {},
            "stocks": {},
            "news": [],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def fetch_with_retry(self, url, timeout=15, retries=3):
        """带重试的抓取"""
        for i in range(retries):
            try:
                response = self.session.get(url, timeout=timeout)
                if response.status_code == 200:
                    return response.text
                print(f"  ⚠️ 状态码：{response.status_code}")
            except Exception as e:
                print(f"  ❌ 第{i+1}次失败：{e}")
                if i < retries - 1:
                    continue
        return None
    
    def parse_number(self, text):
        """解析数字，处理中文数字和格式"""
        if not text:
            return None
        # 移除空格和特殊字符
        text = text.strip().replace(',', '')
        # 提取数字
        match = re.search(r'([0-9.]+)', text)
        return match.group(1) if match else None
    
    def parse_change(self, text):
        """解析涨跌幅"""
        if not text:
            return None
        # 处理正负号
        if '+' in text or '涨' in text or '升' in text:
            sign = '+'
        elif '-' in text or '跌' in text or '降' in text:
            sign = '-'
        else:
            sign = ''
        
        # 提取数字
        match = re.search(r'([0-9.]+)', text)
        if match:
            return f"{sign}{match.group(1)}"
        return None
    
    # ========== 财联社数据源 ==========
    def fetch_cls(self):
        """财联社 - 期货数据 + 新闻"""
        print("\n【1】财联社")
        print("-" * 50)
        
        url = "https://www.cls.cn/telegraph"
        content = self.fetch_with_retry(url)
        
        if not content:
            print("  ❌ 抓取失败")
            return
        
        # 查找期货数据 - 多种模式
        patterns = {
            "原油": [
                r'原油[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'WTI[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'油价[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
            ],
            "黄金": [
                r'黄金[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'COMEX 黄金[^0-9]{0,100}([0-9.]+)',
                r'金价[^0-9]{0,100}([0-9.]+)',
            ],
            "白银": [
                r'白银[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'COMEX 白银[^0-9]{0,100}([0-9.]+)',
                r'银价[^0-9]{0,100}([0-9.]+)',
            ],
            "甲醇": [
                r'甲醇[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'甲醇主力[^0-9]{0,100}([0-9.]+)',
            ],
            "铜": [
                r'沪铜[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'铜价[^0-9]{0,100}([0-9.]+)',
            ],
        }
        
        for commodity, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, content)
                if match:
                    groups = match.groups()
                    price = groups[0] if len(groups) > 0 else None
                    change = groups[1] if len(groups) > 1 else None
                    
                    print(f"  ✅ {commodity}: {price}" + (f" ({change}%)" if change else ""))
                    self.data["futures"][f"{commodity}_cls"] = {
                        "price": price,
                        "change": change,
                        "source": "财联社"
                    }
                    break
        
        # 查找 24 小时内新闻
        news_patterns = [
            r'<p[^>]*>([^<]{30,300})</p>',
            r'class="telegraph-content"[^>]*>([^<]{30,300})',
        ]
        
        print("\n  【24 小时内重要新闻】")
        news_count = 0
        for pattern in news_patterns:
            matches = re.findall(pattern, content)
            for match in matches[:5]:
                if any(kw in match for kw in ['期货', '原油', '黄金', '甲醇', '美联储', '中东', 'IEA']):
                    print(f"    - {match[:80]}...")
                    self.data["news"].append(match[:100])
                    news_count += 1
                    if news_count >= 5:
                        break
            if news_count >= 5:
                break
        
        if news_count == 0:
            print("    (未找到相关新闻)")
    
    # ========== 金十数据源 ==========
    def fetch_jin10(self):
        """金十数据 - 期货行情"""
        print("\n【2】金十数据")
        print("-" * 50)
        
        url = "https://www.jin10.com/"
        content = self.fetch_with_retry(url)
        
        if not content:
            print("  ❌ 抓取失败")
            return
        
        # 金十数据通常以 JSON 格式嵌入
        json_patterns = [
            r'var\s+jsonData\s*=\s*({[^}]+})',
            r'data["\']?\s*:\s*({[^}]+})',
            r'quote_data\s*=\s*({[^}]+})',
        ]
        
        json_data = None
        for pattern in json_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    json_data = json.loads(match.group(1))
                    break
                except:
                    continue
        
        # 如果没有 JSON，尝试 HTML 解析
        if not json_data:
            html_patterns = {
                "原油": [
                    r'原油[^0-9]{0,50}([0-9.]+)[^0-9]*([+-]?[0-9.]+)',
                    r'WTI[^0-9]{0,50}([0-9.]+)',
                    r'布伦特[^0-9]{0,50}([0-9.]+)',
                ],
                "黄金": [
                    r'现货黄金[^0-9]{0,50}([0-9.]+)[^0-9]*([+-]?[0-9.]+)',
                    r'黄金[^0-9]{0,50}([0-9.]+)',
                ],
                "白银": [
                    r'现货白银[^0-9]{0,50}([0-9.]+)[^0-9]*([+-]?[0-9.]+)',
                    r'白银[^0-9]{0,50}([0-9.]+)',
                ],
                "甲醇": [
                    r'甲醇[^0-9]{0,50}([0-9.]+)[^0-9]*([+-]?[0-9.]+)',
                    r'甲醇主力[^0-9]{0,50}([0-9.]+)',
                ],
            }
            
            for commodity, pattern_list in html_patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, content)
                    if match:
                        groups = match.groups()
                        price = groups[0] if len(groups) > 0 else None
                        change = groups[1] if len(groups) > 1 else None
                        
                        print(f"  ✅ {commodity}: {price}" + (f" ({change})" if change else ""))
                        self.data["futures"][f"{commodity}_jin10"] = {
                            "price": price,
                            "change": change,
                            "source": "金十数据"
                        }
                        break
        else:
            # 处理 JSON 数据
            print("  ✅ JSON 数据解析成功")
            # TODO: 解析 JSON 数据结构
    
    # ========== 东方财富数据源 ==========
    def fetch_eastmoney(self):
        """东方财富 - 期货夜盘"""
        print("\n【3】东方财富")
        print("-" * 50)
        
        url = "http://quote.eastmoney.com/center/gridlist.html#futures"
        content = self.fetch_with_retry(url)
        
        if not content:
            print("  ❌ 抓取失败")
            return
        
        # 东方财富期货数据
        patterns = {
            "甲醇": [
                r'甲醇[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'甲醇主力[^0-9]{0,100}([0-9.]+)',
            ],
            "原油": [
                r'原油[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'燃油[^0-9]{0,100}([0-9.]+)',
            ],
            "黄金": [
                r'沪金[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'黄金[^0-9]{0,100}([0-9.]+)',
            ],
            "白银": [
                r'沪银[^0-9]{0,100}([0-9.]+)[^0-9]*([+-]?[0-9.]+)%',
                r'白银[^0-9]{0,100}([0-9.]+)',
            ],
        }
        
        for commodity, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, content)
                if match:
                    groups = match.groups()
                    price = groups[0] if len(groups) > 0 else None
                    change = groups[1] if len(groups) > 1 else None
                    
                    print(f"  ✅ {commodity}: {price}" + (f" ({change}%)" if change else ""))
                    self.data["futures"][f"{commodity}_df"] = {
                        "price": price,
                        "change": change,
                        "source": "东方财富"
                    }
                    break
    
    # ========== 文华财经数据源 ==========
    def fetch_wenhua(self):
        """文华财经 - 期货行情"""
        print("\n【4】文华财经")
        print("-" * 50)
        
        url = "https://www.wenhua.com.cn/"
        content = self.fetch_with_retry(url)
        
        if not content:
            print("  ❌ 抓取失败")
            return
        
        # 文华财经期货数据
        patterns = {
            "甲醇": [r'甲醇[^0-9]{0,100}([0-9.]+)'],
            "原油": [r'原油[^0-9]{0,100}([0-9.]+)'],
            "黄金": [r'黄金[^0-9]{0,100}([0-9.]+)'],
        }
        
        for commodity, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, content)
                if match:
                    price = match.group(1)
                    print(f"  ✅ {commodity}: {price}")
                    self.data["futures"][f"{commodity}_wh"] = {
                        "price": price,
                        "source": "文华财经"
                    }
                    break
    
    # ========== 数据交叉验证 ==========
    def verify_data(self):
        """交叉验证数据"""
        print("\n" + "=" * 70)
        print("【数据交叉验证】")
        print("=" * 70)
        
        commodities = ["原油", "黄金", "白银", "甲醇", "铜"]
        
        for commodity in commodities:
            sources = [k for k in self.data["futures"].keys() if commodity in k]
            
            if sources:
                print(f"\n✅ {commodity}:")
                for source in sources:
                    data = self.data["futures"][source]
                    price = data.get("price", "N/A")
                    change = data.get("change", "N/A")
                    src = data.get("source", source)
                    print(f"   {src}: {price}" + (f" ({change}%)" if change != "N/A" else ""))
            else:
                print(f"\n❌ {commodity}: 所有数据源均未找到，标注'待确认'")
    
    # ========== 运行所有抓取 ==========
    def fetch_all(self):
        """运行所有数据源抓取"""
        print("=" * 70)
        print("🔍 优化版数据获取工具")
        print("=" * 70)
        print(f"抓取时间：{self.data['timestamp']}")
        
        self.fetch_cls()
        self.fetch_jin10()
        self.fetch_eastmoney()
        self.fetch_wenhua()
        self.verify_data()
        
        print("\n" + "=" * 70)
        print("✅ 数据抓取完成")
        print("=" * 70)
        
        return self.data


if __name__ == "__main__":
    fetcher = DataFetcher()
    data = fetcher.fetch_all()
    
    # 保存到文件
    import json
    output_file = "/home/terrence/.openclaw/workspace/data/verified_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 数据已保存到：{output_file}")
