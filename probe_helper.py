#!/usr/bin/env python3
"""
probe_helper.py

Lightweight client for /var/run/metasploitmcp/arp_socket using newline-delimited JSON (ndjson).
Provides a simple API and a tiny CLI for testing.

Usage (library):
    from probe_helper import probe_ips, ProbeError
    result = probe_ips(["10.0.0.62"], iface=None, timeout=12, retries=1)

Usage (CLI):
    ./probe_helper.py 10.0.0.62 10.0.0.1 --iface wlan0 --timeout 12

Behavior:
- Sends a single newline-terminated JSON request {"ips":[...], "iface": ...}
- Reads server messages (ack then final JSON). Final JSON is taken as the last newline-terminated JSON received.
- Returns the parsed final JSON (dict).
- Raises ProbeError on failure.
"""
from __future__ import annotations
import socket
import json
import time
from typing import List, Optional, Dict, Any

SOCKET_PATH_DEFAULT = "/var/run/metasploitmcp/arp_socket"


class ProbeError(RuntimeError):
    pass


def _send_request_and_read(sock: socket.socket, request_json: str, recv_timeout: float) -> str:
    """
    Send newline-terminated request_json and read until socket closes or timeout is reached.
    Returns the raw bytes received as UTF-8 string (may contain multiple newline JSON messages).
    """
    sock.settimeout(recv_timeout)
    sock.sendall(request_json.encode())
    # read loop: collect until the server closes or we hit a read timeout
    out = bytearray()
    while True:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            # timeout: stop reading and return what we have
            break
        if not chunk:
            # peer closed orderly
            break
        out.extend(chunk)
    return out.decode(errors="replace")


def _build_request(ips: List[str], iface: Optional[str]) -> str:
    payload = {"ips": ips}
    if iface:
        payload["iface"] = iface
    return json.dumps(payload) + "\n"


def probe_ips(
    ips: List[str],
    iface: Optional[str] = None,
    socket_path: str = SOCKET_PATH_DEFAULT,
    timeout: float = 12.0,
    retries: int = 1,
    backoff: float = 0.25,
) -> Dict[str, Any]:
    """
    Probe a list of IPs via the metasploitmcp helper.

    Parameters:
    - ips: list of IPv4 strings to probe
    - iface: optional interface hint string (e.g., "wlan1")
    - socket_path: path to the unix domain socket
    - timeout: total timeout in seconds for the call (each attempt uses this as recv timeout)
    - retries: number of attempts (>=1)
    - backoff: seconds to wait between attempts

    Returns:
    - dict parsed from the final JSON the server returns (typically {"results": {...}, "ts": ..., ...})

    Raises:
    - ProbeError if the request cannot be completed or server response is invalid.
    """
    if not ips:
        raise ProbeError("empty ips list")

    request = _build_request(ips, iface)

    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                sock.settimeout(timeout)
                sock.connect(socket_path)
                # send and read
                raw = _send_request_and_read(sock, request, recv_timeout=timeout)
            finally:
                try:
                    sock.close()
                except Exception:
                    pass

            if not raw:
                raise ProbeError("no response from helper")

            # server uses ndjson: split by newlines, ignore empty lines
            lines = [ln for ln in raw.splitlines() if ln.strip()]
            if not lines:
                raise ProbeError("no JSON lines in response")

            # final JSON should be the last non-empty line
            final_line = lines[-1]
            try:
                parsed = json.loads(final_line)
            except Exception as e:
                raise ProbeError(f"failed to parse final JSON from helper: {e}; raw={final_line!r}")

            return parsed

        except (socket.timeout, ConnectionRefusedError, FileNotFoundError) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * attempt)
                continue
            raise ProbeError(f"socket/connect/read failed after {retries} attempts: {exc}") from exc
        except ProbeError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * attempt)
                continue
            raise ProbeError(f"unexpected error contacting helper: {exc}") from exc

    raise ProbeError(f"probe failed: {last_exc!r}")


# Simple CLI
def _cli_main():
    import argparse

    parser = argparse.ArgumentParser(description="Probe IPs via metasploitmcp scapy helper")
    parser.add_argument("ips", nargs="+", help="IP(s) to probe")
    parser.add_argument("--iface", "-i", help="interface hint (optional)")
    parser.add_argument("--socket", "-s", default=SOCKET_PATH_DEFAULT, help="unix socket path")
    parser.add_argument("--timeout", "-t", type=float, default=12.0, help="recv timeout seconds")
    parser.add_argument("--retries", "-r", type=int, default=1, help="number of attempts")
    parser.add_argument("--raw", action="store_true", help="print raw server response (all lines)")
    args = parser.parse_args()

    try:
        parsed = probe_ips(args.ips, iface=args.iface, socket_path=args.socket, timeout=args.timeout, retries=args.retries)
    except ProbeError as e:
        print("ERROR:", e)
        raise SystemExit(2)

    if args.raw:
        # for debugging, request again and show all lines
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(args.timeout)
            sock.connect(args.socket)
            raw = _send_request_and_read(sock, _build_request(args.ips, args.iface), recv_timeout=args.timeout)
            sock.close()
            print(raw)
        except Exception as e:
            print("ERROR reading raw:", e)

    print(json.dumps(parsed, indent=2, sort_keys=True))


if __name__ == "__main__":
    _cli_main()
