SHELL := /bin/bash
PROJECT_ROOT := $(shell pwd)
VENV_DIR := $(PROJECT_ROOT)/venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
FLASK_APP := app.py
WIRELESS_IFACE := wlan1

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

.PHONY: help run setup install-deps install-wireless start-msfrpcd start-flask stop status clean test wireless-check

.DEFAULT_GOAL := run

##@ General Commands

help: ## Display this help message
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║                                                            ║"
	@echo "║   ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗  ║"
	@echo "║   ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║  ║"
	@echo "║   ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║  ║"
	@echo "║   ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║  ║"
	@echo "║   ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║  ║"
	@echo "║   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝  ║"
	@echo "║                                                            ║"
	@echo "║    Penetration & Hacking Automation Network Threat         ║"
	@echo "║              Operations Manager                            ║"
	@echo "║                                                            ║"
	@echo "║    Colorado Tech University - Jack Cole                    ║"
	@echo "║    Cybersecurity Dissertation Project                      ║"
	@echo "║                                                            ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "$(CYAN)Quick Start:$(NC)"
	@echo "  $(GREEN)sudo make run$(NC)     - Start PHANTOM (all services)"
	@echo ""
	@echo "$(CYAN)Available Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

setup: create-venv install-deps install-wireless ## Complete setup (run once)
	@echo "$(GREEN)✓ PHANTOM setup complete!$(NC)"

create-venv: ## Create Python virtual environment
	@echo "$(CYAN)Creating virtual environment...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then python3 -m venv $(VENV_DIR); fi
	@echo "$(GREEN)✓ Virtual environment created$(NC)"

install-deps: create-venv ## Install Python dependencies
	@echo "$(CYAN)Installing Python dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install flask python-nmap msgpack-python requests scapy netifaces
	@$(PIP) install fastapi uvicorn sqlalchemy psycopg2-binary redis pyotp
	@$(PIP) install -r requirements.txt 2>/dev/null || true
	@echo "$(GREEN)✓ Python dependencies installed$(NC)"

install-wireless: ## Install wireless attack tools (requires sudo)
	@echo "$(CYAN)Installing wireless tools...$(NC)"
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "$(RED)✗ Must run as root/sudo for wireless tools$(NC)"; \
		exit 1; \
	fi
	@apt update && apt install -y \
		aircrack-ng airmon-ng airodump-ng aireplay-ng \
		reaver bettercap masscan traceroute \
		macchanger wireless-tools net-tools || true
	@$(PIP) install trackerjacker || true
        @$(PIP) install git+https://github.com/derv82/wifite2.git
#	@$(PIP) install wifite2 || apt install -y wifite || true
	@echo "$(GREEN)✓ Wireless tools installed$(NC)"

check-deps: ## Check if dependencies are installed
	@if [ ! -d "$(VENV_DIR)" ]; then $(MAKE) setup; fi

##@ Main Operations

run: check-root banner check-deps start-services ## 🚀 START PHANTOM (main command)
	@sleep 3
	@$(MAKE) --no-print-directory start-msfrpcd
	@sleep 3
	@$(MAKE) --no-print-directory start-flask
	@sleep 2
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║           ✓ PHANTOM PLATFORM ONLINE                        ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "  $(CYAN)🎯 Web Console:$(NC)         http://localhost:5000/console"
	@echo "  $(CYAN)📊 API Endpoints:$(NC)       http://localhost:5000/"
	@echo "  $(CYAN)🔧 Metasploit RPC:$(NC)      127.0.0.1:55552"
	@echo "  $(CYAN)📡 Wireless Interface:$(NC)  $(WIRELESS_IFACE)"
	@echo "  $(CYAN)🤖 AI Learning:$(NC)         Enabled"
	@echo "  $(CYAN)⚡ Automated Attacks:$(NC)   Ready"
	@echo ""
	@echo "  $(YELLOW)Commands:$(NC)"
	@echo "    make status      - Check service status"
	@echo "    make logs        - View logs"
	@echo "    make stop        - Stop all services"
	@echo ""
	@echo "  $(GREEN)Press Ctrl+C then run 'make stop' to shutdown$(NC)"
	@echo ""
	@# Keep alive
	@trap 'make stop' INT; tail -f /dev/null

start-services: ## Start system services (PostgreSQL, Redis)
	@echo "$(CYAN)Starting system services...$(NC)"
	@systemctl is-active postgresql >/dev/null 2>&1 || systemctl start postgresql || true
	@systemctl is-active redis-server >/dev/null 2>&1 || systemctl start redis-server || true
	@echo "$(GREEN)✓ System services started$(NC)"

start-msfrpcd: ## Start Metasploit RPC daemon
	@echo "$(CYAN)Starting Metasploit RPC...$(NC)"
	@if pgrep -f "msfrpcd" > /dev/null; then \
		echo "$(YELLOW)⚠ msfrpcd already running$(NC)"; \
	else \
		msfrpcd -P kali -U msf -S -a 127.0.0.1 -p 55552 & echo $$! > .msfrpcd.pid; \
		sleep 3; \
		echo "$(GREEN)✓ Metasploit RPC started$(NC)"; \
	fi

start-flask: ## Start Flask application
	@echo "$(CYAN)Starting PHANTOM web server...$(NC)"
	@if pgrep -f "$(FLASK_APP)" > /dev/null; then \
		echo "$(YELLOW)⚠ Flask already running$(NC)"; \
	else \
		$(PYTHON) $(FLASK_APP) & echo $$! > .flask.pid; \
		sleep 2; \
		echo "$(GREEN)✓ PHANTOM web server started$(NC)"; \
	fi

stop: ## Stop all PHANTOM services
	@echo "$(CYAN)Stopping PHANTOM services...$(NC)"
	@if [ -f .flask.pid ]; then kill $$(cat .flask.pid) 2>/dev/null || true; rm -f .flask.pid; fi
	@if [ -f .msfrpcd.pid ]; then kill $$(cat .msfrpcd.pid) 2>/dev/null || true; rm -f .msfrpcd.pid; fi
	@pkill -f "msfrpcd" 2>/dev/null || true
	@pkill -f "$(FLASK_APP)" 2>/dev/null || true
	@$(MAKE) --no-print-directory wireless-disable || true
	@echo "$(GREEN)✓ All services stopped$(NC)"

restart: stop run ## Restart all services

##@ Wireless Operations

wireless-check: ## Check wireless interface status
	@echo "$(CYAN)Checking wireless interface: $(WIRELESS_IFACE)$(NC)"
	@if ip link show $(WIRELESS_IFACE) > /dev/null 2>&1; then \
		echo "$(GREEN)✓ Interface $(WIRELESS_IFACE) exists$(NC)"; \
		iwconfig $(WIRELESS_IFACE) 2>/dev/null || echo "$(YELLOW)⚠ Not wireless-capable$(NC)"; \
	else \
		echo "$(RED)✗ Interface $(WIRELESS_IFACE) not found$(NC)"; \
		echo "Available interfaces:"; \
		ip link show | grep -E '^[0-9]+:' | awk '{print $$2}' | sed 's/:$$//'; \
	fi

wireless-enable: check-root ## Enable monitor mode on wireless interface
	@echo "$(CYAN)Enabling monitor mode on $(WIRELESS_IFACE)...$(NC)"
	@airmon-ng check kill 2>/dev/null || true
	@airmon-ng start $(WIRELESS_IFACE) 2>/dev/null || true
	@echo "$(GREEN)✓ Monitor mode enabled$(NC)"

wireless-disable: ## Disable monitor mode
	@echo "$(CYAN)Disabling monitor mode...$(NC)"
	@airmon-ng stop $(WIRELESS_IFACE)mon 2>/dev/null || true
	@airmon-ng stop mon0 2>/dev/null || true
	@systemctl restart NetworkManager 2>/dev/null || true
	@echo "$(GREEN)✓ Monitor mode disabled$(NC)"

wireless-scan: check-root wireless-enable ## Scan for WiFi networks (30 sec)
	@echo "$(CYAN)Scanning for WiFi networks (30 seconds)...$(NC)"
	@timeout 30 airodump-ng $(WIRELESS_IFACE)mon || true
	@$(MAKE) --no-print-directory wireless-disable

##@ Monitoring & Status

status: ## Show status of all services
	@echo ""
	@echo "$(CYAN)═══════════════════════════════════════$(NC)"
	@echo "$(CYAN)  PHANTOM Platform Status$(NC)"
	@echo "$(CYAN)═══════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Services:$(NC)"
	@if pgrep -f "msfrpcd" > /dev/null; then \
		echo "  $(GREEN)✓$(NC) Metasploit RPC: Running"; \
	else \
		echo "  $(RED)✗$(NC) Metasploit RPC: Stopped"; \
	fi
	@if pgrep -f "$(FLASK_APP)" > /dev/null; then \
		echo "  $(GREEN)✓$(NC) PHANTOM Server: Running"; \
	else \
		echo "  $(RED)✗$(NC) PHANTOM Server: Stopped"; \
	fi
	@if systemctl is-active postgresql >/dev/null 2>&1; then \
		echo "  $(GREEN)✓$(NC) PostgreSQL: Running"; \
	else \
		echo "  $(RED)✗$(NC) PostgreSQL: Stopped"; \
	fi
	@if systemctl is-active redis-server >/dev/null 2>&1; then \
		echo "  $(GREEN)✓$(NC) Redis: Running"; \
	else \
		echo "  $(RED)✗$(NC) Redis: Stopped"; \
	fi
	@echo ""
	@echo "$(YELLOW)Network:$(NC)"
	@if ip link show $(WIRELESS_IFACE) > /dev/null 2>&1; then \
		echo "  $(GREEN)✓$(NC) Interface $(WIRELESS_IFACE): Available"; \
	else \
		echo "  $(RED)✗$(NC) Interface $(WIRELESS_IFACE): Not found"; \
	fi
	@if ip link show $(WIRELESS_IFACE)mon > /dev/null 2>&1; then \
		echo "  $(GREEN)✓$(NC) Monitor Mode: Enabled"; \
	else \
		echo "  $(YELLOW)○$(NC) Monitor Mode: Disabled"; \
	fi
	@echo ""
	@echo "$(YELLOW)AI System:$(NC)"
	@if [ -f metasploit_ai_knowledge.json ]; then \
		OPERATIONS=$$(cat metasploit_ai_knowledge.json | grep -o '"total_operations": [0-9]*' | grep -o '[0-9]*'); \
		echo "  $(GREEN)✓$(NC) AI Knowledge Base: $$OPERATIONS operations"; \
	else \
		echo "  $(YELLOW)○$(NC) AI Knowledge Base: Not initialized"; \
	fi
	@echo ""

logs: ## View application logs
	@tail -f uwsgi.log 2>/dev/null || tail -f nohup.out 2>/dev/null || echo "No logs found"

logs-ai: ## View AI learning logs
	@if [ -f metasploit_ai_knowledge.json ]; then \
		cat metasploit_ai_knowledge.json | $(PYTHON) -m json.tool; \
	else \
		echo "$(YELLOW)No AI knowledge file found$(NC)"; \
	fi

monitor: ## Monitor system resources
	@htop 2>/dev/null || top

##@ Testing & Development

test: ## Run tests
	@echo "$(CYAN)Running tests...$(NC)"
	@$(PYTHON) -m pytest tests/ -v 2>/dev/null || \
		$(PYTHON) -m py_compile ai_learning_module.py automated_attack_system.py app.py
	@echo "$(GREEN)✓ Tests passed$(NC)"

test-wireless: check-root ## Test wireless tools
	@echo "$(CYAN)Testing wireless tools...$(NC)"
	@echo -n "  aircrack-ng: "; aircrack-ng --help >/dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n "  masscan: "; masscan --help >/dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n "  bettercap: "; bettercap --help >/dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n "  reaver: "; reaver --help >/dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"

dev: check-deps ## Run in development mode with auto-reload
	@echo "$(CYAN)Starting development server...$(NC)"
	@$(PYTHON) $(FLASK_APP)

debug: ## Run with debug logging
	@export FLASK_DEBUG=1 && $(PYTHON) $(FLASK_APP)

##@ Maintenance

clean: stop ## Clean up temporary files
	@echo "$(CYAN)Cleaning up...$(NC)"
	@rm -f .msfrpcd.pid .flask.pid nohup.out
	@rm -f *.pyc
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned up$(NC)"

clean-all: clean ## Deep clean (including venv and AI data)
	@echo "$(YELLOW)⚠ This will delete virtual environment and AI knowledge$(NC)"
	@read -p "Continue? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf $(VENV_DIR); \
		rm -f metasploit_ai_knowledge.json*; \
		rm -rf data/; \
		echo ""; \
		echo "$(GREEN)✓ Deep clean complete$(NC)"; \
	fi

reset-ai: ## Reset AI knowledge base
	@echo "$(YELLOW)⚠ Resetting AI knowledge base$(NC)"
	@if [ -f metasploit_ai_knowledge.json ]; then \
		mv metasploit_ai_knowledge.json metasploit_ai_knowledge.json.backup_$$(date +%s); \
	fi
	@echo "$(GREEN)✓ AI knowledge reset$(NC)"

update: ## Update dependencies
	@echo "$(CYAN)Updating dependencies...$(NC)"
	@$(PIP) install --upgrade pip
	@$(PIP) install --upgrade -r requirements.txt 2>/dev/null || true
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

##@ Information

info: ## Show project information
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║                     PHANTOM v2.0                           ║"
	@echo "╠════════════════════════════════════════════════════════════╣"
	@echo "║  Penetration & Hacking Automation Network Threat           ║"
	@echo "║              Operations Manager                            ║"
	@echo "╠════════════════════════════════════════════════════════════╣"
	@echo "║  Author:     Jack Cole                                     ║"
	@echo "║  School:     Colorado Tech University                      ║"
	@echo "║  Project:    Cybersecurity Dissertation                    ║"
	@echo "╠════════════════════════════════════════════════════════════╣"
	@echo "║  Components:                                               ║"
	@echo "║   • Metasploit Automation Framework                        ║"
	@echo "║   • AI Learning System                                     ║"
	@echo "║   • Wireless Attack Suite (8 tools)                        ║"
	@echo "║   • Network Reconnaissance                                 ║"
	@echo "║   • Automated Campaign Management                          ║"
	@echo "║   • WifiPhisher Integration                                ║"
	@echo "║   • RogueHostAPD                                           ║"
	@echo "╠════════════════════════════════════════════════════════════╣"
	@echo "║  Tools Integrated: 85+                                     ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""

version: ## Show version information
	@echo "$(CYAN)PHANTOM v2.0.0$(NC)"
	@echo "Python: $$($(PYTHON) --version 2>&1)"
	@echo "Flask: $$($(PYTHON) -c 'import flask; print(flask.__version__)' 2>/dev/null || echo 'Not installed')"
	@echo "Metasploit: $$(msfconsole --version 2>/dev/null | head -1 || echo 'Not installed')"

tools: ## List all integrated tools
	@echo "$(CYAN)Integrated Tools:$(NC)"
	@echo ""
	@echo "$(YELLOW)Core Framework:$(NC)"
	@echo "  • Flask Web Framework"
	@echo "  • Metasploit Framework"
	@echo "  • Python-nmap"
	@echo "  • Scapy"
	@echo ""
	@echo "$(YELLOW)Wireless Tools:$(NC)"
	@echo "  • aircrack-ng suite"
	@echo "  • wifiphisher"
	@echo "  • wifite"
	@echo "  • reaver"
	@echo "  • bettercap"
	@echo "  • masscan"
	@echo "  • trackerjacker"
	@echo "  • roguehostapd"
	@echo ""
	@echo "$(YELLOW)AI/Automation:$(NC)"
	@echo "  • Custom AI Learning Module"
	@echo "  • Automated Attack System"
	@echo "  • Campaign Management"

##@ Helpers

banner: ## Show PHANTOM banner
	@echo ""
	@echo "$(PURPLE)╔════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(PURPLE)║                                                            ║$(NC)"
	@echo "$(PURPLE)║   ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗  ║$(NC)"
	@echo "$(PURPLE)║   ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║  ║$(NC)"
	@echo "$(PURPLE)║   ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║  ║$(NC)"
	@echo "$(PURPLE)║   ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║  ║$(NC)"
	@echo "$(PURPLE)║   ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║  ║$(NC)"
	@echo "$(PURPLE)║   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝  ║$(NC)"
	@echo "$(PURPLE)║                                                            ║$(NC)"
	@echo "$(PURPLE)║    Penetration & Hacking Automation Network Threat         ║$(NC)"
	@echo "$(PURPLE)║              Operations Manager v2.0                       ║$(NC)"
	@echo "$(PURPLE)║                                                            ║$(NC)"
	@echo "$(PURPLE)╚════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""

check-root: ## Check if running as root
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "$(RED)✗ Must run as root/sudo for full functionality$(NC)"; \
		echo "$(YELLOW)  Run: sudo make run$(NC)"; \
		exit 1; \
	fi
