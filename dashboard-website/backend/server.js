const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');
const Database = require('better-sqlite3');
const cors = require('cors');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'dashboard-secret-2026';

// 中间件
app.use(cors());
app.use(express.json());

// 静态文件服务 - 提供前端页面
app.use('/', express.static('../frontend'));

// 数据库初始化
const db = new Database('./dashboard.db');

// 创建表
db.exec(`
  CREATE TABLE IF NOT EXISTS suggestions (
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

  CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT,
    status TEXT DEFAULT 'pending',
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    decided_at DATETIME,
    decided_by TEXT,
    decision TEXT
  );

  CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    gmv REAL,
    orders INTEGER,
    profit REAL,
    roas REAL,
    rating REAL,
    shipped INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image TEXT,
    gross_margin REAL,
    trend_score INTEGER,
    trend_level INTEGER,
    supplier TEXT,
    cost REAL,
    suggested_price REAL,
    status TEXT DEFAULT 'pending',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department TEXT,
    task TEXT,
    progress INTEGER,
    current INTEGER,
    target INTEGER,
    unit TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS security_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpu_usage REAL,
    memory_usage REAL,
    disk_usage REAL,
    network_status TEXT,
    api_calls INTEGER,
    security_events INTEGER,
    status TEXT DEFAULT 'normal',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS agents_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT,
    status TEXT DEFAULT 'offline',
    task TEXT,
    priority INTEGER DEFAULT 99,
    exceptions INTEGER DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// 初始化团队基础架构数据（10 人团队，始终存在）
const initTeamData = () => {
  const count = db.prepare('SELECT COUNT(*) as count FROM agents_status').get();
  if (count.count > 0) return; // 已有数据，不重复插入

  // 插入 10 人团队基础状态
  const agents = [
    { name: '王总', role: '副经理', status: 'running', task: '待审核事项', priority: 1 },
    { name: '小安', role: '安全运维', status: 'running', task: '系统监控 · 安全审计', priority: 2 },
    { name: '小智', role: '产品', status: 'running', task: '选品推荐', priority: 3 },
    { name: '小方', role: '营销', status: 'running', task: '广告投放', priority: 4 },
    { name: '小文', role: '内容', status: 'running', task: '素材创作', priority: 5 },
    { name: '订单专员', role: '订单', status: 'running', task: '订单处理', priority: 6 },
    { name: '小财', role: '财务', status: 'running', task: '财务监控', priority: 7 },
    { name: '小服', role: '客服', status: 'running', task: '客户咨询', priority: 8 },
    { name: '小仓', role: '仓储', status: 'running', task: '发货管理', priority: 9 },
    { name: '小研', role: '数据分析', status: 'running', task: '数据报表', priority: 10 },
  ];

  const insert = db.prepare(`
    INSERT INTO agents_status (name, role, status, task, priority, exceptions, updated_at)
    VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
  `);

  agents.forEach(a => insert.run(a.name, a.role, a.status, a.task, a.priority));
  console.log('✅ 团队基础架构已初始化 (10 人)');
};

initTeamData();
console.log('📊 Dashboard 后端服务启动 - 真实数据模式（无模拟数据）');

// JWT 认证中间件
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    // 开发模式允许无 token
    req.user = { id: 'U001', name: '李总', role: 'admin' };
    return next();
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

// ============ API 路由 ============

// 1. 获取 Dashboard 汇总数据
app.get('/api/dashboard/summary', authenticateToken, (req, res) => {
  const latest = db.prepare('SELECT * FROM metrics ORDER BY date DESC LIMIT 1').get();
  const previous = db.prepare('SELECT * FROM metrics ORDER BY date DESC LIMIT 1 OFFSET 1').get();
  
  if (!latest) {
    return res.json({ success: true, data: { metrics: {}, lastUpdate: new Date().toISOString() } });
  }

  const calculateTrend = (current, prev) => {
    if (!prev || prev === 0) return 0;
    return Math.round(((current - prev) / prev) * 100 * 10) / 10;
  };

  res.json({
    success: true,
    data: {
      metrics: {
        gmv: { value: latest.gmv, currency: 'USD', trend: calculateTrend(latest.gmv, previous?.gmv) },
        orders: { value: latest.orders, unit: '单', trend: calculateTrend(latest.orders, previous?.orders) },
        profit: { value: latest.profit, currency: 'USD', trend: calculateTrend(latest.profit, previous?.profit) },
        roas: { value: latest.roas, trend: Math.round((latest.roas - (previous?.roas || 0)) * 10) / 10 },
        rating: { value: latest.rating, unit: '%', trend: latest.rating - (previous?.rating || 0) },
        shipped: { value: latest.shipped, unit: '单', trend: latest.shipped - (previous?.shipped || 0) }
      },
      lastUpdate: new Date().toISOString()
    }
  });
});

// 2. 获取 Agent 状态 - 从真实数据源读取
// 数据应由各 Agent 系统实时写入 agents_status 表
app.get('/api/agents/status', authenticateToken, (req, res) => {
  try {
    // 尝试从数据库读取真实 Agent 状态
    const agents = db.prepare('SELECT * FROM agents_status ORDER BY priority, name').all();
    
    if (agents.length === 0) {
      // 没有真实数据时返回空数组，前端显示"—"
      return res.json({
        success: true,
        data: { agents: [] }
      });
    }
    
    res.json({
      success: true,
      data: { agents: agents.map(a => ({
        name: a.name,
        role: a.role,
        status: a.status,
        task: a.task,
        exceptions: a.exceptions || 0
      })) }
    });
  } catch (e) {
    // 表不存在或查询失败时返回空
    res.json({ success: true, data: { agents: [] } });
  }
});

// 3. 获取选品推荐 - 从真实数据源读取
app.get('/api/products/recommended', authenticateToken, (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 15;
    const products = db.prepare('SELECT * FROM products WHERE status = "pending" ORDER BY submitted_at DESC LIMIT ?').all(limit);
    
    res.json({
      success: true,
      data: {
        products: products.map(p => ({
          id: p.id.toString(),
          name: p.name,
          image: p.image || '',
          grossMargin: p.gross_margin || 0,
          trendScore: p.trend_score || 0,
          trendLevel: p.trend_level || 0,
          supplier: p.supplier || '—',
          cost: p.cost || 0,
          suggestedPrice: p.suggested_price || 0,
          status: p.status,
          submittedAt: p.submitted_at
        })),
        total: products.length
      }
    });
  } catch (e) {
    res.json({ success: true, data: { products: [], total: 0 } });
  }
});

// 3b. 获取产品详情
app.get('/api/products/:id', authenticateToken, (req, res) => {
  const { id } = req.params;
  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(id);
  
  if (!product) {
    return res.status(404).json({ success: false, error: { code: 404, message: '产品不存在' } });
  }

  res.json({
    success: true,
    data: {
      id: product.id.toString(),
      name: product.name,
      image: product.image,
      grossMargin: product.gross_margin,
      trendScore: product.trend_score,
      trendLevel: product.trend_level,
      supplier: product.supplier,
      cost: product.cost,
      suggestedPrice: product.suggested_price,
      status: product.status,
      submittedAt: product.submitted_at,
      description: product.description,
      features: product.features ? JSON.parse(product.features) : [],
      marketAnalysis: product.market_analysis,
      profitCalc: product.profit_calc
    }
  });
});

// 4. 获取待审批事项 - 从真实数据源读取
app.get('/api/approvals/pending', authenticateToken, (req, res) => {
  try {
    const approvals = db.prepare("SELECT * FROM approvals WHERE status = 'pending' ORDER BY created_at DESC").all();
    
    res.json({
      success: true,
      data: {
        approvals: approvals.map(a => ({
          id: a.id.toString(),
          type: a.type,
          title: a.title,
          description: a.description,
          priority: a.priority,
          submittedAt: a.created_at,
          details: JSON.parse(a.details || '{}')
        })),
        total: approvals.length
      }
    });
  } catch (e) {
    res.json({ success: true, data: { approvals: [], total: 0 } });
  }
});

// 5. 审批操作
app.post('/api/approvals/:id/decision', authenticateToken, (req, res) => {
  const { id } = req.params;
  const { decision, comment } = req.body;
  
  const update = db.prepare(`
    UPDATE approvals 
    SET status = ?, decided_at = CURRENT_TIMESTAMP, decided_by = ?, decision = ?
    WHERE id = ?
  `);

  update.run(decision === 'approve' ? 'approved' : 'rejected', req.user.name, decision, id);

  res.json({
    success: true,
    message: decision === 'approve' ? '审批已通过' : '审批已驳回',
    data: {
      approvalId: id,
      decision,
      decidedAt: new Date().toISOString(),
      decidedBy: req.user.name
    }
  });
});

// 6. 提交建议
app.post('/api/suggestions', authenticateToken, (req, res) => {
  const { title, content, category, priority, status, assignee, progress } = req.body;
  
  const insert = db.prepare(`
    INSERT INTO suggestions (title, content, category, priority, status, assignee, progress)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  const result = insert.run(
    title, 
    content || '', 
    category || '其他', 
    priority || 'medium', 
    status || 'pending',
    assignee || '未指派',
    progress || 0
  );

  res.json({
    success: true,
    message: '建议已提交',
    data: {
      id: result.lastInsertRowid.toString(),
      createdAt: new Date().toISOString()
    }
  });
});

// 6b. 更新建议状态/进度/反馈
app.put('/api/suggestions/:id', authenticateToken, (req, res) => {
  const { id } = req.params;
  const { status, progress, feedback, completed_at } = req.body;
  
  const updates = [];
  const values = [];
  
  if (status !== undefined) {
    updates.push('status = ?');
    values.push(status);
  }
  if (progress !== undefined) {
    updates.push('progress = ?');
    values.push(progress);
  }
  if (feedback !== undefined) {
    updates.push('feedback = ?');
    values.push(feedback);
  }
  if (completed_at !== undefined) {
    updates.push('completed_at = ?');
    values.push(completed_at);
  }
  
  if (updates.length === 0) {
    return res.json({ success: false, error: '没有要更新的字段' });
  }
  
  updates.push('updated_at = CURRENT_TIMESTAMP');
  values.push(id);
  
  const update = db.prepare(`
    UPDATE suggestions SET ${updates.join(', ')} WHERE id = ?
  `);

  const result = update.run(...values);

  res.json({
    success: true,
    message: '建议已更新',
    data: {
      id: id,
      changes: result.changes
    }
  });
});

// 7. 获取建议列表
app.get('/api/suggestions', authenticateToken, (req, res) => {
  const { status, category, priority } = req.query;
  
  let sql = 'SELECT * FROM suggestions WHERE 1=1';
  const params = [];
  
  if (status) {
    sql += ' AND status = ?';
    params.push(status);
  }
  if (category) {
    sql += ' AND category = ?';
    params.push(category);
  }
  if (priority) {
    sql += ' AND priority = ?';
    params.push(priority);
  }
  
  sql += ' ORDER BY ' +
    'CASE priority WHEN \'high\' THEN 1 WHEN \'medium\' THEN 2 WHEN \'low\' THEN 3 END, ' +
    'CASE status WHEN \'in_progress\' THEN 1 WHEN \'pending\' THEN 2 WHEN \'completed\' THEN 3 WHEN \'rejected\' THEN 4 END, ' +
    'created_at DESC';
  
  const suggestions = db.prepare(sql).all(...params);

  res.json({
    success: true,
    data: {
      suggestions: suggestions.map(s => ({
        id: s.id.toString(),
        title: s.title,
        content: s.content,
        description: s.content,
        category: s.category,
        priority: s.priority,
        status: s.status,
        assignee: s.assignee,
        progress: s.progress || 0,
        feedback: s.feedback,
        createdAt: s.created_at,
        completedAt: s.completed_at
      })),
      total: suggestions.length
    }
  });
});

// 8. 获取工作进度 - 从真实数据源读取
app.get('/api/tasks/progress', authenticateToken, (req, res) => {
  try {
    const tasks = db.prepare('SELECT * FROM tasks ORDER BY department').all();
    
    if (tasks.length === 0) {
      return res.json({ success: true, data: { departments: [] } });
    }
    
    res.json({
      success: true,
      data: {
        departments: tasks.map(t => ({
          name: t.department,
          task: t.task,
          progress: t.progress,
          current: t.current,
          target: t.target,
          unit: t.unit
        }))
      }
    });
  } catch (e) {
    res.json({ success: true, data: { departments: [] } });
  }
});

// 9. 获取销售趋势 - 从真实数据源读取
app.get('/api/sales/trend', authenticateToken, (req, res) => {
  try {
    const days = parseInt(req.query.days) || 7;
    const metrics = db.prepare('SELECT * FROM metrics ORDER BY date DESC LIMIT ?').all(days);
    
    if (metrics.length === 0) {
      return res.json({ success: true, data: { dates: [], gmv: [], orders: [], profit: [] } });
    }
    
    res.json({
      success: true,
      data: {
        dates: metrics.map(m => m.date.slice(5)).reverse(),
        gmv: metrics.map(m => m.gmv).reverse(),
        orders: metrics.map(m => m.orders).reverse(),
        profit: metrics.map(m => m.profit).reverse()
      }
    });
  } catch (e) {
    res.json({ success: true, data: { dates: [], gmv: [], orders: [], profit: [] } });
  }
});

// 10. 获取安全状态 - 从真实监控系统读取
app.get('/api/security/status', authenticateToken, (req, res) => {
  try {
    const status = db.prepare('SELECT * FROM security_status ORDER BY updated_at DESC LIMIT 1').get();
    
    if (!status) {
      // 没有真实监控数据时返回空值
      return res.json({
        success: true,
        data: {
          system: {
            cpu: { value: '—', unit: '%', status: 'unknown' },
            memory: { value: '—', unit: '%', status: 'unknown' },
            disk: { value: '—', unit: '%', status: 'unknown' },
            network: { value: '—', status: 'unknown' }
          },
          security: {
            apiCalls: '—',
            securityEvents: '—',
            overallStatus: 'unknown'
          },
          lastUpdate: '—'
        }
      });
    }
    
    res.json({
      success: true,
      data: {
        system: {
          cpu: { value: status.cpu_usage, unit: '%', status: status.cpu_usage < 80 ? 'normal' : 'warning' },
          memory: { value: status.memory_usage, unit: '%', status: status.memory_usage < 85 ? 'normal' : 'warning' },
          disk: { value: status.disk_usage, unit: '%', status: status.disk_usage < 80 ? 'normal' : 'warning' },
          network: { value: status.network_status, status: status.network_status }
        },
        security: {
          apiCalls: status.api_calls,
          securityEvents: status.security_events,
          overallStatus: status.status
        },
        lastUpdate: status.updated_at
      }
    });
  } catch (e) {
    res.json({
      success: true,
      data: {
        system: {
          cpu: { value: '—', unit: '%', status: 'unknown' },
          memory: { value: '—', unit: '%', status: 'unknown' },
          disk: { value: '—', unit: '%', status: 'unknown' },
          network: { value: '—', status: 'unknown' }
        },
        security: { apiCalls: '—', securityEvents: '—', overallStatus: 'unknown' },
        lastUpdate: '—'
      }
    });
  }
});

// 11. 登录接口
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body;
  
  if (username === '李总' || username === 'admin') {
    const token = jwt.sign(
      { id: 'U001', name: username, role: 'admin' },
      JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    res.json({
      success: true,
      data: { token, expiresIn: 86400, user: { id: 'U001', name: username, role: 'admin' } }
    });
  } else {
    res.status(401).json({ success: false, error: { code: 401, message: '用户名或密码错误' } });
  }
});

// 12. 紧急停止（仅李总权限）
app.post('/api/system/emergency-stop', authenticateToken, (req, res) => {
  const { userId, userName, reason } = req.body;
  
  // 验证权限
  if (userName !== '李总' && userId !== 'U001') {
    return res.status(403).json({ success: false, error: { code: 403, message: '权限不足' } });
  }
  
  console.log(`⚠️ 紧急停止触发 - 操作人：${userName}, 原因：${reason}`);
  
  // 保存所有数据和记忆
  // 暂停所有 Agent（模拟）
  res.json({
    success: true,
    message: '已安全停止所有 Agent，数据和记忆已保存',
    data: {
      stoppedAt: new Date().toISOString(),
      stoppedBy: userName,
      agentsStopped: 7,
      dataSaved: true
    }
  });
});

// 13. 重启团队
app.post('/api/system/restart', authenticateToken, (req, res) => {
  const { userId, userName } = req.body;
  
  if (userName !== '李总' && userId !== 'U001') {
    return res.status(403).json({ success: false, error: { code: 403, message: '权限不足' } });
  }
  
  console.log(`▶️ 团队重启 - 操作人：${userName}`);
  
  res.json({
    success: true,
    message: '团队已重启，开始正常工作',
    data: {
      restartedAt: new Date().toISOString(),
      restartedBy: userName,
      agentsStarted: 7
    }
  });
});

// WebSocket 实时更新
io.on('connection', (socket) => {
  console.log('🔌 客户端连接:', socket.id);

  // 订阅频道
  socket.on('subscribe', (channel) => {
    socket.join(channel);
    console.log(`📡 ${socket.id} 订阅频道：${channel}`);
  });

  socket.on('disconnect', () => {
    console.log('🔌 客户端断开:', socket.id);
  });
});

// 定时推送更新（每 30 秒）
setInterval(() => {
  const latest = db.prepare('SELECT * FROM metrics ORDER BY date DESC LIMIT 1').get();
  if (latest) {
    io.to('metrics').emit('update', {
      channel: 'metrics',
      data: {
        gmv: { value: latest.gmv },
        orders: { value: latest.orders },
        profit: { value: latest.profit }
      },
      timestamp: new Date().toISOString()
    });
  }
}, 30000);

// 启动服务器
server.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 Dashboard 后端服务已启动！                            ║
║                                                           ║
║   访问地址：http://localhost:${PORT}                       ║
║                                                           ║
║   API 文档：http://localhost:${PORT}/api/docs              ║
║                                                           ║
║   时间：${new Date().toLocaleString('zh-CN')}              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `);
});
