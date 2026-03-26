#!/usr/bin/env bash
set -euo pipefail

# Configuration
PORT=5000
MSF_PORT=55553
VENV_PATHS=(".venv" "venv")

echo "========================================"
echo "  Starting Phantom Project"
echo "========================================"

# 1. Clean up existing processes on Flask port
PORT_PID=$(lsof -ti:$PORT 2>/dev/null || true)
if [[ -n "$PORT_PID" ]]; then
    echo "[!] Clearing port $PORT (PID: $PORT_PID)..."
    kill "$PORT_PID" 2>/dev/null || sudo kill -9 "$PORT_PID"
    sleep 1
fi

# 2. Ensure Metasploit RPC is running
if ! pgrep -x "msfrpcd" > /dev/null; then
    echo "[+] Starting msfrpcd on port $MSF_PORT..."
    # Running in background; adjust credentials as needed for your environment
    sudo msfrpcd -P msf -U msf -p $MSF_PORT -a 127.0.0.1 &
    
    # Wait for RPC port to actually open
    for i in {1..10}; do
        if nc -z 127.0.0.1 $MSF_PORT; then
            echo "[+] msfrpcd is ready."
            break
        fi
        echo "    Waiting for msfrpcd... ($i/10)"
        sleep 2
    done
else
    echo "[.] msfrpcd is already running."
fi

# 3. Virtual Environment Activation
VENV_ACTIVE=false
for venv in "${VENV_PATHS[@]}"; do
    if [[ -f "$venv/bin/activate" ]]; then
        echo "[+] Activating venv: $venv"
        source "$venv/bin/activate"
        VENV_ACTIVE=true
        break
    fi
done

if [[ "$VENV_ACTIVE" = false ]]; then
    echo "[!] Warning: No virtual environment found. Running with system python."
fi

# 4. Launch Application
echo "[+] Launching Phantom Web Interface..."
# Use exec to pass signals (like Ctrl+C) directly to the python process
export FLASK_APP=app.py
export FLASK_ENV=development
python3 -m flask run --host=0.0.0.0 --port=$PORT
