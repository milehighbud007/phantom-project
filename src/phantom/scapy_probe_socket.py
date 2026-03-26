#!/usr/bin/env python3
import os
import json
import socket
import time
import logging
import signal
import threading
from scapy.all import srp, Ether, ARP, conf

# Configuration
SOCKET_PATH = "/var/run/metasploitmcp/arp_socket"
BACKLOG = 10
TIMEOUT = 2
RETRY = 1
conf.verb = 0

logging.basicConfig(level=logging.INFO, format='%(asctime)s [SCAPY] %(message)s')
logger = logging.getLogger("ScapyServer")

def probe_ips_bulk(ips, iface=None):
    """
    Sends a bulk ARP request for efficiency.
    Returns a dictionary of {ip: mac}
    """
    if not ips:
        return {}
    
    results = {ip: "unknown" for ip in ips}
    try:
        # Build bulk ARP request
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ips)
        ans, _ = srp(pkt, iface=iface, timeout=TIMEOUT, retry=RETRY, verbose=0)
        
        for _, r in ans:
            if r.psrc in results:
                results[r.psrc] = r.hwsrc.lower()
    except Exception as e:
        logger.error(f"Bulk probe error: {e}")
        
    return results

def handle_client(conn):
    """Handles individual socket connections."""
    try:
        conn.settimeout(5.0)
        raw = conn.recv(16384) # Increased buffer for large IP lists
        if not raw:
            return

        try:
            data = json.loads(raw.decode('utf-8'))
            ips = data.get("ips", [])
            iface = data.get("iface")
            
            logger.info(f"Probing {len(ips)} targets on {iface or 'default'}...")
            results = probe_ips_bulk(ips, iface=iface)
            
            response = {
                "results": results, 
                "ts": int(time.time()),
                "status": "complete"
            }
            conn.sendall((json.dumps(response) + "\n").encode('utf-8'))
            
        except json.JSONDecodeError:
            conn.sendall(json.dumps({"error": "invalid json"}).encode())
    except Exception as e:
        logger.error(f"Client handler error: {e}")
    finally:
        conn.close()

def setup_socket():
    """Ensures socket directory and permissions are correct."""
    d = os.path.dirname(SOCKET_PATH)
    if not os.path.exists(d):
        os.makedirs(d, mode=0o755, exist_ok=True)
    
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
        
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    os.chmod(SOCKET_PATH, 0o777) # Allow web user and root to communicate
    sock.listen(BACKLOG)
    return sock

def cleanup(signum, frame):
    """Graceful shutdown."""
    logger.info("Shutting down Scapy Probe Server...")
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    os._exit(0)

def run_server():
    """Main server loop."""
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        server_sock = setup_socket()
        logger.info(f"Scapy Probe Server active on {SOCKET_PATH}")
        
        while True:
            conn, _ = server_sock.accept()
            # Handle in a thread so bulk scans don't block the listener
            t = threading.Thread(target=handle_client, args=(conn,), daemon=True)
            t.start()
    except Exception as e:
        logger.critical(f"Server crashed: {e}")
        cleanup(None, None)

if __name__ == "__main__":
    if os.getuid() != 0:
        print("CRITICAL: Scapy server must run as ROOT for raw socket access.")
        exit(1)
    run_server()
