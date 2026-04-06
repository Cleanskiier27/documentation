/**
 * Wheel Orbit Backend Simulation Server
 *
 * Exposes endpoints for simulating orbital motion of a wheel over time.
 *
 * Endpoints:
 *   GET /api/orbit/health          → basic ok status
 *   GET /api/orbit/position?t=<s>  → (x, y) position on unit circle at time t (seconds)
 *
 * Orbit model: simple circular orbit with configurable radius and angular velocity.
 *   x(t) = radius * cos(omega * t + phase)
 *   y(t) = radius * sin(omega * t + phase)
 *
 * Default orbit parameters:
 *   radius  = 1.0   (arbitrary units)
 *   omega   = 2π/10 (one full revolution per 10 seconds)
 *   phase   = 0     (radians)
 */

import express from 'express';

const app = express();

// Orbit parameters (can be overridden via env vars for flexibility)
const ORBIT_RADIUS = parseFloat(process.env.ORBIT_RADIUS ?? '1.0');
const ORBIT_PERIOD = parseFloat(process.env.ORBIT_PERIOD ?? '10.0'); // seconds per revolution
const ORBIT_PHASE = parseFloat(process.env.ORBIT_PHASE ?? '0.0');   // initial phase offset (radians)
const OMEGA = (2 * Math.PI) / ORBIT_PERIOD;

const PORT = parseInt(process.env.PORT ?? '3001', 10);

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------
app.use((req, _res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
  next();
});

// ---------------------------------------------------------------------------
// GET /api/orbit/health
// ---------------------------------------------------------------------------
app.get('/api/orbit/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'wheel-orbit-simulation',
    timestamp: new Date().toISOString(),
  });
});

// ---------------------------------------------------------------------------
// GET /api/orbit/position?t=<seconds>
// ---------------------------------------------------------------------------
app.get('/api/orbit/position', (req, res) => {
  const rawT = req.query.t;

  if (rawT === undefined || rawT === '') {
    return res.status(400).json({
      error: 'Missing required query parameter: t (time in seconds)',
    });
  }

  const t = parseFloat(rawT);

  if (!Number.isFinite(t)) {
    return res.status(400).json({
      error: `Invalid value for t: "${rawT}". Must be a finite number.`,
    });
  }

  const angle = OMEGA * t + ORBIT_PHASE;
  const x = ORBIT_RADIUS * Math.cos(angle);
  const y = ORBIT_RADIUS * Math.sin(angle);

  return res.json({
    t,
    angle_rad: angle,
    x,
    y,
    radius: ORBIT_RADIUS,
    period: ORBIT_PERIOD,
  });
});

// ---------------------------------------------------------------------------
// 404 fallback
// ---------------------------------------------------------------------------
app.use((_req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

// ---------------------------------------------------------------------------
// Start server (skipped when imported as a module for testing)
// ---------------------------------------------------------------------------
export { app };

if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`Wheel orbit simulation server running on http://localhost:${PORT}`);
    console.log(`  Health:   GET http://localhost:${PORT}/api/orbit/health`);
    console.log(`  Position: GET http://localhost:${PORT}/api/orbit/position?t=<seconds>`);
  });
}
