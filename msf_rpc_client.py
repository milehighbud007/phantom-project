#!/usr/bin/env python3
"""
Simple MessagePack-RPC client for Metasploit RPC (msfrpcd).
Sends MessagePack-RPC requests to the /api/ endpoint and prints responses.

Usage:
    python msf_rpc_client.py                 # runs a built-in auth/login test
    python msf_rpc_client.py --host 127.0.0.1 --port 55553 --user msf --pass kali

Notes:
- Requires: requests, msgpack
    pip install requests msgpack
- Adjust URL path if your MSF RPC uses a different endpoint.
"""

import argparse
import msgpack
import requests
import sys
import time

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 55553
DEFAULT_PATH = "/api/"
DEFAULT_TIMEOUT = 5.0

class MSFRPCClient:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, path=DEFAULT_PATH, timeout=DEFAULT_TIMEOUT):
        self.host = host
        self.port = int(port)
        self.path = path if path.startswith("/") else "/" + path
        self.url = f"http://{self.host}:{self.port}{self.path}"
        self.headers = {"Content-Type": "binary/message-pack"}
        self._req_id = 1

    def _pack_request(self, method, params):
        payload = [method, params, self._req_id]
        self._req_id += 1
        return msgpack.packb(payload, use_bin_type=True)

    def _unpack_response(self, content):
        # strict_map_key=False allows non-str map keys
        return msgpack.unpackb(content, raw=False, strict_map_key=False)

    def call(self, method, params):
        data = self._pack_request(method, params)
        try:
            resp = requests.post(self.url, data=data, headers=self.headers, timeout=DEFAULT_TIMEOUT)
        except requests.RequestException as e:
            return {"error": True, "error_message": f"Request failed: {e}"}
        if resp.status_code != 200:
            # If server returns HTML or non-200, include body snippet
            body = resp.content.decode("utf-8", errors="replace")
            return {"error": True, "error_message": f"HTTP {resp.status_code}", "body": body[:512]}
        try:
            result = self._unpack_response(resp.content)
            return {"error": False, "result": result}
        except Exception as e:
            return {"error": True, "error_message": f"Unpack failed: {e}", "raw": resp.content[:512]}

def main():
    p = argparse.ArgumentParser(description="Minimal MessagePack-RPC client for Metasploit RPC")
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", default=DEFAULT_PORT, type=int)
    p.add_argument("--path", default=DEFAULT_PATH)
    p.add_argument("--user", default="msf", help="username for auth.login test")
    p.add_argument("--pass", dest="passwd", default="kali", help="password for auth.login test")
    p.add_argument("--timeout", default=DEFAULT_TIMEOUT, type=float)
    args = p.parse_args()

    client = MSFRPCClient(host=args.host, port=args.port, path=args.path, timeout=args.timeout)

    print(f"Testing MSF RPC at {client.url}")
    # try auth.login
    resp = client.call("auth.login", [args.user, args.passwd])
    if resp.get("error"):
        print("Auth call returned error:", resp.get("error_message"))
        if "body" in resp:
            print("HTTP body (truncated):")
            print(resp["body"])
        if "raw" in resp:
            print("Raw response (bytes, truncated):", resp["raw"])
        sys.exit(1)

    # result may be an array or map depending on server version.
    result = resp.get("result")
    print("Raw result from server:", result)

    # The token is commonly found as result.get('token') if server returned a map/dict.
    token = None
    if isinstance(result, dict):
        token = result.get("token") or result.get(b"token")
    elif isinstance(result, (list, tuple)):
        # Some server implementations wrap the actual response; search for token in nested structures.
        def find_token(obj):
            if isinstance(obj, dict):
                return obj.get("token") or obj.get(b"token")
            if isinstance(obj, (list, tuple)):
                for item in obj:
                    t = find_token(item)
                    if t:
                        return t
            return None
        token = find_token(result)

    if token:
        print("✓ Token received:", token)
    else:
        print("✗ No token found in response. Full unpacked result shown above.")

    # Example: make another call if token available (shows how to pass token)
    if token:
        # many RPC methods require the token as the first positional parameter
        resp2 = client.call("module.info", [token, "exploit", "unix/ftp/vsftpd_234_backdoor"])
        if resp2.get("error"):
            print("module.info error:", resp2.get("error_message"))
        else:
            print("module.info result (truncated):")
            # pretty-print maybe large; just show a small sample
            out = resp2.get("result")
            if isinstance(out, (dict, list)):
                import json
                try:
                    print(json.dumps(out, indent=2)[:1000])
                except Exception:
                    print(str(out)[:1000])
            else:
                print(str(out)[:1000])

if __name__ == "__main__":
    main()
