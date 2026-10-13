#!/bin/bash

# 获取当前脚本所在目录的绝对路径
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$DIR/session_monitor.py"
PLIST_NAME="ai.antigravity.session_manager.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "Deploying Session Manager Daemon..."

# 创建 LaunchAgents 目录（如果不存在）
mkdir -p "$HOME/Library/LaunchAgents"

# 获取当前环境的 python3 绝对路径
PYTHON_BIN="$(which python3)"

# 生成 plist 文件
cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.antigravity.session_manager</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_BIN</string>
        <string>$PYTHON_SCRIPT</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/session_manager_daemon.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/session_manager_daemon.err</string>
</dict>
</plist>
EOF

# 卸载旧的（如果存在）
launchctl unload "$PLIST_PATH" 2>/dev/null

# 加载新的守护进程
launchctl load "$PLIST_PATH"

echo "Session Manager Daemon installed and loaded successfully."
echo "Logs can be found at /tmp/session_manager_daemon.log"
