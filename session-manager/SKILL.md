---
name: session-manager
description: |
  自动化会话疲劳与上下文污染监控组件。
  包含 macOS 原生视觉中断防线与后置业务闭环 SOP。
---

# Session Manager

## 技术规范与运行机制
本模块是防止大语言模型上下文溢出的底层基础防线。
基于 Mac 原生 `fsevents` 文件监听实现零轮询 I/O 开销。

## 优雅退场与会话管理标准操作流 (SOP)
一旦 `session_monitor.py` 触发 Mac 系统级弹窗报警，或用户明确下发“进行会话管理和知识沉淀”指令，**必须严格按序执行以下四阶段原子闭环**：

1. **【阶段一：沉淀 (Crystallize)】**
   - 提取当前会话最新有效逻辑、规则、硬参数与治理规范，覆写至对应的 L1 热库（`_SOP.md` 或 `[部门].md`，严格 `< 15KB`）。
   - 将排障日志、报错堆栈、尝试失败细节追加写入 L2 冷库（`_Archive.md`）。
   - 更新物理台账 `agent_scheduled_tasks.json` 与 `cron_registry.json`，确保磁盘状态最新。

2. **【阶段二：注销 (Teardown)】（核心安全门禁）**
   - **自注销原则**：由于 Antigravity `manage_task` 具备严格的会话隔离鉴权（新会话无法跨会话 kill 旧任务，抛出 `belongs to a different conversation`），任务注销必须在旧会话终结前由其自身执行！
   - 调用 `manage_task(Action='list')` 枚举当前会话持有的所有后台任务（`schedule` 定时器与后台 `run_command`）。
   - 对列表中所有非空任务，逐一调用 `manage_task(Action='kill', TaskId=...)` 执行彻底析构。
   - **零任务断言 (Zero-Task Assertion)**：再次调用 `manage_task(Action='list')`，确认返回结果为 `"No background tasks are currently running."`。若有残留，严禁向下一阶段流转。

3. **【阶段三：交割 (Handoff)】**
   - 向用户输出《优雅退场交割报告》：
     - 列明已落盘的 L1/L2 记忆文件与版本；
     - 列明已注销的任务 ID 列表与任务名称；
     - 明确提示用户：“当前会话所有定时任务已注销，后台资源已彻底释放，可安全关闭本会话窗口。”

4. **【阶段四：继承 (Inherit)】**
   - 用户开启全新会话后，发送 `@部门名称 读L1记忆` 指令。
   - 新会话根据首行 `SYSTEM DIRECTIVE` 读取最新的 L1 热库。
   - 依据物理台账 `agent_scheduled_tasks.json` 的活跃白名单任务，在纯净无冲突的环境下幂等重新挂载归属任务，实现干净继承。
