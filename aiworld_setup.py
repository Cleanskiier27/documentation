from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"

DEFAULTS = {
    "APP_NAME": "AI World - NetworkBuster",
    "AIWORLD_HOST": "http://localhost",
    "SATGPU_API_PORT": "8000",
    "SATGPU_WEB_PORT": "3000",
    "SATGPU_WORKER_PORT": "9000",
    "SATELLITE_MAP_PORT": "8100",
    "SATELLITE_VIEW_PORT": "8101",
    "ANALYTICS_PORT": "8200",
    "TELEMETRY_PORT": "8300",
    "UNIVERSAL_API_BASE_URL": "http://localhost",
    "UNIVERSAL_API_PORT": "8080",
    "WIFI7_MESH_MODE": "overlay",
    "WIFI7_MESH_INTERFACE": "mesh0",
    "WIFI7_MESH_SSID": "AI-World-Mesh",
    "WIFI7_MESH_CHANNEL": "6",
}


def load_env_file(path: Path) -> dict[str, str]:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env


def resolve_config() -> dict[str, str]:
    env = load_env_file(ENV_PATH)
    config = {**DEFAULTS, **env}
    host = config.get("AIWORLD_HOST") or config.get("SATGPU_HOST") or "http://localhost"
    config["HOST_BASE"] = host.rstrip("/")
    config["API_URL"] = f"{config['HOST_BASE']}:{config['SATGPU_API_PORT']}"
    config["WEB_URL"] = f"{config['HOST_BASE']}:{config['SATGPU_WEB_PORT']}"
    config["MESH_URL"] = f"{config['HOST_BASE']}:{config['SATGPU_WORKER_PORT']}"
    config["MAP_URL"] = f"{config['HOST_BASE']}:{config['SATELLITE_MAP_PORT']}"
    config["SATELLITE_URL"] = f"{config['HOST_BASE']}:{config['SATELLITE_VIEW_PORT']}"
    config["ANALYTICS_URL"] = f"{config['HOST_BASE']}:{config['ANALYTICS_PORT']}"
    config["TELEMETRY_URL"] = f"{config['HOST_BASE']}:{config['TELEMETRY_PORT']}"
    config["UNIVERSAL_API_URL"] = f"{config['UNIVERSAL_API_BASE_URL'].rstrip('/')}:{config['UNIVERSAL_API_PORT']}"
    return config


def main() -> None:
    config = resolve_config()
    print("AI World - NetworkBuster configuration")
    print(json.dumps({
        "APP_NAME": config["APP_NAME"],
        "HOST": config["HOST_BASE"],
        "endpoints": {
            "api": config["API_URL"],
            "web": config["WEB_URL"],
            "mesh": config["MESH_URL"],
            "map": config["MAP_URL"],
            "satellite": config["SATELLITE_URL"],
            "analytics": config["ANALYTICS_URL"],
            "telemetry": config["TELEMETRY_URL"],
            "universal_api": config["UNIVERSAL_API_URL"],
        },
        "wifi7": {
            "mode": config["WIFI7_MESH_MODE"],
            "interface": config["WIFI7_MESH_INTERFACE"],
            "ssid": config["WIFI7_MESH_SSID"],
            "channel": config["WIFI7_MESH_CHANNEL"],
        },
    }, indent=2))


if __name__ == "__main__":
    main()
