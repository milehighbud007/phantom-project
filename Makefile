# ============================================================================
# Phantom Project - Automated Penetration Testing System
# ============================================================================

.PHONY: help setup run test clean check-root start-msfrpcd stop-msfrpcd status

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Project configuration
VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip3
PROJECT_DIR := /home/devpen11/Desktop/phantom-project

# Metasploit RPC configuration
MSFRPCD_HOST := 127.0.0.1
MSFRPCD_PORT := 55553
MSFRPCD_USER := msf
MSFRPCD_PASS := phantom2024

# ============================================================================
# HELP
# ============================================================================

help:
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Phantom Project - Automated Penetration Testing System$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  $(GREEN)make setup$(NC)         - Create virtual environment and install dependencies"
	@echo "  $(GREEN)make run$(NC)           - Start the web interface (requires sudo)"
	@echo "  $(GREEN)make test$(NC)          - Run all test suites"
	@echo "  $(GREEN)make start-msfrpcd$(NC) - Start Metasploit RPC daemon"
	@echo "  $(GREEN)make stop-msfrpcd$(NC)  - Stop Metasploit RPC daemon"
	@echo "  $(GREEN)make status$(NC)        - Check system status"
	@echo "  $(GREEN)make clean$(NC)         - Clean up generated files"
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  1. make setup"
	@echo "  2. make start-msfrpcd"
	@echo "  3. sudo make run"
	@echo ""

# ============================================================================
# SETUP
# ============================================================================

setup:
	@echo "$(BLUE)═══ Setting up Phantom Project ═══$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Checking Python version...$(NC)"
	@python3 --version || (echo "$(RED)✗ Python 3 not found$(NC)" && exit 1)
	@echo "$(GREEN)✓ Python 3 found$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Creating virtual environment...$(NC)"
	@test -d $(VENV) || python3 -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Upgrading pip...$(NC)"
	@$(PIP) install --upgrade pip > /dev/null 2>&1
	@echo "$(GREEN)✓ pip upgraded$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Installing Python dependencies...$(NC)"
	@$(PIP) install flask python-nmap msgpack requests > /dev/null 2>&1 || \
		(echo "$(RED)✗ Failed to install dependencies$(NC)" && exit 1)
	@echo "$(GREEN)✓ Dependencies installed$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Verifying system tools...$(NC)"
	@command -v nmap > /dev/null 2>&1 || \
		echo "$(RED)✗ nmap not found - install with: sudo pacman -S nmap$(NC)"
	@command -v msfconsole > /dev/null 2>&1 || \
		echo "$(RED)✗ metasploit not found - install with: sudo pacman -S metasploit$(NC)"
	@command -v msfrpcd > /dev/null 2>&1 && \
		echo "$(GREEN)✓ msfrpcd found$(NC)" || \
		echo "$(RED)✗ msfrpcd not found$(NC)"
	@echo ""
	
	@echo "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)✓✓✓ Setup complete!$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Start Metasploit RPC: $(GREEN)make start-msfrpcd$(NC)"
	@echo "  2. Run the application: $(GREEN)sudo make run$(NC)"
	@echo ""

# ============================================================================
# CHECK ROOT
# ============================================================================

check-root:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "$(RED)✗ Must run as root/sudo for full functionality$(NC)"; \
		echo "$(YELLOW)  Run: sudo make run$(NC)"; \
		exit 1; \
	fi

# ============================================================================
# METASPLOIT RPC DAEMON
# ============================================================================

start-msfrpcd:
	@echo "$(BLUE)═══ Starting Metasploit RPC Daemon ═══$(NC)"
	@echo ""
	
	@if pgrep -f "msfrpcd" > /dev/null; then \
		echo "$(YELLOW)⚠ msfrpcd is already running$(NC)"; \
		echo "  PID: $$(pgrep -f msfrpcd)"; \
	else \
		echo "$(YELLOW)→ Starting msfrpcd...$(NC)"; \
		msfrpcd -P $(MSFRPCD_PASS) -U $(MSFRPCD_USER) -a $(MSFRPCD_HOST) -p $(MSFRPCD_PORT) & \
		sleep 3; \
		if pgrep -f "msfrpcd" > /dev/null; then \
			echo "$(GREEN)✓ msfrpcd started successfully$(NC)"; \
			echo "  Host: $(MSFRPCD_HOST)"; \
			echo "  Port: $(MSFRPCD_PORT)"; \
			echo "  User: $(MSFRPCD_USER)"; \
			echo "  PID:  $$(pgrep -f msfrpcd)"; \
		else \
			echo "$(RED)✗ Failed to start msfrpcd$(NC)"; \
			exit 1; \
		fi; \
	fi
	@echo ""

stop-msfrpcd:
	@echo "$(BLUE)═══ Stopping Metasploit RPC Daemon ═══$(NC)"
	@echo ""
	
	@if pgrep -f "msfrpcd" > /dev/null; then \
		echo "$(YELLOW)→ Stopping msfrpcd (PID: $$(pgrep -f msfrpcd))...$(NC)"; \
		pkill -f msfrpcd; \
		sleep 2; \
		if pgrep -f "msfrpcd" > /dev/null; then \
			echo "$(RED)✗ Failed to stop msfrpcd gracefully, forcing...$(NC)"; \
			pkill -9 -f msfrpcd; \
		fi; \
		echo "$(GREEN)✓ msfrpcd stopped$(NC)"; \
	else \
		echo "$(YELLOW)⚠ msfrpcd is not running$(NC)"; \
	fi
	@echo ""

# ============================================================================
# RUN APPLICATION
# ============================================================================

run: check-root
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Starting Phantom Project$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Checking Metasploit RPC...$(NC)"
	@if pgrep -f "msfrpcd" > /dev/null; then \
		echo "$(GREEN)✓ msfrpcd is running$(NC)"; \
	else \
		echo "$(RED)✗ msfrpcd is not running$(NC)"; \
		echo "$(YELLOW)  Start it with: make start-msfrpcd$(NC)"; \
		exit 1; \
	fi
	@echo ""
	
	@echo "$(YELLOW)→ Activating virtual environment...$(NC)"
	@echo "$(GREEN)✓ Virtual environment activated$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Starting Flask application...$(NC)"
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Application starting...$(NC)"
	@echo "$(GREEN)  Access at: http://localhost:5000$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@cd $(PROJECT_DIR) && . $(VENV)/bin/activate && $(PYTHON) app.py

# ============================================================================
# TEST
# ============================================================================

test:
	@echo "$(BLUE)═══ Running Test Suite ═══$(NC)"
	@echo ""
	@bash run_meta_mpc_tests.sh

# ============================================================================
# STATUS
# ============================================================================

status:
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Phantom Project - System Status$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	
	@echo "$(YELLOW)Python Environment:$(NC)"
	@if [ -d "$(VENV)" ]; then \
		echo "  $(GREEN)✓$(NC) Virtual environment: $(GREEN)exists$(NC)"; \
		echo "  $(GREEN)✓$(NC) Python version: $$($(PYTHON) --version | cut -d' ' -f2)"; \
	else \
		echo "  $(RED)✗$(NC) Virtual environment: $(RED)missing$(NC)"; \
		echo "    Run: $(YELLOW)make setup$(NC)"; \
	fi
	@echo ""
	
	@echo "$(YELLOW)System Tools:$(NC)"
	@command -v nmap > /dev/null 2>&1 && \
		echo "  $(GREEN)✓$(NC) nmap: $$(nmap --version | head -1 | cut -d' ' -f3)" || \
		echo "  $(RED)✗$(NC) nmap: $(RED)not installed$(NC)"
	@command -v msfconsole > /dev/null 2>&1 && \
		echo "  $(GREEN)✓$(NC) metasploit: $(GREEN)installed$(NC)" || \
		echo "  $(RED)✗$(NC) metasploit: $(RED)not installed$(NC)"
	@command -v msfrpcd > /dev/null 2>&1 && \
		echo "  $(GREEN)✓$(NC) msfrpcd: $(GREEN)available$(NC)" || \
		echo "  $(RED)✗$(NC) msfrpcd: $(RED)not available$(NC)"
	@echo ""
	
	@echo "$(YELLOW)Running Processes:$(NC)"
	@if pgrep -f "msfrpcd" > /dev/null; then \
		echo "  $(GREEN)✓$(NC) msfrpcd: $(GREEN)running$(NC) (PID: $$(pgrep -f msfrpcd))"; \
	else \
		echo "  $(RED)✗$(NC) msfrpcd: $(RED)not running$(NC)"; \
		echo "    Start: $(YELLOW)make start-msfrpcd$(NC)"; \
	fi
	@if pgrep -f "python.*app.py" > /dev/null; then \
		echo "  $(GREEN)✓$(NC) Flask app: $(GREEN)running$(NC) (PID: $$(pgrep -f 'python.*app.py'))"; \
	else \
		echo "  $(YELLOW)○$(NC) Flask app: not running"; \
	fi
	@echo ""
	
	@echo "$(YELLOW)Project Files:$(NC)"
	@for file in ai_learning_module.py automated_attack_system.py app.py; do \
		if [ -f "$$file" ]; then \
			size=$$(ls -lh "$$file" | awk '{print $$5}'); \
			echo "  $(GREEN)✓$(NC) $$file ($$size)"; \
		else \
			echo "  $(RED)✗$(NC) $$file: $(RED)missing$(NC)"; \
		fi; \
	done
	@echo ""
	
	@echo "$(YELLOW)Permissions:$(NC)"
	@if [ "$$(id -u)" -eq 0 ]; then \
		echo "  $(GREEN)✓$(NC) Running as: $(GREEN)root$(NC)"; \
	else \
		echo "  $(YELLOW)○$(NC) Running as: $(YELLOW)$$(whoami)$(NC)"; \
		echo "    Note: Some features require root access"; \
	fi
	@echo ""

# ============================================================================
# CLEAN
# ============================================================================

clean:
	@echo "$(BLUE)═══ Cleaning up ═══$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Removing Python cache...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Python cache cleaned$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Removing test files...$(NC)"
	@rm -f test_ai_knowledge.json test_ai_knowledge.json.backup 2>/dev/null || true
	@echo "$(GREEN)✓ Test files removed$(NC)"
	@echo ""
	
	@echo "$(YELLOW)→ Removing logs...$(NC)"
	@rm -f *.log 2>/dev/null || true
	@echo "$(GREEN)✓ Logs cleaned$(NC)"
	@echo ""
	
	@echo "$(GREEN)✓ Cleanup complete$(NC)"
	@echo ""

clean-all: clean stop-msfrpcd
	@echo "$(YELLOW)→ Removing virtual environment...$(NC)"
	@rm -rf $(VENV)
	@echo "$(GREEN)✓ Virtual environment removed$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"
	@echo "$(YELLOW)  Run 'make setup' to reinstall$(NC)"
	@echo ""

# ============================================================================
# DEVELOPMENT HELPERS
# ============================================================================

dev-run:
	@echo "$(BLUE)═══ Starting Development Server ═══$(NC)"
	@echo ""
	@cd $(PROJECT_DIR) && . $(VENV)/bin/activate && \
		FLASK_ENV=development FLASK_DEBUG=1 $(PYTHON) app.py

logs:
	@if [ -f "phantom.log" ]; then \
		tail -f phantom.log; \
	else \
		echo "$(YELLOW)No log file found$(NC)"; \
	fi

install-system-deps:
	@echo "$(BLUE)═══ Installing System Dependencies ═══$(NC)"
	@echo ""
	@echo "$(YELLOW)This will install: nmap, metasploit$(NC)"
	@echo "$(RED)Press Ctrl+C to cancel, or Enter to continue...$(NC)"
	@read confirm
	@sudo pacman -Sy nmap metasploit
	@echo ""
	@echo "$(GREEN)✓ System dependencies installed$(NC)"
	@echo ""

# ============================================================================
# END
# ============================================================================
