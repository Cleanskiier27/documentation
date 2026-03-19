#Requires -RunAsAdministrator

<#
.SYNOPSIS
    NetworkBuster Immersive Bootstrapper
.DESCRIPTION
    Launches the suite with a high-fidelity visual sequence on Windows startup.
#>

$InstallDir = $PSScriptRoot
Set-Location $InstallDir

# 1. Clear and Show Immersive Splash
Clear-Host
Write-Host "`n[ INITIALIZING IMMERSIVE BOOT SEQUENCE ]" -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" ".\networkbuster_ascii_art.py"
Start-Sleep -Seconds 3

# 2. Check and Open Ports
Write-Host "`n[ AUTHORIZING FIREWALL PROTOCOLS ]" -ForegroundColor Yellow
& ".\manage_ports.ps1" -open
Start-Sleep -Seconds 1

# 3. Launch Core Services in Background
Write-Host "`n[ BOOTING NETWORKBUSTER MODULES ]" -ForegroundColor Green
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "networkbuster_launcher.py --start" -WindowStyle Hidden

# 4. Final Handoff to Command Center
Write-Host "`n[ REDIRECTING TO UNIFIED COMMAND CENTER ]" -ForegroundColor Magenta
Start-Sleep -Seconds 10
Start-Process "http://localhost:3000"

Write-Host "`n✨ BOOT SEQUENCE COMPLETE. SYSTEM IS LIVE." -ForegroundColor Green
Start-Sleep -Seconds 2
