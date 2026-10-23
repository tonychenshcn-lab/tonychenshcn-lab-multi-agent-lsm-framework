# 归档日志与排错经验 (Archive)

## 排错与异常处理记录
1. **Model Output 异常**: `model output must contain either output text or tool calls, these cannot both be empty` - 确保每次响应带有正确的输出或工具调用。
2. **Bash 脚本中的 Cat/EOF 错误**: 过往曾多次尝试使用 `cat << 'EOF' > ...` 并失败。已验证：应当优先使用原生文件写入工具 `write_to_file`。
3. **状态检查卡带 (Looping)**: 曾出现重复确认同一个任务状态的现象，被记录为“卡带”。教训：获取任务状态后应当立即继续后续逻辑，避免循环调用工具。
4. **冗余的执行日志**: 日志中包含大量 `run_command` 的起止时间戳日志、以及冗长的脚本输出与工具调用记录，已全部压缩。后续应聚焦于上层的业务逻辑，这些历史过程日志不再影响核心规则。
