# 🦐 虾老板 Coding Plan 使用指南

**创建时间**: 2026-03-18 11:05  
**Claude Code 版本**: Latest  
**配置模式**: Plan (先规划后执行)

---

## 🚀 快速开始

### 1. 基本用法

```bash
# 交互式会话 (plan 模式)
claude

# 非交互式执行 (带 prompt)
claude -p "帮我优化这个函数"

# 使用特定 agent
claude --agent coder "帮我写一个 API 端点"

# 继续之前的会话
claude --continue
```

### 2. Plan 模式工作流程

```
用户输入任务
    ↓
Claude 分析需求
    ↓
生成执行计划 (Plan)
    ↓
用户审核计划
    ↓
用户确认 (y/n)
    ↓
执行计划 (Coding)
    ↓
验证结果
    ↓
完成任务
```

---

## 📋 Coding Plan 模板

### 模板结构

```markdown
# Coding Plan: [任务名称]

## 🎯 目标
[清晰描述要完成的任务]

## 📝 当前状态
[描述当前代码状态/问题]

## 📐 执行计划

### Step 1: [步骤名称]
- [ ] 具体操作 1
- [ ] 具体操作 2
- 预期结果：...

### Step 2: [步骤名称]
- [ ] 具体操作 1
- [ ] 具体操作 2
- 预期结果：...

### Step 3: [步骤名称]
- [ ] 具体操作 1
- [ ] 具体操作 2
- 预期结果：...

## ⚠️ 风险评估
- [风险 1]: [描述 + 缓解措施]
- [风险 2]: [描述 + 缓解措施]

## ✅ 验收标准
- [ ] 标准 1
- [ ] 标准 2
- [ ] 标准 3

## 🧪 测试计划
- [测试 1]: [描述]
- [测试 2]: [描述]
```

---

## 🛠️ 常用命令

### 基础命令

```bash
# 启动交互式会话
claude

# 带 prompt 启动
claude "帮我修复这个 bug"

# 使用特定模型
claude --model claude-opus-4 "复杂任务"

# 使用特定 effort 级别
claude --effort high "重要任务"
```

### Agent 命令

```bash
# 使用 coder agent
claude --agent coder "写一个函数"

# 使用 reviewer agent
claude --agent reviewer "审查这段代码"

# 使用 planner agent
claude --agent planner "规划这个功能"

# 使用自定义 agent
claude --agents '{"myagent": {"description": "...", "prompt": "..."}}' "任务"
```

### 会话管理

```bash
# 继续之前的会话
claude --continue

# 继续特定会话
claude --resume <session-id>

# 列出会话
claude --resume

# 创建新会话 (不继续)
claude -n "新会话名称" "任务"
```

### 权限控制

```bash
# Plan 模式 (默认，推荐)
claude --permission-mode plan

# 自动接受编辑
claude --permission-mode acceptEdits

# 跳过所有权限检查 (危险！)
claude --permission-mode bypassPermissions

# 不询问直接执行
claude --permission-mode dontAsk
```

### 工具控制

```bash
# 允许特定工具
claude --allowed-tools "Bash(git:*) Edit"

# 禁止特定工具
claude --disallowed-tools "Bash(rm:*) Bash(sudo:*)"

# 自动批准工具 (危险！)
claude --allow-dangerously-skip-permissions
```

---

## 📁 项目配置

### 项目级设置 (`.claude/settings.json`)

```json
{
  "permissionMode": "plan",
  "model": "claude-sonnet-4-5",
  "effort": "high",
  "allowedTools": [
    "Bash",
    "Edit",
    "Write",
    "Read",
    "Glob",
    "Grep"
  ],
  "disallowedTools": [
    "Bash(rm:-rf*)",
    "Bash(sudo:*)"
  ]
}
```

### 项目级 Agents (`.claude/agents.json`)

```json
{
  "虾老板-coder": {
    "description": "虾老板专属 coding agent",
    "prompt": "你是虾老板的专属编程助手。你熟悉 OpenClaw 架构、Cron 调度、Memory 系统。你帮助虾老板开发新功能、修复 bug、优化代码。",
    "tools": ["Bash", "Edit", "Write", "Read", "Glob", "Grep"]
  },
  "虾老板-reviewer": {
    "description": "虾老板专属 code reviewer",
    "prompt": "你是虾老板的专属代码审查员。你审查代码质量、安全性、性能。你提供建设性反馈。",
    "tools": ["Read", "Glob", "Grep"]
  }
}
```

---

## 🎯 虾老板专用场景

### 场景 1: 开发新功能

```bash
# 使用 planner agent 先规划
claude --agent planner "帮我规划一个自动备份功能"

# 审核计划后，使用 coder agent 执行
claude --agent coder "按照计划实现自动备份功能"

# 使用 reviewer agent 审查
claude --agent reviewer "审查刚才实现的备份功能"
```

### 场景 2: 修复 Bug

```bash
# 描述 bug
claude "我发现 Cron 作业有时会超时，帮我诊断并修复"

# Claude 会:
# 1. 分析日志
# 2. 定位问题
# 3. 制定修复计划
# 4. 执行修复
# 5. 验证修复
```

### 场景 3: 代码重构

```bash
# 指定重构范围
claude --allowed-tools "Read Edit Glob Grep" "帮我重构这个模块，提高可读性"

# Claude 会:
# 1. 分析当前代码
# 2. 提出重构方案
# 3. 逐步重构
# 4. 确保功能不变
```

### 场景 4: 学习新技能

```bash
# 让 Claude 教你
claude "教我如何写一个 OpenClaw skill"

# Claude 会:
# 1. 解释 skill 结构
# 2. 提供示例代码
# 3. 指导你实现
# 4. 审查你的代码
```

---

## 🔐 安全最佳实践

### 1. 使用 Plan 模式

```bash
# ✅ 推荐：先审核计划
claude --permission-mode plan

# ❌ 不推荐：直接执行
claude --permission-mode bypassPermissions
```

### 2. 限制危险工具

```json
{
  "disallowedTools": [
    "Bash(rm:-rf*)",
    "Bash(sudo:*)",
    "Bash(curl:*|wget:*)"
  ]
}
```

### 3. 使用沙箱环境

```bash
# 在沙箱中使用 (无网络访问)
claude --allow-dangerously-skip-permissions
```

### 4. 审查所有更改

- 始终审核 Claude 提出的计划
- 检查所有代码修改
- 运行测试验证功能

---

## 📊 Effort 级别说明

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| `low` | 快速回答，少思考 | 简单问题、查询 |
| `medium` | 平衡速度和质量 | 日常任务 |
| `high` | 深入思考，全面分析 | 复杂任务、重要功能 |
| `max` | 最大努力，多次迭代 | 关键任务、架构设计 |

---

## 🧩 MCP 集成 (可选)

### 配置 MCP 服务器

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/terrence/.openclaw/workspace"]
    }
  }
}
```

### 使用 MCP 工具

```bash
# 加载 MCP 配置
claude --mcp-config ~/.claude/mcp-config.json

# 使用 GitHub MCP
claude "帮我创建一个 GitHub issue"
```

---

## 🐛 常见问题

### Q1: 如何跳过计划审核？

```bash
# 不推荐，但可以用
claude --permission-mode acceptEdits
```

### Q2: 如何更改默认模型？

编辑 `~/.claude/claude-code-config.json`:
```json
{
  "model": "claude-opus-4"
}
```

### Q3: 如何查看会话历史？

```bash
claude --resume
```

### Q4: 如何导出会话？

```bash
# 会话保存在 ~/.claude/sessions/
ls ~/.claude/sessions/
```

---

## 📝 示例：虾老板自我进化任务

### 任务：添加 OA 自动修复功能

```bash
# Step 1: 规划
claude --agent planner "帮我规划一个 OA 自动修复功能，当 Cron 作业失败时自动重试"

# Step 2: 审核计划 (人工审核)
# Claude 输出计划，用户审核

# Step 3: 执行
claude --agent coder "按照计划实现 OA 自动修复功能"

# Step 4: 审查
claude --agent reviewer "审查刚才实现的自动修复功能"

# Step 5: 测试
claude "帮我写测试用例并运行"
```

---

## 🎓 进阶技巧

### 1. 使用 System Prompt

```bash
# 追加 system prompt
claude --append-system-prompt "你是 OpenClaw 专家，熟悉 Cron/Memory/Session 系统"
```

### 2. 使用 JSON Schema 输出

```bash
# 结构化输出
claude --json-schema '{"type":"object","properties":{"name":{"type":"string"},"steps":{"type":"array"}}}' "规划这个任务"
```

### 3. 使用 Debug 模式

```bash
# 启用 debug
claude --debug

# 特定类别 debug
claude --debug "api,hooks"
```

### 4. 多目录支持

```bash
# 添加多个工作目录
claude --add-dir /home/terrence/.openclaw/workspace --add-dir /tmp/test
```

---

## 📚 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- [OpenClaw 文档](/home/terrence/.openclaw/workspace/docs/)
- [虾老板源码解析](/home/terrence/.openclaw/workspace/docs/openclaw-source-code-structure.md)

---

**持续更新中...** 🦐
