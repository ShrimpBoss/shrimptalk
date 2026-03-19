# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

### 宝哥常看资讯源

**韭研公社** (https://www.jiuyangongshe.com) — 宝哥最重要的资讯源！
- 重点作者: 盘前纪要、开盘必读、题材催化剂、财闻私享、八卦猫V、概念百科
- 文章 URL 格式: /p/{article_id}（但需要从首页 HTML 提取 article_id）
- 首页可直接 web_fetch 抓取文章摘要（content 字段在 HTML 的 JS 数据中）
- 用户页面: /u/{user_id}（内容通过 JS 动态加载）

**财联社** (https://www.cls.cn/telegraph) — 电报快讯、早间精选
**格隆汇** (https://www.gelonghui.com) — 实时快讯流
**选股宝** — 涨停表格数据（最完整）
**短线侠** — 情绪指标/板块强度

**公众号（微信封闭，需宝哥转发）:**
- 短线侠复盘
- 新生代投研社（作者：桑田）
- 洞见终局

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
