import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const app = express();
// Default port is 3003 — intentionally avoids port 3000.
// Override via the PORT environment variable: PORT=4000 npm start
const PORT = process.env.PORT || 3003;

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Serve static files from public/
app.use(express.static(join(__dirname, 'public')));

/**
 * Orbit simulator constants.
 * Models a spacecraft in a circular low lunar orbit (LLO).
 *
 * Lunar radius:        1_737_400 m
 * Orbit altitude:        100_000 m  (100 km LLO)
 * Orbital radius:      1_837_400 m
 * Orbital speed:       ~1,633 m/s  (sqrt(GM_moon / r))
 * Orbital period:      ~7,082.5 s  (~1.97 h)
 */
const LUNAR_RADIUS_M = 1_737_400;
const ORBIT_ALTITUDE_M = 100_000;
const ORBITAL_RADIUS_M = LUNAR_RADIUS_M + ORBIT_ALTITUDE_M;
const ORBITAL_SPEED_MS = 1_633; // m/s — circular-orbit speed at 100 km LLO
const ORBITAL_PERIOD_S = (2 * Math.PI * ORBITAL_RADIUS_M) / ORBITAL_SPEED_MS;

/**
 * GET /api/orbit/health
 * Returns service status.
 */
app.get('/api/orbit/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'satgpunasa-orbit-sim',
    timestamp: new Date().toISOString(),
  });
});

/**
 * GET /api/orbit/position?t=<seconds>
 * Returns the orbital position of the spacecraft at time t (seconds).
 *
 * Coordinate system: Moon-centred, equatorial plane.
 *   x — points toward the ascending node at t=0
 *   y — 90° ahead in the orbit
 *   z — normal to orbital plane (north)
 *
 * Query params:
 *   t  {number}  Elapsed time in seconds (required)
 */
app.get('/api/orbit/position', (req, res) => {
  if (req.query.t === undefined || req.query.t === '') {
    return res.status(400).json({ error: 'Missing required query parameter: t' });
  }

  const t = parseFloat(req.query.t);

  if (Number.isNaN(t)) {
    return res.status(400).json({ error: 'Query parameter t must be a number' });
  }

  const theta = (2 * Math.PI * t) / ORBITAL_PERIOD_S; // radians
  const x = ORBITAL_RADIUS_M * Math.cos(theta);
  const y = ORBITAL_RADIUS_M * Math.sin(theta);
  const z = 0; // equatorial orbit

  const vx = -ORBITAL_SPEED_MS * Math.sin(theta);
  const vy = ORBITAL_SPEED_MS * Math.cos(theta);
  const vz = 0;

  res.json({
    t,
    theta_rad: theta,
    position: { x, y, z },
    velocity: { vx, vy, vz },
    orbital_radius_m: ORBITAL_RADIUS_M,
    orbital_period_s: ORBITAL_PERIOD_S,
    units: {
      position: 'metres (Moon-centred)',
      velocity: 'm/s',
      theta: 'radians',
    },
  });
});

app.listen(PORT, () => {
  console.log(`satgpunasa orbit-sim server running on http://localhost:${PORT}`);
  console.log(`  Health:   http://localhost:${PORT}/api/orbit/health`);
  console.log(`  Position: http://localhost:${PORT}/api/orbit/position?t=0`);
});
