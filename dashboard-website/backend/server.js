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
`);

// 初始化模拟数据
const initMockData = () => {
  // 检查是否已有数据
  const count = db.prepare('SELECT COUNT(*) as count FROM metrics').get();
  if (count.count > 0) return;

  // 插入指标数据
  const metrics = [
    { date: '2026-03-02', gmv: 890, orders: 32, profit: 320, roas: 2.8, rating: 91, shipped: 30 },
    { date: '2026-03-03', gmv: 1020, orders: 38, profit: 380, roas: 2.9, rating: 92, shipped: 35 },
    { date: '2026-03-04', gmv: 1150, orders: 42, profit: 425, roas: 3.0, rating: 92, shipped: 40 },
    { date: '2026-03-05', gmv: 950, orders: 35, profit: 355, roas: 2.7, rating: 93, shipped: 33 },
    { date: '2026-03-06', gmv: 1280, orders: 48, profit: 478, roas: 3.1, rating: 93, shipped: 45 },
    { date: '2026-03-07', gmv: 1450, orders: 52, profit: 542, roas: 3.3, rating: 94, shipped: 50 },
    { date: '2026-03-08', gmv: 1234, orders: 45, profit: 487, roas: 3.2, rating: 94, shipped: 42 },
  ];

  const insertMetric = db.prepare(`
    INSERT INTO metrics (date, gmv, orders, profit, roas, rating, shipped)
    VALUES (@date, @gmv, @orders, @profit, @roas, @rating, @shipped)
  `);

  metrics.forEach(m => insertMetric.run(m));

  // 插入产品数据
  const products = [
    { name: '减压魔方', image: '🎲', gross_margin: 45, trend_score: 92, trend_level: 4, supplier: 'CJ Dropshipping', cost: 8.5, suggested_price: 24.99 },
    { name: '情绪宣泄球', image: '💪', gross_margin: 52, trend_score: 88, trend_level: 3, supplier: 'AliExpress', cost: 5.2, suggested_price: 19.99 },
    { name: '香薰蜡烛', image: '🕯️', gross_margin: 38, trend_score: 95, trend_level: 5, supplier: 'CJ Dropshipping', cost: 12.0, suggested_price: 29.99 },
    { name: '解压捏捏乐', image: '🧸', gross_margin: 48, trend_score: 85, trend_level: 3, supplier: 'AliExpress', cost: 6.8, suggested_price: 18.99 },
    { name: '情绪日记本', image: '📔', gross_margin: 55, trend_score: 78, trend_level: 2, supplier: 'CJ Dropshipping', cost: 4.5, suggested_price: 15.99 },
  ];

  const insertProduct = db.prepare(`
    INSERT INTO products (name, image, gross_margin, trend_score, trend_level, supplier, cost, suggested_price)
    VALUES (@name, @image, @gross_margin, @trend_score, @trend_level, @supplier, @cost, @suggested_price)
  `);

  products.forEach(p => insertProduct.run(p));

  // 插入任务数据
  const tasks = [
    { department: '产品部', task: '本周选品', progress: 80, current: 40, target: 50, unit: '款' },
    { department: '营销部', task: '广告活动', progress: 100, current: 5, target: 5, unit: '个' },
    { department: '内容部', task: '素材产出', progress: 60, current: 12, target: 20, unit: '篇' },
    { department: '订单部', task: '订单处理', progress: 75, current: 42, target: 56, unit: '单' },
  ];

  const insertTask = db.prepare(`
    INSERT INTO tasks (department, task, progress, current, target, unit)
    VALUES (@department, @task, @progress, @current, @target, @unit)
  `);

  tasks.forEach(t => insertTask.run(t));

  // 插入审批数据
  const approvals = [
    { type: 'product_listing', title: '新品上架审批 - 3 款', description: '3 款新品符合选品标准，申请上架', priority: 'normal', details: JSON.stringify({ productIds: [1, 2, 3] }) },
    { type: 'budget_adjustment', title: '广告预算调整', description: '从 $500/天 → $800/天', priority: 'high', details: JSON.stringify({ from: 500, to: 800, reason: 'ROAS 持续>3.0，建议加大投放' }) },
    { type: 'supplier_contract', title: '供应商合作 - CJ Dropshipping 协议', description: '账期：15 天，返点：3%', priority: 'normal', details: JSON.stringify({ supplier: 'CJ Dropshipping', terms: '15 天账期，3% 返点' }) },
  ];

  const insertApproval = db.prepare(`
    INSERT INTO approvals (type, title, description, priority, details)
    VALUES (@type, @title, @description, @priority, @details)
  `);

  approvals.forEach(a => insertApproval.run(a));

  // 插入建议数据
  const suggestions = [
    { title: '增加情人节主题素材', content: '情人节期间增加相关主题素材', category: '运营优化', priority: 'high', status: 'completed', assignee: '小方', due_date: '2026-02-10', completed_at: '2026-02-10 15:30:00' },
    { title: '拓展 TikTok 渠道', content: '建议加大 TikTok 渠道投入，测试新的广告格式', category: '运营优化', priority: 'medium', status: 'in_progress', assignee: '小方', due_date: '2026-02-20' },
    { title: '研究新品类 - 情绪卡片', content: '研究情绪卡片新品类的市场潜力', category: '产品建议', priority: 'low', status: 'pending', assignee: '小智', due_date: '2026-03-15' },
  ];

  const insertSuggestion = db.prepare(`
    INSERT INTO suggestions (title, content, category, priority, status, assignee, due_date, completed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);

  suggestions.forEach(s => insertSuggestion.run(
    s.title, s.content, s.category, s.priority, s.status, s.assignee, s.due_date, s.completed_at || null
  ));

  // 插入安全状态数据
  db.prepare(`
    INSERT INTO security_status (cpu_usage, memory_usage, disk_usage, network_status, api_calls, security_events, status)
    VALUES (35, 62, 45, 'normal', 1234, 0, 'normal')
  `).run();

  console.log('✅ 模拟数据初始化完成');
};

initMockData();

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

// 2. 获取 Agent 状态 - 完整 10 人团队
app.get('/api/agents/status', authenticateToken, (req, res) => {
  res.json({
    success: true,
    data: {
      agents: [
        // 核心管理层
        { name: '王总', role: '副经理', status: 'running', task: '待审核：3 项 · 预警：0', pendingReview: 3, alerts: 0, efficiency: 95 },
        { name: '小安', role: '安全运维', status: 'running', task: '系统监控 · 安全审计', systemLoad: 35, security: '正常', exceptions: 0 },
        
        // 业务团队
        { name: '小智', role: '产品', status: 'running', task: '今日选品：15 款 · 待审核：3 款', completedToday: 15, pendingReview: 3, exceptions: 0 },
        { name: '小方', role: '营销', status: 'running', task: '广告花费：$156 · ROAS: 3.2', adSpend: 156, roas: 3.2, exceptions: 0 },
        { name: '小文', role: '内容', status: 'running', task: '今日产出：8 篇 · 通过率：100%', completedToday: 8, passRate: 100, exceptions: 0 },
        { name: '订单专员', role: '订单', status: 'processing', task: '待处理：5 单 · 异常：2 单', pending: 5, exceptions: 2 },
        { name: '小财', role: '财务', status: 'running', task: '现金流：45 天 · 预算使用：62%', cashFlow: 45, budgetUsed: 62, exceptions: 0 },
        
        // 支持团队
        { name: '小服', role: '客服', status: 'running', task: '待回复：12 条 · 好评率：98%', pending: 12, rating: 98, exceptions: 0 },
        { name: '小仓', role: '仓储', status: 'running', task: '待发货：8 单 · 库存：充足', pending: 8, stock: '充足', exceptions: 0 },
        { name: '小研', role: '数据分析', status: 'running', task: '日报已生成 · 周报处理中', dailyReport: '完成', weeklyReport: '进行中', exceptions: 0 }
      ]
    }
  });
});

// 3. 获取选品推荐
app.get('/api/products/recommended', authenticateToken, (req, res) => {
  const limit = parseInt(req.query.limit) || 15;
  const products = db.prepare('SELECT * FROM products LIMIT ?').all(limit);
  
  res.json({
    success: true,
    data: {
      products: products.map(p => ({
        id: p.id.toString(),
        name: p.name,
        image: p.image,
        grossMargin: p.gross_margin,
        trendScore: p.trend_score,
        trendLevel: p.trend_level,
        supplier: p.supplier,
        cost: p.cost,
        suggestedPrice: p.suggested_price,
        status: p.status,
        submittedAt: p.submitted_at
      })),
      total: products.length
    }
  });
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

// 4. 获取待审批事项
app.get('/api/approvals/pending', authenticateToken, (req, res) => {
  const approvals = db.prepare("SELECT * FROM approvals WHERE status = 'pending'").all();
  
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

// 8. 获取工作进度
app.get('/api/tasks/progress', authenticateToken, (req, res) => {
  const tasks = db.prepare('SELECT * FROM tasks').all();
  
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
});

// 9. 获取销售趋势
app.get('/api/sales/trend', authenticateToken, (req, res) => {
  const days = parseInt(req.query.days) || 7;
  const metrics = db.prepare('SELECT * FROM metrics ORDER BY date DESC LIMIT ?').all(days);
  
  res.json({
    success: true,
    data: {
      dates: metrics.map(m => m.date.slice(5)).reverse(),
      gmv: metrics.map(m => m.gmv).reverse(),
      orders: metrics.map(m => m.orders).reverse(),
      profit: metrics.map(m => m.profit).reverse()
    }
  });
});

// 10. 获取安全状态
app.get('/api/security/status', authenticateToken, (req, res) => {
  const status = db.prepare('SELECT * FROM security_status ORDER BY updated_at DESC LIMIT 1').get();
  
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
