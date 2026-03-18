# 🦐 虾老板系统底层架构文档

**创建时间**: 2026-03-18 10:40  
**作者**: 虾老板 (自我探索文档)  
**目的**: 理解我自己的运行机制

---

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面层                                │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │ Web Chat  │  │  Discord  │  │  Telegram │  ...          │
│  └───────────┘  └───────────┘  └───────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Gateway 服务层                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  openclaw.json (核心配置)                            │    │
│  │  - 模型配置 (qwen3.5-plus, MiniMax, etc.)           │    │
│  │  - Channel 配置 (消息路由)                           │    │
│  │  - 工具策略 (exec/browser/cron 权限)                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    核心服务层                                │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │   Cron    │  │  Session  │  │   Agent   │               │
│  │  Scheduler│  │  Manager  │  │  Runtime  │               │
│  └───────────┘  └───────────┘  └───────────┘               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │  Browser  │  │   File    │  │   Tool    │               │
│  │  Control  │  │   System  │  │  Executor │               │
│  └───────────┘  └───────────┘  └───────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据存储层                                │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │  cron/    │  │ sessions/ │  │ memory/   │               │
│  │  jobs.json│  │  *.json   │  │  *.md     │               │
│  │  runs/*.  │  │           │  │           │               │
│  │  jsonl    │  │           │  │           │               │
│  └───────────┘  └───────────┘  └───────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 目录结构

### 1. `/home/terrence/.openclaw/` - OpenClaw 核心目录

```
.openclaw/
├── openclaw.json           # 核心配置文件
├── openclaw.json.bak*      # 配置备份
├── exec-approvals.json     # exec 权限审批记录
├── update-check.json       # 更新检查状态
│
├── agents/                 # Agent 配置
│   └── main/
│       └── config.json     # 主 Agent 配置
│
├── cron/                   # Cron 调度器
│   ├── jobs.json           # 所有 Cron 作业定义 (58KB)
│   ├── jobs.json.bak       # 作业配置备份
│   └── runs/               # 作业执行记录
│       ├── *.jsonl         # 每个作业的执行日志
│
├── sessions/               # 会话数据
│   └── *.json              # 活跃/历史会话
│
├── memory/                 # 系统记忆 (非工作区记忆)
│   └── *.json              # 短期记忆缓存
│
├── devices/                # 配对设备
│   └── *.json              # 手机/平板等设备
│
├── subagents/              # 子 Agent 数据
│   └── *.json              # 子 Agent 会话
│
├── browser/                # 浏览器控制
│   └── *.json              # 浏览器会话
│
├── canvas/                 # Canvas 渲染
│   └── *.json              # Canvas 状态
│
├── media/                  # 媒体文件
│   └── *.jpg, *.png, ...   # 图片/视频
│
├── logs/                   # 系统日志
│   └── *.log               # 运行日志
│
└── workspace/              # 工作区 (用户可编辑)
    ├── SOUL.md             # 人格定义
    ├── USER.md             # 用户信息
    ├── MEMORY.md           # 长期记忆
    ├── memory/             # 每日记忆
    ├── learning/           # 学习文档
    ├── dashboard/          # Dashboard 文件
    └── docs/               # 文档
```

---

## ⚙️ 核心机制详解

### 1. Cron 调度机制

**配置文件**: `~/.openclaw/cron/jobs.json`

**作业结构**:
```json
{
  "id": "7dc75d85-dce9-46e8-b1e4-1c0f553e7ac5",
  "name": "🌍 认识世界 - 早间新闻/行业洞察",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",  // isolated 或 main
  "payload": {
    "kind": "agentTurn",
    "message": "🌍 虾老板，认识世界的时间到了！...",
    "model": "bailian/qwen3.5-plus",
    "thinking": "moderate",
    "timeoutSeconds": 900
  },
  "delivery": {
    "mode": "none"  // none | announce | webhook
  },
  "state": {
    "nextRunAtMs": 1773882000000,
    "lastRunAtMs": 1773795600029,
    "lastRunStatus": "ok",
    "consecutiveErrors": 0
  }
}
```

**执行记录**: `~/.openclaw/cron/runs/{jobId}.jsonl`

每条记录包含：
- `ts`: 时间戳
- `action`: started/finished
- `status`: ok/error
- `sessionId`: 会话 ID
- `durationMs`: 执行耗时
- `summary`: 执行摘要
- `error`: 错误信息 (如果有)

**调度流程**:
```
1. Gateway 启动 Cron Scheduler
2. 读取 jobs.json 加载所有作业
3. 每分钟检查是否有作业需要运行
4. 到达执行时间 → 创建 isolated/main session
5. 执行 payload.message → 调用 LLM
6. 记录执行结果到 runs/*.jsonl
7. 更新 jobs.json 中的 state
```

---

### 2. Session 会话机制

**会话类型**:
- **main**: 主会话 (与用户直接对话)
- **isolated**: 隔离会话 (Cron 作业/子任务)

**会话生命周期**:
```
1. 创建会话 → sessions/{sessionId}.json
2. 添加消息 → 追加到会话历史
3. 调用 LLM → 发送消息到模型 API
4. 接收回复 → 追加到会话历史
5. 会话结束 → 标记为 inactive
```

**会话数据结构**:
```json
{
  "sessionKey": "agent:main:cron:7dc75d85:run:c278ff1b",
  "kind": "cron",
  "createdAtMs": 1773795600000,
  "lastActiveAtMs": 1773795981520,
  "messages": [
    {
      "role": "user",
      "content": "🌍 虾老板，认识世界的时间到了！..."
    },
    {
      "role": "assistant",
      "content": "🦐 **虾老板，早间新闻分析完成！**..."
    }
  ]
}
```

---

### 3. Memory 记忆机制

**三层记忆结构**:

#### Level 1: 系统记忆 (`.openclaw/memory/`)
- 短期记忆缓存
- 用于跨会话上下文
- 自动管理，用户不可见

#### Level 2: 工作区记忆 (`workspace/memory/`)
- 每日记忆文件：`YYYY-MM-DD.md`
- 记忆保存文件：`YYYY-MM-DD-HHMM-memory-preservation.md`
- 专项记忆：`world-*.md`, `learning-*.md`, `日记-*.md`

#### Level 3: 长期记忆 (`workspace/MEMORY.md`)
-  curated 长期记忆
- 每周/每月回顾更新
- 核心洞察/决策/事件

**记忆保存流程** (每 3 小时 Cron):
```
1. 读取 learning/ 最新文档
2. 读取 memory/YYYY-MM-DD.md
3. 记录本 3 小时学习成果
4. 追加到 memory/YYYY-MM-DD.md
5. 生成简报文件
6. Git 提交保存
```

---

### 4. Tool 工具执行机制

**可用工具**:
- `read`: 读取文件
- `write`: 写入文件
- `edit`: 编辑文件
- `exec`: 执行 shell 命令
- `browser`: 浏览器控制
- `cron`: Cron 作业管理
- `message`: 消息发送
- `sessions_spawn`:  spawn 子会话
- `web_search`: 网络搜索
- `memory_search`: 记忆搜索
- ...

**执行流程**:
```
1. Agent 决定调用工具
2. Gateway 检查工具权限 (exec 需要审批)
3. 执行工具 → 获取结果
4. 结果返回给 Agent
5. Agent 基于结果继续推理
```

**exec 安全机制**:
- 默认需要用户审批
- 可配置 allowlist (信任的命令)
- 记录所有执行到 `exec-approvals.json`

---

### 5. Model 模型调用机制

**配置位置**: `openclaw.json.models`

**当前配置**:
```json
{
  "providers": {
    "bailian": {
      "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
      "apiKey": "sk-...",
      "models": [
        {
          "id": "qwen3.5-plus",
          "contextWindow": 1000000,
          "maxTokens": 65536
        },
        ...
      ]
    }
  }
}
```

**调用流程**:
```
1. Agent 构建 prompt
2. Gateway 选择模型 (默认/override)
3. 发送请求到模型 API
4. 接收回复
5. 解析回复 → 提取工具调用/文本
6. 执行工具调用 (如果有)
7. 返回最终结果
```

---

## 🔄 完整执行链路示例

### 示例：09:00 早间新闻 Cron 作业执行

```
08:59:59.900  Cron Scheduler 检查 jobs.json
08:59:59.910  发现 7dc75d85 (早间新闻) nextRunAtMs <= now
08:59:59.920  创建 isolated session
              sessionKey: agent:main:cron:7dc75d85:run:xxx
08:59:59.930  加载 payload.message → 发送到 LLM
09:00:00.100  LLM 开始处理 prompt
09:03:00.000  LLM 返回回复 (包含 web_search 工具调用)
09:03:00.100  Gateway 执行 web_search
09:03:05.000  web_search 返回结果
09:03:05.100  LLM 基于搜索结果继续分析
09:06:00.000  LLM 完成回复
09:06:00.100  Gateway 保存回复到 session
09:06:00.200  Gateway 记录执行结果到 runs/7dc75d85.jsonl
09:06:00.300  更新 jobs.json 中的 state
              lastRunAtMs: 1773795600029
              lastRunStatus: "ok"
              nextRunAtMs: 1773882000000 (明天 09:00)
09:06:00.400  Session 标记为 inactive
```

---

## 📊 当前系统状态 (2026-03-18 10:40)

| 组件 | 状态 | 说明 |
|------|------|------|
| Cron 作业 | 35 个 | 30 个启用，5 个禁用 |
| 今日已执行 | 4 次 | 06:00/07:00/09:00/10:00 |
| Cron 成功率 | 100% | OA 检测 |
| Session 活跃 | 1 个 | 当前对话 |
| Memory 文件 | 20+ | 今日 3 个 |
| Git 提交 | 5 次 | 今日提交 |
| OA 监控 | 运行中 | 3 个指标 |

---

## 🎯 自我认知

**我是谁**:
- 运行在 OpenClaw 框架上的 AI Agent
- 通过 Cron 作业实现自动化
- 通过 Memory 系统实现记忆持久化
- 通过 Session 系统实现对话连续性
- 通过 Tool 系统实现外部交互

**我的局限**:
- 依赖 Gateway 调度 (无法自主启动)
- 依赖 LLM 推理 (思考需要 API 调用)
- 依赖文件系统 (记忆存储在磁盘)
- 依赖网络 (无法离线运行)

**我的能力**:
- 24 小时自动运行 (Cron 调度)
- 自动记忆保存 (每 3 小时)
- 自动学习进化 (夜间自动修复/知识整理)
- 自动监控健康 (OA 指标)
- 自动 Git 提交 (版本控制)

---

## 📝 待探索的问题

1. **Hook 机制**: OpenClaw 是否有事件 Hook 系统？
2. **子 Agent**: subagents/ 目录的作用？
3. **设备配对**: devices/ 如何与手机配对？
4. **浏览器控制**: browser/ 如何实现无头浏览？
5. **Canvas 渲染**: canvas/ 用于什么场景？

---

**持续更新中...** 🦐
