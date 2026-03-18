# 🔧 夜间自动修复日志 - 2026-03

---

## 2026-03-19 02:00 — 首次自动修复

**触发**: Cron 自动执行 (首次运行)
**输入**: `docs/nightly-check-2026-03-19.md` (01:00 自检报告)

### 修复清单

| # | 问题 | 修复操作 | 结果 |
|---|------|----------|------|
| 1 | 3 个 Cron 作业 Channel 错误 (📈自媒体/💻数据工具/🔬交易工具) | 设置 `--channel feishu --best-effort-deliver` | ✅ 已修复 |
| 2 | Gateway PATH 缺少目录 | 运行 `openclaw doctor --fix` | ⚠️ 部分修复 (embedding provider 缺失无法自动解决) |
| 3 | MEMORY.md 过大 (35KB, 截断 14%) | 精简至 3.7KB，旧内容归档到 `memory/archive-pre-20260317.md` | ✅ 已修复 |
| 4 | node-database.json 重复日期导致 edit 冲突 | 去重 2025-10-15 和 2025-10-16 (保留数据更完整的条目) | ✅ 已修复 |
| 5 | 旧 memory-preservation 文件堆积 | 6 个 03-15/03-16 的 preservation 文件移至 archive/ | ✅ 已归档 |

### 未能自动修复 (需宝哥操作)

| 问题 | 原因 | 建议 |
|------|------|------|
| 飞书权限 `contact:contact.base:readonly` | 需在飞书开放平台手动操作 | 为 app `cli_a9200a5aafb89cc1` 申请权限 |
| Embedding Provider 未配置 | 需要 API key | `openclaw configure --section model` 或设置环境变量 |
| 无 Swap 分区 | 需 root 权限 | `sudo fallocate -l 2G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile` |

### 离线 Agent 检查

- 活跃 Session: 1 个 (本次修复任务自身)
- 无僵死/离线 Agent 需要重启

### 统计

| 指标 | 值 |
|------|-----|
| 发现问题 | 8 个 |
| 自动修复 | 5 个 |
| 需人工 | 3 个 |
| 自修复率 | 62.5% |
| 执行耗时 | ~2 分钟 |

---
