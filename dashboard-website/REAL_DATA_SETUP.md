# Dashboard 真实数据接入指南

## 🚫 模拟数据已禁用

从 2026-03-12 起，Dashboard 不再使用任何模拟数据。所有数据显示规则：

- **有真实数据** → 显示实际值
- **无数据** → 显示 `—`

## 📊 数据表结构

### 1. agents_status (Agent 实时状态)

```sql
CREATE TABLE agents_status (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,        -- Agent 名字：王总、小安、小智、小方、小文、订单专员、小财、小服、小仓、小研
  role TEXT,                 -- 角色：副经理、安全运维、产品、营销、内容、订单、财务、客服、仓储、数据分析
  status TEXT DEFAULT 'offline',  -- 状态：running、processing、error、offline
  task TEXT,                 -- 当前任务描述
  priority INTEGER DEFAULT 99, -- 排序优先级（数字越小越靠前）
  exceptions INTEGER DEFAULT 0, -- 异常数量
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**示例数据**（由各 Agent 系统实时更新）:
```sql
INSERT INTO agents_status (name, role, status, task, priority, exceptions) VALUES
  ('王总', '副经理', 'running', '待审核：3 项 · 预警：0', 1, 0),
  ('小安', '安全运维', 'running', '系统监控 · 安全审计', 2, 0),
  ('小智', '产品', 'running', '今日选品：15 款', 3, 0),
  ('小方', '营销', 'running', '广告花费：$156 · ROAS: 3.2', 4, 0),
  ('小文', '内容', 'running', '今日产出：8 篇', 5, 0),
  ('订单专员', '订单', 'processing', '待处理：5 单 · 异常：2 单', 6, 2),
  ('小财', '财务', 'running', '现金流：45 天 · 预算使用：62%', 7, 0),
  ('小服', '客服', 'running', '待回复：12 条 · 好评率：98%', 8, 0),
  ('小仓', '仓储', 'running', '待发货：8 单 · 库存：充足', 9, 0),
  ('小研', '数据分析', 'running', '日报已生成 · 周报处理中', 10, 0);
```

### 2. metrics (核心指标)

```sql
CREATE TABLE metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date DATE,                 -- 日期：2026-03-12
  gmv REAL,                  -- GMV (USD)
  orders INTEGER,            -- 订单数
  profit REAL,               -- 利润 (USD)
  roas REAL,                 -- ROAS
  rating REAL,               -- 好评率 (%)
  shipped INTEGER,           -- 发货数
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**数据来源**: 每日由数据分析 Agent (小研) 从 Shopify、Meta Ads、电商平台同步

### 3. products (选品推荐)

```sql
CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,                 -- 产品名称
  image TEXT,                -- 图片 URL 或 emoji
  gross_margin REAL,         -- 毛利率 (%)
  trend_score INTEGER,       -- 趋势评分 (0-100)
  trend_level INTEGER,       -- 趋势等级 (1-5，对应🔥数量)
  supplier TEXT,             -- 供应商
  cost REAL,                 -- 成本 (USD)
  suggested_price REAL,      -- 建议售价 (USD)
  status TEXT DEFAULT 'pending', -- 状态：pending、approved、rejected
  submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**数据来源**: 产品 Agent (小智) 实时提交选品推荐

### 4. approvals (审批事项)

```sql
CREATE TABLE approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT,                 -- 类型：product_listing、budget_adjustment、supplier_contract
  title TEXT NOT NULL,       -- 标题
  description TEXT,          -- 描述
  priority TEXT,             -- 优先级：high、medium、low
  status TEXT DEFAULT 'pending', -- 状态：pending、approved、rejected
  details TEXT,              -- 详细数据 (JSON)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  decided_at DATETIME,       -- 决策时间
  decided_by TEXT,           -- 决策人
  decision TEXT              -- 决策：approve、reject
);
```

**数据来源**: 各 Agent 提交需要李总审批的事项

### 5. tasks (工作进度)

```sql
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  department TEXT,           -- 部门：产品部、营销部、内容部、订单部
  task TEXT,                 -- 任务名称
  progress INTEGER,          -- 进度 (0-100)
  current INTEGER,           -- 当前完成数
  target INTEGER,            -- 目标数
  unit TEXT,                 -- 单位：款、个、篇、单
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**数据来源**: 各部门 Agent 每日更新工作进度

### 6. security_status (系统安全监控)

```sql
CREATE TABLE security_status (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cpu_usage REAL,            -- CPU 使用率 (%)
  memory_usage REAL,         -- 内存使用率 (%)
  disk_usage REAL,           -- 磁盘使用率 (%)
  network_status TEXT,       -- 网络状态：normal、warning、error
  api_calls INTEGER,         -- API 调用次数
  security_events INTEGER,   -- 安全事件数
  status TEXT DEFAULT 'normal', -- 整体状态：normal、warning、critical
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**数据来源**: 安全运维 Agent (小安) 实时监控系统，每 5 分钟更新

### 7. suggestions (建议与指示)

```sql
CREATE TABLE suggestions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT,
  category TEXT,
  priority TEXT DEFAULT 'medium',
  status TEXT DEFAULT 'pending',
  assignee TEXT,
  progress INTEGER DEFAULT 0,
  feedback TEXT,
  due_date DATE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  completed_at DATETIME,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**数据来源**: 李总通过 Dashboard 提交建议，各 Agent 执行并反馈

---

## 🔌 数据同步方式

### 方式 1: 直接写入 SQLite

```javascript
const Database = require('better-sqlite3');
const db = new Database('./dashboard.db');

// 更新 Agent 状态
db.prepare(`
  INSERT OR REPLACE INTO agents_status (name, role, status, task, priority, exceptions, updated_at)
  VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
`).run('小安', '安全运维', 'running', '系统监控 · 无异常', 2, 0);
```

### 方式 2: 调用 API

```bash
# 更新 Agent 状态
curl -X POST http://localhost:3000/api/agents/status/update \
  -H "Content-Type: application/json" \
  -d '{"name":"小安","role":"安全运维","status":"running","task":"系统监控","exceptions":0}'
```

### 方式 3: Cron 定时任务

设置定时任务，每分钟/每小时同步数据：

```bash
# 每 5 分钟同步一次安全状态
*/5 * * * * /usr/bin/node /path/to/sync-security-status.js
```

---

## 📝 待开发 API

以下 API 需要开发以支持数据写入：

- [ ] `POST /api/agents/status/update` - 更新 Agent 状态
- [ ] `POST /api/metrics/daily` - 写入每日指标
- [ ] `POST /api/products/submit` - 提交选品推荐
- [ ] `POST /api/approvals/create` - 创建审批事项
- [ ] `POST /api/tasks/update` - 更新工作进度
- [ ] `POST /api/security/status/update` - 更新安全状态

---

## ✅ 检查清单

- [x] 禁用模拟数据初始化
- [x] 修改 API 返回空值时显示"—"
- [x] 添加 agents_status 表结构
- [ ] 开发数据写入 API
- [ ] 各 Agent 系统接入数据同步
- [ ] 设置定时同步任务
- [ ] 测试真实数据流

---

**最后更新**: 2026-03-12  
**状态**: 真实数据模式已启用，等待各系统接入
