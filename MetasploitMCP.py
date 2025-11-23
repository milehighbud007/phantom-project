from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/list_targets")
def list_targets():
    targets = [
        {"ip": "192.168.1.10", "open_ports": 5},
        {"ip": "192.168.1.15", "open_ports": 3},
        {"ip": "192.168.1.20", "open_ports": 7},
        {"ip": "192.168.1.25", "open_ports": 2}
    ]
    return jsonify({"targets": targets})

@app.route("/scan")
def scan():
    target = request.args.get("target")
    exploits = [
        "windows/smb/ms17_010",
        "linux/http/apache_mod_cgi_bash_env_exec",
        "multi/handler/reverse_tcp"
    ]
    return jsonify({"target": target, "exploits": exploits})

@app.route("/payloads")
def payloads():
    return jsonify({
        "payloads": [
            "windows/meterpreter/reverse_tcp",
            "linux/x86/shell_reverse_tcp",
            "cmd/unix/reverse_netcat"
        ]
    })

@app.route("/launch", methods=["POST"])
def launch():
    data = request.get_json()
    target = data.get("target")
    exploit = data.get("exploit")
    payload = data.get("payload")
    return f"Exploit {exploit} with payload {payload} launched against {target}"

@app.route("/sessions")
def sessions():
    return jsonify({
        "sessions": [
            {"id": 1, "status": "active", "ip": "192.168.1.10"},
            {"id": 2, "status": "idle", "ip": "192.168.1.15"}
        ]
    })

@app.route("/backdoor", methods=["POST"])
def backdoor():
    data = request.get_json()
    command = data.get("command")
    return f"Executed: {command}\nOutput: Simulated response from target"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8085)
