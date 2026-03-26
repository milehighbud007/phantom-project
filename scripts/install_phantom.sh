#!/bin/bash
# PHANTOM Installation Script - Refactored with Git Update Support

set -e

# Define project root
PROJECT_ROOT="/home/DevPen187/projects/phantom-project"
mkdir -p "$PROJECT_ROOT"
cd "$PROJECT_ROOT"

echo "========================================="
echo "  Installing PHANTOM Makefile"
echo "========================================="

# 1. Backup old Makefile
if [ -f Makefile ]; then
    BACKUP="Makefile.backup.$(date +%s)"
    cp Makefile "$BACKUP"
    echo "✓ Old Makefile backed up to $BACKUP"
fi

# 2. Generate new Makefile with 'update' target
echo "[+] Generating new Makefile..."
cat << 'MAKEFILE' > Makefile
# PHANTOM Project Makefile

.PHONY: setup run test clean info update help

help:
	@echo "PHANTOM Control Menu:"
	@echo "  make setup   - Install dependencies and venv"
	@echo "  make update  - Pull latest git changes and re-run setup"
	@echo "  make run     - Start MSF RPC and Flask App"
	@echo "  make test    - Run project tests"
	@echo "  make clean   - Remove logs and temp files"
	@echo "  make info    - System and project status"

setup:
	@echo "[+] Running setup script..."
	@bash scripts/setup.sh

update:
	@echo "[+] Checking for Git repository..."
	@if [ -d .git ]; then \
		echo "[+] Pulling latest changes..."; \
		git pull origin main || git pull origin master; \
		$(MAKE) setup; \
		echo "✓ Update complete."; \
	else \
		echo "❌ Error: Not a git repository. Cannot update."; \
		exit 1; \
	fi

run:
	@echo "[+] Starting PHANTOM..."
	@bash scripts/start.sh

test:
	@if [ -d .venv ]; then \
		.venv/bin/python3 -m pytest tests/ || echo "Tests failed or no tests found."; \
	else \
		echo "❌ Error: Virtual environment not found. Run 'make setup' first."; \
	fi

clean:
	@rm -rf logs/*.log
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✓ Cleanup complete"

info:
	@echo "--- PHANTOM INFO ---"
	@echo "Location: $(shell pwd)"
	@echo "Python:   $(shell .venv/bin/python3 --version 2>/dev/null || echo 'Not found')"
	@echo "MSF RPC:  $(shell pgrep -f msfrpcd > /dev/null && echo 'Running' || echo 'Stopped')"
	@if [ -d .git ]; then echo "Branch:   $(shell git rev-parse --abbrev-ref HEAD)"; fi

MAKEFILE

# 3. Finalize
chmod +x scripts/*.sh 2>/dev/null || true
echo "✓ PHANTOM Makefile installed successfully with 'update' support"
echo ""
echo "Quick start:"
echo "  make setup        - Initialize project"
echo "  make update       - Sync with remote repo"
echo "  make run          - Start PHANTOM"
echo "========================================="
