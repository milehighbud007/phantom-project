#!/bin/bash
# Start script for MetasploitMCP

echo "Starting MetasploitMCP..."

# Check if MSF RPC is running
if ! pgrep -f "msfrpcd" > /dev/null; then
    echo "Starting Metasploit RPC..."
    msfrpcd -P kali -S -a 127.0.0.1 &
    sleep 3
else
    echo "Metasploit RPC already running"
fi

# Activate virtual environment
source .venv/bin/activate

# Start Flask app
echo "Starting Flask application..."
python3 app.py