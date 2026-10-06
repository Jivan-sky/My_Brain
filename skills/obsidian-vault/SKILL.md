---
name: obsidian-vault
description: 查看 Obsidian 知识库结构、定位和导航笔记。用于理解 vault 目录组织与命名约定。
---

# Obsidian Vault

## Vault 位置

`{{VAULT_PATH}}/`

## 目录结构

```
{{VAULT_PATH}}/
├── 00_Inbox/             — 待处理条目
├── 01_Daily/YYYY-MM/     — 日报（按月分层）
├── 02_Reports/周报|月报/  — 周报/月报
├── 03_Knowledge/         — 知识（01-踩坑_漏点 / 02-部署_运维 / 03-接口_数据 / 04-技术栈_归纳）
└── 04_Projects/          — 项目决策/里程碑（按项目子目录，见 _MOC.md）
```

## 命名与约定

- 日报文件名：`YYYY-MM-DD.md`（`01_Daily/YYYY-MM/`）
- 周报文件名：`YYYY-WXX.md`（`02_Reports/周报/YYYY/`）
- 月报文件名：`YYYY-MM.md`（`02_Reports/月报/YYYY/`）
- 所有 note 带 frontmatter：`title` / `created` / `tags`。`tags` 里**恰好 1 个** `type/`，按所在目录取 `type/daily` / `type/weekly` / `type/monthly` / `type/meeting` / `type/knowledge` / `type/project` / `type/moc` / `type/inbox`（旧写法 `type/知识捕获` 已废弃）
- 其余 tag 只能从 vault 根目录 `_词表.md` 的受控词表里选

## 工作流

### 定位笔记

```bash
find "{{VAULT_PATH}}/" -name "*.md" | grep -i "关键词"
grep -rl "关键词" "{{VAULT_PATH}}/" --include="*.md"
```

或直接对 `{{VAULT_PATH}}` 用 Glob/Grep 工具。

### 写入规范

- 日报/周报/月报 → 对应 report skill（`/daily-report` `/weekly-report` `/monthly-report`）
- 知识 → `/save-knowledge`
- 项目决策 → `/save-project`
- 综合提取 → `/save-to-brain`
