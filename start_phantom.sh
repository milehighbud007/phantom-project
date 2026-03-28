#!/bin/bash

# 1. Configuration
PROJECT_DIR="/home/DevPen187/projects/phantom-project"
VENV_PATH="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# 2. Activate Virtual Environment
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "[+] Virtual environment activated."
else
    echo "[!] Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# 3. Check if Metasploit RPC is running
if ! pgrep -f msfrpcd > /dev/null; then
    echo "[!] Warning: msfrpcd does not appear to be running."
    echo "    Start it with: msfrpcd -P yourpassword -S -a 127.0.0.1 -p 55553"
fi

# 4. Run the Server
# Defaulting to HTTP mode for browser/SSE access. 
# Use --transport stdio if running via Claude Desktop config.
echo "[*] Starting Metasploit MCP Server..."
python3 -m phantom.metasploit.MetasploitMCP --transport http --host 0.0.0.0 --port 8085
