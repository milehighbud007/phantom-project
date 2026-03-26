# ============================================================================
# Phantom Project - Automated Penetration Testing System
# ============================================================================

.PHONY: help setup run update test clean status check-msf

# Colors
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
BLUE   := \033[0;34m
NC     := \033[0m

# Config
VENV       := .venv
PYTHON     := $(VENV)/bin/python3
PIP        := $(VENV)/bin/pip3
MSF_PORT   := 55553

help:
	@echo -e "$(BLUE)Phantom Project Management:$(NC)"
	@echo "  make setup    - Create venv and install dependencies"
	@echo "  make update   - Pull latest changes and refresh env"
	@echo "  make run      - Start MSF RPC and Flask application"
	@echo "  make status   - Check service and environment health"
	@echo "  make test     - Run test suite"
	@echo "  make clean    - Remove temporary files and logs"

setup:
	@echo -e "$(GREEN)[+] Setting up environment...$(NC)"
	@bash scripts/setup.sh
	@bash scripts/setup_venv.sh

update:
	@echo -e "$(GREEN)[+] Updating Phantom...$(NC)"
	@if [ -d .git ]; then \
		git pull origin main || git pull origin master; \
	fi
	@$(MAKE) setup
	@echo -e "$(GREEN)✓ Update complete$(NC)"

check-msf:
	@echo -e "$(YELLOW)[?] Checking Metasploit RPC...$(NC)"
	@if ! pgrep -f msfrpcd > /dev/null; then \
		echo -e "$(RED)[!] msfrpcd not found. Starting...$(NC)"; \
		sudo msfrpcd -P msf -U msf -p $(MSF_PORT) -a 127.0.0.1 & \
		sleep 5; \
	fi

run: check-msf
	@echo -e "$(GREEN)[+] Launching Phantom...$(NC)"
	@if [ -f "$(PYTHON)" ]; then \
		bash scripts/start.sh; \
	else \
		echo -e "$(RED)❌ Error: Virtual env not found. Run 'make setup' first.$(NC)"; \
	fi

status:
	@echo -e "$(BLUE)--- Phantom Status ---$(NC)"
	@echo -n "Venv:    "
	@[ -d $(VENV) ] && echo -e "$(GREEN)Ready$(NC)" || echo -e "$(RED)Missing$(NC)"
	@echo -n "MSF RPC: "
	@pgrep -f msfrpcd > /dev/null && echo -e "$(GREEN)Running$(NC)" || echo -e "$(RED)Stopped$(NC)"
	@echo -n "Port 5000: "
	@nc -z 127.0.0.1 5000 2>/dev/null && echo -e "$(GREEN)Active$(NC)" || echo -e "$(YELLOW)Idle$(NC)"

test:
	@echo -e "$(YELLOW)[*] Running tests...$(NC)"
	@$(PYTHON) -m pytest tests/ 2>/dev/null || echo "No tests found."

clean:
	@echo -e "$(YELLOW)[*] Cleaning project...$(NC)"
	@rm -rf logs/*.log
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo -e "$(GREEN)✓ Clean complete$(NC)"
