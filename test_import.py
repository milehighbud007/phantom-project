#!/usr/bin/env python3
import sys
import os

def check_environment():
    """Diagnostic tool to verify Phantom Project dependencies and permissions."""
    
    # Colors for output
    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    NC = "\033[0m"

    dependencies = [
        ("fastapi", "FastAPI (Web Framework)"),
        ("uvicorn", "Uvicorn (ASGI Server)"),
        ("pymetasploit3", "PyMetasploit3 (MSF RPC Client)"),
        ("scapy.all", "Scapy (Packet Manipulation)"),
        ("flask", "Flask (Dashboard UI)"),
        ("nmap", "Python-Nmap (Scanner Interface)")
    ]

    print(f"{YELLOW}=== Phantom Environment Diagnostic ==={NC}")
    
    # 1. Check Python Version
    if sys.version_info >= (3, 10):
        print(f"[{GREEN}PASS{NC}] Python Version: {sys.version.split()[0]}")
    else:
        print(f"[{RED}FAIL{NC}] Python 3.10+ required. Current: {sys.version.split()[0]}")

    # 2. Check Dependencies
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"[{GREEN}PASS{NC}] {name}")
        except ImportError:
            print(f"[{RED}FAIL{NC}] {name} is NOT installed.")

    # 3. Check Privileges (Important for Scapy)
    if os.getuid() == 0:
        print(f"[{GREEN}PASS{NC}] Running as Root (Required for Raw Sockets)")
    else:
        print(f"[{YELLOW}WARN{NC}] Not running as Root. Scapy probing may fail.")

    print(f"{YELLOW}======================================{NC}")

if __name__ == "__main__":
    check_environment()
