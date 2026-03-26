#!/bin/bash
# setup_venv.sh — creates and activates a safe Python virtual environment
set -euo pipefail

VENV_DIR=".venv"

echo "========================================"
echo "  Phantom VENV Setup"
echo "========================================"

# 1. Ensure Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed. Please install it first."
    exit 1
fi

# 2. Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "[.] Virtual environment already exists."
fi

# 3. Activate and Install
echo "[+] Activating environment and updating pip..."
# Use a subshell or source properly
source "$VENV_DIR/bin/activate"

pip install --upgrade pip -q

# Install dependencies if files exist
for req in "requirements.txt" "requirements-test.txt"; do
    if [ -f "$req" ]; then
        echo "[+] Installing from $req..."
        pip install -r "$req" --no-cache-dir
    else
        echo "[.] $req not found, skipping."
    fi
done

# 4. Git maintenance
if [ -d ".git" ] && ! grep -q "$VENV_DIR" .gitignore 2>/dev/null; then
    echo "$VENV_DIR/" >> .gitignore
    echo "[+] Added $VENV_DIR to .gitignore"
fi

echo "========================================"
echo "✅ Environment ready! Run: source $VENV_DIR/bin/activate"
echo "========================================"
