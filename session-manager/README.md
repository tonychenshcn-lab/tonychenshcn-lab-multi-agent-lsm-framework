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

## Post-Interruption SOP (Four-Phase Graceful Teardown)
When the system triggers an OS notification, the operational flow MUST be:
1. **Phase 1: Crystallize**: Summarize verified logic and state, overwrite to L1 hot cache (`< 15KB`), append troubleshooting logs to L2 archive.
2. **Phase 2: Teardown (Self-Termination)**: The active session MUST inspect its own tasks via `manage_task(Action='list')`, kill all registered schedule/daemon tasks via `manage_task(Action='kill')`, and assert that the task count is 0.
3. **Phase 3: Handoff**: Emit handoff report and notify operator that background resources are fully released and the session is safe to close.
4. **Phase 4: Inherit**: Launch new session, inherit sanitized L1 rules, and remount tasks cleanly based on `agent_scheduled_tasks.json`.

## Disaster Recovery
Adheres to the `Boot Recovery Protocol`: In the event of a server shutdown, the agent will autonomously restart this daemon upon noticing the system crash.
