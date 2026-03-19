# 🔐 OpenClaw 安全配置

**配置时间**: 2026-03-19 23:20  
**配置人**: 宝哥

---

## 🔑 API Key 安全

### 当前配置
- **API Key**: `sk-sp-cc2eaf42ae044f4f91e39d4b3a58c9af`
- **Base URL**: `https://coding.dashscope.aliyuncs.com/v1`
- **模型**: `qwen3.5-plus`

### 安全措施
1. ✅ API Key 存储在 `~/.openclaw/openclaw.json`（权限 600）
2. ✅ 不提交到 Git
3. ✅ 不在日志中明文显示
4. ✅ 使用 HTTPS 加密传输

---

## 🌐 网络安全

### 防火墙规则
```bash
# 仅允许本地访问
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 127.0.0.1 to any port 18800  # OpenClaw Gateway
sudo ufw enable
```

### 网络访问控制
- ✅ 仅允许本地回环访问 Gateway
- ✅ 禁止外部访问 API 端口
- ✅ 所有外部请求使用 HTTPS

---

## 📁 数据安全

### 文件权限
```bash
# 配置文件权限
chmod 600 ~/.openclaw/openclaw.json
chmod 700 ~/.openclaw/workspace

# 数据目录权限
chmod 700 /home/terrence/Desktop/龙虾 demo
chmod 700 /home/terrence/.openclaw/workspace/data
```

### 数据备份
- ✅ 每日自动备份到 `memory/` 目录
- ✅ Git 版本控制（敏感数据除外）
- ✅ 重要数据本地存储

---

## 📊 资讯数据安全

### 数据源验证
- ✅ 仅访问官方数据源（韭研公社、财联社、格隆汇）
- ✅ HTTPS 加密传输
- ✅ 不存储原始 HTML，仅存储提取的数据

### 推送安全
- ✅ 仅推送到宝哥飞书账号
- ✅ 不包含敏感信息（API key、密码等）
- ✅ 推送失败不重试超过 3 次

---

## 🔒 访问控制

### 用户权限
- ✅ 仅宝哥账号可访问
- ✅ 飞书 channel 配置为私有
- ✅ Cron 任务仅宝哥可修改

### 审计日志
```bash
# 查看 OpenClaw 日志
tail -f ~/.openclaw/logs/*.log

# 查看 Cron 执行记录
openclaw cron runs --id <job_id>
```

---

## ⚠️ 安全提醒

1. **不要分享 API key** - 包含在 openclaw.json 中
2. **不要开放 Gateway 端口** - 仅允许本地访问
3. **定期检查日志** - 查看异常访问
4. **定期更新配置** - 保持最新版本

---

## 📞 紧急处理

### API key 泄露
1. 立即在阿里云控制台撤销 key
2. 生成新 key
3. 更新 `~/.openclaw/openclaw.json`
4. 重启 Gateway

### 网络攻击
1. 立即停止 Gateway 服务
2. 检查防火墙规则
3. 查看日志定位攻击源
4. 报告宝哥

---

**安全配置完成时间**: 2026-03-19 23:20
