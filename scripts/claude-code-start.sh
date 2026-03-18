#!/bin/bash

# 🦐 虾老板 Coding Plan 快速启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🦐 虾老板 Coding Plan 启动器          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 检查 Claude Code 是否安装
if ! command -v claude &> /dev/null; then
    echo -e "${RED}❌ Claude Code 未安装${NC}"
    echo "请先运行：npm install -g @anthropic-ai/claude-code"
    exit 1
fi

echo -e "${GREEN}✅ Claude Code 已安装${NC}"
echo ""

# 显示配置状态
echo -e "${YELLOW}📋 配置状态:${NC}"

if [ -f ~/.claude/claude-code-config.json ]; then
    echo -e "  ${GREEN}✅${NC} 全局配置：~/.claude/claude-code-config.json"
else
    echo -e "  ${RED}❌${NC} 全局配置不存在"
fi

if [ -f .claude/settings.json ]; then
    echo -e "  ${GREEN}✅${NC} 项目配置：.claude/settings.json"
else
    echo -e "  ${YELLOW}⚠️${NC} 项目配置不存在 (将使用全局配置)"
fi

echo ""

# 显示使用帮助
echo -e "${YELLOW}📖 快速使用:${NC}"
echo ""
echo "  # 交互式会话 (Plan 模式)"
echo "  claude"
echo ""
echo "  # 带 prompt 启动"
echo "  claude \"帮我修复这个 bug\""
echo ""
echo "  # 使用特定 agent"
echo "  claude --agent coder \"写一个函数\""
echo ""
echo "  # 继续之前的会话"
echo "  claude --continue"
echo ""
echo "  # 查看会话历史"
echo "  claude --resume"
echo ""

echo -e "${YELLOW}🎯 常用 Agents:${NC}"
echo ""
echo "  - coder:     编程助手 (写代码/修复 bug)"
echo "  - reviewer:  代码审查员 (审查代码质量)"
echo "  - planner:   技术规划师 (规划复杂任务)"
echo ""

echo -e "${YELLOW}⚙️  权限模式:${NC}"
echo ""
echo "  - plan:           先规划后执行 (推荐，默认)"
echo "  - acceptEdits:    自动接受编辑"
echo "  - dontAsk:        不询问直接执行"
echo "  - bypassPermissions: 跳过所有权限检查 (危险!)"
echo ""

# 询问是否启动
echo -ne "${BLUE}是否启动 Claude Code? (y/n): ${NC}"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo -e "${GREEN}🚀 启动 Claude Code...${NC}"
    echo ""
    claude "$@"
else
    echo ""
    echo -e "${YELLOW}👋 已取消启动${NC}"
fi
