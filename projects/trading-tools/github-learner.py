#!/usr/bin/env python3
"""
GitHub 每日学习简报自动抓取工具
数据源：GitHub Trending、ClawHub
输出：learning/github-daily-YYYY-MM-DD.md
"""

import json
import requests
from datetime import datetime
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path("/home/terrence/.openclaw/workspace/learning")

# 关注的关键词
KEYWORDS = [
    "openclaw",
    "ai-agent",
    "auto-gpt",
    "langchain",
    "automation",
    "stock-analysis",
    "trading",
    "memory-system",
    "vector-db",
    "openviking"
]


def fetch_github_trending() -> list:
    """
    获取 GitHub Trending 项目
    使用 GitHub API（免费）
    """
    trending = []
    
    # 方法 1: 使用 GitHub Search API
    # https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories
    url = "https://api.github.com/search/repositories"
    
    for keyword in KEYWORDS[:3]:  # 避免 API 限制，先查前 3 个关键词
        params = {
            "q": f"{keyword} stars:>1000 pushed:>2025-03-17",
            "sort": "stars",
            "order": "desc",
            "per_page": 5
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for repo in data.get("items", [])[:2]:
                    trending.append({
                        "name": repo["full_name"],
                        "stars": repo["stargazers_count"],
                        "description": repo.get("description", ""),
                        "url": repo["html_url"],
                        "keyword": keyword,
                        "updated_at": repo.get("updated_at", "")[:10]
                    })
        except Exception as e:
            print(f"⚠️  抓取 {keyword} 失败：{e}")
    
    # 去重
    seen = set()
    unique = []
    for item in trending:
        if item["name"] not in seen:
            seen.add(item["name"])
            unique.append(item)
    
    return unique[:10]  # 返回前 10 个


def fetch_clawhub_skills() -> list:
    """
    获取 ClawHub 新技能
    需要研究 ClawHub API
    """
    # TODO: 实现 ClawHub 抓取
    # 目前先用静态数据
    return [
        {
            "name": "healthcheck",
            "description": "主机安全审计和风险评估",
            "url": "https://clawhub.com/skills/healthcheck"
        },
        {
            "name": "weather",
            "description": "天气查询技能",
            "url": "https://clawhub.com/skills/weather"
        }
    ]


def generate_daily_brief(trending: list, clawhub: list) -> str:
    """生成每日学习简报"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    md = f"""# 📚 GitHub 每日学习简报 - {today}

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**数据源**: GitHub API + ClawHub

---

## 🔥 Trending 项目（AI/OpenClaw 相关）

| 项目 | Stars | 更新 | 说明 |
|------|-------|------|------|
"""
    
    for repo in trending:
        md += f"| [{repo['name']}]({repo['url']}) | ⭐ {repo['stars']:,} | {repo['updated_at']} | {repo['description'][:30]}... |\n"
    
    md += f"""
---

## 🆕 ClawHub 新技能

"""
    
    for skill in clawhub:
        md += f"- **{skill['name']}**: {skill['description']}  \n  [{skill['url']}]({skill['url']})\n\n"
    
    md += f"""
---

## 💡 今日启发

（待补充：根据 trending 项目分析可借鉴的技术点）

---

## 🎯 明日学习重点

1. 研究 [待填写] 的源码结构
2. 学习 [待填写] 的功能实现
3. 探索与虾老板项目的结合点

---

**自动生成** | 下次更新：{today} 04:00
"""
    
    return md


def main():
    """主函数"""
    print("📚 GitHub 学习简报生成工具启动...")
    
    # 1. 抓取 GitHub Trending
    print("🔍 正在抓取 GitHub Trending...")
    trending = fetch_github_trending()
    print(f"✅ 抓取到 {len(trending)} 个项目")
    
    # 2. 抓取 ClawHub 技能
    print("🔍 正在抓取 ClawHub 技能...")
    clawhub = fetch_clawhub_skills()
    print(f"✅ 抓取到 {len(clawhub)} 个技能")
    
    # 3. 生成简报
    print("📝 正在生成学习简报...")
    brief = generate_daily_brief(trending, clawhub)
    
    # 4. 保存文件
    today = datetime.now().strftime("%Y-%m-%d")
    brief_file = OUTPUT_DIR / f"github-daily-{today}.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(brief_file, "w", encoding="utf-8") as f:
        f.write(brief)
    
    print(f"💾 学习简报已保存：{brief_file}")
    print("✅ GitHub 学习简报生成完成！")
    
    return {
        "status": "success",
        "brief_file": str(brief_file),
        "trending_count": len(trending),
        "clawhub_count": len(clawhub)
    }


if __name__ == "__main__":
    main()
