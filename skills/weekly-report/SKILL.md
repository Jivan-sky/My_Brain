---
name: weekly-report
description: 汇总本周日报生成周报,写入 Obsidian 02_Reports/周报。触发词:周报、本周总结、周报生成。
---

# 技能: weekly-report

## 使用方式
用户输入 `/weekly-report` 或 `/weekly-report 2026-W34`。

## 功能描述
读取本周（周一至周日）的 `01_Daily/` 日报，抽取「完成」「关键决策」「遗留」「阻塞」，汇总生成周报，写入 `02_Reports/周报/`。**默认精简版**。

## Vault 位置

`{{VAULT_PATH}}\`（结构见 `/obsidian-vault` skill）

## 目录结构

```
{{VAULT_PATH}}\
├── 01_Daily\YYYY-MM\YYYY-MM-DD.md   — 日报（数据源）
└── 02_Reports\周报\YYYY\YYYY-WXX.md  — 周报（写入目标）
```

## 执行流程

### 步骤 1：确定本周时间范围与周号
- 默认本周：取当前日期所在周的周一至周日。
- 周号用 ISO 周号（`date +%V`），文件名 `YYYY-WXX.md`。
- 支持参数指定周，如 `/weekly-report 2026-W33` 则解析该周日期范围。

### 步骤 2：收集日报
- 遍历本周日期对应的 `01_Daily/YYYY-MM/YYYY-MM-DD.md`。
- 对每个存在的日报，抽取：
  - `## 完成` 内容
  - `## 遗留` 内容
  - `## 阻塞` 内容
  - `## 关键决策` 内容（如有）
- 记录日报覆盖的天数；缺失的日期可询问用户是否有遗漏工作。

### 步骤 3：生成周报
- 写入 `02_Reports/周报/YYYY/YYYY-WXX.md`。
- 若目标文件已存在 → **合并更新**，不覆盖（保留已有内容，追加本周新增）。

格式：
```markdown
---
title: "周报 — YYYY年第X周 (M/D-M/D)"
created: YYYY-MM-DD
tags:
  - type/知识捕获
  - weekly
---

# 周报 — YYYY年第X周

> **周期**：YYYY.MM.DD - YYYY.MM.DD

## 业务进展

- 完成内容1
- 完成内容2

## 关键决策

- 决策1：原因和影响

## 遗留待办

- [ ] 事项1

## 阻塞

- 阻塞项1
```

- 无内容的小节（如无阻塞）省略。
- 保持精简，只列实事不铺陈。

### 步骤 4：交互确认
| 时机 | 询问 |
|------|------|
| 写入前 | 周报预览，确认无误？ |

写入后一句话确认：周报已写入 Obsidian。

## 注意
- 周报汇总周一到周日，缺日报的日期主动询问补录。
- 遗留待办跨周保留，下周 `start-my-day` 会承接。
