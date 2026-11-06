$ErrorActionPreference = 'Stop'

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Warning 'Docker is not installed or not on PATH. Nothing to stop.'
    return
}

Write-Host 'Stopping SatGPU Docker services...' -ForegroundColor Cyan

docker compose --env-file "$PSScriptRoot\.env" down --remove-orphans
