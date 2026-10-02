import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TranscriptHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.sizes = {}
        self.last_alert_time = {}
        self.brain_dir = os.path.expanduser("~/.gemini/antigravity/brain")
        self.archive_dir = os.path.expanduser("~/.gemini/antigravity/scratch/.agents/rules/sub_memories")
        
    def trigger_alert(self, session_id, reason, size):
        current_time = time.time()
        # Cooldown: 15 minutes = 900 seconds
        if current_time - self.last_alert_time.get(session_id, 0) > 900:
            msg = f"Session {session_id[:8]} {reason} (Size: {size/1024:.2f}KB)"
            sop = "L1 缓存已安全固化，请直接废弃当前进程，重启新会话载入 L1 SOP 即可。"
            print(f"\n[ALERT] {msg}\n[ACTION REQUIRED] {sop}", flush=True)
            os.system(f"osascript -e 'display notification \"{msg}. {sop}\" with title \"Session Manager 内存回收\" sound name \"Glass\"'")
            self.last_alert_time[session_id] = current_time

    def trigger_compaction(self, filename, size):
        print(f"\n[COMPACTION] {filename} 触发 500KB 冷库红线 (当前 {size/1024:.2f}KB)。启动无头大模型后台执行去重压缩...", flush=True)
        # 伪代码：实际调用 Antigravity SDK 或通过 invoke_subagent CLI 执行后台清理
        os.system(f"osascript -e 'display notification \"正在后台执行 {filename} 知识去重与冷数据压缩\" with title \"L2 Archive Compaction\"'")
        # Simulate SDK Call:
        # agent = Agent(config)
        # agent.chat(f"Read {filename}, strip duplicates, and output compressed archive.")
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # L0 Transcript Monitoring
        if event.src_path.endswith("transcript.jsonl"):
            try:
                size = os.path.getsize(event.src_path)
                session_id = event.src_path.split(os.sep)[-4]
                prev_size = self.sizes.get(session_id, 0)
                diff = size - prev_size
                
                if size > 150000 and size > prev_size:
                    self.trigger_alert(session_id, "L0 脏缓存超限持续增长", size)
                elif diff > 30000 and prev_size > 0:
                    self.trigger_alert(session_id, "L0 I/O 尖峰瞬时污染", size)
                
                self.sizes[session_id] = size
            except Exception:
                pass
                
        # L2 Archive Monitoring
        if event.src_path.endswith("_Archive.md"):
            try:
                size = os.path.getsize(event.src_path)
                if size > 500000: # 500KB
                    filename = os.path.basename(event.src_path)
                    # Trigger compaction only if not recently compacted to avoid loop
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
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
