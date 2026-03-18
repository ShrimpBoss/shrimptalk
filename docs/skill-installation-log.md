# 🦐 OpenClaw Skills 安装记录

**安装时间**: 2026-03-18 14:20  
**目标 Skills**: OpenViking, self-improving-agent, skill-vetter

---

## ✅ 已安装 (部分完成)

### 1. OpenViking (向量记忆系统)

**仓库**: https://github.com/swizardlv/openclaw_openviking_skill  
**安装位置**: `/home/terrence/.npm-global/lib/node_modules/openclaw/skills/openviking/`  
**状态**: 🟡 文件已安装，待配置

**功能**:
- 语义搜索文档库
- 自动生成 L0/L1/L2 三级摘要
- 虚拟文件系统浏览 (`viking://resources/...`)
- 批量索引目录文件
- 使用 NVIDIA NIM API (免费)

**安装步骤**:
1. ✅ Git clone 到 skills 目录
2. ⏳ pip install openviking (超时，需重试)
3. ✅ 创建配置文件 `~/.openviking/ov.conf`
4. ⏳ 设置环境变量 `OPENVIKING_CONFIG_FILE`

**配置状态**:
```json
{
  "embedding": {
    "api_base": "https://integrate.api.nvidia.com/v1",
    "api_key": "nvapi-placeholder",  // 需要替换为真实 API key
    "provider": "openai",
    "dimension": 4096,
    "model": "nvidia/nv-embed-v1"
  },
  "vlm": {
    "api_base": "https://integrate.api.nvidia.com/v1",
    "api_key": "nvapi-placeholder",  // 需要替换为真实 API key
    "provider": "openai",
    "model": "meta/llama-3.3-70b-instruct"
  }
}
```

**下一步**:
- [ ] 重试 pip install openviking
- [ ] 获取 NVIDIA API key (https://build.nvidia.com/)
- [ ] 更新 `~/.openviking/ov.conf` 中的 API key
- [ ] 设置环境变量
- [ ] 测试技能

---

## ⏳ 待安装

### 2. Self-Improving-Agent (自改进 Agent)

**目标功能**: 让 Agent 能够从历史任务中学习并自我改进

**搜索状态**: 🔍 需要找到正确的仓库地址

**可能的位置**:
- 待用户确认具体仓库

---

### 3. Skill-Vetter (技能审查工具)

**目标功能**: 审查和验证 Skills 的质量

**搜索状态**: 🔍 需要找到正确的仓库地址

**可能的位置**:
- 待用户确认具体仓库

---

## 📋 安装计划

### P0 (今日)
- [x] OpenViking Git clone
- [ ] OpenViking pip 安装完成 (需重试)
- [ ] 获取 NVIDIA API key
- [ ] 配置 OpenViking
- [ ] 测试 OpenViking

### P1 (待确认)
- [ ] 找到 self-improving-agent 正确地址
- [ ] 安装 self-improving-agent
- [ ] 找到 skill-vetter 正确地址
- [ ] 安装 skill-vetter

### P2 (本周)
- [ ] 配置所有 Skills
- [ ] 集成到工作流
- [ ] 测试效果

---

## 🎯 预期效果

### OpenViking
- ✅ 语义搜索文档库
- ✅ 自动摘要生成
- ✅ Token 节省 (只加载需要的内容)
- ✅ 支持大规模文档管理

### Self-Improving-Agent
- ✅ 从历史任务学习
- ✅ 自动优化 Prompt
- ✅ 持续改进表现

### Skill-Vetter
- ✅ 审查 Skills 质量
- ✅ 验证最佳实践
- ✅ 提供改进建议

---

**持续更新中...** 🦐
