$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\porty-manager.ps1"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$config = Get-PortyConfig
$originUrl = if ([string]::IsNullOrWhiteSpace($env:MAIN_ORIGIN_URL)) { $config.MainOriginUrl } else { $env:MAIN_ORIGIN_URL.TrimEnd('/') }
$nasaUrl = if ([string]::IsNullOrWhiteSpace($env:NASA_PORTAL_URL)) { $config.NASAUrl } else { $env:NASA_PORTAL_URL.TrimEnd('/') }
$publicUrl = if ([string]::IsNullOrWhiteSpace($env:PUBLIC_PORTAL_URL)) { $config.PublicUrl } else { $env:PUBLIC_PORTAL_URL.TrimEnd('/') }
$universalUrl = if ([string]::IsNullOrWhiteSpace($env:UNIVERSAL_API_BASE_URL)) { $config.UniversalApiUrl } else { "$($env:UNIVERSAL_API_BASE_URL.TrimEnd('/')):$($env:UNIVERSAL_API_PORT)" }

Write-Host 'Configuring the user-led origin launch structure with Porty...' -ForegroundColor Cyan
Write-Host "Main origin: $originUrl" -ForegroundColor Green
Write-Host "NASA portal: $nasaUrl" -ForegroundColor Yellow
Write-Host "Public portal: $publicUrl" -ForegroundColor Yellow

$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
$node = Get-Command node -ErrorAction SilentlyContinue
$dotnet = Get-Command dotnet -ErrorAction SilentlyContinue

if ($dotnet) {
    Write-Host 'Detected .NET SDK; C# startup is available.' -ForegroundColor Green
}
else {
    Write-Warning 'No .NET SDK was found in PATH. The project will continue using the Python landing page and browser fallback.'
}

if ($python) {
    Write-Host 'Starting the AI World landing page with Python...' -ForegroundColor Cyan
    $pythonPath = $python.Source
    $psArgs = @('-NoLogo', '-NoProfile', '-Command', "Set-Location '$root'; & '$pythonPath' .\serve_aiworld.py")
    Start-Process powershell.exe -ArgumentList $psArgs | Out-Null
}
elseif ($node) {
    Write-Host 'Starting the AI World landing page with Node.js...' -ForegroundColor Cyan
    Start-Process node -ArgumentList @('.\serve_aiworld.py') | Out-Null
}
else {
    Write-Host 'No Python or Node runtime detected; opening the HTML files directly.' -ForegroundColor Yellow
}

try {
    Start-Process $originUrl
    Write-Host 'Main origin page opened.' -ForegroundColor Green
}
catch {
    Write-Warning "Unable to open the main origin automatically. Use this URL manually: $originUrl"
}

Write-Host "Universal API: $universalUrl" -ForegroundColor Yellow
Write-Host 'Available project paths:' -ForegroundColor Cyan
Write-Host "  Origin: $originUrl"
Write-Host "  NASA: $nasaUrl"
Write-Host "  Public: $publicUrl"
