#!/usr/bin/env python3
import os
import json
import socket
from scapy.all import srp, Ether, ARP, conf

SOCKET_PATH = "/var/run/metasploitmcp/arp_socket"
BACKLOG = 5
CONF_TIMEOUT = 2
CONF_RETRY = 1

conf.verb = 0

def probe_ip(ip, iface=None, timeout=CONF_TIMEOUT):
    try:
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
        ans, _ = srp(pkt, iface=iface, timeout=timeout, retry=CONF_RETRY)
        for _, r in ans:
            if getattr(r, "psrc", None) == ip:
                return r.hwsrc.lower()
    except Exception:
        pass
    return None

def handle_request(data):
    ips = data.get("ips", [])
    iface = data.get("iface")
    results = {}
    for ip in ips:
        mac = probe_ip(ip, iface=iface)
        results[ip] = mac or "unknown"
    return {"results": results, "ts": int(__import__('time').time())}

def ensure_socket_dir():
    d = os.path.dirname(SOCKET_PATH)
    os.makedirs(d, exist_ok=True)
    os.chmod(d, 0o750)

def run_server():
    if os.path.exists(SOCKET_PATH):
        try:
            os.remove(SOCKET_PATH)
        except Exception:
            pass
    ensure_socket_dir()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    os.chmod(SOCKET_PATH, 0o770)
    sock.listen(BACKLOG)
    try:
        while True:
            conn, _ = sock.accept()
            try:
                raw = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    raw += chunk
                if not raw:
                    conn.close()
                    continue
                try:
                    data = json.loads(raw.decode())
                except Exception:
                    conn.sendall(json.dumps({"error":"invalid json"}).encode())
                    conn.close()
                    continue
                result = handle_request(data)
                conn.sendall(json.dumps(result).encode())
            finally:
                conn.close()
    finally:
        try:
            sock.close()
        except Exception:
            pass
        try:
            os.remove(SOCKET_PATH)
        except Exception:
            pass

if __name__ == "__main__":
    run_server()
