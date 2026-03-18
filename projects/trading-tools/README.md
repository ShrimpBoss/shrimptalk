# 🦐 虾老板交易工具集

**创建时间**: 2026-03-18  
**用途**: A 股复盘数据自动抓取 + GitHub 学习简报

---

## 📁 目录结构

```
trading-tools/
├── data-scraper.py          # A 股复盘数据抓取（选股宝/短线侠/东财/同花顺）
├── github-learner.py        # GitHub 学习简报抓取
├── setup-cron.sh            # Cron 任务配置脚本
├── fetchers/
│   └── xuangubao.py         # 选股宝抓取模块
└── raw-data/
    └── market-review-raw-YYYY-MM-DD.json  # 原始数据备份
```

---

## 🚀 快速开始

### 1. 手动测试复盘抓取

```bash
cd /home/terrence/.openclaw/workspace/projects/trading-tools
python3 data-scraper.py
```

**输出**:
- `memory/market-review-YYYY-MM-DD.md` - 结构化复盘
- `raw-data/market-review-raw-YYYY-MM-DD.json` - 原始数据

### 2. 手动测试 GitHub 学习

```bash
python3 github-learner.py
```

**输出**:
- `learning/github-daily-YYYY-MM-DD.md` - 学习简报

### 3. 配置 Cron 自动任务

```bash
./setup-cron.sh
```

**配置的任务**:
| 任务 | 时间 | 说明 |
|------|------|------|
| 📊 A 股涨停复盘 | 工作日 15:30 | 收盘后自动抓取 |
| 📚 GitHub 学习简报 | 每日 04:00 | 夜间学习 |
| 📝 周报复盘 | 周一 08:00 | 每周总结 |

---

## 📊 数据源

| 数据源 | 类型 | 用途 | 验证方式 |
|--------|------|------|----------|
| **选股宝** | 网站 | 主数据源（涨停表格） | 东财验证总数 |
| **短线侠** | 网站 | 情绪指标/板块强度 | - |
| **东方财富** | 网站 | 涨跌停总数验证 | - |
| **同花顺** | 网站 | 连板梯队验证 | - |
| **GitHub API** | API | Trending 项目 | - |
| **ClawHub** | 网站 | 新技能发现 | - |

---

## ✅ 数据准确性保证

### 原则
1. **原始数据优先**：直接引用原始数据，不做人工推断
2. **双重验证**：连板数必须同时满足"连板字段"和"X 连板标注"
3. **标注不确定性**：不一致时标注"待确认"

### 验证规则
| 字段 | 验证方式 | 不一致处理 |
|------|----------|------------|
| 涨停总数 | 选股宝 vs 东财 | 取东财数据（更权威） |
| 连板数 | 选股宝 vs 同花顺 | 取同花顺（连板池更专业） |
| 个股连板 | 多源对比 | 标注"待确认"，人工核对 |

### 输出格式
每次输出两份文件：
1. **原始数据 JSON**：方便随时核对
2. **结构化 Markdown**：便于阅读

---

## 🛠️ 开发指南

### 添加新数据源

1. 在 `fetchers/` 目录创建抓取模块
2. 实现统一的 `fetch()` 接口
3. 在 `data-scraper.py` 中注册
4. 添加验证规则

### 示例：添加东方财富抓取

```python
# fetchers/dongfangcaifu.py
def fetch_dongfangcaifu() -> Dict[str, Any]:
    """从东方财富抓取涨跌停总数"""
    # 实现抓取逻辑
    return {
        "limit_up": 72,
        "limit_down": 13,
        "source": "dongfangcaifu"
    }
```

---

## 📝 更新日志

### 2026-03-18
- ✅ 项目框架创建
- ✅ 选股宝抓取模块（browser 集成）
- ✅ GitHub 学习简报模块
- ✅ Cron 配置脚本
- ✅ 数据验证机制
- ✅ 原始数据备份

### 待办
- [ ] 短线侠抓取模块
- [ ] 东方财富验证模块
- [ ] 同花顺连板池验证
- [ ] ClawHub API 研究
- [ ] 多渠道交叉验证

---

**维护者**: 虾老板  
**最后更新**: 2026-03-18 21:35
