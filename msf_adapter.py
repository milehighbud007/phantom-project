import re
from pymetasploit3.msfrpc import MsfRpcClient

class MsftAdapter:
    def __init__(self, password="kali", host="127.0.0.1"):
        self.client = MsfRpcClient(password, server=host)

    def list_modules_by_type(self, module_type="exploit"):
        mods = getattr(self.client.modules, module_type, None)
        if mods is None:
            return []
        return list(mods)

    def get_module_meta(self, module_type, module_name):
        mod = self.client.modules.use(module_type, module_name)
        info = mod.info or {}
        return {
            "name": module_name,
            "type": module_type,
            "description": info.get("description", ""),
            "references": info.get("references", []),
            "targets": info.get("targets", []),
            "options": list(info.get("options", {}).keys())
        }

    def find_modules_by_keyword(self, keyword, module_type="exploit", limit=50):
        keyword = keyword.lower()
        matches = []
        mods = getattr(self.client.modules, module_type, None)
        if mods is None:
            return matches
        for m in mods:
            if keyword in m.lower():
                matches.append(m)
                if len(matches) >= limit:
                    break
        return matches

    def suggest_candidates(self, fingerprint, module_type="exploit", top=30):
        candidates = []
        for svc in fingerprint.get("services", []):
            svcstr = f"{svc.get('service','')} {svc.get('version','')}".strip().lower()
            tokens = re.findall(r"[a-z0-9\.]+", svcstr)
            seen = set()
            for t in tokens:
                mods = self.find_modules_by_keyword(t, module_type=module_type, limit=20)
                for m in mods:
                    key = (m, t)
                    if key not in seen:
                        candidates.append({"module": m, "matched_kw": t, "service": svcstr})
                        seen.add(key)
        def score(c):
            s = 0
            if c["matched_kw"] in c["service"]:
                s += 2
            return s
        candidates = sorted(candidates, key=score, reverse=True)
        return candidates[:top]
