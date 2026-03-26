#!/usr/bin/env python3
"""
reporting_module.py - Generates High-Impact "Intense" HTML Reports
"""
import argparse
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PHANTOM // INTENSE REPORT</title>
    <style>
        :root { --bg: #020202; --neon: #00f3ff; --warn: #ff0055; --sub: #1a1a1a; }
        body { background: var(--bg); color: var(--neon); font-family: 'Courier New', monospace; padding: 30px; margin: 0; }
        .glitch-header { border-left: 5px solid var(--warn); padding-left: 20px; margin-bottom: 40px; text-transform: uppercase; letter-spacing: 5px; }
        h1 { font-size: 3em; margin: 0; text-shadow: 0 0 10px var(--neon); }
        .meta { color: var(--warn); font-size: 0.9em; animation: blink 1s infinite; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 25px; }
        .host-card { background: var(--sub); border: 1px solid #333; padding: 20px; position: relative; transition: 0.3s; }
        .host-card:hover { border-color: var(--neon); box-shadow: 0 0 20px rgba(0, 243, 255, 0.2); }
        .critical { border-color: var(--warn) !important; background: linear-gradient(145deg, #1a1a1a, #2a000a); }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th { color: #888; text-align: left; font-size: 0.7em; text-transform: uppercase; border-bottom: 1px solid #333; }
        td { padding: 8px 0; font-size: 0.85em; border-bottom: 1px solid #222; }
        .port-red { color: var(--warn); font-weight: bold; }
        .screenshot-box { width: 100%; height: 200px; background: #000; margin-top: 15px; border: 1px dashed #444; display: flex; align-items: center; justify-content: center; color: #444; font-size: 0.8em; overflow: hidden; }
        .screenshot-box img { max-width: 100%; max-height: 100%; object-fit: cover; opacity: 0.7; }
        @keyframes blink { 50% { opacity: 0.5; } }
    </style>
</head>
<body>
    <div class="glitch-header">
        <h1>PHANTOM <span style="color:#fff">INTENSE</span></h1>
        <div class="meta">ACCESS_DATE: {timestamp} // THREAT_LEVEL: MAXIMUM</div>
    </div>
    <div class="grid">{content}</div>
</body>
</html>
"""

def parse_xml(xml_file):
    try:
        root = ET.parse(xml_file).getroot()
    except Exception as e:
        print(f"[!] Error reading XML: {e}")
        return ""

    cards = ""
    for host in root.findall('host'):
        addr = host.find('address').get('addr')
        is_crit = False
        ports_html = ""
        
        ports = host.find('ports')
        has_web = False
        if ports:
            for p in ports.findall('port'):
                pid = p.get('portid')
                svc = p.find('service')
                name = svc.get('name', '???') if svc is not None else '???'
                ver = svc.get('product', '') if svc is not None else ''
                
                style = 'class="port-red"' if pid in ['445', '3389', '21', '23'] else ''
                if pid in ['445', '3389']: is_crit = True
                if pid in ['80', '443', '8080']: has_web = True
                
                ports_html += f'<tr><td {style}>{pid}</td><td>{name}</td><td>{ver}</td></tr>'

        screenshot_html = ""
        if has_web:
            # Expects images named by IP in a 'screenshots' subfolder
            screenshot_html = f'<div class="screenshot-box"><img src="screenshots/{addr}.png" onerror="this.parentElement.innerHTML=\'[NO_SIGNAL]\'"></div>'

        status_class = "host-card critical" if is_crit else "host-card"
        cards += f'<div class="{status_class}"><h2>{addr}</h2><table><tr><th>PORT</th><th>SVC</th><th>VER</th></tr>{ports_html}</table>{screenshot_html}</div>'
    
    return HTML_TEMPLATE.format(timestamp=datetime.now().isoformat(), content=cards)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_file")
    parser.add_argument("-o", "--output", default="dashboard.html")
    args = parser.parse_args()
    
    html = parse_xml(args.xml_file)
    with open(args.output, "w") as f:
        f.write(html)
    print(f"[\u2713] Dashboard Generated: {args.output}")
