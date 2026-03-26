#!/bin/bash
# Start script for MetasploitMCP

set -euo pipefail

echo "========================================"
echo "  Starting MetasploitMCP"
echo "========================================"

# 1. Check/Start MSF RPC
if ! pgrep -f "msfrpcd" > /dev/null; then
    echo "[+] Starting Metasploit RPC..."
    # Note: Ensure you have permissions to run msfrpcd
    msfrpcd -P kali -S -a 127.0.0.1 &
    
    # Wait for service to be ready (max 15 seconds)
    echo -n "[+] Waiting for RPC service"
    for i in {1..15}; do
        if ss -tuln | grep -q ":55553"; then
            echo " [OK]"
            break
        fi
        echo -n "."
        sleep 1
        if [ $i -eq 15 ]; then
            echo " [TIMEOUT]"
            echo "❌ Error: msfrpcd failed to start."
            exit 1
        fi
    done
else
    echo "[.] Metasploit RPC is already running."
fi

# 2. Virtual Environment Activation
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "[+] Virtual environment activated."
else
    echo "❌ Error: .venv directory not found. Please run setup.sh first."
    exit 1
fi

# 3. Start Flask app
echo "[+] Starting Flask application..."
# Use exec so the python process receives system signals directly
export FLASK_ENV=development
exec python3 app.py
