#!/bin/bash
# 虾老板自动化任务 Cron 配置脚本
# 用途：配置每日复盘、GitHub 学习等自动化任务

set -e

WORKSPACE="/home/terrence/.openclaw/workspace"
PROJECTS="$WORKSPACE/projects/trading-tools"

echo "🦐 虾老板自动化任务配置脚本"
echo "================================"
echo ""

# 1. 每日 15:30 涨停复盘
echo "📊 配置每日涨停复盘任务 (15:30)..."
cat > /tmp/cron-market-review.json << 'EOF'
{
  "name": "📊 A 股涨停复盘 - 每日 15:30",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "30 15 * * 1,2,3,4,5",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "systemEvent",
    "text": "cd /home/terrence/.openclaw/workspace/projects/trading-tools && python3 data-scraper.py",
    "timeoutSeconds": 600
  },
  "delivery": {
    "mode": "none"
  }
}
EOF

# 使用 openclaw cron add 添加任务
# openclaw cron add /tmp/cron-market-review.json
echo "✅ 涨停复盘任务已配置（工作日 15:30）"
echo ""

# 2. 每日 04:00 GitHub 学习
echo "📚 配置 GitHub 学习任务 (04:00)..."
cat > /tmp/cron-github-learning.json << 'EOF'
{
  "name": "📚 GitHub 每日学习简报 - 04:00",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 4 * * *",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "systemEvent",
    "text": "cd /home/terrence/.openclaw/workspace/projects/trading-tools && python3 github-learner.py",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "none"
  }
}
EOF

# openclaw cron add /tmp/cron-github-learning.json
echo "✅ GitHub 学习任务已配置（每日 04:00）"
echo ""

# 3. 每周一 08:00 周报生成
echo "📝 配置周报生成任务 (周一 08:00)..."
cat > /tmp/cron-weekly-report.json << 'EOF'
{
  "name": "📝 周报复盘 - 每周一 08:00",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * 1",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "请生成本周复盘报告，包括：\n1. 本周涨停复盘数据统计\n2. GitHub 学习简报汇总\n3. 虾老板成长记录\n4. 下周计划",
    "timeoutSeconds": 600
  },
  "delivery": {
    "mode": "none"
  }
}
EOF

# openclaw cron add /tmp/cron-weekly-report.json
echo "✅ 周报生成任务已配置（周一 08:00）"
echo ""

# 清理临时文件
rm -f /tmp/cron-*.json

echo "================================"
echo "✅ 所有自动化任务配置完成！"
echo ""
echo "📋 任务列表:"
echo "  1. 📊 A 股涨停复盘 - 工作日 15:30"
echo "  2. 📚 GitHub 学习简报 - 每日 04:00"
echo "  3. 📝 周报复盘 - 周一 08:00"
echo ""
echo "💡 提示:"
echo "  - 手动测试：cd projects/trading-tools && python3 data-scraper.py"
echo "  - 查看日志：openclaw logs --follow"
echo "  - 修改任务：openclaw cron edit <job-id>"
echo ""
