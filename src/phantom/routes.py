#!/usr/bin/env python3
"""
routes.py — Safe read-only API routes for MetasploitMCP.
Interfaces with the MetasploitMCP service adapter.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from phantom.MetasploitMCP import mcp_service

router = APIRouter(prefix="/api")

@router.get("/modules")
async def list_modules(mtype: str = "exploit") -> Dict:
    """Returns a list of available modules filtered by type."""
    if not mcp_service.is_connected():
        return {"modules": [], "status": "disconnected"}
    
    # Fetch from local cache in the adapter for speed
    modules = mcp_service.search_modules("") 
    return {"modules": modules, "count": len(modules)}

@router.get("/module")
async def get_module(name: str = Query(..., description="Full module path")) -> Dict:
    """Returns detailed metadata for a specific module."""
    if not mcp_service.is_connected():
        raise HTTPException(status_code=503, detail="Metasploit RPC disconnected")
    
    # Using 'exploit' as default type; logic can be expanded
    mtype = "exploit" if "exploit" in name else "auxiliary"
    info = mcp_service.client.modules.use(mtype, name).info
    
    if not info:
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
    if not mcp_service.is_connected():
        return {"payloads": []}
    
    payloads = list(mcp_service.client.modules.payloads)
    return {"payloads": payloads, "count": len(payloads)}

@router.get("/sessions")
async def list_sessions() -> Dict:
    """Returns all active meterpreter or shell sessions."""
    if not mcp_service.is_connected():
        return {"sessions": [], "error": "RPC offline"}
    
    sessions = mcp_service.get_sessions()
    return {"sessions": sessions, "count": len(sessions)}

@router.get("/health")
async def health_check() -> Dict:
    """System health status for the MCP dashboard."""
    return {
        "status": "online" if mcp_service.is_connected() else "offline",
        "host": mcp_service.host,
        "port": mcp_service.port
    }
