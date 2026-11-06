# AI World - NetworkBuster local setup

This workspace includes a PowerShell-friendly localhost configuration for the AI World NetworkBuster stack, with a universal API gateway, a satellite map layer, and a Wi‑Fi 7 mesh overlay profile.

## Project identity and access model

- Main committer and project origin: the user / primary operator
- Dedicated mission domain: NASA operations and institutional overlays
- Public-facing access: general public landing page and overview portal
- Main origin entry: the landing page and manager flow remain the default operational gateway

## Default endpoint values

- AI API: http://localhost:8000
- AI Web: http://localhost:3000
- Mesh overlay: http://localhost:9000
- Satellite map: http://localhost:8100
- Satellite view: http://localhost:8101
- Analytics: http://localhost:8200
- Telemetry: http://localhost:8300
- Universal API: http://localhost:8080

These values are set in the `.env` file and are used when the environment variables are not already defined.

## Docker CLI commands

```powershell
docker compose --env-file .\.env up -d --remove-orphans
Start-Process "http://localhost:8080"
```

## Start the stack

```powershell
powershell -ExecutionPolicy Bypass -File .\start-satgpu.ps1
```

## Open universal API link

```powershell
powershell -ExecutionPolicy Bypass -File .\open-universal-api.ps1
```

## Stop the stack

```powershell
powershell -ExecutionPolicy Bypass -File .\stop-satgpu.ps1
```

## Override the default ports or host

```powershell
$env:AIWORLD_HOST = 'http://localhost'
$env:SATGPU_API_PORT = '8001'
$env:SATGPU_WEB_PORT = '3001'
$env:SATGPU_WORKER_PORT = '9001'
$env:SATELLITE_MAP_PORT = '8102'
$env:SATELLITE_VIEW_PORT = '8103'
$env:ANALYTICS_PORT = '8201'
$env:TELEMETRY_PORT = '8301'
$env:UNIVERSAL_API_BASE_URL = 'http://localhost'
$env:UNIVERSAL_API_PORT = '8081'
$env:WIFI7_MESH_MODE = 'overlay'
$env:WIFI7_MESH_INTERFACE = 'mesh0'
.\start-satgpu.ps1
```
