# Antigravity Session Manager

## Overview
A zero-overhead context pollution defense system for Antigravity LLM architectures, designed to prevent model fatigue and hallucination caused by massive context windows.

## Architecture Core
1. **Master-Sub Memory Tree**: Global settings are stored in `MEMORY.md`. Session-specific configurations are physically isolated in `sub_memories/*.md`.
2. **Dual-Track Context Monitoring**:
   - Velocity Peak (Instant I/O > 30KB)
   - Capacity Threshold (Cumulative Volume > 150KB)
3. **OS-Level Watchdog**: Uses Mac `fsevents` (via Python `watchdog` library) for zero-polling file system event monitoring.
4. **Physical Visual Interruption**: Leverages macOS native `NSUserNotificationCenter` via AppleScript to bypass application frontend boundaries and force visual UI notification.

## Deployment & Usage
1. Move this directory to `~/.gemini/config/skills/session-manager/`.
2. Install dependencies: `pip install watchdog`.
3. Execution: The agent or `hooks.json` mounts `scripts/session_monitor.py` as a background Daemon.

## Post-Interruption SOP (LSM-Tree & Task Lifecycle Migration)
When the system triggers an OS notification (L1 cache flush), the operational flow MUST be:
1. **Cache Flush**: Terminate the active bloated session in the UI.
2. **Zombie Purge**: The new session MUST scan for and explicitly `kill` any background daemon processes (`schedule` cron jobs) left behind by the abandoned session.
3. **Cold Boot Recovery**: Upon loading the `_SOP.md` (L1), the agent MUST proactively invoke `schedule` to remount all business-critical cron tasks extracted from the L1 configurations.
4. **Resumption**: Launch the new session, triggering the system directives to inherit the L1 rules without pollution.

## Disaster Recovery
Adheres to the `Boot Recovery Protocol`: In the event of a server shutdown, the agent will autonomously restart this daemon upon noticing the system crash.
