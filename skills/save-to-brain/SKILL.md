---
name: save-to-brain
description: 分析对话内容并提取知识决策待办,归档到 MyBrain 知识库。
---

# 技能: save-to-brain

## 使用方式
用户输入 `/save-to-brain` 或 `/save-to-brain 关于XX的发现`。

## 功能描述
深度分析当前对话内容，提取：
- 新增知识或技巧
- 项目决策或里程碑
- 待办事项或后续行动

将提取的内容按类型分类写入 MyBrain 知识库：
- 知识 → 03_Knowledge/（按主题子目录：01-AI与Claude / 02-工具链 / 03-业务域/<项目> / 04-开发与运维）
- 决策/里程碑 → 04_Projects/（按项目子目录）
- 待办事项 → 生成一个待处理列表或直接写入 01_Daily/ 的对应日记录中
- 周报/月报 → 02_Reports/周报|月报/

> 提示：细分场景可用 `/save-knowledge`（专管知识）或 `/save-project`（专管项目决策）。

最后输出一段清晰的摘要，告知用户归档了哪些内容及所在位置。
