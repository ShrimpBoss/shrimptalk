# Dashboard API 服务

## 接口文档

### 基础信息
- **Base URL:** `http://localhost:3000/api`
- **认证方式:** JWT Token
- **数据格式:** JSON

---

## 接口列表

### 1. 获取 Dashboard 汇总数据

**GET** `/dashboard/summary`

**响应:**
```json
{
  "success": true,
  "data": {
    "metrics": {
      "gmv": { "value": 1234, "currency": "USD", "trend": 12.5 },
      "orders": { "value": 45, "unit": "单", "trend": 8 },
      "profit": { "value": 487, "currency": "USD", "trend": 56 },
      "roas": { "value": 3.2, "trend": 0.3 },
      "rating": { "value": 94, "unit": "%", "trend": 2 },
      "shipped": { "value": 42, "unit": "单", "trend": 5 }
    },
    "lastUpdate": "2026-03-08T19:48:00+08:00"
  }
}
```

---

### 2. 获取 Agent 状态

**GET** `/agents/status`

**响应:**
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "name": "产品 Agent",
        "status": "running",
        "task": "今日选品：15 款 · 待审核：3 款",
        "completedToday": 15,
        "pendingReview": 3,
        "exceptions": 0
      },
      {
        "name": "营销 Agent",
        "status": "running",
        "task": "广告花费：$156 · ROAS: 3.2",
        "adSpend": 156,
        "roas": 3.2,
        "exceptions": 0
      },
      {
        "name": "订单 Agent",
        "status": "processing",
        "task": "待处理：5 单 · 异常：2 单",
        "pending": 5,
        "exceptions": 2
      }
    ]
  }
}
```

---

### 3. 获取选品推荐

**GET** `/products/recommended`

**查询参数:**
- `limit` (可选): 返回数量，默认 15
- `status` (可选): pending/approved/rejected

**响应:**
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "id": "P001",
        "name": "减压魔方",
        "image": "🎲",
        "grossMargin": 45,
        "trendScore": 92,
        "trendLevel": 4,
        "supplier": "CJ Dropshipping",
        "cost": 8.5,
        "suggestedPrice": 24.99,
        "status": "pending",
        "submittedAt": "2026-03-08T10:30:00+08:00"
      }
    ],
    "total": 15
  }
}
```

---

### 4. 获取待审批事项

**GET** `/approvals/pending`

**响应:**
```json
{
  "success": true,
  "data": {
    "approvals": [
      {
        "id": "A001",
        "type": "product_listing",
        "title": "新品上架审批 - 3 款",
        "description": "3 款新品符合选品标准，申请上架",
        "priority": "normal",
        "submittedAt": "2026-03-08T11:00:00+08:00",
        "details": {
          "productIds": ["P001", "P002", "P003"]
        }
      },
      {
        "id": "A002",
        "type": "budget_adjustment",
        "title": "广告预算调整",
        "description": "从 $500/天 → $800/天",
        "priority": "high",
        "submittedAt": "2026-03-08T14:20:00+08:00",
        "details": {
          "from": 500,
          "to": 800,
          "reason": "ROAS 持续>3.0，建议加大投放"
        }
      }
    ],
    "total": 3
  }
}
```

---

### 5. 审批操作

**POST** `/approvals/:id/decision`

**请求体:**
```json
{
  "decision": "approve",
  "comment": "同意，按计划执行"
}
```

**响应:**
```json
{
  "success": true,
  "message": "审批已通过",
  "data": {
    "approvalId": "A001",
    "decision": "approve",
    "decidedAt": "2026-03-08T19:50:00+08:00",
    "decidedBy": "李总"
  }
}
```

---

### 6. 提交建议/指示

**POST** `/suggestions`

**请求体:**
```json
{
  "title": "拓展 TikTok 渠道",
  "content": "建议加大 TikTok 渠道投入，测试新的广告格式",
  "category": "运营优化",
  "priority": "medium",
  "dueDate": "2026-02-20",
  "assignee": "营销 Agent"
}
```

**响应:**
```json
{
  "success": true,
  "message": "建议已提交",
  "data": {
    "id": "S001",
    "createdAt": "2026-03-08T19:50:00+08:00"
  }
}
```

---

### 7. 获取建议列表

**GET** `/suggestions`

**查询参数:**
- `status` (可选): pending/in_progress/completed
- `category` (可选): 战略方向/产品建议/运营优化/其他

**响应:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "id": "S001",
        "title": "增加情人节主题素材",
        "category": "运营优化",
        "priority": "high",
        "status": "completed",
        "assignee": "营销 Agent",
        "createdAt": "2026-02-01T10:00:00+08:00",
        "completedAt": "2026-02-10T15:30:00+08:00"
      }
    ],
    "total": 3
  }
}
```

---

### 8. 获取工作进度

**GET** `/tasks/progress`

**响应:**
```json
{
  "success": true,
  "data": {
    "departments": [
      {
        "name": "产品部",
        "task": "本周选品",
        "progress": 80,
        "current": 40,
        "target": 50,
        "unit": "款"
      },
      {
        "name": "营销部",
        "task": "广告活动",
        "progress": 100,
        "current": 5,
        "target": 5,
        "unit": "个"
      }
    ]
  }
}
```

---

### 9. 获取销售趋势

**GET** `/sales/trend`

**查询参数:**
- `days` (可选): 天数，默认 7

**响应:**
```json
{
  "success": true,
  "data": {
    "dates": ["3/2", "3/3", "3/4", "3/5", "3/6", "3/7", "3/8"],
    "gmv": [890, 1020, 1150, 950, 1280, 1450, 1234],
    "orders": [32, 38, 42, 35, 48, 52, 45],
    "profit": [320, 380, 425, 355, 478, 542, 487]
  }
}
```

---

### 10. WebSocket 实时更新

**连接:** `ws://localhost:3000/ws`

**订阅频道:**
- `metrics` - 核心指标更新
- `agents` - Agent 状态变化
- `approvals` - 新审批事项
- `alerts` - 预警通知

**消息格式:**
```json
{
  "channel": "metrics",
  "type": "update",
  "data": {
    "gmv": { "value": 1250, "trend": 13.2 }
  },
  "timestamp": "2026-03-08T19:55:00+08:00"
}
```

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**错误响应:**
```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "请求参数错误",
    "details": "缺少必需参数：id"
  }
}
```

---

## 认证流程

1. 李总登录（用户名 + 密码）
2. 服务器验证并返回 JWT Token
3. 后续请求在 Header 中携带 Token
4. Token 有效期 24 小时，支持刷新

**登录请求:**
```json
POST /auth/login
{
  "username": "李总",
  "password": "******"
}
```

**登录响应:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 86400,
    "user": {
      "id": "U001",
      "name": "李总",
      "role": "admin"
    }
  }
}
```

---

## 部署说明

### 环境变量

```bash
# .env
PORT=3000
NODE_ENV=production
JWT_SECRET=your-secret-key
DATABASE_URL=sqlite:./dashboard.db
OPENCLAW_API_URL=http://localhost:8080
```

### 启动服务

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 启动生产服务器
npm start
```

### 与 OpenClaw 集成

```javascript
// openclaw-sync.js
const OpenClawAPI = require('openclaw-sdk');

const openclaw = new OpenClawAPI({
  apiKey: process.env.OPENCLAW_API_KEY,
  baseUrl: process.env.OPENCLAW_API_URL
});

// 订阅 Agent 事件
openclaw.subscribe('agent.task.complete', (event) => {
  // 更新 Dashboard 数据
  updateDashboard(event);
});

// 推送审批决策
openclaw.approve('A001', {
  decision: 'approve',
  decidedBy: '李总'
});
```

---

**版本:** 1.0  
**创建日期:** 2026-03-08  
**最后更新:** 2026-03-08
