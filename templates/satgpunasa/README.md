# satgpunasa — Orbit Simulation Server Template

A self-contained Node/Express orbit simulation server. Based on the `deep-lunar-tracking/orbit-sim` layout.

> **Port:** Default **3003** — intentionally avoids port 3000.

## Directory structure

```
templates/satgpunasa/
├── server.js       # Express server (ESM, default port 3003)
├── package.json    # Local dependencies ("type": "module")
├── README.md       # This file
└── public/
    └── index.html  # Minimal HTML landing page
```

## Quick start

```bash
cd templates/satgpunasa
npm install
npm start
```

The server starts on **http://localhost:3003** by default.

Override the port with the `PORT` environment variable:

```bash
PORT=4000 npm start
```

## API

### `GET /api/orbit/health`

Returns service status.

**Example**

```bash
curl http://localhost:3003/api/orbit/health
```

**Response**

```json
{
  "status": "ok",
  "service": "satgpunasa-orbit-sim",
  "timestamp": "2026-04-06T20:00:00.000Z"
}
```

---

### `GET /api/orbit/position?t=<seconds>`

Returns the orbital position and velocity of the spacecraft at elapsed time `t` seconds.

**Query parameters**

| Parameter | Type   | Required | Description                   |
|-----------|--------|----------|-------------------------------|
| `t`       | number | ✅        | Elapsed time in seconds (≥ 0)|

**Example**

```bash
curl "http://localhost:3003/api/orbit/position?t=0"
curl "http://localhost:3003/api/orbit/position?t=3600"
```

**Response**

```json
{
  "t": 0,
  "theta_rad": 0,
  "position": { "x": 1837400, "y": 0, "z": 0 },
  "velocity": { "vx": 0, "vy": 1633, "vz": 0 },
  "orbital_radius_m": 1837400,
  "orbital_period_s": 7082.5,
  "units": {
    "position": "metres (Moon-centred)",
    "velocity": "m/s",
    "theta": "radians"
  }
}
```

**Coordinate system**

- **x** — points toward the ascending node at `t = 0`
- **y** — 90° ahead in the orbit direction
- **z** — normal to the orbital plane (lunar north)

**Orbital parameters**

| Parameter       | Value                |
|-----------------|----------------------|
| Lunar radius    | 1 737 400 m          |
| Orbit altitude  | 100 000 m (100 km)   |
| Orbital radius  | 1 837 400 m          |
| Orbital period  | ~7 082.5 s (~1.97 h) |
| Orbital speed   | ~1 633 m/s           |

**Error responses**

| Status | Reason                               |
|--------|--------------------------------------|
| `400`  | Missing `t` parameter                |
| `400`  | `t` is not a valid number            |

---

## Static UI

Open **http://localhost:3003** in a browser for a minimal HTML landing page with quick links to the endpoints.
