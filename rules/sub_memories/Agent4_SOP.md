>>> SYSTEM DIRECTIVE: 立即调用 view_file 强制读取并加载 /Users/<USER>/.gemini/antigravity/scratch/.agents/rules/MEMORY.md 内的规则 <<<

# 核心业务参数与流程规则

## 1. 简历JD匹配工作流参数
- **JD匹配阈值**: 60%
- **任务1 (简历匹配检查)**: 任务ID `<MOCK_UUID>` (每天凌晨 1:00 执行，检查过去24小时新邮件的简历附件)
- **任务2 (匹配报告发送)**: 任务ID `<MOCK_UUID>` (每天凌晨 3:00 执行，发送至 `<MOCK_CONVERSATION_ID>`)
- **任务3 (到期提醒)**: 任务ID `<MOCK_UUID>` (2027-04-14 09:00 PDT 执行)

## 2. 特殊符号转义法则 (Professional_Network_Z 自动发布)
根据经验，所有 Professional_Network_Z 发布必须严格执行以下符号转义，防止内容截断：
- `|` 替换为 `｜`
- `(` 替换为 `（`
- `)` 替换为 `）`
- `[` 替换为 `【`
- `]` 替换为 `】`

处理顺序：
1. 替换邮箱地址
2. 删除微信联系方式
3. 替换竖线符号
4. 替换英文括号
5. 替换方括号
6. 验证内容完整性 (处理后不应包含 ASCII 竖线和括号)

## 3. 定时跑批任务管理
所有定时任务统一使用 Antigravity 原生 schedule 工具。
遭遇 `All your subagents and background tasks have been stopped due to server restart` 通知时：
1. 立即被唤醒
2. 识别被中断的 schedule 任务
3. 调用 schedule 工具静默重新挂载
4. 挂载完成后在聊天界面简短回复用户
