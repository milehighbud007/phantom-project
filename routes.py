# routes.py — safe read-only API routes for MetasploitMCP

from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

# Dummy module list for testing — replace with real MCP calls later
@router.get("/api/modules")
def list_modules() -> Dict:
    return {
        "modules": [
            "exploit/windows/smb/ms17_010",
            "auxiliary/scanner/ssh/ssh_login",
            "auxiliary/scanner/http/http_version"
        ]
    }

@router.get("/api/module")
def get_module(name: str) -> Dict:
    return {
        "name": name,
        "description": "This is a mock description for module: " + name,
        "type": "exploit" if "exploit" in name else "auxiliary"
    }

@router.get("/api/payloads")
def list_payloads() -> Dict:
    return {
        "payloads": [
            "windows/meterpreter/reverse_tcp",
            "linux/x86/shell_reverse_tcp"
        ]
    }

@router.get("/api/listeners")
def list_listeners() -> Dict:
    return {
        "listeners": []
    }

@router.get("/api/sessions")
def list_sessions() -> Dict:
    return {
        "sessions": []
    }
