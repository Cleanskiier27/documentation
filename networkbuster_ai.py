import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import psutil
import socket
from datetime import datetime
import json
import time

# Import integrated engines
from mission_control_engine import engine as mc_engine
from network_tools_engine import nt_engine
from business_intelligence import BusinessIntelligence

app = Flask(__name__)
CORS(app)
bi_engine = BusinessIntelligence()

# NetworkBuster AI Template - Universal Command Center
NBAI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetworkBuster AI - Universal Command Center</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #581c87 100%);
            min-height: 100vh;
            color: #e2e8f0;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
        }
        .container {
            background: rgba(0, 0, 0, 0.9);
            border-radius: 12px;
            width: 100%;
            max-width: 1300px;
            height: 95vh;
            display: flex;
            flex-direction: column;
            border: 2px solid rgba(168, 85, 247, 0.3);
            overflow: hidden;
            box-shadow: 0 0 50px rgba(0,0,0,0.8);
        }
        .header {
            background: linear-gradient(90deg, #7e22ce, #3b82f6);
            padding: 15px 25px;
            text-align: center;
        }
        .tabs {
            display: flex;
            background: rgba(0,0,0,0.5);
            border-bottom: 1px solid rgba(168, 85, 247, 0.2);
            overflow-x: auto;
        }
        .tab {
            padding: 15px 20px;
            cursor: pointer;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            color: #94a3b8;
            border-bottom: 3px solid transparent;
            white-space: nowrap;
        }
        .tab.active {
            color: #fff;
            border-bottom-color: #a855f7;
            background: rgba(168, 85, 247, 0.1);
        }
        .status-bar {
            padding: 8px 25px;
            background: rgba(30, 41, 59, 0.5);
            font-size: 11px;
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .content-area { flex: 1; overflow: hidden; position: relative; }
        .tab-content { display: none; height: 100%; overflow-y: auto; padding: 20px; }
        .tab-content.active { display: flex; flex-direction: column; }
        
        /* Grid Layouts */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }
        .card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 10px; padding: 20px; }
        .card h3 { color: #a855f7; margin-bottom: 15px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
        
        /* Network Tools Styles */
        .throughput-meter {
            display: flex;
            justify-content: space-around;
            text-align: center;
            margin-bottom: 20px;
        }
        .meter-box {
            padding: 15px;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            min-width: 120px;
        }
        .meter-val { font-size: 24px; font-weight: bold; color: #22c55e; }
        .meter-label { font-size: 10px; color: #94a3b8; margin-top: 5px; }
        
        .service-list { list-style: none; }
        .service-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 12px;
        }
        .status-pill { padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }
        .status-up { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .status-down { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        
        /* Chat Styles */
        .chat-area { flex: 1; display: flex; flex-direction: column; }
        .chat-messages { flex: 1; overflow-y: auto; margin-bottom: 15px; padding-right: 10px; }
        .message { margin-bottom: 15px; }
        .msg-content { background: rgba(30, 41, 59, 0.8); padding: 12px 18px; border-radius: 12px; font-size: 13px; line-height: 1.5; border-left: 3px solid #a855f7; }
        .user .msg-content { border-left-color: #3b82f6; background: rgba(30, 58, 138, 0.4); }
        .input-box { display: flex; gap: 10px; background: rgba(0,0,0,0.5); padding: 15px; border-radius: 10px; }
        input { flex: 1; background: transparent; border: 1px solid #334155; color: #fff; padding: 12px; border-radius: 8px; outline: none; font-family: inherit; }
        button { background: #7e22ce; color: #fff; border: none; padding: 0 25px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        
        /* Mobile Specific */
        @media (max-width: 768px) {
            .container { height: 100vh; border-radius: 0; border: none; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="font-size: 20px;">🛰️ NETWORKBUSTER UNIVERSAL</h1>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('chat')">Assistant</div>
            <div class="tab" onclick="switchTab('network')">Network Tools</div>
            <div class="tab" onclick="switchTab('missions')">Missions</div>
            <div class="tab" onclick="switchTab('galaxy')">Galaxy</div>
            <div class="tab" onclick="switchTab('eco')">Eco</div>
            <div class="tab" onclick="switchTab('business')">Business Magic</div>
        </div>
        
        <div class="status-bar">
            <span>CORE: ONLINE</span>
            <span id="throughput-display">UP: 0 KB/s | DOWN: 0 KB/s</span>
            <span id="time-display">--:--:--</span>
        </div>
        
        <div class="content-area">
            <!-- Chat Tab -->
            <div id="chatTab" class="tab-content active">
                <div class="chat-area">
                    <div class="chat-messages" id="chatArea">
                        <div class="message ai">
                            <div class="msg-content">
                                📱 <strong>Universal Command Center Active.</strong><br>
                                I am now monitoring your local network and system resources.<br>
                                Try asking <code>run network diagnostic</code> or <code>scan ports</code>.
                            </div>
                        </div>
                    </div>
                    <div class="input-box">
                        <input type="text" id="chatInput" placeholder="Command or question..." />
                        <button onclick="sendMessage()">SEND</button>
                    </div>
                </div>
            </div>
            
            <!-- Network Tools Tab -->
            <div id="networkTab" class="tab-content">
                <div class="grid">
                    <div class="card">
                        <h3>📈 Real-time Traffic</h3>
                        <div class="throughput-meter">
                            <div class="meter-box">
                                <div class="meter-val" id="val-up">0.0</div>
                                <div class="meter-label">UPLOAD (KB/s)</div>
                            </div>
                            <div class="meter-box">
                                <div class="meter-val" id="val-down">0.0</div>
                                <div class="meter-label">DOWNLOAD (KB/s)</div>
                            </div>
                        </div>
                        <div id="throughput-stats" style="font-size: 11px; opacity: 0.7; text-align: center;">
                            Total: 0 MB Sent | 0 MB Recv
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>🛡️ Service Health</h3>
                        <div class="service-list" id="service-list">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>🔍 Diagnostics</h3>
                        <button style="width:100%; padding:15px; margin-bottom:15px;" onclick="runDiagnostic()">RUN FULL SYSTEM DIAGNOSTIC</button>
                        <div id="diagnostic-result" style="font-size: 11px; line-height: 1.6;">
                            <p style="opacity:0.5; text-align:center;">Click button to start analysis</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Missions Tab -->
            <div id="missionsTab" class="tab-content">
                <div class="grid">
                    <div class="card">
                        <h3>🛰️ Active Missions</h3>
                        <div id="mission-list" style="opacity:0.6">No active missions.</div>
                        <button style="width:100%; margin-top:15px; padding:10px;" onclick="alert('Starting scan...')">START SYSTEM SCAN</button>
                    </div>
                </div>
            </div>

            <!-- Galaxy Tab -->
            <div id="galaxyTab" class="tab-content">
                <div class="grid">
                    <div class="card">
                        <h3>🌌 Star Systems</h3>
                        <div id="star-list" style="font-size: 12px;"></div>
                    </div>
                </div>
            </div>

            <!-- Eco Tab -->
            <div id="ecoTab" class="tab-content">
                <div class="grid">
                    <div class="card">
                        <h3>🌱 Sustainability</h3>
                        <div id="eco-metrics" style="text-align:center; padding:20px;">
                            <div id="eco-score-val" style="font-size:48px; color:#22c55e; font-weight:bold;">--</div>
                            <div style="font-size:12px; margin-top:10px;">ECO SCORE</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Business Tab -->
            <div id="businessTab" class="tab-content">
                <div class="grid">
                    <div class="card">
                        <h3>💰 Financial Health</h3>
                        <div id="biz-financials" style="font-size: 13px; line-height: 1.8;">
                            <p>Loading business data...</p>
                        </div>
                    </div>
                    <div class="card">
                        <h3>🔮 Magic Recommendations</h3>
                        <div id="biz-recs" style="font-size: 12px; line-height: 1.6;">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab Management
        function switchTab(id) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            const btn = Array.from(document.querySelectorAll('.tab')).find(t => t.textContent.toLowerCase().includes(id));
            if (btn) btn.classList.add('active');
            
            const content = document.getElementById(id + 'Tab');
            if (content) content.classList.add('active');
            
            if (id === 'network') refreshNetwork();
            if (id === 'galaxy') loadGalaxy();
            if (id === 'eco') loadEco();
            if (id === 'business') loadBusiness();
        }

        // Network Tools Logic
        async function refreshNetwork() {
            try {
                const res = await fetch('/api/nbai/network/throughput');
                const data = await res.json();
                document.getElementById('val-up').textContent = data.up_kbps;
                document.getElementById('val-down').textContent = data.down_kbps;
                document.getElementById('throughput-display').textContent = `UP: ${data.up_kbps} KB/s | DOWN: ${data.down_kbps} KB/s`;
                document.getElementById('throughput-stats').textContent = `Total: ${data.total_sent_mb} MB Sent | ${data.total_recv_mb} MB Recv`;
                
                const statusRes = await fetch('/api/nbai/status');
                const statusData = await statusRes.json();
                const list = document.getElementById('service-list');
                list.innerHTML = statusData.status.map(s => `
                    <div class="service-item">
                        <span>${s.name} (:${s.port})</span>
                        <span class="status-pill ${s.active ? 'status-up' : 'status-down'}">${s.active ? 'ONLINE' : 'OFFLINE'}</span>
                    </div>
                `).join('');
            } catch (e) { console.error(e); }
        }

        async function runDiagnostic() {
            const div = document.getElementById('diagnostic-result');
            div.innerHTML = '<p style="text-align:center;">⌛ Analyzing network environment...</p>';
            
            try {
                const res = await fetch('/api/nbai/network/diagnostic');
                const data = await res.json();
                div.innerHTML = `
                    <div style="background:rgba(0,0,0,0.3); padding:10px; border-radius:5px;">
                        <p>🎯 Target: <strong>${data.target}</strong></p>
                        <p>📶 Latency: <strong>${data.connectivity.latency_ms || 'N/A'} ms</strong></p>
                        <p>🛡️ Health Score: <strong style="color:${data.health_score > 80 ? '#22c55e' : '#ef4444'}">${data.health_score}/100</strong></p>
                        <p>📊 Load: CPU ${data.system_load.cpu}% | MEM ${data.system_load.mem}%</p>
                    </div>
                `;
            } catch (e) { div.innerHTML = '<p style="color:#ef4444">Error running diagnostic.</p>'; }
        }

        // Chat Logic
        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const msg = input.value.trim();
            if (!msg) return;
            
            addMsg(msg, 'user');
            input.value = '';
            
            const res = await fetch('/api/nbai/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: msg })
            });
            const data = await res.json();
            addMsg(data.response, 'ai');
        }

        function addMsg(text, role) {
            const div = document.createElement('div');
            div.className = `message ${role}`;
            div.innerHTML = `<div class="msg-content">${text}</div>`;
            const area = document.getElementById('chatArea');
            area.appendChild(div);
            area.scrollTop = area.scrollHeight;
        }

        // Data Loading
        async function loadGalaxy() {
            const res = await fetch('/api/nbai/galaxy/stars');
            const data = await res.json();
            const list = document.getElementById('star-list');
            list.innerHTML = Object.values(data).map(s => `
                <div style="margin-bottom:5px; padding:5px; border-bottom:1px solid rgba(255,255,255,0.05)">
                    <strong>${s.name}</strong> - ${s.distance} ly
                </div>
            `).join('');
        }

        async function loadEco() {
            const res = await fetch('/api/nbai/sustainability/status');
            const data = await res.json();
            document.getElementById('eco-score-val').textContent = data.eco_score;
        }

        async function loadBusiness() {
            try {
                const res = await fetch('/api/nbai/business/status');
                const data = await res.json();
                const fin = data.metrics.financial;
                const baseline = data.budget_baseline;
                
                document.getElementById('biz-financials').innerHTML = `
                    <div style="background:rgba(0,0,0,0.3); padding:15px; border-radius:8px;">
                        <p>💹 <strong>Projected Monthly:</strong> $${fin.estimated_monthly_infra}</p>
                        <p>🎯 <strong>Budget Target:</strong> $${baseline.azure_core}</p>
                        <p>🔥 <strong>Daily Burn:</strong> $${fin.daily_burn_rate}</p>
                        <p>👥 <strong>Team Burn:</strong> $${baseline.team_cost_min.toLocaleString()} - $${baseline.team_cost_max.toLocaleString()}/mo</p>
                    </div>
                `;
                
                document.getElementById('biz-recs').innerHTML = data.recommendations.map(r => `
                    <div style="margin-bottom:10px; padding:10px; border-left:3px solid ${r.priority === 'HIGH' ? '#ef4444' : '#a855f7'}; background:rgba(255,255,255,0.05);">
                        <strong style="font-size:10px; color:#94a3b8;">${r.category} | ${r.priority}</strong><br>
                        ${r.msg}
                    </div>
                `).join('');
            } catch (e) { console.error(e); }
        }

        // Background loops
        setInterval(() => {
            document.getElementById('time-display').textContent = new Date().toLocaleTimeString();
            if (document.getElementById('networkTab').classList.contains('active')) refreshNetwork();
        }, 2000);

        // Initial setup
        input.addEventListener('keypress', (e) => { if(e.key === 'Enter') sendMessage(); });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(NBAI_TEMPLATE)

# AI Chat API
@app.route('/api/nbai/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '').lower()
    
    if 'diagnostic' in msg or 'health' in msg:
        diag = nt_engine.run_full_diagnostic()
        return jsonify({'response': f"📋 <strong>Diagnostic complete.</strong> Health score: {diag['health_score']}/100. Target: {diag['target']}."})
    elif 'speed' in msg or 'traffic' in msg:
        speed = nt_engine.get_realtime_throughput()
        return jsonify({'response': f"📈 <strong>Current Traffic:</strong> UP: {speed['up_kbps']} KB/s | DOWN: {speed['down_kbps']} KB/s."})
    else:
        # Default AI response
        return jsonify({'response': f"🤖 I am monitoring your network. Current Eco Score: {nt_engine.run_full_diagnostic()['health_score']}%."})

# Network Tools APIs
@app.route('/api/nbai/network/throughput')
def get_throughput():
    return jsonify(nt_engine.get_realtime_throughput())

@app.route('/api/nbai/network/diagnostic')
def run_diagnostic():
    target = request.args.get('target')
    return jsonify(nt_engine.run_full_diagnostic(target))

# Existing Integrated Endpoints
@app.route('/api/nbai/status')
def status():
    services = [
        {'name': 'Web Server', 'port': 3000, 'active': check_port(3000)},
        {'name': 'API Server', 'port': 3001, 'active': check_port(3001)},
        {'name': 'AI Command', 'port': 4000, 'active': True},
        {'name': 'Mission Control', 'port': 5000, 'active': check_port(5000)},
        {'name': 'Network Map', 'port': 6000, 'active': check_port(6000)}
    ]
    return jsonify({'status': services})

def check_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN': return True
    return False

@app.route('/api/nbai/galaxy/stars')
def galaxy_stars():
    return jsonify(mc_engine.galaxy.STARS)

@app.route('/api/nbai/sustainability/status')
def eco_status():
    load = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return jsonify(mc_engine.eco.calculate_eco_score(load, mem, 5))

@app.route('/api/nbai/business/status')
def business_status():
    metrics = bi_engine.get_realtime_metrics()
    recommendations = bi_engine.get_business_recommendations(metrics)
    return jsonify({
        'metrics': metrics,
        'recommendations': recommendations,
        'budget_baseline': bi_engine.budget_data
    })

# MOBILE BRIDGE ENDPOINT
@app.route('/api/nbai/mobile/bridge')
def mobile_bridge():
    """Endpoint for Capacitor/Mobile app synchronization"""
    return jsonify({
        'app_name': 'NetworkBuster Universal',
        'api_version': '2.0.0',
        'diagnostic_summary': nt_engine.run_full_diagnostic(),
        'throughput': nt_engine.get_realtime_throughput(),
        'mobile_optimized': True
    })

def main():
    print("\n" + "═" * 60)
    print("║  NetworkBuster AI - UNIVERSAL COMMAND CENTER               ║")
    print("═" * 60)
    print("   Assistant: http://localhost:4000")
    print("   Bridge:    http://localhost:4000/api/nbai/mobile/bridge")
    app.run(host='0.0.0.0', port=4000, debug=False)

if __name__ == '__main__':
    main()
