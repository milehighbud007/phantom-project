#!/usr/bin/env python3
"""
AI Learning Module for MetasploitMCP
Adds adaptive learning capabilities to improve exploit selection and success rates
"""

import json
import os
import time
from datetime import datetime
from collections import defaultdict
import logging

log = logging.getLogger(__name__)

class PenetrationTestingAI:
    """
    Learning system that adapts based on:
    - Exploit success/failure rates
    - Target characteristics and vulnerabilities
    - Network topology patterns
    - Timing and detection avoidance
    """
    
    def __init__(self, knowledge_file="ai_knowledge.json"):
        self.knowledge_file = knowledge_file
        self.knowledge = self._load_knowledge()
        
    def _load_knowledge(self):
        """Load existing knowledge base or create new one"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Failed to load knowledge base: {e}")
        
        # Initialize empty knowledge base
        return {
            "exploit_success_rates": {},
            "target_profiles": {},
            "network_patterns": {},
            "payload_effectiveness": {},
            "exploit_target_mapping": {},
            "learned_techniques": [],
            "scan_optimizations": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_operations": 0,
                "successful_operations": 0
            }
        }
    
    def _save_knowledge(self):
        """Persist knowledge to disk"""
        self.knowledge["metadata"]["last_updated"] = datetime.now().isoformat()
        try:
            if os.path.exists(self.knowledge_file):
                backup_file = f"{self.knowledge_file}.backup"
                os.rename(self.knowledge_file, backup_file)
            
            with open(self.knowledge_file, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
            
            log.info("Knowledge base saved successfully")
        except Exception as e:
            log.error(f"Failed to save knowledge base: {e}")
            if os.path.exists(f"{self.knowledge_file}.backup"):
                os.rename(f"{self.knowledge_file}.backup", self.knowledge_file)
    
    def record_scan_result(self, network, num_hosts, scan_time):
        """Learn from network scanning performance"""
        if network not in self.knowledge["network_patterns"]:
            self.knowledge["network_patterns"][network] = []
        
        self.knowledge["network_patterns"][network].append({
            "hosts_found": num_hosts,
            "scan_time": scan_time,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.knowledge["network_patterns"][network]) > 10:
            self.knowledge["network_patterns"][network] = \
                self.knowledge["network_patterns"][network][-10:]
        
        self._save_knowledge()
        log.info(f"Recorded scan: {network} - {num_hosts} hosts in {scan_time:.2f}s")
    
    def update_target_profile(self, mac, ip, hostname, vendor, services=None, os_guess=None):
        """Build and update target profiles over time"""
        if mac not in self.knowledge["target_profiles"]:
            self.knowledge["target_profiles"][mac] = {
                "ip": ip,
                "hostname": hostname,
                "vendor": vendor,
                "services": [],
                "vulnerabilities": [],
                "os_guess": None,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "times_seen": 1
            }
        else:
            profile = self.knowledge["target_profiles"][mac]
            profile["ip"] = ip
            profile["last_seen"] = datetime.now().isoformat()
            profile["times_seen"] += 1
        
        if os_guess:
            self.knowledge["target_profiles"][mac]["os_guess"] = os_guess
        
        if services:
            existing_services = set(self.knowledge["target_profiles"][mac]["services"])
            existing_services.update(services)
            self.knowledge["target_profiles"][mac]["services"] = list(existing_services)
        
        self._save_knowledge()
    
    def record_exploit_attempt(self, exploit, payload, target_mac, success, error_msg=None):
        """Learn from exploit attempts - success or failure"""
        if exploit not in self.knowledge["exploit_success_rates"]:
            self.knowledge["exploit_success_rates"][exploit] = {"success": 0, "failure": 0}
        
        if success:
            self.knowledge["exploit_success_rates"][exploit]["success"] += 1
        else:
            self.knowledge["exploit_success_rates"][exploit]["failure"] += 1
        
        if payload not in self.knowledge["payload_effectiveness"]:
            self.knowledge["payload_effectiveness"][payload] = {"success": 0, "failure": 0}
        
        if success:
            self.knowledge["payload_effectiveness"][payload]["success"] += 1
        else:
            self.knowledge["payload_effectiveness"][payload]["failure"] += 1
        
        if target_mac in self.knowledge["target_profiles"]:
            os_guess = self.knowledge["target_profiles"][target_mac].get("os_guess", "unknown")
            mapping_key = f"{exploit}:{os_guess}"
            
            if mapping_key not in self.knowledge["exploit_target_mapping"]:
                self.knowledge["exploit_target_mapping"][mapping_key] = {"success": 0, "failure": 0}
            
            if success:
                self.knowledge["exploit_target_mapping"][mapping_key]["success"] += 1
            else:
                self.knowledge["exploit_target_mapping"][mapping_key]["failure"] += 1
        
        self.knowledge["metadata"]["total_operations"] += 1
        if success:
            self.knowledge["metadata"]["successful_operations"] += 1
        
        if not success and error_msg:
            self._analyze_failure(exploit, payload, target_mac, error_msg)
        
        self._save_knowledge()
        log.info(f"Recorded exploit attempt: {exploit} -> {'SUCCESS' if success else 'FAILURE'}")
    
    def _analyze_failure(self, exploit, payload, target_mac, error_msg):
        """Analyze why an exploit failed and learn from it"""
        failure_patterns = {
            "connection_refused": ["connection refused", "no route to host"],
            "authentication_failed": ["authentication failed", "access denied"],
            "incompatible_target": ["incompatible", "not vulnerable"],
            "payload_failed": ["payload execution failed", "handler error"],
            "timeout": ["timeout", "timed out"]
        }
        
        for pattern_name, keywords in failure_patterns.items():
            if any(keyword in error_msg.lower() for keyword in keywords):
                learning = {
                    "timestamp": datetime.now().isoformat(),
                    "exploit": exploit,
                    "payload": payload,
                    "target": target_mac,
                    "failure_type": pattern_name,
                    "error_message": error_msg
                }
                self.knowledge["learned_techniques"].append(learning)
                
                if len(self.knowledge["learned_techniques"]) > 50:
                    self.knowledge["learned_techniques"] = \
                        self.knowledge["learned_techniques"][-50:]
                
                log.info(f"Learned failure pattern: {pattern_name}")
                break
    
    def recommend_exploit(self, target_mac):
        """Recommend best exploit based on learned success rates"""
        if target_mac not in self.knowledge["target_profiles"]:
            return None
        
        os_guess = self.knowledge["target_profiles"][target_mac].get("os_guess", "unknown")
        
        recommendations = []
        for mapping_key, stats in self.knowledge["exploit_target_mapping"].items():
            if os_guess in mapping_key:
                total = stats["success"] + stats["failure"]
                if total > 0:
                    success_rate = stats["success"] / total
                    exploit = mapping_key.split(":")[0]
                    recommendations.append({
                        "exploit": exploit,
                        "success_rate": success_rate,
                        "attempts": total
                    })
        
        recommendations.sort(key=lambda x: x["success_rate"], reverse=True)
        
        if recommendations:
            best = recommendations[0]
            log.info(f"Recommended exploit for {target_mac}: {best['exploit']} "
                    f"(success rate: {best['success_rate']:.2%})")
            return best
        
        return None
    
    def recommend_payload(self, exploit):
        """Recommend best payload based on past success"""
        payload_scores = {}
        
        for payload, stats in self.knowledge["payload_effectiveness"].items():
            total = stats["success"] + stats["failure"]
            if total > 0:
                success_rate = stats["success"] / total
                payload_scores[payload] = success_rate
        
        if payload_scores:
            best_payload = max(payload_scores.items(), key=lambda x: x[1])
            log.info(f"Recommended payload: {best_payload[0]} "
                    f"(success rate: {best_payload[1]:.2%})")
            return best_payload[0]
        
        return None
    
    def get_statistics(self):
        """Get current AI learning statistics"""
        total_ops = self.knowledge["metadata"]["total_operations"]
        successful_ops = self.knowledge["metadata"]["successful_operations"]
        
        stats = {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "success_rate": successful_ops / total_ops if total_ops > 0 else 0,
            "targets_profiled": len(self.knowledge["target_profiles"]),
            "exploits_learned": len(self.knowledge["exploit_success_rates"]),
            "payloads_learned": len(self.knowledge["payload_effectiveness"]),
            "patterns_discovered": len(self.knowledge["learned_techniques"]),
            "networks_scanned": len(self.knowledge["network_patterns"]),
            "last_updated": self.knowledge["metadata"]["last_updated"]
        }
        
        return stats
    
    def optimize_scan_parameters(self, network):
        """Suggest optimal scan parameters based on history"""
        if network in self.knowledge["network_patterns"]:
            scans = self.knowledge["network_patterns"][network]
            if scans:
                avg_time = sum(s["scan_time"] for s in scans) / len(scans)
                avg_hosts = sum(s["hosts_found"] for s in scans) / len(scans)
                
                if avg_time > 120:
                    return {
                        "suggestion": "use_faster_scan",
                        "reason": f"Average scan time is {avg_time:.1f}s",
                        "recommended_args": "-T4 -F"
                    }
                
                if avg_hosts < 5:
                    return {
                        "suggestion": "small_network",
                        "reason": f"Typically only {avg_hosts:.1f} hosts found",
                        "recommended_args": "-T5 --min-parallelism 10"
                    }
        
        return None
    
    def should_retry_exploit(self, exploit, target_mac):
        """Decide if we should retry an exploit based on past performance"""
        if target_mac not in self.knowledge["target_profiles"]:
            return True
        
        os_guess = self.knowledge["target_profiles"][target_mac].get("os_guess", "unknown")
        mapping_key = f"{exploit}:{os_guess}"
        
        if mapping_key in self.knowledge["exploit_target_mapping"]:
            stats = self.knowledge["exploit_target_mapping"][mapping_key]
            total = stats["success"] + stats["failure"]
            
            if total >= 3 and stats["success"] == 0:
                log.info(f"Skipping {exploit} for {target_mac} - 0% success rate over {total} attempts")
                return False
        
        return True
    
    def export_knowledge_report(self):
        """Export a human-readable report of learned knowledge"""
        report = []
        report.append("=" * 60)
        report.append("PENETRATION TESTING AI - KNOWLEDGE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        stats = self.get_statistics()
        report.append("OVERALL STATISTICS:")
        report.append(f"  Total Operations: {stats['total_operations']}")
        report.append(f"  Successful Operations: {stats['successful_operations']}")
        report.append(f"  Success Rate: {stats['success_rate']:.2%}")
        report.append(f"  Targets Profiled: {stats['targets_profiled']}")
        report.append(f"  Exploits Learned: {stats['exploits_learned']}")
        report.append("")
        
        exploit_rates = []
        for exploit, stats_dict in self.knowledge["exploit_success_rates"].items():
            total = stats_dict["success"] + stats_dict["failure"]
            if total > 0:
                rate = stats_dict["success"] / total
                exploit_rates.append((exploit, rate, total))
        
        exploit_rates.sort(key=lambda x: x[1], reverse=True)
        report.append("TOP EXPLOITS BY SUCCESS RATE:")
        for exploit, rate, total in exploit_rates[:5]:
            report.append(f"  {exploit}: {rate:.2%} ({total} attempts)")
        report.append("")
        
        report.append(f"TARGET PROFILES: {len(self.knowledge['target_profiles'])} targets")
        for mac, profile in list(self.knowledge["target_profiles"].items())[:10]:
            report.append(f"  {mac}:")
            report.append(f"    IP: {profile['ip']}")
            report.append(f"    OS: {profile.get('os_guess', 'Unknown')}")
            report.append(f"    Times Seen: {profile['times_seen']}")
        
        return "\n".join(report)


if __name__ == "__main__":
    print("AI Learning Module loaded successfully")
