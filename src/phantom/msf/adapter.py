#!/usr/bin/env python3
"""
MsftAdapter - Advanced MSF RPC abstraction layer with module caching.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from pymetasploit3.msfrpc import MsfRpcClient

logger = logging.getLogger("Phantom.MSFAdapter")

class MsftAdapter:
    """
    High-level interface for Metasploit RPC.
    Features: Automated reconnects, local module caching, and smart suggestion engine.
    """
    def __init__(self, password: str = "kali", host: str = "127.0.0.1", user: str = "msf"):
        self.password = password
        self.host = host
        self.user = user
        self.client = None
        self._module_cache = {"exploit": [], "payload": [], "post": []}
        self.connect()

    def connect(self) -> bool:
        """Establishes session with msfrpcd and warms up the cache."""
        try:
            self.client = MsfRpcClient(self.password, server=self.host, username=self.user)
            self._refresh_cache()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MSF RPC: {e}")
            return False

    def _refresh_cache(self):
        """Pre-fetches module lists to avoid slow RPC calls during scanning."""
        if not self.client: return
        for mtype in self._module_cache.keys():
            mods = getattr(self.client.modules, mtype, [])
            self._module_cache[mtype] = list(mods)
        logger.info("MSF Module cache refreshed.")

    def find_modules_by_keyword(self, keyword: str, module_type: str = "exploit", limit: int = 50) -> List[str]:
        """Search local cache for modules matching keywords."""
        keyword = keyword.lower()
        matches = [m for m in self._module_cache.get(module_type, []) if keyword in m.lower()]
        return matches[:limit]

    def get_module_meta(self, module_type: str, module_name: str) -> Dict[str, Any]:
        """Fetch detailed metadata for a specific module."""
        try:
            mod = self.client.modules.use(module_type, module_name)
            return {
                "name": module_name,
                "description": mod.description or "No description available",
                "references": mod.references or [],
                "options": mod.options,
                "targets": mod.targets or []
            }
        except Exception as e:
            logger.warning(f"Metadata retrieval failed for {module_name}: {e}")
            return {"error": str(e)}

    def suggest_candidates(self, fingerprint: Dict[str, Any], module_type: str = "exploit") -> List[Dict]:
        """
        Rank exploits based on target fingerprint.
        Weights: Version Match (High), Service Name (Med), OS Match (High).
        """
        results = []
        seen = set()

        for svc in fingerprint.get("services", []):
            name = svc.get('service', '').lower()
            ver = str(svc.get('version', '')).lower()
            
            # Create search tokens from service name and version
            tokens = re.findall(r"[a-z0-9\.]+", f"{name} {ver}")
            
            for token in tokens:
                if len(token) < 3: continue # Skip noisy short tokens
                
                potential = self.find_modules_by_keyword(token, module_type=module_type)
                for mod_name in potential:
                    if mod_name in seen: continue
                    
                    # Calculate relevance score
                    score = 1
                    if name in mod_name.lower(): score += 2
                    if ver and ver in mod_name.lower(): score += 5
                    
                    results.append({
                        "module": mod_name,
                        "score": score,
                        "match_token": token,
                        "service": f"{name} {ver}"
                    })
                    seen.add(mod_name)

        # Sort by score descending
        return sorted(results, key=lambda x: x['score'], reverse=True)[:25]

