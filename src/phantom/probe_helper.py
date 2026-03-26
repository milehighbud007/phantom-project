#!/usr/bin/env python3
"""
probe_helper.py - Optimized NDJSON client for MetasploitMCP ARP socket.
Refactored for buffered I/O, robust error handling, and JSON piping.
"""
from __future__ import annotations
import socket
import json
import time
import os
import sys
import logging
from typing import List, Optional, Dict, Any

SOCKET_PATH_DEFAULT = "/var/run/metasploitmcp/arp_socket"
logger = logging.getLogger("Phantom.ProbeHelper")

class ProbeError(RuntimeError):
    """Raised when the probe helper communication fails."""
    pass

def _parse_ndjson(raw_data: str) -> Dict[str, Any]:
    """Extracts the final JSON object from a newline-delimited stream."""
    lines = [ln.strip() for ln in raw_data.splitlines() if ln.strip()]
    if not lines:
        raise ProbeError("Server returned empty response")
    
    final_line = lines[-1]
    try:
        return json.loads(final_line)
    except json.JSONDecodeError as e:
        raise ProbeError(f"Failed to parse server response: {e}. Raw: {final_line[:50]}...")

def probe_ips(
    ips: List[str],
    iface: Optional[str] = None,
    socket_path: str = SOCKET_PATH_DEFAULT,
    timeout: float = 12.0,
    retries: int = 2,
    backoff: float = 0.5,
) -> Dict[str, Any]:
    """
    Probes a list of IPs via the Unix Domain Socket helper using buffered I/O.
    """
    if not ips:
        raise ProbeError("IP list cannot be empty")

    if not os.path.exists(socket_path):
        raise ProbeError(f"Socket not found at {socket_path}. Is the scapy helper running?")

    request = json.dumps({"ips": ips, "iface": iface} if iface else {"ips": ips}) + "\n"

    for attempt in range(1, retries + 1):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect(socket_path)
                sock.sendall(request.encode('utf-8'))
                
                with sock.makefile('r', encoding='utf-8', errors='replace') as reader:
                    raw_response = reader.read()
                
                return _parse_ndjson(raw_response)

        except (socket.timeout, ConnectionRefusedError, BrokenPipeError) as e:
            if attempt == retries:
                raise ProbeError(f"Connection failed after {retries} attempts: {e}")
            logger.warning(f"Probe attempt {attempt} failed ({e}), retrying in {backoff}s...")
            time.sleep(backoff * attempt)
        except Exception as e:
            raise ProbeError(f"Unexpected error during probing: {e}")

    raise ProbeError("Unknown error during IP probing")

def _cli_main():
    import argparse
    parser = argparse.ArgumentParser(description="Phantom Probe CLI")
    parser.add_argument("ips", nargs="+", help="Target IPs")
    parser.add_argument("--iface", "-i", help="Interface hint")
    parser.add_argument("--socket", "-s", default=SOCKET_PATH_DEFAULT, help="Socket path")
    parser.add_argument("--timeout", "-t", type=float, default=12.0, help="Timeout (sec)")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON for piping")
    
    args = parser.parse_args()
    try:
        result = probe_ips(
            args.ips, 
            iface=args.iface, 
            socket_path=args.socket, 
            timeout=args.timeout
        )
        if args.json:
            print(json.dumps(result))
        else:
            print(json.dumps(result, indent=2))
    except ProbeError as e:
        if args.json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    _cli_main()
