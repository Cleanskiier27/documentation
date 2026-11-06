$ErrorActionPreference = 'Stop'

$baseUrl = if ([string]::IsNullOrWhiteSpace($env:UNIVERSAL_API_BASE_URL)) { 'http://localhost' } else { $env:UNIVERSAL_API_BASE_URL.TrimEnd('/') }
$port = if ([string]::IsNullOrWhiteSpace($env:UNIVERSAL_API_PORT)) { '8080' } else { $env:UNIVERSAL_API_PORT }
$url = "$baseUrl:$port"

Write-Host "Opening AI World universal API: $url" -ForegroundColor Cyan

try {
    Start-Process $url
    Write-Host 'Browser launched successfully.' -ForegroundColor Green
}
catch {
    Write-Warning "Could not open the browser automatically. Use this URL manually: $url"
}
