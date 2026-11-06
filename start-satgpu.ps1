$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\satgpu.config.ps1"

$config = Get-SatGpuConfig

$env:APP_NAME = $config.AppName
$env:AIWORLD_HOST = $config.Host
$env:SATGPU_HOST = $config.Host
$env:SATGPU_API_PORT = $config.ApiPort
$env:SATGPU_WEB_PORT = $config.WebPort
$env:SATGPU_WORKER_PORT = $config.WorkerPort
$env:SATELLITE_MAP_PORT = $config.MapPort
$env:SATELLITE_VIEW_PORT = $config.SatellitePort
$env:ANALYTICS_PORT = $config.AnalyticsPort
$env:TELEMETRY_PORT = $config.TelemetryPort
$env:UNIVERSAL_API_BASE_URL = $config.UniversalApiBaseUrl
$env:UNIVERSAL_API_PORT = $config.UniversalApiPort
$env:WIFI7_MESH_MODE = $config.Wifi7MeshMode
$env:WIFI7_MESH_INTERFACE = $config.Wifi7MeshInterface

Write-Host 'AI World - NetworkBuster localhost endpoints:' -ForegroundColor Cyan
foreach ($endpoint in $config.Endpoints) {
    Write-Host ("  {0}: {1}" -f $endpoint.Name, $endpoint.Url) -ForegroundColor Green
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Warning 'Docker is not installed or not on PATH. The AI World mesh overlay and service endpoints are configured for localhost use, but Docker startup was skipped.'
    return
}

Write-Host 'Starting AI World services with Docker Compose...' -ForegroundColor Cyan

docker compose --env-file "$PSScriptRoot\.env" up -d --remove-orphans

foreach ($endpoint in $config.Endpoints) {
    $uri = [Uri]$endpoint.Url
    $ready = $false

    for ($attempt = 1; $attempt -le 20; $attempt++) {
        try {
            Invoke-WebRequest -Uri $uri -Method Get -UseBasicParsing -TimeoutSec 5 | Out-Null
            $ready = $true
            break
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    if ($ready) {
        Write-Host ("Endpoint ready: {0}" -f $endpoint.Url) -ForegroundColor Green
    }
    else {
        Write-Warning ("Endpoint did not respond in time: {0}" -f $endpoint.Url)
    }
}
