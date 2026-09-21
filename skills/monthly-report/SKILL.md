---
name: monthly-report
description: 汇总本月周报与日报生成月报,写入 Obsidian 02_Reports/月报。触发词:月报、月度总结、本月总结。
---

# 技能: monthly-report

## 使用方式
用户输入 `/monthly-report` 或 `/monthly-report 2026-08`。

## 功能描述
读取本月（YYYY-MM）的 `02_Reports/周报/` 周报 + `01_Daily/` 日报，汇总生成本月月报，写入 `02_Reports/月报/`。**默认精简版**。

## Vault 位置

`{{VAULT_PATH}}/`（结构见 `/obsidian-vault` skill）

## 目录结构

```
{{VAULT_PATH}}/
├── 01_Daily/YYYY-MM/YYYY-MM-DD.md   — 日报（数据源）
├── 02_Reports/周报/YYYY/YYYY-WXX.md  — 周报（数据源）
└── 02_Reports/月报/YYYY/YYYY-MM.md   — 月报（写入目标）
```

## 执行流程

### 步骤 1：确定目标月份
- 默认本月（当前日期所在月）。
- 支持参数指定，如 `/monthly-report 2026-06`。
- 若指定月的月末还没到且非补写场景，询问用户是否强制生成。

### 步骤 2：收集数据源
- 遍历本月所有周报：`02_Reports/周报/YYYY/*.md`，按文件名周号筛选属于本月者。
- 遍历本月日报：`01_Daily/YYYY-MM/*.md`，抽取「完成」「遗留」「关键决策」。
- 特别处理兼月报的周报（如 `2026-W25.md` 含 6 月总结），纳入本月月报时注明引用。

### 步骤 3：生成月报
- 写入 `02_Reports/月报/YYYY/YYYY-MM.md`。
- 若已存在 → **合并更新**，不覆盖。

格式：
```markdown
---
title: "月报 — YYYY年MM月"
created: YYYY-MM-DD
tags:
  - type/monthly
---

# 月报 — YYYY年MM月

> **周期**：YYYY年MM月

## 本月主线

1. 主线项目A：一句话概括
2. 主线项目B：...

## 业务进展

- 完成内容（来自各周报聚合）

## 关键决策

- 决策1

## 遗留待办（跨月）

- [ ] 事项1

## 月报与周报引用

- 2026-W25.md（含6月总结）已并入本月月报
```

- 无内容的小节省略。
- 保持精简，聚合去重，避免重复罗列。

### 步骤 4：交互确认
| 时机 | 询问 |
|------|------|
| 写入前 | 月报预览，确认无误？ |

写入后一句话确认：月报已写入 Obsidian。

## 注意
- 月报 = 周报聚合 + 日报补充，避免重复罗列。
- 跨月遗留待办单独一节，供下月 `start-my-day` 承接。
