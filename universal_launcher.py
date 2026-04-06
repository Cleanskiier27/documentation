"""
NetworkBuster - Universal Tool Launcher
Unix-style dashboard for all services and tools
"""

from flask import Flask, render_template_string, jsonify
import subprocess
import psutil
import socket
from datetime import datetime

app = Flask(__name__)

# Define all tools and services
TOOLS = {
    'core_services': [
        {'name': 'Web Server', 'port': 3000, 'cmd': 'node server-universal.js', 'url': 'http://localhost:3000'},
        {'name': 'API Server', 'port': 3001, 'cmd': 'cd api && node server-universal.js', 'url': 'http://localhost:3001'},
        {'name': 'Audio Stream', 'port': 3002, 'cmd': 'node server-audio.js', 'url': 'http://localhost:3002'},
        {'name': 'YouTube Trends', 'port': 8001, 'cmd': 'python youtube_trends_service.py', 'url': 'http://localhost:8001'},
        {'name': 'Mission Control', 'port': 5000, 'cmd': 'python nasa_home_base.py', 'url': 'http://localhost:5000'},
        {'name': 'Network Map', 'port': 6000, 'cmd': 'python network_map_viewer.py', 'url': 'http://localhost:6000'},
    ],
    'utilities': [
        {'name': 'NetworkBuster AI', 'port': 4000, 'cmd': 'python networkbuster_ai.py', 'url': 'http://localhost:4000'},
        {'name': 'Git Cloud Shortcuts', 'cmd': 'python git_cloud_shortcuts.py', 'type': 'script'},
        {'name': 'Flash Git Backup', 'cmd': 'python flash_git_backup.py', 'type': 'script'},
        {'name': 'Drone Simulation', 'cmd': 'python run_drone_simulation.py', 'type': 'script'},
        {'name': 'NetworkBuster Mission', 'cmd': 'python networkbuster_mission_runner.py', 'type': 'script'},
    ],
    'dashboards': [
        {'name': 'Dashboard Control', 'url': 'http://localhost:3000/dashboard-control.html'},
        {'name': 'YouTube Trends', 'url': 'http://localhost:8001'},
        {'name': 'WiFi 7 Mesh Overlay', 'url': 'http://localhost:3000/wifi7-mesh-overlay.html'},
        {'name': 'Control Panel', 'url': 'http://localhost:3000/control-panel'},
        {'name': 'Git Dashboard', 'url': 'file:///NetworkBuster_Git_Shortcuts/git_dashboard.html'},
        {'name': 'Business Magic Hub', 'url': 'http://localhost:4000'},
    ],
    'api_endpoints': [
        {'name': 'Health Check', 'url': 'http://localhost:3001/health'},
        {'name': 'YouTube Trends API', 'url': 'http://localhost:8001/api/trends'},
        {'name': 'System Specs', 'url': 'http://localhost:3001/api/specs'},
        {'name': 'Device Status', 'url': 'http://localhost:6000/api/devices'},
        {'name': 'Documentation', 'url': 'http://localhost:6000/api/docs'},
        {'name': 'Audio Lab', 'url': 'http://localhost:3002/audio-lab'},
    ]
}

def check_port(port):
    """Check if a port is listening"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return True
    return False

def get_all_statuses():
    """Get status of all services"""
    statuses = {}
    
    for category, tools in TOOLS.items():
        statuses[category] = []
        for tool in tools:
            if 'port' in tool:
                status = 'online' if check_port(tool['port']) else 'offline'
                statuses[category].append({
                    **tool,
                    'status': status
                })
            else:
                statuses[category].append({
                    **tool,
                    'status': 'available'
                })
    
    return statuses

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetworkBuster :: Universal Tool Launcher</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: #000;
            color: #0f0;
            padding: 0;
            overflow-x: hidden;
        }
        
        .terminal {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Unix-style header */
        .header {
            border: 2px solid #0f0;
            padding: 15px;
            margin-bottom: 20px;
            background: #001100;
            box-shadow: 0 0 20px #0f0;
        }
        
        .header-line {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
        }
        
        .header-title {
            font-size: 24px;
            font-weight: bold;
            text-shadow: 0 0 10px #0f0;
        }
        
        .header-time {
            font-size: 14px;
            color: #0a0;
        }
        
        .breadcrumb {
            color: #0a0;
            font-size: 12px;
            padding: 5px 0;
        }
        
        /* Navigation bar */
        .navbar {
            border: 1px solid #0f0;
            background: #002200;
            padding: 10px;
            margin-bottom: 20px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .nav-item {
            color: #0f0;
            text-decoration: none;
            padding: 5px 10px;
            border: 1px solid #0f0;
            background: #000;
            transition: all 0.2s;
        }
        
        .nav-item:hover {
            background: #0f0;
            color: #000;
            box-shadow: 0 0 10px #0f0;
        }
        
        /* Section headers */
        .section {
            border: 2px solid #0a0;
            margin-bottom: 20px;
            background: #001100;
        }
        
        .section-header {
            background: #003300;
            border-bottom: 1px solid #0f0;
            padding: 10px 15px;
            font-size: 18px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .section-content {
            padding: 15px;
        }
        
        /* Tool grid */
        .tool-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }
        
        .tool-card {
            border: 1px solid #0a0;
            padding: 15px;
            background: #000;
            position: relative;
            transition: all 0.3s;
        }
        
        .tool-card:hover {
            border-color: #0f0;
            box-shadow: 0 0 15px #0f0;
            transform: translateX(5px);
        }
        
        .tool-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px dashed #0a0;
        }
        
        .tool-name {
            font-size: 16px;
            font-weight: bold;
        }
        
        .status-badge {
            padding: 3px 10px;
            border: 1px solid;
            font-size: 11px;
            animation: pulse 2s infinite;
        }
        
        .status-online {
            color: #0f0;
            border-color: #0f0;
            background: #002200;
        }
        
        .status-offline {
            color: #f00;
            border-color: #f00;
            background: #220000;
        }
        
        .status-available {
            color: #ff0;
            border-color: #ff0;
            background: #222200;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .tool-details {
            font-size: 12px;
            color: #0a0;
            margin: 5px 0;
        }
        
        .tool-actions {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .btn {
            flex: 1;
            padding: 8px;
            border: 1px solid #0f0;
            background: #002200;
            color: #0f0;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            transition: all 0.2s;
        }
        
        .btn:hover {
            background: #0f0;
            color: #000;
            box-shadow: 0 0 10px #0f0;
        }
        
        .btn:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }
        
        /* Index/Directory listing style */
        .index-list {
            list-style: none;
        }
        
        .index-item {
            padding: 8px;
            border-bottom: 1px dotted #0a0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .index-item:hover {
            background: #002200;
        }
        
        .index-link {
            color: #0f0;
            text-decoration: none;
            flex: 1;
        }
        
        .index-link:hover {
            text-decoration: underline;
            text-shadow: 0 0 5px #0f0;
        }
        
        /* Footer */
        .footer {
            border: 2px solid #0f0;
            padding: 15px;
            margin-top: 20px;
            background: #001100;
            box-shadow: 0 0 20px #0f0;
        }
        
        .footer-line {
            padding: 5px 0;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }
        
        .footer-section {
            flex: 1;
        }
        
        /* Blinking cursor */
        .cursor {
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        /* Statistics bar */
        .stats-bar {
            display: flex;
            gap: 20px;
            padding: 10px;
            background: #002200;
            border: 1px solid #0a0;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stat-label {
            color: #0a0;
        }
        
        .stat-value {
            color: #0f0;
            font-weight: bold;
        }
        
        /* Command line style */
        .command-line {
            background: #000;
            border: 1px solid #0f0;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
        }
        
        .prompt {
            color: #0f0;
        }
        
        .command {
            color: #ff0;
        }
    </style>
</head>
<body>
    <div class="terminal">
        <!-- Header -->
        <div class="header">
            <div class="header-line">
                <div class="header-title">╔══ NETWORKBUSTER UNIVERSAL TOOL LAUNCHER ══╗</div>
                <div class="header-time" id="currentTime">--:--:--</div>
            </div>
            <div class="breadcrumb">
                [root@networkbuster ~]$ pwd → /home/networkbuster/tools/launcher<span class="cursor">_</span>
            </div>
            <div class="header-line">
                <div style="color: #0a0; font-size: 12px;">
                    System: Windows ARM64 | Python 3.14.2 | Node.js v25.2.1 | Git: bigtree@1598d7e
                </div>
            </div>
        </div>
        
        <!-- Navigation Bar -->
        <div class="navbar">
            <a href="#services" class="nav-item">[ SERVICES ]</a>
            <a href="#utilities" class="nav-item">[ UTILITIES ]</a>
            <a href="#dashboards" class="nav-item">[ DASHBOARDS ]</a>
            <a href="#api" class="nav-item">[ API ]</a>
            <a href="#" onclick="location.reload()" class="nav-item">[ REFRESH ]</a>
            <a href="#" onclick="openAll()" class="nav-item">[ OPEN ALL ]</a>
        </div>
        
        <!-- Statistics Bar -->
        <div class="stats-bar">
            <div class="stat-item">
                <span class="stat-label">Total Tools:</span>
                <span class="stat-value" id="totalTools">--</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Services Online:</span>
                <span class="stat-value" id="onlineServices">--</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Uptime:</span>
                <span class="stat-value" id="uptime">--</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Last Update:</span>
                <span class="stat-value" id="lastUpdate">--</span>
            </div>
        </div>
        
        <!-- Core Services Section -->
        <div class="section" id="services">
            <div class="section-header">
                <div>═══ CORE SERVICES ═══</div>
                <div style="font-size: 12px; color: #0a0;">[5 services]</div>
            </div>
            <div class="section-content">
                <div class="tool-grid" id="coreServices"></div>
            </div>
        </div>
        
        <!-- Utilities Section -->
        <div class="section" id="utilities">
            <div class="section-header">
                <div>═══ UTILITIES & SCRIPTS ═══</div>
                <div style="font-size: 12px; color: #0a0;">[5 utilities]</div>
            </div>
            <div class="section-content">
                <div class="tool-grid" id="utilities"></div>
            </div>
        </div>
        
        <!-- Dashboards Section -->
        <div class="section" id="dashboards">
            <div class="section-header">
                <div>═══ DASHBOARDS & INTERFACES ═══</div>
                <div style="font-size: 12px; color: #0a0;">[4 dashboards]</div>
            </div>
            <div class="section-content">
                <ul class="index-list" id="dashboardsList"></ul>
            </div>
        </div>
        
        <!-- API Endpoints Section -->
        <div class="section" id="api">
            <div class="section-header">
                <div>═══ API ENDPOINTS & DOCUMENTATION ═══</div>
                <div style="font-size: 12px; color: #0a0;">[5 endpoints]</div>
            </div>
            <div class="section-content">
                <ul class="index-list" id="apiList"></ul>
            </div>
        </div>
        
        <!-- Command Line Reference -->
        <div class="section">
            <div class="section-header">
                <div>═══ QUICK REFERENCE COMMANDS ═══</div>
            </div>
            <div class="section-content">
                <div class="command-line">
                    <span class="prompt">networkbuster@localhost:~$</span> <span class="command">node server-universal.js</span> → Start web server on port 3000
                </div>
                <div class="command-line">
                    <span class="prompt">networkbuster@localhost:~$</span> <span class="command">python nasa_home_base.py</span> → Launch NASA Mission Control
                </div>
                <div class="command-line">
                    <span class="prompt">networkbuster@localhost:~$</span> <span class="command">python network_map_viewer.py</span> → Open network topology map
                </div>
                <div class="command-line">
                    <span class="prompt">networkbuster@localhost:~$</span> <span class="command">python flash_git_backup.py</span> → Flash backup to D: and K: drives
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-line">
                <div class="footer-section">
                    <strong>NetworkBuster v1.0.1</strong> | Branch: bigtree | Commit: 1598d7e
                </div>
                <div class="footer-section" style="text-align: right;">
                    Generated: <span id="footerTime"></span>
                </div>
            </div>
            <div class="footer-line">
                <div class="footer-section">
                    Backups: D:\\ NetworkBuster_Git_Cloud | K:\\ NetworkBuster_Git_Cloud
                </div>
                <div class="footer-section" style="text-align: right;">
                    Ports Active: <span id="activePorts">--</span>
                </div>
            </div>
            <div class="footer-line" style="border-top: 1px solid #0a0; padding-top: 10px; margin-top: 10px;">
                <div style="text-align: center; width: 100%; color: #0a0;">
                    [root@networkbuster ~]$ System Status: <span id="systemStatus" style="color: #0f0;">OPERATIONAL</span> | Memory: <span id="memUsage">--</span> | CPU: <span id="cpuUsage">--</span> | Disk: <span id="diskUsage">--</span><span class="cursor">_</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let startTime = Date.now();
        
        function updateTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = now.toLocaleTimeString();
            document.getElementById('footerTime').textContent = now.toISOString();
            
            // Update uptime
            const uptime = Math.floor((Date.now() - startTime) / 1000);
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            const seconds = uptime % 60;
            document.getElementById('uptime').textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        async function loadStatuses() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                renderCoreServices(data.core_services);
                renderUtilities(data.utilities);
                renderDashboards(data.dashboards);
                renderAPIEndpoints(data.api_endpoints);
                updateStats(data);
                
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            } catch (error) {
                console.error('Failed to load statuses:', error);
            }
        }
        
        function renderCoreServices(services) {
            const container = document.getElementById('coreServices');
            container.innerHTML = services.map(service => `
                <div class="tool-card">
                    <div class="tool-header">
                        <div class="tool-name">${service.name}</div>
                        <div class="status-badge status-${service.status}">${service.status.toUpperCase()}</div>
                    </div>
                    <div class="tool-details">Port: ${service.port}</div>
                    <div class="tool-details">CMD: ${service.cmd}</div>
                    <div class="tool-actions">
                        <button class="btn" onclick="window.open('${service.url}', '_blank')" ${service.status === 'offline' ? 'disabled' : ''}>
                            [ OPEN ]
                        </button>
                        <button class="btn" onclick="copyToClipboard('${service.url}')">
                            [ COPY URL ]
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        function renderUtilities(utilities) {
            const container = document.getElementById('utilities');
            container.innerHTML = utilities.map(util => `
                <div class="tool-card">
                    <div class="tool-header">
                        <div class="tool-name">${util.name}</div>
                        <div class="status-badge status-${util.status}">${util.status.toUpperCase()}</div>
                    </div>
                    <div class="tool-details">CMD: ${util.cmd}</div>
                    ${util.url ? `<div class="tool-details">URL: ${util.url}</div>` : ''}
                    <div class="tool-actions">
                        ${util.url ? `<button class="btn" onclick="window.open('${util.url}', '_blank')">[ OPEN ]</button>` : ''}
                        <button class="btn" onclick="copyToClipboard('${util.cmd}')">
                            [ COPY CMD ]
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        function renderDashboards(dashboards) {
            const list = document.getElementById('dashboardsList');
            list.innerHTML = dashboards.map(dash => `
                <li class="index-item">
                    <a href="${dash.url}" target="_blank" class="index-link">${dash.name}</a>
                    <span style="color: #0a0; font-size: 11px;">${dash.url}</span>
                </li>
            `).join('');
        }
        
        function renderAPIEndpoints(endpoints) {
            const list = document.getElementById('apiList');
            list.innerHTML = endpoints.map(ep => `
                <li class="index-item">
                    <a href="${ep.url}" target="_blank" class="index-link">${ep.name}</a>
                    <span style="color: #0a0; font-size: 11px;">${ep.url}</span>
                </li>
            `).join('');
        }
        
        function updateStats(data) {
            const totalTools = data.core_services.length + data.utilities.length + 
                              data.dashboards.length + data.api_endpoints.length;
            const onlineServices = data.core_services.filter(s => s.status === 'online').length;
            const activePorts = data.core_services.filter(s => s.status === 'online')
                .map(s => s.port).join(', ');
            
            document.getElementById('totalTools').textContent = totalTools;
            document.getElementById('onlineServices').textContent = `${onlineServices}/${data.core_services.length}`;
            document.getElementById('activePorts').textContent = activePorts || 'None';
            
            // Simulated system stats (replace with real ones if needed)
            document.getElementById('memUsage').textContent = '45%';
            document.getElementById('cpuUsage').textContent = '12%';
            document.getElementById('diskUsage').textContent = '38%';
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('[COPIED] ' + text);
            });
        }
        
        function openAll() {
            if (confirm('Open all available services?')) {
                fetch('/api/status').then(r => r.json()).then(data => {
                    data.core_services.filter(s => s.status === 'online').forEach(s => {
                        window.open(s.url, '_blank');
                    });
                });
            }
        }
        
        // Initialize
        updateTime();
        setInterval(updateTime, 1000);
        loadStatuses();
        setInterval(loadStatuses, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    return jsonify(get_all_statuses())

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'universal-launcher',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster - Universal Tool Launcher                 ║
║  Unix-style dashboard for all services                    ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("🚀 Starting Universal Tool Launcher on http://localhost:7000")
    print("⚡ All services and tools accessible from one interface")
    print("")
    
    app.run(host='0.0.0.0', port=7000, debug=False)
