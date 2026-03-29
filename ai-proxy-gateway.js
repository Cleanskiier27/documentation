/**
 * AI Proxy Gateway - Standalone gateway server for AI inference requests
 * Routes requests from devices to multiple AI providers with authentication,
 * rate limiting, caching, and usage tracking.
 * 
 * Run: node ai-proxy-gateway.js
 * Port: AI_GATEWAY_PORT (default: 3002)
 */

import express from 'express';
import crypto from 'crypto';

// Dynamic import for aiProviders and device store
const aiProviders = await import('./lib/aiProviders.js').then(m => m.default);
let deviceStore;
try {
    deviceStore = await import('./lib/deviceStore.js');
} catch {
    deviceStore = {
        getRegistration: () => null,
        saveRegistration: () => null
    };
}

const app = express();
const PORT = parseInt(process.env.AI_GATEWAY_PORT || '3002');

// Request logging
const requestLog = [];
const MAX_LOG_ENTRIES = 1000;

function logRequest(req, status, duration, provider = null) {
    const entry = {
        id: crypto.randomUUID?.() || crypto.randomBytes(8).toString('hex'),
        timestamp: new Date().toISOString(),
        method: req.method,
        path: req.path,
        deviceId: req.deviceId || 'unknown',
        provider,
        status,
        duration,
        ip: req.ip || req.connection?.remoteAddress
    };

    requestLog.unshift(entry);
    if (requestLog.length > MAX_LOG_ENTRIES) requestLog.pop();

    console.log(`[${entry.timestamp}] ${entry.method} ${entry.path} -> ${status} (${duration}ms) device:${entry.deviceId}`);
}

// Middleware
app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

// CORS for all origins (devices may come from anywhere)
app.use((req, res, next) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Device-Id, X-API-Key');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        return res.end();
    }
    next();
});

// Request timing
app.use((req, res, next) => {
    req.startTime = Date.now();
    next();
});

// Device authentication middleware
function authenticateDevice(req, res, next) {
    const deviceId = req.headers['x-device-id'] || req.query.deviceId;
    const apiKey = req.headers['x-api-key'] || req.headers['authorization']?.replace('Bearer ', '');

    // API key authentication
    if (apiKey && (apiKey === process.env.AI_API_KEY || apiKey === process.env.ADMIN_KEY)) {
        req.deviceId = 'api-key-user';
        req.authenticated = true;
        req.isAdmin = apiKey === process.env.ADMIN_KEY;
        return next();
    }

    // Device ID authentication
    if (deviceId) {
        const device = deviceStore.getRegistration?.(deviceId);
        if (device) {
            req.deviceId = deviceId;
            req.device = device;
            req.authenticated = true;
            return next();
        }
        // Allow unregistered device IDs if configured
        if (process.env.AI_ALLOW_UNREGISTERED === 'true') {
            req.deviceId = deviceId;
            req.authenticated = false;
            return next();
        }
    }

    // Anonymous access
    if (process.env.AI_ALLOW_ANONYMOUS === 'true') {
        req.deviceId = 'anon-' + crypto.randomBytes(4).toString('hex');
        req.authenticated = false;
        return next();
    }

    const duration = Date.now() - req.startTime;
    logRequest(req, 401, duration);
    return res.status(401).json({
        error: 'Authentication required',
        hint: 'Provide X-Device-Id or X-API-Key header'
    });
}

// Rate limit headers
function addRateLimitHeaders(req, res) {
    if (req.deviceId) {
        const info = aiProviders.checkRateLimit(req.deviceId);
        res.setHeader('X-RateLimit-Limit', process.env.AI_RATE_LIMIT_PER_MINUTE || '60');
        res.setHeader('X-RateLimit-Remaining', info.remaining);
        res.setHeader('X-RateLimit-Reset', info.resetIn);
    }
}

// ============ ROUTES ============

// Health check (no auth required)
app.get('/health', (req, res) => {
    const providers = aiProviders.getAvailableProviders();
    res.json({
        status: 'healthy',
        service: 'ai-proxy-gateway',
        port: PORT,
        providers: providers.length,
        defaultProvider: aiProviders.getDefaultProvider(),
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

// List providers (no auth required)
app.get('/providers', (req, res) => {
    res.json({
        providers: aiProviders.getAvailableProviders(),
        default: aiProviders.getDefaultProvider()
    });
});

// Chat completion
app.post('/chat', authenticateDevice, async (req, res) => {
    const startTime = Date.now();

    try {
        addRateLimitHeaders(req, res);

        const {
            provider = aiProviders.getDefaultProvider(),
            messages,
            model,
            maxTokens,
            temperature,
            useCache = true,
            stream = false
        } = req.body;

        if (!messages || !Array.isArray(messages)) {
            logRequest(req, 400, Date.now() - startTime, provider);
            return res.status(400).json({ error: 'messages array required' });
        }

        if (!provider) {
            logRequest(req, 503, Date.now() - startTime);
            return res.status(503).json({ error: 'No AI providers configured' });
        }

        const result = await aiProviders.chat(provider, messages, {
            model,
            maxTokens,
            temperature,
            deviceId: req.deviceId,
            useCache,
            stream
        });

        if (stream && result instanceof ReadableStream) {
            res.setHeader('Content-Type', 'text/event-stream');
            res.setHeader('Cache-Control', 'no-cache');
            res.setHeader('Connection', 'keep-alive');

            const reader = result.getReader();
            const decoder = new TextDecoder();

            try {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    res.write(value);
                }
            } catch (err) {
                console.error('Streaming error:', err);
            } finally {
                res.end();
                logRequest(req, 200, Date.now() - startTime, provider + ' (streamed)');
            }
            return;
        }

        const tokens = result.usage?.total_tokens || 0;
        aiProviders.trackUsage(req.deviceId, provider, 'chat', tokens);

        logRequest(req, 200, Date.now() - startTime, provider);
        res.json({ success: true, ...result });

    } catch (err) {
        const status = err.message.includes('Rate limit') ? 429 : 500;
        logRequest(req, status, Date.now() - startTime);
        res.status(status).json({ error: err.message });
    }
});

// Embeddings
app.post('/embed', authenticateDevice, async (req, res) => {
    const startTime = Date.now();

    try {
        addRateLimitHeaders(req, res);

        const {
            provider = aiProviders.getDefaultProvider(),
            text,
            model
        } = req.body;

        if (!text) {
            logRequest(req, 400, Date.now() - startTime, provider);
            return res.status(400).json({ error: 'text required' });
        }

        const result = await aiProviders.embed(provider, text, {
            model,
            deviceId: req.deviceId
        });

        aiProviders.trackUsage(req.deviceId, provider, 'embed', result.usage?.total_tokens || 0);

        logRequest(req, 200, Date.now() - startTime, provider);
        res.json({ success: true, ...result });

    } catch (err) {
        const status = err.message.includes('Rate limit') ? 429 :
            err.message.includes('does not support') ? 400 : 500;
        logRequest(req, status, Date.now() - startTime);
        res.status(status).json({ error: err.message });
    }
});

// Image generation
app.post('/image', authenticateDevice, async (req, res) => {
    const startTime = Date.now();

    try {
        addRateLimitHeaders(req, res);

        const {
            provider = 'openai',
            prompt,
            model,
            size,
            quality,
            n
        } = req.body;

        if (!prompt) {
            logRequest(req, 400, Date.now() - startTime, provider);
            return res.status(400).json({ error: 'prompt required' });
        }

        const result = await aiProviders.generateImage(provider, prompt, {
            model,
            size,
            quality,
            n,
            deviceId: req.deviceId
        });

        aiProviders.trackUsage(req.deviceId, provider, 'image', 0);

        logRequest(req, 200, Date.now() - startTime, provider);
        res.json({ success: true, ...result });

    } catch (err) {
        const status = err.message.includes('Rate limit') ? 429 :
            err.message.includes('does not support') ? 400 : 500;
        logRequest(req, status, Date.now() - startTime);
        res.status(status).json({ error: err.message });
    }
});

// Device usage
app.get('/usage', authenticateDevice, (req, res) => {
    addRateLimitHeaders(req, res);
    const usage = aiProviders.getDeviceUsage(req.deviceId);
    const rateInfo = aiProviders.checkRateLimit(req.deviceId);

    res.json({
        deviceId: req.deviceId,
        usage,
        rateLimit: {
            limit: parseInt(process.env.AI_RATE_LIMIT_PER_MINUTE || '60'),
            remaining: rateInfo.remaining,
            resetIn: rateInfo.resetIn
        }
    });
});

// Admin: reset usage
app.post('/usage/reset', authenticateDevice, (req, res) => {
    if (!req.isAdmin) {
        return res.status(403).json({ error: 'Admin access required' });
    }

    const result = aiProviders.resetUsage();
    res.json(result);
});

// Admin: all usage
app.get('/usage/all', authenticateDevice, (req, res) => {
    if (!req.isAdmin) {
        return res.status(403).json({ error: 'Admin access required' });
    }

    res.json({
        usage: aiProviders.getAllUsage(),
        timestamp: new Date().toISOString()
    });
});

// Admin: request logs
app.get('/logs', authenticateDevice, (req, res) => {
    if (!req.isAdmin) {
        return res.status(403).json({ error: 'Admin access required' });
    }

    const limit = parseInt(req.query.limit || '100');
    res.json({
        logs: requestLog.slice(0, limit),
        total: requestLog.length
    });
});

// Gateway status
app.get('/status', (req, res) => {
    const providers = aiProviders.getAvailableProviders();
    const allUsage = aiProviders.getAllUsage();

    let totalRequests = 0;
    let totalTokens = 0;
    for (const usage of Object.values(allUsage)) {
        totalRequests += usage.requests || 0;
        totalTokens += usage.tokens || 0;
    }

    res.json({
        gateway: {
            status: 'running',
            port: PORT,
            uptime: Math.floor(process.uptime()),
            memory: Math.round(process.memoryUsage().heapUsed / 1024 / 1024) + 'MB'
        },
        providers: {
            available: providers.length,
            default: aiProviders.getDefaultProvider(),
            list: providers.map(p => ({ id: p.id, name: p.name, capabilities: p.capabilities }))
        },
        stats: {
            activeDevices: Object.keys(allUsage).length,
            totalRequests,
            totalTokens,
            recentLogs: requestLog.length
        },
        config: {
            rateLimitPerMinute: parseInt(process.env.AI_RATE_LIMIT_PER_MINUTE || '60'),
            cacheTTL: parseInt(process.env.AI_CACHE_TTL_SECONDS || '300'),
            allowAnonymous: process.env.AI_ALLOW_ANONYMOUS === 'true',
            allowUnregistered: process.env.AI_ALLOW_UNREGISTERED === 'true'
        },
        timestamp: new Date().toISOString()
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not found',
        endpoints: [
            'GET  /health',
            'GET  /providers',
            'GET  /status',
            'POST /chat',
            'POST /embed',
            'POST /image',
            'GET  /usage',
            'GET  /usage/all (admin)',
            'GET  /logs (admin)'
        ]
    });
});

// Error handler
app.use((err, req, res, next) => {
    console.error('Gateway error:', err);
    res.status(500).json({ error: 'Internal gateway error' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║             🤖 AI Proxy Gateway Started                  ║
╠══════════════════════════════════════════════════════════╣
║  Port:      ${String(PORT).padEnd(44)}║
║  Health:    http://localhost:${PORT}/health${' '.repeat(24 - String(PORT).length)}║
║  Status:    http://localhost:${PORT}/status${' '.repeat(24 - String(PORT).length)}║
╠══════════════════════════════════════════════════════════╣
║  Providers Available:                                    ║`);

    const providers = aiProviders.getAvailableProviders();
    for (const p of providers) {
        const caps = Object.entries(p.capabilities)
            .filter(([, v]) => v)
            .map(([k]) => k)
            .join(', ');
        console.log(`║    ✓ ${p.name.padEnd(20)} (${caps})`.padEnd(59) + '║');
    }

    if (providers.length === 0) {
        console.log('║    ⚠ No providers configured - set API keys              ║');
    }

    console.log(`╠══════════════════════════════════════════════════════════╣
║  Rate Limit:  ${(process.env.AI_RATE_LIMIT_PER_MINUTE || '60') + '/min'.padEnd(42)}║
║  Cache TTL:   ${(process.env.AI_CACHE_TTL_SECONDS || '300') + 's'.padEnd(43)}║
╚══════════════════════════════════════════════════════════╝
`);
});

export default app;
