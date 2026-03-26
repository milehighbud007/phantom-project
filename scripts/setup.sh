#!/bin/bash
# Setup script for MetasploitMCP
set -e

echo "========================================="
echo "  MetasploitMCP Setup"
echo "========================================="

# 1. Create directory structure
echo "[1/5] Creating directory structure..."
DIRS=("data/campaigns" "data/knowledge" "logs" "static/css" "static/js" "templates")
for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
    echo "  + Created $dir"
done

# 2. Create Python virtual environment
echo "[2/5] Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
    # Check if python3-venv is installed (common fail point on Ubuntu/Debian)
    if ! dpkg -l | grep -q python3-venv; then
        echo "  ! Error: python3-venv is missing. Install it with: sudo apt install python3-venv"
        exit 1
    fi
    python3 -m venv .venv
    echo "  + .venv created successfully."
else
    echo "  . .venv already exists."
fi

# 3. Install Requirements
echo "[3/5] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    source .venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt
    echo "  + Dependencies installed."
else
    echo "  ! Warning: requirements.txt not found. Skipping installation."
fi

# 4. Initialize Data
echo "[4/5] Initializing local databases..."
touch data/knowledge/base.db
echo "  + Knowledge base initialized."

# 5. Finalize Permissions
echo "[5/5] Setting executable permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
echo "  + Permissions set."

echo "========================================="
echo "  Setup Complete! Use 'source .venv/bin/activate'"
echo "========================================="
