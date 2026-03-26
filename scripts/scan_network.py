#!/usr/bin/env python3
"""
scan_network.py - Discovery -> Nmap Pipeline
DEFAULT MODE: INTENSE (-A -T4 -p- --script=vuln)
"""
import sys
import json
import subprocess
import argparse
import os
import shutil
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent
PROBE = ROOT / "src/phantom/probe_helper.py"
REPORTER = ROOT / "scripts/reporting_module.py"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target range (e.g. 10.0.0.0/24)")
    parser.add_argument("-o", "--output", default="scan_results.xml", help="Output XML file")
    parser.add_argument("--fast", action="store_true", help="Downgrade to fast scan mode")
    args = parser.parse_args()

    # 1. DISCOVERY
    print(f"[*] [PHANTOM] Engaging Target: {args.target}")
    print("[*] Phase 1: Stealth Discovery...")
    
    # Ensure probe_helper exists
    if not PROBE.exists():
        print(f"[!] Error: {PROBE} not found.")
        sys.exit(1)

    disc = subprocess.run([sys.executable, str(PROBE), args.target, "--json"], capture_output=True, text=True)
    try:
        ips = list(json.loads(disc.stdout)["results"].keys())
        print(f"[+] Hosts Locked: {len(ips)}")
    except:
        print("[-] No targets found. Aborting.")
        sys.exit(0)

    # 2. SCANNING (Defaulting to INTENSE)
    if args.fast:
        nmap_flags = ["-F", "-sV"]
        print("[*] Phase 2: Fast Scan Engaged")
    else:
        # Aggressive, All Ports, Vulnerability Scripts
        nmap_flags = ["-A", "-T4", "-p-", "--script", "vuln", "--min-rate", "500"]
        print("[!] Phase 2: INTENSE SCAN ENGAGED (This may take time)")

    nmap_cmd = ["nmap", "-iL", "-"] + nmap_flags + ["-oX", args.output]
    
    with subprocess.Popen(nmap_cmd, stdin=subprocess.PIPE, text=True) as proc:
        proc.communicate(input="\n".join(ips))

    # 3. VISUAL ACQUISITION (Screenshots)
    if shutil.which("gowitness"):
        print("[*] Phase 3: Visual Acquisition (gowitness)...")
        os.makedirs("screenshots", exist_ok=True)
        for ip in ips:
            # Attempt screenshot on common web ports
            subprocess.run(["gowitness", "single", "-o", f"screenshots/{ip}.png", f"http://{ip}"], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("[*] Phase 3: Skipped (gowitness not installed)")

    # 4. REPORTING
    print("[*] Phase 4: Generating Dashboard...")
    subprocess.run([sys.executable, str(REPORTER), args.output, "-o", "dashboard.html"])
    print(f"\n[+] MISSION COMPLETE. ACCESS: dashboard.html")

if __name__ == "__main__":
    main()
