from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import threading
import time
import random

app = Flask(__name__)
CORS(app)

# Virtual Machine State
vm_state = {
    "status": "BOOTING",
    "recording": False,
    "nexus_data": [],
    "audio_level": 0
}

VM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NEXUS ONE | ARCH MATRIX VM</title>
    <style>
        :root {
            --bg: #000500;
            --term-green: #00ff41;
            --term-dim: #003b0f;
            --alert: #ff0000;
            --nexus: #00ffff;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Courier New', monospace; }
        body { background: var(--bg); color: var(--term-green); overflow: hidden; height: 100vh; }
        
        .crt-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            background-size: 100% 2px, 3px 100%;
            pointer-events: none; z-index: 999;
        }

        .vm-container {
            display: grid;
            grid-template-columns: 300px 1fr 300px;
            grid-template-rows: 60px 1fr 200px;
            height: 100vh;
            padding: 20px;
            gap: 20px;
        }

        .window {
            border: 2px solid var(--term-green);
            background: rgba(0, 20, 0, 0.9);
            position: relative;
            box-shadow: 0 0 15px var(--term-dim);
        }
        
        .win-title {
            background: var(--term-green);
            color: #000;
            padding: 5px 10px;
            font-weight: bold;
            font-size: 0.8rem;
            text-transform: uppercase;
        }

        /* Matrix Canvas */
        #matrixCanvas { width: 100%; height: 100%; display: block; }

        /* Nexus Recorder */
        .recorder-interface { padding: 15px; height: 100%; display: flex; flex-direction: column; }
        .rec-btn {
            background: transparent; border: 2px solid var(--alert); color: var(--alert);
            padding: 10px; margin-bottom: 10px; cursor: pointer; text-transform: uppercase;
            font-weight: bold; transition: 0.2s;
        }
        .rec-btn.active { background: var(--alert); color: #000; box-shadow: 0 0 20px var(--alert); }
        .data-stream {
            flex: 1; overflow-y: hidden; font-size: 0.7rem; color: var(--term-green);
            border: 1px solid var(--term-dim); padding: 5px; opacity: 0.8;
        }

        /* Audio Nodes */
        .audio-node-list { padding: 10px; overflow-y: auto; height: 100%; }
        .node-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.75rem; border-bottom: 1px dashed var(--term-dim); }
        .node-val { color: var(--nexus); }

        .scan-line {
            position: absolute; top: 0; left: 0; width: 100%; height: 5px;
            background: rgba(0, 255, 65, 0.3); opacity: 0.5;
            animation: scan 6s linear infinite; pointer-events: none;
        }
        @keyframes scan { 0% { top: -10%; } 100% { top: 110%; } }

        .blink { animation: blink 1s infinite; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    </style>
</head>
<body>
    <div class="crt-overlay"></div>
    <div class="scan-line"></div>

    <div class="vm-container">
        <!-- Header -->
        <div class="window" style="grid-column: 1 / -1; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;">
            <div>> SYSTEM_ARCH_VM // <span class="blink">ONLINE</span></div>
            <div style="color: var(--nexus);">NEXUS_ONE: CONNECTED</div>
            <div>
                <a href="http://localhost:3000" style="color: var(--term-green); text-decoration: none; border: 1px solid var(--term-green); padding: 5px 10px;">[ EXIT_VM ]</a>
            </div>
        </div>

        <!-- Left: Audio Nodes -->
        <div class="window" style="grid-row: 2 / -1;">
            <div class="win-title">AUDIO_NODES</div>
            <div class="audio-node-list" id="audioNodes">
                <!-- Dynamic Content -->
            </div>
        </div>

        <!-- Center: Arch Matrix -->
        <div class="window" style="grid-column: 2; grid-row: 2 / 3;">
            <div class="win-title">ARCH_MATRIX_VISUALIZER</div>
            <canvas id="matrixCanvas"></canvas>
        </div>

        <!-- Right: Nexus Recorder -->
        <div class="window" style="grid-column: 3; grid-row: 2 / -1;">
            <div class="win-title">NEXUS_ONE_RECORDER</div>
            <div class="recorder-interface">
                <button id="recBtn" class="rec-btn" onclick="toggleRec()">[ REC ] NEXUS_STREAM</button>
                <div class="data-stream" id="nexusStream">
                    > WAITING_FOR_CAPTURE...
                </div>
            </div>
        </div>

        <!-- Bottom: Console -->
        <div class="window" style="grid-column: 2; grid-row: 3;">
            <div class="win-title">VM_CONSOLE</div>
            <div id="console" style="padding: 10px; font-size: 0.8rem; height: 100%; overflow: hidden;"></div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('matrixCanvas');
        const ctx = canvas.getContext('2d');
        let nodes = [];
        let isRecording = false;
        
        // Resize canvas
        function resize() {
            canvas.width = canvas.parentElement.offsetWidth;
            canvas.height = canvas.parentElement.offsetHeight;
            initNodes();
        }
        window.onresize = resize;

        class Node {
            constructor(type) {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 2;
                this.vy = (Math.random() - 0.5) * 2;
                this.type = type; // 'nexus', 'audio', 'server'
                this.pulse = 0;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                if(this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if(this.y < 0 || this.y > canvas.height) this.vy *= -1;
                
                // Pulse effect
                this.pulse = Math.max(0, this.pulse - 0.05);
                if(Math.random() > 0.98) this.pulse = 1;
            }

            draw() {
                ctx.beginPath();
                let color = '#00ff41'; // default green
                let size = 3;
                
                if(this.type === 'nexus') { color = '#00ffff'; size = 8 + (this.pulse * 5); }
                else if(this.type === 'audio') { color = '#bc13fe'; size = 4 + (this.pulse * 3); }
                
                ctx.fillStyle = color;
                ctx.arc(this.x, this.y, size, 0, Math.PI * 2);
                ctx.fill();
                
                // Halo for Nexus
                if(this.type === 'nexus') {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(0, 255, 255, ${this.pulse})`;
                    ctx.arc(this.x, this.y, size * 2, 0, Math.PI * 2);
                    ctx.stroke();
                }
            }
        }

        function initNodes() {
            nodes = [];
            // Central Nexus One
            nodes.push(new Node('nexus'));
            // Audio Nodes
            for(let i=0; i<8; i++) nodes.push(new Node('audio'));
            // Standard Nodes
            for(let i=0; i<20; i++) nodes.push(new Node('server'));
        }

        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 5, 0, 0.3)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Connections
            ctx.strokeStyle = 'rgba(0, 255, 65, 0.1)';
            for(let i=0; i<nodes.length; i++) {
                for(let j=i+1; j<nodes.length; j++) {
                    const d = Math.hypot(nodes[i].x - nodes[j].x, nodes[i].y - nodes[j].y);
                    if(d < 100) {
                        ctx.beginPath();
                        ctx.moveTo(nodes[i].x, nodes[i].y);
                        ctx.lineTo(nodes[j].x, nodes[j].y);
                        ctx.stroke();
                    }
                }
                nodes[i].update();
                nodes[i].draw();
            }
            requestAnimationFrame(drawMatrix);
        }

        function toggleRec() {
            isRecording = !isRecording;
            const btn = document.getElementById('recBtn');
            const log = document.getElementById('console');
            
            if(isRecording) {
                btn.classList.add('active');
                btn.innerText = "[ REC ] RECORDING...";
                log.innerHTML += "> CAPTURE_INITIATED: NEXUS_ONE<br>";
            } else {
                btn.classList.remove('active');
                btn.innerText = "[ REC ] NEXUS_STREAM";
                log.innerHTML += "> CAPTURE_SAVED: /data/nexus_one.log<br>";
            }
        }

        function updateData() {
            // Simulate Audio Nodes Data
            const audioList = document.getElementById('audioNodes');
            audioList.innerHTML = '';
            for(let i=1; i<=8; i++) {
                const hz = Math.floor(Math.random() * 800 + 200);
                const vol = Math.floor(Math.random() * 100);
                audioList.innerHTML += `
                    <div class="node-row">
                        <span>AUDIO_NODE_0${i}</span>
                        <span class="node-val">${hz}Hz / ${vol}%</span>
                    </div>`;
            }

            // Simulate Nexus Stream
            if(isRecording) {
                const stream = document.getElementById('nexusStream');
                const hex = Math.random().toString(16).substring(2, 14).toUpperCase();
                const div = document.createElement('div');
                div.textContent = `HEX: ${hex} | PKT: ${Math.floor(Math.random()*999)}`;
                stream.prepend(div);
                if(stream.children.length > 20) stream.lastChild.remove();
            }
        }

        setTimeout(() => { resize(); drawMatrix(); }, 100);
        setInterval(updateData, 200);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(VM_HTML)

def run_server():
    app.run(host='0.0.0.0', port=9001)

if __name__ == "__main__":
    print("Virtual Machine Booting...")
    run_server()
