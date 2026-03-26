#!/usr/bin/env python3
"""
AI Learning Module for MetasploitMCP
Refactored for atomic I/O, thread-safety, and weighted scoring.
"""
import json
import os
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger("Phantom.AI")

class PenetrationTestingAI:
    """
    Adaptive learning system for exploit optimization.
    Uses success/failure telemetry to rank attack vectors.
    """
    def __init__(self, knowledge_file="data/knowledge/ai_knowledge.json"):
        self.knowledge_file = Path(knowledge_file)
        self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._dirty = False
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self) -> Dict[str, Any]:
        """Loads knowledge base with fallback to default schema."""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Knowledge load failed: {e}")

        return {
            "exploit_stats": {},  # {exploit_name: {"success": 0, "fail": 0}}
            "target_profiles": {},
            "mapping": {},        # "exploit:os" -> stats
            "metadata": {"created": datetime.now().isoformat(), "ops": 0}
        }

    def _save_knowledge(self):
        """Atomic write to prevent corruption during concurrent access."""
        if not self._dirty:
            return
            
        with self._lock:
            temp_file = self.knowledge_file.with_suffix('.tmp')
            try:
                with open(temp_file, 'w') as f:
                    json.dump(self.knowledge, f, indent=2)
                temp_file.replace(self.knowledge_file)
                self._dirty = False
            except Exception as e:
                logger.error(f"Atomic save failed: {e}")

    def record_exploit_attempt(self, exploit: str, target_mac: str, success: bool, os_guess: str = "unknown"):
        """Updates learning metrics based on attack outcome."""
        with self._lock:
            # Update global exploit stats
            stats = self.knowledge["exploit_stats"].setdefault(exploit, {"success": 0, "fail": 0})
            if success:
                stats["success"] += 1
            else:
                stats["fail"] += 1

            # Update OS-specific mapping
            map_key = f"{exploit}:{os_guess}"
            m_stats = self.knowledge["mapping"].setdefault(map_key, {"success": 0, "fail": 0})
            if success:
                m_stats["success"] += 1
            else:
                m_stats["fail"] += 1

            self.knowledge["metadata"]["ops"] += 1
            self._dirty = True
        
        self._save_knowledge()

    def recommend_exploit(self, target_mac: str, os_guess: str = "unknown") -> Optional[Dict]:
        """
        Recommends an exploit using a weighted success score.
        Score = (Successes / Total) * log(Total attempts + 1)
        """
        recommendations = []
        
        with self._lock:
            for key, stats in self.knowledge["mapping"].items():
                if os_guess in key:
                    total = stats["success"] + stats["fail"]
                    if total > 0:
                        success_rate = stats["success"] / total
                        # Weighting prevents high scores for 1/1 lucky shots
                        score = success_rate * (total ** 0.5) 
                        
                        recommendations.append({
                            "exploit": key.split(":")[0],
                            "score": round(score, 3),
                            "confidence": total
                        })

        if not recommendations:
            return None

        # Sort by weighted score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        logger.info(f"AI recommendation for {os_guess}: {recommendations[0]['exploit']}")
        return recommendations[0]

    def get_statistics(self) -> Dict:
        """Returns high-level AI performance metrics."""
        return {
            "total_operations": self.knowledge["metadata"].get("ops", 0),
            "known_exploits": len(self.knowledge["exploit_stats"]),
            "last_updated": datetime.now().isoformat()
        }
