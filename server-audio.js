import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

// Optional performance packages
let compression = null;
let helmet = null;

try {
  compression = (await import('compression')).default;
} catch {
  console.warn('⚠️  compression module not found');
}

try {
  helmet = (await import('helmet')).default;
} catch {
  console.warn('⚠️  helmet module not found');
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.AUDIO_PORT || 3002;
const SERVICE_NAME = process.env.SERVICE_NAME || 'Audio Server';

// Middleware
if (compression) app.use(compression());
if (helmet) app.use(helmet());

// Security: Add specific CSP for Audio Lab
if (helmet) {
  app.use(helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      connectSrc: ["'self'", "http://localhost:*"],
      mediaSrc: ["'self'", "blob:", "data:"],
      imgSrc: ["'self'", "data:", "https://*"]
    }
  }));
}

app.use(express.json({ limit: '10mb' }));

// Audio processing state
const audioStreams = new Map();
let streamIdCounter = 0;

// ============================================
// AUDIO STREAMING ENDPOINTS
// ============================================

// Create audio stream session
app.post('/api/audio/stream/create', (req, res) => {
  const streamId = ++streamIdCounter;
  const timestamp = Date.now();
  
  audioStreams.set(streamId, {
    id: streamId,
    createdAt: timestamp,
    duration: 0,
    chunks: 0,
    format: 'wav',
    sampleRate: 44100,
    bitDepth: 16,
    channels: 2,
    status: 'active'
  });

  res.json({
    streamId,
    timestamp,
    status: 'ready',
    message: 'Audio stream created successfully'
  });
});

// Process audio chunk (AI analysis)
app.post('/api/audio/process', (req, res) => {
  const { streamId, audioData, frequency } = req.body;

  if (!streamId || !audioData) {
    return res.status(400).json({ error: 'Missing streamId or audioData' });
  }

  const stream = audioStreams.get(streamId);
  if (!stream) {
    return res.status(404).json({ error: 'Stream not found' });
  }

  // Simulate AI audio analysis
  const analysis = {
    streamId,
    frequency: frequency || 440,
    amplitude: Math.random() * 100,
    noiseLevel: Math.random() * 20,
    clarity: (Math.random() * 50 + 50).toFixed(2) + '%',
    detectedPitch: frequency ? `${frequency.toFixed(2)} Hz` : 'N/A',
    audioQuality: Math.random() > 0.5 ? 'Good' : 'Excellent',
    timestamp: new Date().toISOString()
  };

  stream.chunks++;
  stream.duration += 0.1;

  res.json({
    success: true,
    analysis,
    streamStatus: stream
  });
});

// Synthesize audio tone
app.post('/api/audio/synthesize', (req, res) => {
  const { frequency, duration, waveform } = req.body;
  
  if (!frequency || !duration) {
    return res.status(400).json({ error: 'Missing frequency or duration' });
  }

  const synthParams = {
    frequency: parseFloat(frequency),
    duration: parseFloat(duration),
    waveform: waveform || 'sine',
    sampleRate: 44100,
    timestamp: new Date().toISOString()
  };

  res.json({
    success: true,
    synthesis: synthParams,
    message: `Synthesizing ${synthParams.waveform} wave at ${synthParams.frequency}Hz for ${synthParams.duration}ms`,
    downloadUrl: `/api/audio/download/${Date.now()}`
  });
});

// Real-time frequency detection
app.post('/api/audio/detect-frequency', (req, res) => {
  const { audioBuffer } = req.body;
  
  if (!audioBuffer) {
    return res.status(400).json({ error: 'Missing audioBuffer' });
  }

  // Simulate frequency detection (FFT-like analysis)
  const detectedFrequencies = [
    { frequency: 440, strength: 95, note: 'A4' },
    { frequency: 880, strength: 45, note: 'A5' },
    { frequency: 220, strength: 30, note: 'A3' }
  ];

  res.json({
    success: true,
    dominantFrequency: detectedFrequencies[0].frequency,
    detectedFrequencies,
    confidence: (Math.random() * 30 + 70).toFixed(2) + '%'
  });
});

// Audio spectrum analysis
app.get('/open', (req, res) => {
  import('child_process').then(cp => {
    cp.exec(`start http://localhost:${PORT}/audio-lab`);
    res.json({ success: true, message: 'Launching Audio Lab...' });
  });
});

app.post('/api/audio/spectrum', (req, res) => {
  const { streamId } = req.body;

  const spectrum = {
    bass: (Math.random() * 100).toFixed(2),
    lowMid: (Math.random() * 100).toFixed(2),
    mid: (Math.random() * 100).toFixed(2),
    highMid: (Math.random() * 100).toFixed(2),
    treble: (Math.random() * 100).toFixed(2),
    overall: (Math.random() * 100).toFixed(2)
  };

  res.json({
    success: true,
    streamId,
    spectrum,
    analyzed: true,
    timestamp: new Date().toISOString()
  });
});

// Get stream status
app.get('/api/audio/stream/:streamId', (req, res) => {
  const stream = audioStreams.get(parseInt(req.params.streamId));
  
  if (!stream) {
    return res.status(404).json({ error: 'Stream not found' });
  }

  res.json({
    success: true,
    stream,
    elapsedTime: Date.now() - stream.createdAt
  });
});

// List all active streams
app.get('/api/audio/streams', (req, res) => {
  const streams = Array.from(audioStreams.values());
  
  res.json({
    success: true,
    totalStreams: streams.length,
    activeStreams: streams.filter(s => s.status === 'active').length,
    streams
  });
});

// Close stream
app.post('/api/audio/stream/:streamId/close', (req, res) => {
  const streamId = parseInt(req.params.streamId);
  const stream = audioStreams.get(streamId);
  
  if (!stream) {
    return res.status(404).json({ error: 'Stream not found' });
  }

  stream.status = 'closed';
  
  res.json({
    success: true,
    message: 'Stream closed',
    streamData: stream
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'audio-streaming',
    activeStreams: audioStreams.size,
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// Audio processing UI
app.get('/audio-lab', (req, res) => {
  const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Audio Lab | NetworkBuster</title>
    <style>
        :root {
            --bg: #050505;
            --panel: rgba(20, 20, 25, 0.8);
            --neon-blue: #00d4ff;
            --neon-purple: #bc13fe;
            --text: #e0e0e0;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body { background: var(--bg); color: var(--text); padding: 20px; min-height: 100vh; }
        .glass { background: var(--panel); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 25px; }
        .header { margin-bottom: 30px; text-align: center; }
        h1 { color: var(--neon-blue); text-transform: uppercase; letter-spacing: 4px; text-shadow: 0 0 10px var(--neon-blue); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card-title { font-size: 0.9rem; color: var(--neon-purple); text-transform: uppercase; margin-bottom: 20px; border-bottom: 1px solid rgba(188, 19, 254, 0.3); padding-bottom: 10px; }
        .btn { background: transparent; border: 1px solid var(--neon-blue); color: var(--neon-blue); padding: 12px; width: 100%; border-radius: 6px; cursor: pointer; transition: 0.3s; margin-top: 10px; font-weight: 600; }
        .btn:hover { background: var(--neon-blue); color: #000; box-shadow: 0 0 15px var(--neon-blue); }
        .input { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #fff; padding: 10px; width: 100%; border-radius: 6px; margin-bottom: 15px; }
        .visualizer { height: 150px; display: flex; align-items: flex-end; gap: 3px; background: #000; padding: 10px; border-radius: 8px; border: 1px solid #222; }
        .bar { flex: 1; background: var(--neon-blue); min-height: 2px; }
        .status { font-family: monospace; font-size: 0.8rem; color: #888; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎵 AI AUDIO LAB</h1>
        <div style="margin-top: 10px;">
            <a href="http://localhost:3000" style="color: var(--neon-purple); text-decoration: none; font-size: 0.7rem; font-weight: 800; border: 1px solid var(--neon-purple); padding: 5px 15px; border-radius: 4px; transition: 0.3s;">➔ RETURN_TO_MANAGER</a>
        </div>
    </div>
    <div class="grid">
        <div class="glass">
            <div class="card-title">Stream Engine</div>
            <button class="btn" onclick="createStream()">INIT_SESSION</button>
            <div id="streamStatus" class="status">IDLE_STANDBY</div>
            <div class="visualizer" id="viz"></div>
        </div>
        <div class="glass">
            <div class="card-title">Synthesizer (Hz)</div>
            <input type="number" id="freq" class="input" value="440">
            <select id="wave" class="input">
                <option>sine</option><option>square</option><option>sawtooth</option>
            </select>
            <button class="btn" onclick="synth()">EXEC_SYNTH</button>
        </div>
        <div class="glass">
            <div class="card-title">Spectrum Analysis</div>
            <button class="btn" onclick="detect()">DETECT_FREQ</button>
            <div id="results" class="status" style="white-space: pre;">TELEMETRY_READY</div>
        </div>
    </div>
    <script>
        function createStream() {
            fetch('/api/audio/stream/create', {method:'POST'})
                .then(r=>r.json()).then(d=>{
                    document.getElementById('streamStatus').innerHTML = '<span style="color:var(--neon-blue)">SESSION_ACTIVE: '+d.streamId+'</span>';
                    startViz();
                });
        }
        function synth() {
            fetch('/api/audio/synthesize', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({frequency: document.getElementById('freq').value, duration: 1000, waveform: document.getElementById('wave').value})
            }).then(r=>r.json()).then(d=>document.getElementById('results').textContent = 'SYNTH_OK: ' + d.message);
        }
        function startViz() {
            const viz = document.getElementById('viz');
            viz.innerHTML = '';
            for(let i=0; i<40; i++) {
                const b = document.createElement('div');
                b.className = 'bar';
                viz.appendChild(b);
            }
            setInterval(() => {
                document.querySelectorAll('.bar').forEach(b => {
                    const h = Math.random() * 100;
                    b.style.height = h + '%';
                    b.style.background = h > 70 ? 'var(--neon-purple)' : 'var(--neon-blue)';
                });
            }, 100);
        }
        function detect() {
            fetch('/api/audio/detect-frequency', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({audioBuffer: [0]})
            }).then(r=>r.json()).then(d=>document.getElementById('results').textContent = 'DOMINANT: ' + d.dominantFrequency + 'Hz\\nCONF: ' + d.confidence);
        }
    </script>
</body>
</html>`;
  res.send(htmlContent);
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Audio endpoint not found' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n🎵 ${SERVICE_NAME} running at http://localhost:${PORT}`);
  console.log(`⚡ Features:`);
  if (compression) console.log(`   ✓ Compression enabled`);
  if (helmet) console.log(`   ✓ Security headers enabled`);
  console.log(`   ✓ Audio streaming: /api/audio/stream/*`);
  console.log(`   ✓ Frequency synthesis: /api/audio/synthesize`);
  console.log(`   ✓ Real-time analysis: /api/audio/detect-frequency`);
  console.log(`   ✓ Audio Lab UI: /audio-lab\n`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down Audio Server...');
  server.close(() => {
    console.log('Audio Server closed');
    process.exit(0);
  });
});
