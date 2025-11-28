#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "  Starting Phantom Project"
echo "========================================"

# Kill any process on port 5000
PORT_PID=$(sudo lsof -ti:5000 2>/dev/null || true)
if [[ -n "$PORT_PID" ]]; then
    echo "Killing process on port 5000..."
    sudo kill -9 $PORT_PID
    sleep 1
fi

# Check if msfrpcd is running
if ! pgrep -x "msfrpcd" > /dev/null; then
    echo "Starting msfrpcd..."
    sudo msfrpcd -P msf -U msf -p 55553 -a 127.0.0.1 &
    sleep 2
fi

# Activate venv if it exists
if [[ -d "venv" ]]; then
    source venv/bin/activate
fi

# Start the application
echo "Starting Flask application..."
python3 app.py
