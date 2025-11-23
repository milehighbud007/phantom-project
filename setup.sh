#!/bin/bash
# Setup script for MetasploitMCP

echo "========================================="
echo "  MetasploitMCP Setup"
echo "========================================="
echo

# Create directory structure
echo "[1/5] Creating directory structure..."
mkdir -p data/campaigns
mkdir -p data/knowledge
mkdir -p logs
mkdir -p static/css
mkdir -p static/js
mkdir -p templates

# Create Python virtual environment
echo "[2/5] Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "[3/5] Installing Python dependencies..."
pip install --upgrade pip
pip install flask python-nmap msgpack-python requests

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "[4/5] Creating .env file..."
    cat > .env << 'EOF'
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
MSF_RPC_HOST=127.0.0.1
MSF_RPC_PORT=55553
MSF_RPC_PASSWORD=kali
AI_KNOWLEDGE_FILE=data/knowledge/metasploit_ai_knowledge.json
LOG_LEVEL=INFO
EOF
fi

# Initialize database
echo "[5/5] Initializing database..."
python3 -c "from database import db; print('Database initialized!')"

echo
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo
echo "To start MetasploitMCP:"
echo "  1. Start Metasploit RPC: msfrpcd -P kali -S -a 127.0.0.1"
echo "  2. Run: python3 app.py"
echo "  3. Open: http://localhost:5000/console"
echo