#!/usr/bin/env python3
"""
routes.py — Safe read-only API routes for MetasploitMCP.
Interfaces with the MetasploitMCP service adapter.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict

from phantom.config import config
from phantom.msf.adapter import MsftAdapter

router = APIRouter(prefix="/api")
_mcp_service = None


def get_mcp_service():
    """Create the adapter lazily so imports do not open RPC sessions."""
    global _mcp_service
    if _mcp_service is None:
        _mcp_service = MsftAdapter(
            password=config.MSF_RPC_PASSWORD,
            host=config.MSF_RPC_HOST,
            port=config.MSF_RPC_PORT,
            user=config.MSF_RPC_USER,
        )
    return _mcp_service

@router.get("/modules")
async def list_modules(mtype: str = "exploit") -> Dict:
    """Returns a list of available modules filtered by type."""
    mcp_service = get_mcp_service()
    if not mcp_service.is_connected():
        return {"modules": [], "status": "disconnected"}

    # Fetch from local cache in the adapter for speed
    modules = mcp_service.find_modules_by_keyword("", module_type=mtype)
    return {"modules": modules, "count": len(modules)}

@router.get("/module")
async def get_module(name: str = Query(..., description="Full module path")) -> Dict:
    """Returns detailed metadata for a specific module."""
    mcp_service = get_mcp_service()
    if not mcp_service.is_connected():
        raise HTTPException(status_code=503, detail="Metasploit RPC disconnected")

    # Using 'exploit' as default type; logic can be expanded
    mtype = "exploit" if "exploit" in name else "auxiliary"
    normalized_name = name.split("/", 1)[1] if name.startswith(f"{mtype}/") else name
    info = mcp_service.get_module_meta(mtype, normalized_name)

    if not info or info.get("error"):
        raise HTTPException(status_code=404, detail="Module not found")

    return {
        "name": name,
        "description": info.get("description", "No description provided"),
        "type": mtype,
        "references": info.get("references", []),
        "options": list(info.get("options", {}).keys())
    }

@router.get("/payloads")
async def list_payloads() -> Dict:
    """Lists available payloads from the RPC server."""
    mcp_service = get_mcp_service()
    if not mcp_service.is_connected():
        return {"payloads": []}

    payloads = list(mcp_service.client.modules.payloads)
    return {"payloads": payloads, "count": len(payloads)}

@router.get("/sessions")
async def list_sessions() -> Dict:
    """Returns all active meterpreter or shell sessions."""
    mcp_service = get_mcp_service()
    if not mcp_service.is_connected():
        return {"sessions": [], "error": "RPC offline"}

    sessions = mcp_service.client.sessions.list
    if callable(sessions):
        sessions = sessions()
    return {"sessions": sessions, "count": len(sessions)}

@router.get("/health")
async def health_check() -> Dict:
    """System health status for the MCP dashboard."""
    mcp_service = get_mcp_service()
    return {
        "status": "online" if mcp_service.is_connected() else "offline",
        "host": mcp_service.host,
        "port": mcp_service.port
    }
