# 📋 任务清单 - GitHub 授权登录

**创建时间**: 2026-03-21 12:20  
**优先级**: P0（最高优先级）  
**状态**: 🔄 进行中

---

## ✅ 已完成步骤

### 1. 尝试安装 GitHub CLI
- ❌ `apt-get install gh` - 失败（仓库目录问题）
- ❌ `snap install gh` - 失败（snap 未安装）
- ❌ `wget + dpkg` - 失败（触发文件问题）
- ❌ `curl + tar` - 失败（下载不完整）

### 2. 当前状态
- gh 未安装成功
- 需要寻找其他安装方式

---

## 📝 待完成任务

### 任务 1: 安装 GitHub CLI ✅ 进行中
**方案 A**: 手动下载二进制文件
```bash
cd /tmp
curl -LO https://github.com/cli/cli/releases/download/v2.40.1/gh_2.40.1_linux_amd64.tar.gz
tar xvf gh_2.40.1_linux_amd64.tar.gz
sudo cp gh_2.40.1_linux_amd64/bin/gh /usr/local/bin/
gh --version
```

**方案 B**: 使用官方安装脚本
```bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y
```

### 任务 2: GitHub 设备授权 🔄 等待验证码
- 已打开浏览器：https://github.com/login/device
- 已登录账号：ShrimpBoss
- 状态：等待输入 8 位验证码

**下一步**:
1. 在另一个设备/标签页打开 https://github.com/login/device
2. 获取显示的 8 位验证码
4. 在浏览器中输入验证码完成授权

### 任务 3: 验证授权 ✅ 待执行
```bash
gh auth status
gh repo list
```

### 任务 4: 配置 Git 使用 GitHub CLI ✅ 待执行
```bash
git config --global credential.helper '!gh auth git-credential'
```

---

## 🎯 执行计划

1. **立即执行**: 任务 1（安装 gh）- 使用方案 A
2. **并行进行**: 任务 2（设备授权）- 等待宝哥提供验证码
3. **完成后**: 任务 3 + 任务 4（验证 + 配置）

---

## 📊 进度

- [ ] 任务 1: 安装 GitHub CLI (0%)
- [ ] 任务 2: GitHub 设备授权 (50% - 已打开页面)
- [ ] 任务 3: 验证授权 (0%)
- [ ] 任务 4: 配置 Git (0%)

**总体进度**: 12.5%

---

**备注**: 宝哥提到其他账号也是这样授权的，说明设备授权流程是正确的。需要找到之前授权时显示的验证码或者重新发起授权。
