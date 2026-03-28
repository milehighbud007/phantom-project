#!/usr/bin/env python3
"""
Metasploit MCP Server for Phantom Project
"""

from fastmcp import FastMCP

mcp = FastMCP("metasploit-mcp")


def get_msf_client():
    from phantom.msf.rpc_client import MSFRPCClient
    from phantom.config import config

    client = MSFRPCClient(
        host=config.MSF_RPC_HOST,
        port=config.MSF_RPC_PORT,
        user=config.MSF_RPC_USER,
        password=config.MSF_RPC_PASSWORD,
        use_ssl=config.MSF_RPC_SSL,
    )
    client.login()
    return client


@mcp.tool()
def list_sessions() -> str:
    try:
        client = get_msf_client()
        sessions = client.call("session.list", [])
        return str(sessions)
    except Exception as e:
        return f"Error: {e}"


@mcp.resource("msf://sessions")
def sessions_resource() -> str:
    client = get_msf_client()
    data = client.call("session.list", [])
    return str(data)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
