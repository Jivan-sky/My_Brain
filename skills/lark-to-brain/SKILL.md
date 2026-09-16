---
name: lark-to-brain
description: 拉取飞书消息并提取决策与待办,归档到 MyBrain 知识库。
---

# 技能: lark-to-brain

## 前置条件
- 已在飞书开放平台创建应用，并开通以下权限：
  - im:message
  - im:message:readonly
  - im:message.group_at_msg.include_bot:readonly
  - im:chat:readonly
- 已从"凭证与基础信息"获取 App ID 和 App Secret。

## 使用方式
- `/lark-to-brain` ：立即拉取最近的飞书消息并处理。
- `/loop 30m /lark-to-brain` ：每30分钟自动执行一次。

## 执行流程
1. 使用 App ID 和 App Secret 调用飞书 OAuth API 获取 tenant_access_token。
2. 调用 `im/v1/messages` 或 `im/v1/chats` API 拉取消息。
3. 分析消息内容，提取决策、待办、关键信息。
4. 将提取的内容写入 MyBrain 的 `00_Inbox/飞书-日期.md` 文件中。
5. 标记已处理的消息（通过记录 message_id 避免重复）。

## API 调用示例（供参考）
```bash
# 获取 tenant_access_token
curl -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id": "YOUR_APP_ID", "app_secret": "YOUR_APP_SECRET"}'

# 拉取单聊消息
curl -X GET "https://open.feishu.cn/open-apis/im/v1/messages?container_type=chat&page_size=20" \
  -H "Authorization: Bearer ${TOKEN}"
```
