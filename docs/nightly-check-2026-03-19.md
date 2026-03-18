# 🔧 夜间系统自检报告

**日期**: 2026-03-19 01:00 (Asia/Shanghai)
**执行者**: 虾老板 (Cron 自动触发)

---

## 1. 系统资源

| 项目 | 状态 | 详情 |
|------|------|------|
| 磁盘 | ✅ 正常 | /dev/vda 20G，已用 7.1G (39%)，可用 12G |
| 内存 | ✅ 正常 | 总计 11Gi，已用 3.4Gi，可用 8.2Gi |
| 交换 | ⚠️ 无交换分区 | 0B swap，高内存时无缓冲 |
| 运行时间 | ✅ | 已运行 8 小时 23 分 |
| 负载 | ✅ 正常 | 1.43 / 0.72 / 0.49 |

---

## 2. Gateway 状态

| 项目 | 状态 |
|------|------|
| 进程 | ✅ 运行中 (pid 318, active) |
| RPC | ✅ 正常 |
| 监听 | 127.0.0.1:18789 (loopback) |
| Service 配置 | ⚠️ PATH 缺少目录 |

**⚠️ Service PATH 问题**: Gateway service PATH 缺少以下目录:
- `/home/terrence/.volta/bin`
- `/home/terrence/.asdf/shims`
- `/home/terrence/.bun/bin`
- `/home/terrence/.nvm/current/bin`
- `/home/terrence/.fnm/current/bin`
- `/home/terrence/.local/share/pnpm`

**建议**: 运行 `openclaw doctor --fix` 修复

---

## 3. Cron 作业状态

**总计**: 22 个 Cron 作业

### ✅ 正常运行 (16 个)

| 作业 | 上次执行 | 状态 |
|------|----------|------|
| 2 小时自动唤醒检查 | 57m ago | ok |
| 🦐 3D 开发期间 - 每 2 小时记忆备份 | 44m ago | ok |
| 每 3 小时记忆保存 - 深度学习 | 55m ago | ok |
| 🌍 早间资讯 + 市场关注点 | 16h ago | ok |
| ✍️ 交易日记 - 复盘思考/自媒体文案 | 15h ago | ok |
| 📊 OA 数据收集 - 午间 | 13h ago | ok |
| 📚 交易体系学习 - 情绪周期/技术分析 | 11h ago | ok |
| 👀 盘中情绪监控 - 涨停/炸板/异动 | 9h ago | ok |
| 📊 A 股收盘复盘 - 涨停/炸板/新高 | 7h ago | ok |
| 📊 OA 数据收集 - 晚间 | 6h ago | ok |
| 🧘 休息反思 - 冥想/散步/放空 | 4h ago | ok |
| 每日记忆与工作日志保存 - 增强版 | 1h ago | ok |
| 🦐 虾老板 - 每日记忆保存 | 58m ago | ok |

### ⏳ 空闲/首次 (4 个)

| 作业 | 下次执行 | 备注 |
|------|----------|------|
| 🤖 夜间自动修复 | in 60m | 从未执行 (首次) |
| 📚 夜间知识整理 | in 2h | 从未执行 (首次) |
| 🌅 晨间准备 | in 5h | 从未执行 (首次) |
| 📅 周总结 - 每周日 22:00 | in 4d | 从未执行 (首次) |

### ❌ 错误 (3 个) — 需要关注

| 作业 | Schedule | 上次执行 | 下次执行 |
|------|----------|----------|----------|
| 📈 自媒体运营 - B站内容策略 | 周二/四/六 15:00 | 1d ago | in 14h |
| 💻 数据工具学习 - Python/数据 | 周一/三/五 11:00 | 14h ago | in 1d |
| 🔬 交易工具开发 - 数据抓取/分析脚本 | 周一/三/五 19:00 | 6h ago | in 2d |

**分析**: 这 3 个作业均为近期新增的学习/开发类 Cron，错误原因可能是任务执行中的逻辑问题（如 edit 操作冲突）。日志中发现 `edit failed: Found 2 occurrences` 的错误出现在 trading-tools 的 node-database.json 文件中，说明 🔬 交易工具开发 在编辑 JSON 时遇到了文本不唯一的问题。

---

## 4. Session 健康

| 项目 | 详情 |
|------|------|
| Session 存储 | 73 条记录 |
| 活跃 Session | 当前仅 1 个 (本次自检) |
| Session 锁 | 2 个锁文件，均属于 pid 318 (Gateway)，非过期 |
| 异常 Session | ❌ 无 |

**状态**: 正常，无僵死或过期 Session。

---

## 5. 错误日志分析

### 🔴 高频错误: 飞书权限不足 (code 99991672)

**频率**: 每 ~5 分钟触发一次 (00:19 → 00:57 期间至少 8 次)
**错误**: `contact:contact.base:readonly` 等权限未开通
**影响**: 飞书联系人信息查询失败，但 Gateway 已自动忽略 (`ignoring stale permission scope error`)
**修复**: 在飞书开放平台为应用 `cli_a9200a5aafb89cc1` 申请以下任一权限:
- `contact:contact.base:readonly`
- `contact:contact:access_as_app`
- `contact:contact:readonly`

### 🟡 Warning: 未处理的飞书事件

**内容**: `no im.chat.access_event.bot_p2p_chat_entered_v1 handle`
**频率**: 多次 (00:24, 00:33, 00:36, 00:47, 00:48)
**影响**: 低 — 飞书 Bot 进入私聊事件未被处理，功能性无影响
**修复**: 无需处理，属于 OpenClaw 尚未实现的事件类型

### 🟡 edit 操作冲突

**文件**: `projects/trading-tools/node-database.json`
**原因**: 文本匹配到 2 个位置，edit 要求唯一匹配
**影响**: 交易工具开发 Cron 执行失败
**修复**: 下次 Cron 执行时需提供更精确的匹配上下文

---

## 6. Doctor 诊断汇总

| 检查项 | 状态 | 详情 |
|--------|------|------|
| Session 锁 | ✅ | 2 个活跃锁，无过期 |
| Gateway 服务配置 | ⚠️ | PATH 缺少目录 |
| 安全 | ✅ | 无安全警告 |
| Skills | ℹ️ | 8 个可用，47 个缺少依赖 |
| Plugins | ✅ | 5 个加载，33 个禁用，0 错误 |
| Bootstrap 文件 | ⚠️ | MEMORY.md 21,031 字符，被截断 14% |
| Memory Search | ❌ | 无 embedding provider 配置，语义搜索不可用 |

---

## 7. 修复建议 (优先级排序)

### P0 — 立即修复
1. **飞书权限**: 开通 `contact:contact.base:readonly` 权限，消除高频错误日志噪音
2. **Memory Search**: 配置 embedding provider (推荐用 bailian 或本地模型)，否则 `memory_search` 功能完全失效

### P1 — 近期修复
3. **Gateway PATH**: 运行 `openclaw doctor --fix` 修复 service 配置
4. **MEMORY.md 瘦身**: 当前 21KB，被截断 14%，需要整理精简
5. **3 个错误 Cron**: 排查失败原因，特别是 trading-tools 的 JSON 编辑冲突

### P2 — 优化项
6. **无交换分区**: 考虑配置 swap，防止高负载时 OOM
7. **47 个 Skills 缺少依赖**: 按需安装，非紧急

---

## 8. 为夜间自动修复 (02:00) 准备的任务

以下问题可由 `🤖 夜间自动修复` Cron 自动处理:
- [ ] 运行 `openclaw doctor --fix` 修复 Gateway PATH
- [ ] 精简 MEMORY.md (去除过时信息，降到 15KB 以下)
- [ ] 检查 `projects/trading-tools/node-database.json` 中的重复文本

以下需要宝哥手动操作:
- [ ] 飞书开放平台权限申请
- [ ] 配置 embedding provider (需要 API key)

---

*报告生成时间: 2026-03-19 01:00 CST*
*下次自检: 2026-03-20 01:00*
