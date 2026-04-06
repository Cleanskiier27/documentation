/**
 * Tests for the Wheel Orbit Simulation Server
 *
 * Uses Node.js built-in test runner (node:test) + node:assert.
 * Run with:  node --test api/orbit-server.test.js
 */

import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';

process.env.NODE_ENV = 'test';

// Import after setting NODE_ENV so the server does not auto-start.
const { app } = await import('./orbit-server.js');

let server;
let baseUrl;

before(() => {
  server = http.createServer(app);
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      baseUrl = `http://127.0.0.1:${port}`;
      resolve();
    });
  });
});

after(() => {
  return new Promise((resolve, reject) => {
    server.close((err) => (err ? reject(err) : resolve()));
  });
});

/**
 * Helper: perform a GET request and return { status, body }.
 */
function get(path) {
  return new Promise((resolve, reject) => {
    http.get(`${baseUrl}${path}`, (res) => {
      let raw = '';
      res.on('data', (chunk) => { raw += chunk; });
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: JSON.parse(raw) });
        } catch {
          resolve({ status: res.statusCode, body: raw });
        }
      });
    }).on('error', reject);
  });
}

// ---------------------------------------------------------------------------
// Health endpoint
// ---------------------------------------------------------------------------
describe('GET /api/orbit/health', () => {
  it('returns 200 with status ok', async () => {
    const { status, body } = await get('/api/orbit/health');
    assert.equal(status, 200);
    assert.equal(body.status, 'ok');
    assert.equal(body.service, 'wheel-orbit-simulation');
    assert.ok(body.timestamp, 'timestamp should be present');
  });
});

// ---------------------------------------------------------------------------
// Position endpoint – valid inputs
// ---------------------------------------------------------------------------
describe('GET /api/orbit/position', () => {
  it('returns 200 with x, y, angle_rad and metadata for t=0', async () => {
    const { status, body } = await get('/api/orbit/position?t=0');
    assert.equal(status, 200);
    assert.equal(body.t, 0);
    // At t=0, angle = 0 → x = radius, y ≈ 0
    assert.ok(typeof body.x === 'number', 'x should be a number');
    assert.ok(typeof body.y === 'number', 'y should be a number');
    assert.ok(typeof body.angle_rad === 'number', 'angle_rad should be present');
    assert.ok(typeof body.radius === 'number', 'radius should be present');
    assert.ok(typeof body.period === 'number', 'period should be present');
    assert.ok(Math.abs(body.x - 1.0) < 1e-10, 'x at t=0 should equal radius (1.0)');
    assert.ok(Math.abs(body.y) < 1e-10, 'y at t=0 should be ~0');
  });

  it('returns correct position for t=period/4 (quarter revolution)', async () => {
    // Default period = 10 s → quarter at t=2.5 s → angle = π/2 → x≈0, y≈1
    const { status, body } = await get('/api/orbit/position?t=2.5');
    assert.equal(status, 200);
    assert.ok(Math.abs(body.x) < 1e-10, `x at t=2.5 should be ~0, got ${body.x}`);
    assert.ok(Math.abs(body.y - 1.0) < 1e-10, `y at t=2.5 should be ~1.0, got ${body.y}`);
  });

  it('returns correct position for a full revolution (t=period)', async () => {
    // At t = 10 s (one full period), x should equal 1, y ≈ 0 (same as t=0)
    const { status, body } = await get('/api/orbit/position?t=10');
    assert.equal(status, 200);
    assert.ok(Math.abs(body.x - 1.0) < 1e-10, `x at t=10 should be ~1.0, got ${body.x}`);
    assert.ok(Math.abs(body.y) < 1e-10, `y at t=10 should be ~0, got ${body.y}`);
  });

  it('accepts negative time values', async () => {
    const { status, body } = await get('/api/orbit/position?t=-5');
    assert.equal(status, 200);
    assert.equal(body.t, -5);
  });

  it('accepts decimal time values', async () => {
    const { status, body } = await get('/api/orbit/position?t=1.234');
    assert.equal(status, 200);
    assert.ok(Number.isFinite(body.x));
    assert.ok(Number.isFinite(body.y));
  });
});

// ---------------------------------------------------------------------------
// Position endpoint – invalid inputs
// ---------------------------------------------------------------------------
describe('GET /api/orbit/position – error cases', () => {
  it('returns 400 when t is missing', async () => {
    const { status, body } = await get('/api/orbit/position');
    assert.equal(status, 400);
    assert.ok(body.error, 'error message should be present');
  });

  it('returns 400 when t is not a number', async () => {
    const { status, body } = await get('/api/orbit/position?t=abc');
    assert.equal(status, 400);
    assert.ok(body.error, 'error message should be present');
  });

  it('returns 400 when t is empty string', async () => {
    const { status, body } = await get('/api/orbit/position?t=');
    assert.equal(status, 400);
    assert.ok(body.error, 'error message should be present');
  });
});

// ---------------------------------------------------------------------------
// 404 for unknown routes
// ---------------------------------------------------------------------------
describe('Unknown routes', () => {
  it('returns 404 for unrecognised paths', async () => {
    const { status } = await get('/api/orbit/unknown');
    assert.equal(status, 404);
  });
});
