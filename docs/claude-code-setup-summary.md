# 🦐 虾老板 Claude Code Coding Plan 配置完成总结

**配置时间**: 2026-03-18 11:05  
**配置状态**: ✅ 完成

---

## ✅ 已完成的配置

### 1. 全局配置

**文件**: `~/.claude/claude-code-config.json`

```json
{
  "permissionMode": "plan",
  "model": "claude-sonnet-4-5",
  "effort": "high",
  "agents": {
    "coder": { ... },
    "reviewer": { ... },
    "planner": { ... }
  }
}
```

**作用**: 定义全局默认行为

---

### 2. 项目配置

**文件**: `.claude/settings.json`

```json
{
  "permissionMode": "plan",
  "model": "claude-sonnet-4-5",
  "effort": "high",
  "allowedTools": ["Bash", "Edit", "Write", "Read", "Glob", "Grep"]
}
```

**作用**: 项目级别的权限和工具控制

---

### 3. 使用指南文档

**文件**: `docs/claude-code-coding-plan.md` (5.9KB)

**内容**:
- 快速开始
- Coding Plan 模板
- 常用命令参考
- 项目配置方法
- 虾老板专用场景
- 安全最佳实践
- Effort 级别说明
- MCP 集成
- 常见问题
- 进阶技巧

---

### 4. 快速启动脚本

**文件**: `scripts/claude-code-start.sh`

**功能**:
- 检查安装状态
- 显示配置状态
- 快速使用帮助
- 交互式启动

**使用**:
```bash
./scripts/claude-code-start.sh
```

---

## 🎯 核心特性

### Plan 模式工作流程

```
用户输入任务
    ↓
Claude 分析需求
    ↓
生成执行计划 (Plan)  ← 用户审核这里!
    ↓
用户确认 (y/n)
    ↓
执行计划 (Coding)
    ↓
验证结果
    ↓
完成任务
```

**优点**:
- ✅ 避免盲目修改代码
- ✅ 用户可以提前审核计划
- ✅ 减少错误和返工
- ✅ 清晰的执行路径

---

## 🛠️ 自定义 Agents

### 1. Coder (编程助手)

**职责**: 写代码、修复 bug、实现功能

**Prompt**:
> "You are an expert coding assistant. You help users write, debug, and improve code."

**工具**: Bash, Edit, Write, Read, Glob, Grep

**使用**:
```bash
claude --agent coder "帮我写一个 API 端点"
```

---

### 2. Reviewer (代码审查员)

**职责**: 审查代码质量、安全性、性能

**Prompt**:
> "You are a senior code reviewer. You review code for quality, security, performance."

**工具**: Read, Glob, Grep

**使用**:
```bash
claude --agent reviewer "审查这段代码"
```

---

### 3. Planner (技术规划师)

**职责**: 分解复杂任务、制定计划

**Prompt**:
> "You are a technical planner. You break down complex tasks into manageable steps."

**工具**: Read, Write, Edit

**使用**:
```bash
claude --agent planner "帮我规划这个功能"
```

---

## 📋 使用示例

### 示例 1: 开发新功能

```bash
# Step 1: 规划
claude --agent planner "帮我规划一个自动备份功能"

# Step 2: 审核计划 (人工)
# Claude 输出计划，用户审核

# Step 3: 执行
claude --agent coder "按照计划实现自动备份功能"

# Step 4: 审查
claude --agent reviewer "审查刚才实现的备份功能"
```

---

### 示例 2: 修复 Bug

```bash
claude "我发现 Cron 作业有时会超时，帮我诊断并修复"
```

**Claude 会自动**:
1. 分析日志
2. 定位问题
3. 制定修复计划
4. 执行修复
5. 验证修复

---

### 示例 3: 代码重构

```bash
claude --allowed-tools "Read Edit Glob Grep" "帮我重构这个模块"
```

---

### 示例 4: 自我进化任务

```bash
# 规划自我进化功能
claude --agent planner "帮我规划一个 OA 自动修复功能"

# 执行
claude --agent coder "实现自动修复功能"

# 审查
claude --agent reviewer "审查代码"

# 测试
claude "帮我写测试用例并运行"
```

---

## 🔐 安全配置

### 推荐的权限设置

```json
{
  "permissionMode": "plan",  // 先规划后执行 (推荐)
  "disallowedTools": [
    "Bash(rm:-rf*)",        // 禁止递归删除
    "Bash(sudo:*)"          // 禁止 sudo
  ]
}
```

### 危险配置 (不推荐)

```bash
# ❌ 跳过所有权限检查
claude --permission-mode bypassPermissions

# ❌ 自动批准所有工具
claude --allow-dangerously-skip-permissions
```

---

## 📊 Effort 级别

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| `low` | 快速回答 | 简单查询 |
| `medium` | 平衡速度和质量 | 日常任务 |
| `high` | 深入思考 | 复杂任务 ✅ |
| `max` | 最大努力 | 关键任务 |

**推荐**: 使用 `high` 级别，平衡质量和速度。

---

## 🚀 快速启动

### 方法 1: 使用启动脚本

```bash
cd /home/terrence/.openclaw/workspace
./scripts/claude-code-start.sh
```

### 方法 2: 直接启动

```bash
# 交互式会话
claude

# 带 prompt
claude "帮我优化这个函数"

# 使用 agent
claude --agent coder "写一个 API"

# 继续会话
claude --continue
```

---

## 📁 文件结构

```
~/.claude/
├── claude-code-config.json    # 全局配置
└── sessions/                   # 会话历史

/home/terrence/.openclaw/workspace/
├── .claude/
│   └── settings.json          # 项目配置
├── docs/
│   ├── claude-code-coding-plan.md      # 使用指南
│   └── claude-code-setup-summary.md    # 配置总结
└── scripts/
    └── claude-code-start.sh   # 启动脚本
```

---

## 🎓 下一步

### 1. 试用 Plan 模式

```bash
claude "帮我写一个简单的函数"
```

观察 Claude 如何:
1. 分析需求
2. 制定计划
3. 等待你确认
4. 执行代码

### 2. 尝试不同 Agents

```bash
claude --agent planner "规划一个任务"
claude --agent coder "实现功能"
claude --agent reviewer "审查代码"
```

### 3. 配置 MCP (可选)

如果需要访问 GitHub、文件系统外部资源:

```bash
claude --mcp-config ~/.claude/mcp-config.json
```

### 4. 集成到工作流

将 Claude Code 集成到你的日常开发流程:
- 代码审查 → `claude --agent reviewer`
- 功能开发 → `claude --agent coder`
- 任务规划 → `claude --agent planner`

---

## 📚 相关文档

- [使用指南](docs/claude-code-coding-plan.md)
- [OpenClaw 源码解析](docs/openclaw-source-code-structure.md)
- [24 小时自动进化系统](docs/24h-auto-evolution-system.md)

---

## ❤️ 配置完成!

现在你可以：
- ✅ 使用 Plan 模式安全开发
- ✅ 使用自定义 Agents 提高效率
- ✅ 通过审核计划减少错误
- ✅ 集成到虾老板的自我进化流程

**开始编码吧！** 🦐💻
