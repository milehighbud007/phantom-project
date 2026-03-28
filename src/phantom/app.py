#!/usr/bin/env python3
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import msgpack
import requests
from flask import Flask, jsonify, render_template_string

from phantom.ai_learning_module import PenetrationTestingAI
from phantom.config import config

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Configure a file-backed logger once for the Flask app."""
    if logger.handlers:
        return

    log_path = Path(config.LOG_FILE)
    if log_path.parent:
        log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        log_path,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    logger.addHandler(handler)
    logger.propagate = False


class MetasploitProvider:
    """Handles low-level MSF RPC communication."""

    def __init__(
        self,
        host: str = config.MSF_RPC_HOST,
        port: int = config.MSF_RPC_PORT,
        user: str = config.MSF_RPC_USER,
        password: str = config.MSF_RPC_PASSWORD,
        use_ssl: bool = config.MSF_RPC_SSL,
    ):
        protocol = "https" if use_ssl else "http"
        self.url = f"{protocol}://{host}:{port}/api/"
        self.user = user
        self.password = password
        self.token = None

    def _call(self, method, params):
        try:
            payload = msgpack.packb({"method": method, "params": params}, use_bin_type=True)
            headers = {"Content-Type": "binary/message-pack"}
            resp = requests.post(self.url, data=payload, headers=headers, timeout=10, verify=False)
            resp.raise_for_status()
            return msgpack.unpackb(resp.content, raw=False, strict_map_key=False)
        except Exception as exc:
            logger.exception("RPC call failed for %s", method)
            return {"error": str(exc)}

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
            "LPORT": lport,
        }]
        result = self._call("module.execute", params)
        return ("job_id" in result), result.get("error")


def _build_attack_system(ai, msf):
    """
    Delay import of the reconnaissance module so the Flask app can still boot
    when optional scanner dependencies are not installed.
    """
    try:
        from phantom.automated_attack_system import AutomatedAttackSystem
    except ModuleNotFoundError as exc:
        logger.warning("Attack system unavailable because an optional dependency is missing: %s", exc)
        return None

    def attack_executor(mac, exploit_name, payload):
        target_ip = "127.0.0.1"
        return msf.execute(target_ip, exploit_name, payload)

    return AutomatedAttackSystem(ai, attack_executor)


def create_app() -> Flask:
    _configure_logging()

    app = Flask(__name__)
    ai = PenetrationTestingAI(config.AI_KNOWLEDGE_FILE)
    msf = MetasploitProvider()
    attack_system = _build_attack_system(ai, msf)

    app.config["PHANTOM_AI"] = ai
    app.config["PHANTOM_MSF"] = msf
    app.config["PHANTOM_ATTACK_SYSTEM"] = attack_system

    @app.route("/")
    def api_index():
        return jsonify({
            "status": "online",
            "ai_stats": ai.get_statistics(),
            "attack_system_ready": attack_system is not None,
            "endpoints": {
                "/console": "Web UI Interface",
                "/ai/stats": "Current AI learning state",
            },
        })

    @app.route("/console")
    def console():
        return render_template_string("""
        <html>
        <head><title>Phantom Console</title></head>
        <body style="background:#0a0a0a; color:#00ff00; font-family:monospace;">
            <h1>Phantom Console</h1>
            <div id="output" style="border:1px solid #00ff00; padding:20px; height:400px; overflow:auto;">
                [SYSTEM] Ready for commands...
            </div>
        </body>
        </html>
        """)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
