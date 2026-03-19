#!/usr/bin/env python3
"""
NASA Home Base Mission Control
NetworkBuster Integration Package
"""

import sys
import time
import json
import requests
import subprocess
import webbrowser
import threading
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# Check for required packages
try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask not available. Install with: pip install flask")

class NASAHomeBase:
    """NASA Home Base Mission Control System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ports = {
            'web': {'port': 3000, 'name': 'Web Server', 'status': 'offline'},
            'api': {'port': 3001, 'name': 'API Server', 'status': 'offline'},
            'audio': {'port': 3002, 'name': 'Audio Stream', 'status': 'offline'},
            'mission': {'port': 5000, 'name': 'Mission Control', 'status': 'offline'},
            'map': {'port': 6000, 'name': 'Network Map', 'status': 'offline'},
            'launcher': {'port': 7000, 'name': 'Universal Launcher', 'status': 'offline'},
            'tracer': {'port': 8000, 'name': 'API Tracer', 'status': 'offline'}
        }
        self.artemis_status = {
            'mission': 'Artemis II',
            'status': 'Nominal',
            'phase': 'Lunar Insertion',
            'crew': ['Cmdr. Network', 'Pilot Buster'],
            'fuel': '85%',
            'velocity': '3.2 km/s'
        }
        self.mission_start_time = datetime.now()
        self.mission_log = []
        
    def get_artemis_data(self):
        """Get Artemis mission data"""
        return self.artemis_status

    def log_event(self, event, level='INFO'):
        """Log mission event"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {event}"
        self.mission_log.append(log_entry)
        print(f"  {log_entry}")
        
    def check_port_status(self, port):
        """Check if a port is active"""
        try:
            response = requests.get(f'http://localhost:{port}/api/health', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def check_all_ports(self):
        """Check status of all NetworkBuster ports"""
        for service, info in self.ports.items():
            is_active = self.check_port_status(info['port'])
            info['status'] = 'online' if is_active else 'offline'
            
    def start_service(self, service_name):
        """Start a NetworkBuster service"""
        self.log_event(f"Starting {service_name}...", 'COMMAND')
        # Services should already be running via start-servers.js
        
    def open_dashboard(self, service='web'):
        """Open service dashboard in browser"""
        port = self.ports[service]['port']
        url = f'http://localhost:{port}'
        self.log_event(f"Opening {service} dashboard: {url}", 'ACTION')
        webbrowser.open(url)
        
    def get_system_status(self):
        """Get comprehensive system status"""
        self.check_all_ports()
        
        online_count = sum(1 for p in self.ports.values() if p['status'] == 'online')
        uptime = (datetime.now() - self.mission_start_time).total_seconds()
        
        return {
            'mission_time': uptime,
            'ports': self.ports,
            'online_services': online_count,
            'total_services': len(self.ports),
            'status': 'NOMINAL' if online_count == len(self.ports) else 'DEGRADED'
        }

# Flask web interface for Mission Control
if FLASK_AVAILABLE:
    app = Flask(__name__)
    home_base = NASAHomeBase()
    
    MISSION_CONTROL_HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>NASA Mission Control | NetworkBuster</title>
        <style>
            :root { --bg: #050505; --neon-blue: #00d4ff; --neon-green: #00ff88; --neon-orange: #ffaa00; }
            body { background: var(--bg); color: #e0e0e0; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; overflow: hidden; }
            .glass { background: rgba(20, 20, 25, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid var(--neon-blue); padding-bottom: 10px; }
            .mission-grid { display: grid; grid-template-columns: 1fr 1.5fr 1fr; gap: 20px; height: calc(100vh - 120px); }
            .telemetry-card { margin-bottom: 15px; }
            .stat-val { font-size: 1.5rem; font-weight: 800; color: var(--neon-green); font-family: monospace; }
            .stat-label { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
            .map-container { width: 100%; height: 100%; position: relative; background: #000; border-radius: 8px; border: 1px solid #222; }
            .log-box { height: 100%; overflow-y: auto; font-family: monospace; font-size: 0.8rem; color: #aaa; background: rgba(0,0,0,0.3); padding: 10px; }
            .pulse { animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        </style>
    </head>
    <body>
        <div class="header">
            <h2 style="color: var(--neon-blue); letter-spacing: 3px;">🛰️ MISSION_CONTROL // ALPHA-7</h2>
            <div id="clock" style="font-family: monospace; color: var(--neon-orange);">00:00:00 UTC</div>
        </div>
        <div class="mission-grid">
            <div class="sidebar">
                <div class="glass telemetry-card">
                    <div class="stat-label">Mission Phase</div>
                    <div class="stat-val" id="phase">LUNAR_INSERTION</div>
                </div>
                <div class="glass telemetry-card">
                    <div class="stat-label">Velocity</div>
                    <div class="stat-val" id="vel">24,500 KM/H</div>
                </div>
                <div class="glass telemetry-card">
                    <div class="stat-label">Fuel Remaining</div>
                    <div class="stat-val" id="fuel" style="color: var(--neon-orange);">84.2%</div>
                </div>
            </div>
            <div class="glass map-container">
                <div style="text-align: center; margin-top: 100px;">
                    <div style="font-size: 5rem; color: var(--neon-blue);" class="pulse">🌕</div>
                    <h3 style="color: #fff; margin-top: 20px;">TARGET: LUNAR_SOUTH_POLE</h3>
                    <p style="color: #888;">ORBITAL_PATH: STABLE</p>
                </div>
            </div>
            <div class="glass">
                <div class="stat-label" style="margin-bottom: 10px;">Telemetry Log</div>
                <div id="logs" class="log-box"></div>
            </div>
        </div>
        <script>
            function updateClock() {
                document.getElementById('clock').textContent = new Date().toISOString().split('T')[1].split('.')[0] + ' UTC';
            }
            function addLog(m) {
                const l = document.getElementById('logs');
                const e = document.createElement('div');
                e.textContent = `[${new Date().toLocaleTimeString()}] ${m}`;
                l.prepend(e);
            }
            setInterval(updateClock, 1000);
            setInterval(() => {
                const v = 24000 + Math.random() * 1000;
                document.getElementById('vel').textContent = Math.floor(v).toLocaleString() + ' KM/H';
                if(Math.random() > 0.7) addLog('TELEMETRY_PACKET_RECEIVED');
            }, 2000);
            addLog('SYSTEM_BOOT_SEQUENCE_COMPLETE');
            addLog('ESTABLISHING_LINK_WITH_VEGAS_DOME...');
        </script>
    </body>
    </html>
    """
    
    @app.route('/')
    def index():
        return render_template_string(MISSION_CONTROL_HTML)
    
    @app.route('/api/status')
    def api_status():
        return jsonify(home_base.get_system_status())

    @app.route('/api/artemis/status')
    def artemis_status():
        return jsonify(home_base.get_artemis_data())
    
    @app.route('/api/open/<service>')
    def api_open_service(service):
        if service in home_base.ports:
            home_base.open_dashboard(service)
            return jsonify({'success': True, 'message': f'Opened {service} dashboard'})
        return jsonify({'success': False, 'message': 'Service not found'}), 404

def run_mission_control(port=5000):
    """Run the NASA Home Base Mission Control interface"""
    if not FLASK_AVAILABLE:
        print("❌ Flask is required to run Mission Control")
        print("   Install with: pip install flask")
        return
    
    print("\n" + "="*60)
    print("🚀 NASA HOME BASE MISSION CONTROL")
    print("="*60)
    print(f"\n🌐 Mission Control Interface: http://localhost:{port}")
    print("\nChecking NetworkBuster services...")
    
    home_base.check_all_ports()
    for service, info in home_base.ports.items():
        status_icon = "✅" if info['status'] == 'online' else "⚠️"
        print(f"  {status_icon} {info['name']} (Port {info['port']}): {info['status'].upper()}")
    
    print(f"\n🎯 Opening Mission Control in browser...")
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()
    
    print(f"\n📡 Mission Control Active - Press Ctrl+C to abort mission\n")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Mission Control shutdown initiated")
        print("✅ All systems secured")

def main():
    """Main entry point"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " NASA HOME BASE - NetworkBuster Integration".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("\nUsage: python nasa_home_base.py [options]")
        print("\nOptions:")
        print("  --help          Show this help message")
        print("  --port PORT     Set Mission Control port (default: 5000)")
        print("  --check         Check service status only")
        print("\nExample:")
        print("  python nasa_home_base.py")
        print("  python nasa_home_base.py --port 5001")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        base = NASAHomeBase()
        base.check_all_ports()
        print("\n📊 Service Status:")
        for service, info in base.ports.items():
            print(f"  • {info['name']}: {info['status'].upper()}")
        return
    
    port = 5000
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    
    run_mission_control(port)

if __name__ == "__main__":
    main()
