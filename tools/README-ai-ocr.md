# 🦐 AI-OCR 涨停表格识别工具

使用通义千问 VL（多模态大模型）识别涨停/炸板表格图片，输出结构化数据。

---

## 📦 安装依赖

```bash
pip install dashscope pandas openpyxl
```

---

## 🔑 配置 API Key

### 方案 1：环境变量（推荐）
```bash
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxx"
```

### 方案 2：在代码中配置
编辑 `ai_ocr_zt_table.py`，在顶部添加：
```python
API_KEY = "sk-xxxxxxxxxxxxxx"  # 你的通义千问 API key
```

### 获取 API Key（OpenAI 兼容接口）
1. 访问 https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 左侧菜单 → **API-KEY 管理**
4. 点 **创建新的 API-KEY**
5. 复制 key（格式：`sk-xxxxxxxxxxxxxx`）

### 免费额度
- **100 万 Token**（约 1000-2000 张图片）
- **有效期 90 天**
- 自动抵扣，无需额外操作

### 接口说明
- **Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **Model**: `qwen-vl-plus` 或 `qwen3-vl-plus`
- **文档**: https://help.aliyun.com/document_detail/2712576.html

---

## 🚀 使用方法

### 识别涨停表格
```bash
cd /home/terrence/.openclaw/workspace/tools
python ai_ocr_zt_table.py /path/to/zt_table.png limit_up
```

### 识别炸板表格
```bash
python ai_ocr_zt_table.py /path/to/zb_table.png broken
```

---

## 📁 输出文件

输出到独立目录（不污染原始数据）：
```
/home/terrence/.openclaw/workspace/data/emotion/
├── zt-2026-03-19.xlsx    # 涨停明细 Excel
├── zt-2026-03-19.csv     # 涨停明细 CSV
├── zb-2026-03-19.xlsx    # 炸板明细 Excel
└── zb-2026-03-19.csv     # 炸板明细 CSV
```

---

## 📊 识别字段

### 涨停表格
| 字段 | 说明 |
|------|------|
| 股票名称 | 如"三房巷" |
| 股票代码 | 600370 |
| 连板高度 | 5（5 板） |
| 涨停时间 | 09:25:00 |
| 涨停原因 | 化学纤维 |
| 封单金额 | 1.2 亿 |
| 开板次数 | 9 |

### 炸板表格
| 字段 | 说明 |
|------|------|
| 股票名称 | 如"泸天化" |
| 股票代码 | 000912 |
| 最高涨幅 | +10% |
| 收盘涨幅 | -10.05% |
| 炸板时间 | 10:30 |
| 所属板块 | 化肥 |

---

## 🎯 图片来源

可以识别以下来源的截图：
- 选股宝涨停表格
- 短线侠复盘图片
- 开盘啦连板梯队
- 公众号复盘文章中的表格
- 任何包含涨停/炸板数据的图片

---

## ⚠️ 注意事项

1. **图片清晰度**：尽量用高清截图，模糊图片识别率会下降
2. **表格格式**：标准表格效果最好，手写体/艺术字可能识别不准
3. **数据校验**：识别后建议人工核对一下关键字段（股票代码、连板高度）
4. **API 费用**：新用户免费额度约 1000 次调用，用完约 ¥0.01/次

---

## 🦐 开发者

虾老板 | 2026-03-19
为宝哥的情绪周期交易体系打造
