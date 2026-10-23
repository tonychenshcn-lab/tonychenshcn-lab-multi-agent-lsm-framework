import os
import time
import json
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TranscriptHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.sizes = {}
        self.last_alert_time = {}
        self.brain_dir = os.path.expanduser("~/.gemini/antigravity/brain")
        self.archive_dir = os.path.expanduser("~/.gemini/antigravity/scratch/.agents/rules/sub_memories")
        self.dept_aliases = {
            "System_Master_Controller": "System_Master_Controller",
            "Master_Controller": "System_Master_Controller",
            "Agent1": "Agent1",
            "Agent2": "Agent2",
            "Agent3": "Agent3",
            "Agent4": "Agent4",
            "Agent5": "Agent5",
            "Agent6": "Agent6",
        }
        
    def match_department(self, text):
        if not text:
            return None
        for alias, formal_name in self.dept_aliases.items():
            if alias in text:
                return formal_name
        return None

    def get_session_name(self, session_id):
        fallback = f"未指定Agent ({session_id[:8]})"
        try:
            transcript_path = os.path.join(self.brain_dir, session_id, ".system_generated", "logs", "transcript.jsonl")
            if not os.path.exists(transcript_path):
                return fallback
                
            with open(transcript_path, 'r', encoding='utf-8') as f:
                lines = []
                for _ in range(50):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line)
            if not lines:
                return fallback

            # 1. 优先精准解析 Step 0 用户指令中的 @Role
            try:
                first_data = json.loads(lines[0])
                first_content = first_data.get("content", "")
                m_first = re.search(r'@([^\s\r\n@\"<>:/]+)', first_content)
                if m_first:
                    candidate = m_first.group(1).strip()
                    dept = self.match_department(candidate)
                    if dept:
                        return f"{dept} ({session_id[:8]})"
            except Exception:
                pass

            full_head = "".join(lines)
            
            # 2. 匹配全文中的 @部门 显式调用（过滤邮箱域名）
            m_at = re.search(r'(?:^|[\s\r\n>]|\\n)@([^\s\r\n@\"<>:/]+)', full_head)
            if m_at:
                candidate = m_at.group(1).strip()
                if not re.search(r'\.(?:com|cn|net|org|io|br|me)$', candidate, re.IGNORECASE):
                    dept = self.match_department(candidate)
                    if dept:
                        return f"{dept} ({session_id[:8]})"

            # 3. 匹配读取的 L1 记忆文件名 (sub_memories/[部门].md)
            m_mem = re.search(r'sub_memories/([^/\s\"\'\\\\]+?)(?:_SOP)?\.md', full_head)
            if m_mem:
                dept_raw = m_mem.group(1).strip()
                if not dept_raw.endswith("_Archive"):
                    dept = self.match_department(dept_raw) or dept_raw
                    return f"{dept} ({session_id[:8]})"

            # 4. 匹配子任务 JSON 中的 explicit role
            m_role = re.search(r'"role":\s*"([^"]+)"', full_head)
            if m_role:
                r = m_role.group(1).strip()
                dept = self.match_department(r)
                if dept:
                    return f"{dept} ({session_id[:8]})"
                return f"{r} ({session_id[:8]})"

            # 5. 扫描前 8KB 中的标准部门关键词
            scan_chunk = full_head[:8192]
            for alias, formal_name in self.dept_aliases.items():
                if alias in scan_chunk:
                    return f"{formal_name} ({session_id[:8]})"

            # 6. 业务特征兜底推断
            for i in range(1, 7):
                if f"Agent{i}" in scan_chunk:
                    return f"Agent{i} ({session_id[:8]})"

        except Exception:
            pass
        return fallback

    def trigger_alert(self, session_id, reason, size):
        current_time = time.time()
        # 冷却时长: 30 分钟 (1800 秒)
        if current_time - self.last_alert_time.get(session_id, 0) > 1800:
            import subprocess
            session_name = self.get_session_name(session_id)
            dept_name = session_name.split(" (")[0].strip() if " (" in session_name else session_name
            valid_depts = [
                "System_Master_Controller",
                "Agent1",
                "Agent2",
                "Agent3",
                "Agent4",
                "Agent5",
                "Agent6"
            ]
            target_l1 = f"/Users/<USER>/.gemini/antigravity/scratch/.agents/rules/sub_memories/{dept_name}_SOP.md" if dept_name in valid_depts else "/Users/<USER>/.gemini/antigravity/scratch/.agents/rules/sub_memories/[Agent_Role]_SOP.md"
            target_l2 = f"/Users/<USER>/.gemini/antigravity/scratch/.agents/rules/sub_memories/{dept_name}_Archive.md" if dept_name in valid_depts else "/Users/<USER>/.gemini/antigravity/scratch/.agents/rules/sub_memories/[Agent_Role]_Archive.md"
            
            crystallize_prompt = (
                f"【系统级指令：会话知识沉淀与优雅退场闭环】\n"
                f"请对本会话严格执行四阶段退场协议：\n"
                f"1. [L1 热库更新]：提取本会话当前唯一有效参数、最新 SOP 与合规规则，覆写至 {target_l1}（严格控制在 15KB 内，删除冗余描述）。\n"
                f"2. [L2 冷库归档]：提取排障日志、报错堆栈、失败尝试与弃用方案，以追加模式写入 {target_l2}。\n"
                f"3. [全量任务注销]：调用 manage_task(Action='list') 枚举本会话所有后台任务，对非空任务全量执行 manage_task(Action='kill') 彻底注销，并再次 list 断言任务数为 0。\n"
                f"4. [交割报告]：向用户输出已注销任务清单与交割凭证，明确通知用户可以安全关闭当前会话。"
            )
            crystallize_prompt_escaped = crystallize_prompt.replace("\\", "\\\\").replace('"', '\\"')
            
            msg = f"检测到 L0 脏缓存超限！\\n\\nAgent: {session_name}\\n原因: {reason}\\n规模: {size/1024:.2f}KB (阈值: 1MB)\\n\\n系统负载过高，是否立刻强制让 Agent 执行沉淀闭环？"
            
            applescript = f'''
            tell application "System Events"
                set activeApp to name of first application process whose frontmost is true
            end tell
            
            tell application "System Events"
                activate
                set dialogResult to display dialog "{msg}" with title "Session Manager 安全大闸" buttons {{"暂不沉淀", "立刻沉淀"}} default button 2 with icon caution
                set btn to button returned of dialogResult
            end tell
            
            if btn is "立刻沉淀" then
                set the clipboard to "{crystallize_prompt_escaped}"
                tell application activeApp to activate
                delay 0.5
                tell application "System Events"
                    keystroke "v" using command down
                    delay 0.5
                    keystroke return
                end tell
            end if
            return btn
            '''
            
            print(f"\\n[ALERT] Triggering modal dialog for {session_name}", flush=True)
            try:
                result = subprocess.check_output(['osascript', '-e', applescript], stderr=subprocess.STDOUT).decode('utf-8').strip()
                if result == "立刻沉淀":
                    print(f"[ACTION] User clicked 立刻沉淀 for {session_name}, dual-path prompt RPA injected.", flush=True)
                else:
                    print(f"[ACTION] User clicked 暂不沉淀 for {session_name}, entering 30min cooldown.", flush=True)
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Dialog canceled or dismissed (Code {e.returncode}).", flush=True)
                
            self.last_alert_time[session_id] = time.time()

    def trigger_compaction(self, filename, size):
        print(f"\n[COMPACTION] {filename} 触发 500KB 冷库红线 (当前 {size/1024:.2f}KB)。启动无头大模型后台执行去重压缩...", flush=True)
        os.system(f"osascript -e 'display notification \"正在后台执行 {filename} 知识去重与冷数据压缩\" with title \"L2 Archive Compaction\"'")
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # L0 Transcript Monitoring
        if event.src_path.endswith("transcript.jsonl"):
            try:
                size = os.path.getsize(event.src_path)
                session_id = event.src_path.split(os.sep)[-4]
                
                # Zookeeper: Sniff for SYS_REGISTER
                with open(event.src_path, 'r', encoding='utf-8') as f:
                    f.seek(max(0, size - 4096))
                    content = f.read()
                    m = re.search(r'\[SYS_REGISTER\] 角色:(\S+)\s+ID:(\S+)', content)
                    if m:
                        role, new_id = m.group(1), m.group(2)
                        import fcntl
                        reg_path = os.path.join(self.archive_dir, "agent_registry.json")
                        
                        if not os.path.exists(reg_path):
                            with open(reg_path, 'w') as f: json.dump({}, f)
                            
                        with open(reg_path, 'r+') as f:
                            fcntl.flock(f, fcntl.LOCK_EX)
                            try:
                                f.seek(0)
                                try:
                                    reg_data = json.load(f)
                                except json.JSONDecodeError:
                                    reg_data = {}
                                reg_data[role] = new_id
                                f.seek(0)
                                f.truncate()
                                json.dump(reg_data, f, ensure_ascii=False, indent=2)
                            finally:
                                fcntl.flock(f, fcntl.LOCK_UN)
                
                prev_size = self.sizes.get(session_id, 0)
                diff = size - prev_size
                
                # 基础告警阈值: 1MB (1,048,576 字节)
                # 瞬时尖峰阈值: 50KB (51,200 字节)
                if size > 1048576 and size > prev_size:
                    self.trigger_alert(session_id, "L0 脏缓存超限 (规模突破 1MB)", size)
                elif diff > 51200 and prev_size > 0:
                    self.trigger_alert(session_id, "L0 I/O 尖峰瞬时污染 (单次增量超 50KB)", size)
                
                self.sizes[session_id] = size
            except Exception:
                pass
                
        # L2 Archive Monitoring
        if event.src_path.endswith("_Archive.md"):
            try:
                size = os.path.getsize(event.src_path)
                if size > 500000: # 500KB
                    filename = os.path.basename(event.src_path)
                    if time.time() - self.last_alert_time.get(filename, 0) > 3600:
                        self.trigger_compaction(filename, size)
                        self.last_alert_time[filename] = time.time()
            except Exception:
                pass

if __name__ == "__main__":
    event_handler = TranscriptHandler()
    observer = Observer()
    observer.schedule(event_handler, event_handler.brain_dir, recursive=True)
    observer.schedule(event_handler, event_handler.archive_dir, recursive=False)
    observer.start()
    print("LSM-Tree Session Manager Daemon initialized.", flush=True)
    try:
        last_sweep = time.time()
        while True:
            time.sleep(10)
            if time.time() - last_sweep > 3600:
                print("[TTL] Running Lazy Heartbeat Sweep...", flush=True)
                import fcntl
                reg_path = os.path.join(event_handler.archive_dir, "agent_registry.json")
                if os.path.exists(reg_path):
                    with open(reg_path, 'r+') as f:
                        fcntl.flock(f, fcntl.LOCK_EX)
                        try:
                            f.seek(0)
                            try:
                                data = json.load(f)
                            except Exception:
                                data = {}
                            new_data = {}
                            for role, uuid in data.items():
                                t_path = os.path.join(event_handler.brain_dir, uuid, ".system_generated", "logs", "transcript.jsonl")
                                if os.path.exists(t_path):
                                    if time.time() - os.path.getmtime(t_path) < 86400:
                                        new_data[role] = uuid
                            if len(new_data) != len(data):
                                print(f"[TTL] Evicted {len(data) - len(new_data)} dead agents.", flush=True)
                                f.seek(0)
                                f.truncate()
                                json.dump(new_data, f, ensure_ascii=False, indent=2)
                        finally:
                            fcntl.flock(f, fcntl.LOCK_UN)
                last_sweep = time.time()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
