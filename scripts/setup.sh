#!/bin/bash
# Setup script for MetasploitMCP

# Exit immediately if a command exits with a non-zero status
set -e 

echo "========================================="
echo "  MetasploitMCP Setup"
echo "========================================="

# 1. Create directory structure
echo "[1/5] Creating directory structure..."
DIRS=(
    "data/campaigns"
    "data/knowledge"
    "logs"
    "static/css"
    "static/js"
    "templates"
)

for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  + Created $dir"
    else
        echo "  . $dir already exists"
    fi
done

# 2. Create Python virtual environment
echo "[2/5] Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  + Virtual environment created."
else
    echo "  + Virtual environment already exists."
fi

# 3. Install dependencies
echo "[3/5] Installing dependencies..."
if [ -f "requirements.txt" ]; then
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "  + Dependencies installed successfully."
else
    echo "  ! requirements.txt not found. Skipping pip install."
fi

# 4. Initialize Data Stores
echo "[4/5] Initializing data stores..."
# Ensure the knowledge directory exists before touching files
mkdir -p data/knowledge
touch data/knowledge/base.db
echo "  + Database file initialized."

# 5. Finalize Permissions
echo "[5/5] Finalizing setup..."
if [ -d "scripts" ]; then
    chmod +x scripts/*.sh 2>/dev/null || true
    echo "  + Script permissions updated."
fi

echo "========================================="
echo "  Setup Complete!"
echo "  Run 'source .venv/bin/activate' to start."
echo "========================================="
