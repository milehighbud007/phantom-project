#!/bin/bash
# setup_venv.sh — creates and activates a safe Python virtual environment

VENV_DIR=".venv"

echo "Creating virtual environment in $VENV_DIR..."
python -m venv "$VENV_DIR"

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi
if [ -f requirements-test.txt ]; then
  pip install -r requirements-test.txt
fi

echo "✅ Virtual environment ready and dependencies installed."
