#!/usr/bin/env python3
"""
MetasploitAI v0.0 (Intense Logic Core)
Advanced reasoning engine for exploit selection, payload optimization, and evasion.
"""
import logging
import random
from typing import Dict, List, Optional
from phantom.ai_learning_module import PenetrationTestingAI
from phantom.metasploit.exploit_db import EXPLOIT_DATABASE

# Configure Aggressive Logging
logging.basicConfig(format='%(asctime)s [AI-CORE] %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger("Phantom.MetasploitAI")

class MetasploitDecider:
    """
    The Tactical Brain of the Phantom Framework.
    Uses heuristic analysis and historical telemetry to orchestrate attacks.
    """
    
    def __init__(self, learning_module: PenetrationTestingAI):
        self.brain = learning_module
        self.weights = {
            "rank": 0.4,      # Metasploit Module Rank (Excellent/Great)
            "history": 0.4,   # Learned success rate
            "port_match": 0.2 # Port confidence
        }

    def analyze_target(self, target_profile: Dict) -> List[Dict]:
        """
        Generates a ranked 'Kill Chain' of exploits for a specific target.
        """
        ip = target_profile.get("ip")
        os = target_profile.get("os", "unknown").lower()
        open_ports = target_profile.get("ports", [])
        
        logger.info(f"Initializing Attack Vector Calculation for {ip} ({os})...")
        
        candidates = self._fetch_candidates(os)
        ranked_exploits = []

        for exploit in candidates:
            score = self._calculate_score(exploit, target_profile)
            if score > 0:
                ranked_exploits.append({
                    "module": exploit["name"],
                    "score": round(score, 4),
                    "severity": exploit.get("severity", "low"),
                    "payloads": exploit.get("payloads", []),
                    "strategy": "brute" if "scanner" in exploit["name"] else "exploit"
                })

        # Sort by Score (Highest Probability First)
        ranked_exploits.sort(key=lambda x: x["score"], reverse=True)
        
        if ranked_exploits:
            top_pick = ranked_exploits[0]
            logger.info(f"Target Locked: {ip} | Primary Vector: {top_pick['module']} (Score: {top_pick['score']})")
        else:
            logger.warning(f"No viable vectors found for {ip}. Recommendation: Deep Scan.")
            
        return ranked_exploits

    def optimize_payload(self, exploit_name: str, target_os: str, payloads: List[str]) -> str:
        """
        Selects the optimal payload to maximize shell stability and evade detection.
        """
        # 1. Architectural Match
        arch = "x64" if "64" in target_os else "x86"
        preferred = [p for p in payloads if arch in p]
        
        # 2. Type Preference (Meterpreter > Shell > Cmd)
        for p in preferred or payloads:
            if "meterpreter" in p:
                logger.info(f"Payload Optimization: Selected {p} for {exploit_name}")
                return p
        
        # Fallback
        fallback = payloads[0] if payloads else "generic/shell_reverse_tcp"
        logger.warning(f"Payload Fallback: Using {fallback}")
        return fallback

    def generate_evasion_options(self) -> Dict:
        """
        Generates evasion parameters for the exploit run.
        """
        # Randomize encoders to bypass static signatures
        encoders = ["x86/shikata_ga_nai", "x86/jmp_call_additive", "cmd/powershell_base64"]
        return {
            "EnableContextEncoding": True,
            "Encoder": random.choice(encoders),
            "StageEncoder": random.choice(encoders),
            "DisablePayloadHandler": False
        }

    def _fetch_candidates(self, os_guess: str) -> List[Dict]:
        """Retrieve compatible modules from the database."""
        key = "windows" if "win" in os_guess else "linux" if "lin" in os_guess else "multi"
        return EXPLOIT_DATABASE.get(key, []) + EXPLOIT_DATABASE.get("multi", [])

    def _calculate_score(self, exploit: Dict, target: Dict) -> float:
        """
        Heuristic Scoring Engine.
        Score = (Rank * 0.4) + (History * 0.4) + (Port * 0.2)
        """
        # 1. Port Match (Binary)
        req_ports = exploit.get("ports", [])
        port_score = 1.0 if any(p in target.get("ports", []) for p in req_ports) else 0.0
        if not req_ports: port_score = 0.5 # Client-side/Local exploits
        
        # 2. Severity Rank
        rank_map = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2, "info": 0.1}
        rank_score = rank_map.get(exploit.get("severity", "low"), 0.1)
        
        # 3. AI Memory (Historical Success)
        # In a real scenario, fetch this from self.brain.get_success_rate(exploit['name'])
        history_score = 0.5 # Default neutral
        
        # Final Calculation
        total = (rank_score * self.weights["rank"]) + \
                (history_score * self.weights["history"]) + \
                (port_score * self.weights["port_match"])
                
        # Boost for CVE matches if target has vulnerability data
        if "cves" in target and any(cve in target["cves"] for cve in exploit.get("cve", [])):
            total *= 1.5 # Massive boost for confirmed CVE
            
        return total

# --- Test Harness for Standalone Execution ---
if __name__ == "__main__":
    print(f"{chr(27)}[31m") # Red Text
    print("   (      (      ")
    print(r"   )\ )   )\ )   ")
    print(r"  (()/(  (()/(   PHANTOM METASPLOIT AI")
    print("   /(_))  /(_))  INITIALIZING NEURAL DECISION CORE...")
    print(f"{chr(27)}[0m")
    
    # Mock Knowledge Base
    mock_kb = PenetrationTestingAI("data/knowledge/mock_ai.json")
    ai = MetasploitDecider(mock_kb)
    
    # Mock Target: Windows Server 2012 with SMB open
    test_target = {
        "ip": "192.168.1.50",
        "os": "Windows Server 2012 R2",
        "ports": [445, 3389],
        "cves": ["CVE-2017-0144"] # EternalBlue
    }
    
    print("[*] Simulating Attack Decision Process...")
    plan = ai.analyze_target(test_target)
    
    if plan:
        best = plan[0]
        payload = ai.optimize_payload(best["module"], test_target["os"], best["payloads"])
        evasion = ai.generate_evasion_options()
        
        print(f"\n[+] OPTIMAL STRATEGY GENERATED:")
        print(f"    > Exploit: {best['module']}")
        print(f"    > Payload: {payload}")
        print(f"    > Confidence: {best['score'] * 100}%")
        print(f"    > Evasion: {evasion['Encoder']}")
