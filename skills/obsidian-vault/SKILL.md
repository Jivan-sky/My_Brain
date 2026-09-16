---
name: obsidian-vault
description: 查看 Obsidian 知识库结构、定位和导航笔记。用于理解 vault 目录组织与命名约定。
---

# Obsidian Vault

## Vault 位置

`{{VAULT_PATH}}\`

## 目录结构

```
{{VAULT_PATH}}\
├── 00_Inbox\             — 待处理条目
├── 01_Daily\YYYY-MM\     — 日报（按月分层）
├── 02_Reports\周报|月报\  — 周报/月报
├── 03_Knowledge\         — 知识（01-AI与Claude / 02-工具链 / 03-业务域 / 04-开发与运维）
└── 04_Projects\          — 项目决策/里程碑（按项目子目录）
```

## 命名与约定

- 日报文件名：`YYYY-MM-DD.md`（`01_Daily\YYYY-MM\`）
- 周报文件名：`YYYY-WXX.md`（`02_Reports\周报\YYYY\`）
- 月报文件名：`YYYY-MM.md`（`02_Reports\月报\YYYY\`）
- 所有 note 带 frontmatter：`title` / `created` / `tags`（tags 至少含 `type/知识捕获`）

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
