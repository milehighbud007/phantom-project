#!/usr/bin/env python3
"""
MSFRPCClient - Robust MessagePack-RPC client for Metasploit.
"""
import msgpack
import requests
import logging
import argparse
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Phantom.MSFRPC")

class MSFRPCClient:
    """
    Handles authentication and low-level MessagePack-RPC communication with msfrpcd.
    """
    def __init__(self, host="127.0.0.1", port=55553, user="msf", password="kali", use_ssl=False):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.protocol = "https" if use_ssl else "http"
        self.url = f"{self.protocol}://{self.host}:{self.port}/api/"
        self.headers = {"Content-Type": "binary/message-pack"}
        self.token = None
        self.session = requests.Session()

        if use_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.session.verify = False

    def _pack(self, method: str, params: list) -> bytes:
        # Standard MSF RPC format: [method, param1, param2, ...]
        payload = [method] + params
        return msgpack.packb(payload, use_bin_type=True)

    def _unpack(self, content: bytes) -> Any:
        return msgpack.unpackb(content, raw=False, strict_map_key=False)

    def login(self) -> bool:
        """Authenticate and store the session token."""
        resp = self.call("auth.login", [self.user, self.password])
        if isinstance(resp, dict) and resp.get("result") == "success":
            self.token = resp.get("token")
            logger.info("MSF RPC Authentication successful.")
            return True
        
        logger.error(f"MSF RPC Authentication failed: {resp}")
        return False

    def call(self, method: str, params: list) -> Any:
        """Executes an RPC call. Automatically prepends token if authenticated."""
        no_token_methods = ["auth.login"]
        
        # Build params: [token, p1, p2] or just [p1, p2]
        call_params = params
        if self.token and method not in no_token_methods:
            call_params = [self.token] + params

        data = self._pack(method, call_params)
        try:
            resp = self.session.post(self.url, data=data, headers=self.headers, timeout=12)
            resp.raise_for_status()
            result = self._unpack(resp.content)
            
            # Handle token expiration (Metasploit returns 'error' key)
            if isinstance(result, dict) and result.get("error") and "token" in result.get("error_message", "").lower():
                logger.warning("MSF Token expired. Attempting re-login...")
                if self.login():
                    return self.call(method, params) # Retry once
            
            return result
        except Exception as e:
            logger.error(f"RPC Call '{method}' failed: {e}")
            return {"error": True, "message": str(e)}

def _cli_main():
    parser = argparse.ArgumentParser(description="Metasploit RPC Diagnostic Tool")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=55553)
    parser.add_argument("--user", default="msf")
    parser.add_argument("--pass", dest="passwd", default="kali")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS")
    args = parser.parse_args()

    client = MSFRPCClient(host=args.host, port=args.port, user=args.user, password=args.passwd, use_ssl=args.ssl)
    
    print(f"[*] Attempting connection to {client.url}...")
    if client.login():
        print(f"[+] Connected! Token: {client.token}")
        ver = client.call("core.version", [])
        print(f"[+] MSF Version: {ver.get('version', 'Unknown')}")
    else:
        print("[-] Connection failed. Check your credentials and msfrpcd status.")
        sys.exit(1)

if __name__ == "__main__":
    _cli_main()
