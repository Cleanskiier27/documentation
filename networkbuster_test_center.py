from flask import Flask, render_template_string, jsonify
import requests
import time

app = Flask(__name__)

TEST_CENTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NetworkBuster | Test Center</title>
    <style>
        :root {
            --bg: #0a0a0c;
            --card: rgba(30, 30, 35, 0.9);
            --neon-blue: #00d4ff;
            --neon-green: #00ff88;
            --neon-yellow: #ffee00;
            --neon-red: #ff3131;
            --text: #ffffff;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', monospace; }
        body { background: var(--bg); color: var(--text); padding: 30px; }
        .glass { background: var(--card); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        header { margin-bottom: 30px; display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid var(--neon-blue); padding-bottom: 15px; }
        h1 { color: var(--neon-blue); letter-spacing: 2px; text-transform: uppercase; font-size: 1.5rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .test-card { transition: 0.3s; position: relative; overflow: hidden; }
        .test-card:hover { transform: translateY(-5px); border-color: var(--neon-blue); }
        .status-badge { float: right; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; }
        .status-online { background: rgba(0, 255, 136, 0.1); color: var(--neon-green); border: 1px solid var(--neon-green); }
        .status-offline { background: rgba(255, 49, 49, 0.1); color: var(--neon-red); border: 1px solid var(--neon-red); }
        .url-text { color: var(--neon-blue); font-size: 0.85rem; margin: 10px 0; display: block; text-decoration: none; }
        .btn { background: transparent; border: 1px solid var(--neon-blue); color: var(--neon-blue); padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; margin-top: 10px; transition: 0.3s; }
        .btn:hover { background: var(--neon-blue); color: #000; box-shadow: 0 0 15px var(--neon-blue); }
        .btn-run { border-color: var(--neon-green); color: var(--neon-green); }
        .btn-run:hover { background: var(--neon-green); color: #000; box-shadow: 0 0 15px var(--neon-green); }
        .console { background: #000; color: #aaa; padding: 10px; border-radius: 6px; font-size: 0.75rem; margin-top: 15px; height: 100px; overflow-y: auto; border: 1px solid #333; white-space: pre-wrap; }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <header>
        <h1>🧪 NETWORKBUSTER_TEST_CENTER // V1.0</h1>
        <div style="display: flex; gap: 15px; align-items: center;">
            <a href="http://localhost:3000" style="color: var(--neon-blue); text-decoration: none; font-size: 0.7rem; font-weight: 800; border: 1px solid var(--neon-blue); padding: 5px 15px; border-radius: 4px; transition: 0.3s;">➔ RETURN_TO_MANAGER</a>
            <div style="font-size: 0.8rem; color: #888;">CORE_DIAGNOSTICS_ACTIVE</div>
        </div>
    </header>

    <div class="grid">
        <!-- Dashboard Test -->
        <div class="glass test-card">
            <span id="status-3000" class="status-badge status-offline">OFFLINE</span>
            <h3>Main Dashboard</h3>
            <a href="http://localhost:3000" target="_blank" class="url-text">http://localhost:3000</a>
            <p style="font-size: 0.8rem; color: #888;">Primary entry point and music player interface.</p>
            <button class="btn btn-run" onclick="runTest(3000, '/')">EXEC_HEALTH_CHECK</button>
            <div id="console-3000" class="console">> Waiting for command...</div>
        </div>

        <!-- Control Panel Test -->
        <div class="glass test-card">
            <span id="status-3000-cp" class="status-badge status-offline">OFFLINE</span>
            <h3>Control Panel</h3>
            <a href="http://localhost:3000/control-panel" target="_blank" class="url-text">http://localhost:3000/control-panel</a>
            <p style="font-size: 0.8rem; color: #888;">Equalizer and operational dashboard controls.</p>
            <button class="btn btn-run" onclick="runTest(3000, '/control-panel', 'status-3000-cp', 'console-3000-cp')">EXEC_UI_VALIDATION</button>
            <div id="console-3000-cp" class="console">> Waiting for command...</div>
        </div>

        <!-- API Health Test -->
        <div class="glass test-card">
            <span id="status-3001-health" class="status-badge status-offline">OFFLINE</span>
            <h3>API Health Check</h3>
            <a href="http://localhost:3001/api/health" target="_blank" class="url-text">http://localhost:3001/api/health</a>
            <p style="font-size: 0.8rem; color: #888;">Backend service health and uptime telemetry.</p>
            <button class="btn btn-run" onclick="runTest(3001, '/api/health', 'status-3001-health', 'console-3001-health')">FETCH_JSON_TELEMETRY</button>
            <div id="console-3001-health" class="console">> Waiting for command...</div>
        </div>

        <!-- API Specs Test -->
        <div class="glass test-card">
            <span id="status-3001-specs" class="status-badge status-offline">OFFLINE</span>
            <h3>System Specifications</h3>
            <a href="http://localhost:3001/api/specs" target="_blank" class="url-text">http://localhost:3001/api/specs</a>
            <p style="font-size: 0.8rem; color: #888;">Hardware and OS resource allocation data.</p>
            <button class="btn btn-run" onclick="runTest(3001, '/api/specs', 'status-3001-specs', 'console-3001-specs')">GET_HARDWARE_SPECS</button>
            <div id="console-3001-specs" class="console">> Waiting for command...</div>
        </div>

        <!-- Audio Lab Test -->
        <div class="glass test-card">
            <span id="status-3002" class="status-badge status-offline">OFFLINE</span>
            <h3>Audio Lab</h3>
            <a href="http://localhost:3002/audio-lab" target="_blank" class="url-text">http://localhost:3002/audio-lab</a>
            <p style="font-size: 0.8rem; color: #888;">Interactive frequency analysis and synthesis.</p>
            <button class="btn btn-run" onclick="runTest(3002, '/audio-lab')">VALIDATE_AUDIO_ENGINE</button>
            <button class="btn" onclick="createStream()">CREATE_STREAM_POST</button>
            <div id="console-3002" class="console">> Waiting for command...</div>
        </div>
    </div>

    <script>
        async function runTest(port, path, statusId = 'status-'+port, consoleId = 'console-'+port) {
            const cons = document.getElementById(consoleId);
            const status = document.getElementById(statusId);
            cons.textContent = `> INITIATING REQUEST: http://localhost:${port}${path}\\n`;
            
            try {
                const startTime = Date.now();
                const res = await fetch(`http://localhost:4000/api/proxy?port=${port}&path=${encodeURIComponent(path)}`);
                const duration = Date.now() - startTime;
                const data = await res.json();
                
                if (res.ok) {
                    status.className = 'status-badge status-online';
                    status.textContent = 'ONLINE';
                    cons.textContent += `> RESPONSE_OK (${duration}ms)\\n`;
                    cons.textContent += JSON.stringify(data, null, 2);
                } else {
                    throw new Error(data.error || 'Request failed');
                }
            } catch (e) {
                status.className = 'status-badge status-offline';
                status.textContent = 'ERROR';
                cons.textContent += `> ERROR: ${e.message}`;
            }
        }

        async function createStream() {
            const cons = document.getElementById('console-3002');
            cons.textContent = `> POST /api/audio/stream/create\\n`;
            try {
                const res = await fetch('http://localhost:4000/api/proxy_post?port=3002&path=/api/audio/stream/create');
                const data = await res.json();
                cons.textContent += `> STREAM_CREATED\\n` + JSON.stringify(data, null, 2);
            } catch (e) {
                cons.textContent += `> FAILED: ${e.message}`;
            }
        }

        // Auto-check on load
        window.onload = () => {
            runTest(3000, '/');
            runTest(3001, '/api/health', 'status-3001-health', 'console-3001-health');
            runTest(3002, '/audio-lab');
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEST_CENTER_HTML)

@app.route('/api/proxy')
def proxy():
    port = requests.args.get('port')
    path = requests.args.get('path')
    try:
        r = requests.get(f"http://localhost:{port}{path}", timeout=3)
        try:
            return jsonify(r.json())
        except:
            return jsonify({"status": "ok", "content_type": r.headers.get('Content-Type')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxy_post')
def proxy_post():
    port = requests.args.get('port')
    path = requests.args.get('path')
    try:
        r = requests.post(f"http://localhost:{port}{path}", timeout=3)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\\n🚀 NetworkBuster Test Center hosting on http://localhost:4000")
    app.run(host='0.0.0.0', port=4000)
