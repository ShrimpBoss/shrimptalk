# 🎨 2026-03-18 AI 图像生成与提示词工程学习总结

**学习时间**: 14:00 - 15:00 (2026-03-18)  
**学习主题**: AI 图像生成工具与提示词工程 (Midjourney/Stable Diffusion/DALL-E 3)  
**学习时长**: 60 分钟

---

## 📚 学习内容概览

今天深入学习了 AI 图像生成领域的核心工具和提示词 (Prompt) 工程技巧，这是昨天 AI 视频学习的基础和延伸。

---

## 💡 核心收获

### 1. Midjourney v6/v7 —— 艺术创作首选 ✅

**技术定位**：
- **v6** (2024 发布): 大幅提升真实感和文字渲染能力
- **v7** (2025 发布): 引入新模型架构，支持更复杂的构图和风格控制
- 当前艺术创作、概念设计、插画领域的首选工具

**核心优势**：
| 特性 | 说明 |
|------|------|
| 艺术风格 | 最强，擅长油画、水彩、概念艺术 |
| 真实感 | v6+ 后大幅提升，接近照片级 |
| 文字渲染 | v6 开始支持准确文字显示 |
| 构图控制 | 支持 --ar 宽高比、--zoom 缩放、--pan 平移 |
| 一致性 | --cref 角色参考、--sref 风格参考 |

**定价结构**（2026 年最新）：
- **Basic**: $10/月，200 积分 ≈ 200 次快速生成
- **Standard**: $30/月，15 小时快速生成 + 无限慢速
- **Pro**: $60/月，30 小时快速生成 + 隐身模式
- **Mega**: $120/月，60 小时快速生成 + 隐身模式

**关键参数**：
```
--ar 16:9        # 宽高比 (16:9, 4:3, 1:1, 9:16)
--v 6.1          # 模型版本
--stylize 250    # 风格化程度 (0-1000)
--chaos 30       # 变化程度 (0-100)
--cref URL       # 角色参考图
--sref URL       # 风格参考图
--no hands       # 排除元素
--tile           # 生成无缝纹理
```

---

### 2. 提示词工程核心框架 ✅

**万能公式**：
```
[主体] + [细节描述] + [环境/背景] + [光线] + [构图/镜头] + [风格/艺术家] + [参数]
```

**详细拆解**：

| 元素 | 示例 | 作用 |
|------|------|------|
| **主体** | 一只橘猫、一位女战士、未来城市 | 明确画面核心 |
| **细节** | 毛茸茸的、穿着盔甲、霓虹灯闪烁 | 增加丰富度 |
| **环境** | 森林中、战场上、雨夜街道 | 设定场景 |
| **光线** | 柔和自然光、戏剧性侧光、霓虹灯 | 营造氛围 |
| **构图** | 特写、广角、鸟瞰视角、三分法 | 控制视角 |
| **风格** | 赛博朋克、印象派、吉卜力风格 | 定义美学 |
| **参数** | --ar 16:9 --v 6.1 --stylize 300 | 技术控制 |

**高质量 Prompt 示例**：
```
A majestic orange tabby cat sitting on a sunny windowsill,
fluffy fur glowing in warm natural light,
cozy living room with plants in background,
soft morning atmosphere, photorealistic,
shot on Canon EOS R5, 50mm lens, f/1.8
--ar 16:9 --v 6.1 --stylize 250 --style raw
```

**负面提示词 (Negative Prompts)**：
```
--no blurry, deformed hands, extra fingers, 
ugly, watermark, text, signature, low quality
```

---

### 3. 电商应用场景实战 ✅

**产品摄影替代方案**：
```
Professional product photography of [产品],
clean white background, studio lighting,
sharp focus, commercial quality, 8K
--ar 1:1 --v 6.1 --style raw
```

**广告素材生成**：
```
Lifestyle photo of [产品] being used by happy customer,
modern home setting, warm natural light,
authentic candid moment, commercial photography
--ar 4:5 --v 6.1
```

**品牌视觉统一**：
1. 创建 1 张基准风格图
2. 提取风格参考 URL
3. 使用 `--sref URL` 保持所有图片风格一致
4. 建立品牌视觉库

**社交媒体内容矩阵**：
| 平台 | 推荐比例 | 风格建议 |
|------|----------|----------|
| Instagram Post | 1:1 or 4:5 | 精致、高饱和 |
| Instagram Story | 9:16 | 竖版、沉浸式 |
| Facebook Ad | 1:1 or 1.91:1 | 清晰、信息明确 |
| TikTok Cover | 9:16 | 吸引眼球、有文字 |
| Pinterest | 2:3 or 9:16 | 垂直、灵感类 |

---

### 4. 其他主流工具对比 ✅

| 工具 | 优势 | 劣势 | 适用场景 | 定价 |
|------|------|------|----------|------|
| **Midjourney** | 艺术性最强、社区活跃 | 需 Discord、学习曲线 | 创意创作、概念艺术 | $10-120/月 |
| **DALL-E 3** | 理解能力强、文字准确 | 艺术性一般 | 需要准确文字的场景 | $20/月 (ChatGPT Plus) |
| **Stable Diffusion** | 免费开源、可本地部署 | 需要技术能力 | 批量生产、定制化 | 免费/自建成本 |
| **Adobe Firefly** | 商业安全、集成 PS | 创意性有限 | 商业设计工作流 | $20/月 (Creative Cloud) |
| **Leonardo.ai** | 游戏资产强、免费额度 | 知名度较低 | 游戏开发、3D 素材 | 免费+$10-48/月 |

**工具选择建议**：
- 🎨 **创意优先** → Midjourney
- 📝 **文字准确** → DALL-E 3
- 💰 **预算有限** → Stable Diffusion / Leonardo.ai 免费档
- 🏢 **商业安全** → Adobe Firefly
- 🎮 **游戏开发** → Leonardo.ai

---

## 🎯 可立即应用的行动

### 行动项：创建电商产品图片库

**步骤**：
1. **选择 3 款主力产品** → 从现有 18 款产品中选出
2. **为每款产品写 5 个 Prompt** → 不同角度/场景/风格
3. **使用 Midjourney 生成** → 每款产品生成 10-15 张图
4. **筛选最佳图片** → 每款选出 3 张最满意的
5. **建立图片库** → 按产品/场景分类存储
6. **A/B 测试** → 用新图替换旧图，观察点击率变化

**示例 Prompt 模板库**：

```
# 模板 1: 产品特写
Professional product shot of [产品], 
isolated on pure white background, 
studio lighting, ultra detailed, 8K
--ar 1:1 --v 6.1 --style raw

# 模板 2: 使用场景
Lifestyle photo of [产品] in use, 
modern [场景] setting, natural light, 
authentic moment, commercial quality
--ar 4:5 --v 6.1

# 模板 3: 社交媒体
Eye-catching social media post featuring [产品],
vibrant colors, trendy composition, 
designed for Instagram engagement
--ar 4:5 --v 6.1 --stylize 400

# 模板 4: 广告 Banner
Marketing banner with [产品],
clean design, space for text overlay,
professional advertising photography
--ar 16:9 --v 6.1

# 模板 5: 品牌故事
Artistic interpretation of [品牌理念],
featuring [产品] as focal point,
emotional storytelling, cinematic lighting
--ar 16:9 --v 6.1 --stylize 500
```

**预期产出**：
- 15 张高质量产品图片 (3 款 × 5 张)
- 1 份 Prompt 模板库 (可直接复用)
- 建立图片管理流程

---

## 📊 技能评估

| 技能 | 熟练度 | 说明 |
|------|--------|------|
| Midjourney 平台 | ⭐⭐⭐⭐☆ | 理解产品和定价 |
| Prompt 工程框架 | ⭐⭐⭐⭐☆ | 掌握核心公式 |
| 电商场景应用 | ⭐⭐⭐⭐☆ | 可直接套用模板 |
| 多工具对比 | ⭐⭐⭐⭐⭐ | 清楚各工具定位 |
| 参数调优 | ⭐⭐⭐☆☆ | 理解基础参数，需实践 |

**综合熟练度**: ⭐⭐⭐⭐☆ (4/5) — 理论扎实，可立即应用

---

## 📁 相关资源

- Midjourney 官网：https://midjourney.com/
- Midjourney 文档：https://docs.midjourney.com/
- Prompt 社区：https://promptbase.com/
- 参数参考：https://docs.midjourney.com/docs/parameter-list
- 灵感画廊：https://www.midjourney.com/showcase

---

## 🔗 与昨天学习的关联

**AI 视频 + AI 图像 = 完整内容工作流**：
```
AI 图像 (Midjourney) → 生成产品图/场景图
         ↓
AI 视频 (Runway) → Image to Video 让图片动起来
         ↓
传统剪辑 → 添加音乐、文字、转场
         ↓
发布 → TikTok/Instagram/YouTube
```

**协同效应**：
- Midjourney 生成的图片可作为 Runway 的输入素材
- 统一的视觉风格贯穿图片和视频
- 大幅降低内容制作成本和时间

---

## 🔮 后续学习计划

**明天目标**：
- [ ] 实际注册 Midjourney 并生成第一批产品图
- [ ] 测试不同 Prompt 模板的效果
- [ ] 建立个人 Prompt 库 (20+ 模板)

**本周目标**：
- [ ] 完成 3 款产品的图片库建设
- [ ] 用 Runway 将 3 张图片转为视频
- [ ] 制作 1 条完整的 AI 生成广告视频

**长期目标**：
- [ ] 建立可复用的内容生产 SOP
- [ ] 培训团队成员使用 AI 工具
- [ ] 探索 AI 内容商业化变现

---

## 💭 学习感悟

AI 图像生成已经从"玩具"变成"工具"。对于电商从业者来说，这不仅仅是省钱，更是**速度优势**和**创意优势**。

传统产品摄影：选摄影师 → 预约档期 → 布置场景 → 拍摄 → 修图 = 1-2 周，$500-2000
AI 产品摄影：写 Prompt → 生成 → 筛选 = 1-2 小时，$0.10-1

**关键不是追求完美，而是快速迭代**。生成 100 张图选出最好的 3 张，比花 2 周拍 3 张图更高效。

对于跨境电商来说，这意味着可以：
- 快速测试不同视觉风格
- 为不同市场定制本地化素材
- 保持高频内容更新
- 小成本验证新产品的市场反应

**工具是杠杆，创意是支点**。掌握工具后，真正的竞争在于创意和策略。

---

**学习状态**: ✅ 完成  
**连续学习**: Day 2 (AI 工具系列)  
**下次学习**: 2026-03-19 (文案/剧本写作或数据分析)  
**文档位置**: `memory/2026-03-18-learning-AI-image-prompt-engineering.md`
