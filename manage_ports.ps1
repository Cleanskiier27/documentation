#Requires -RunAsAdministrator

<#
.SYNOPSIS
    NetworkBuster Port Management Utility
.DESCRIPTION
    Allows manual control over opening and closing firewall ports for the suite.
#>

$ports = @(3000, 3001, 3002, 5000, 6000, 7000, 8000, 9000)

function Open-Ports {
    Write-Host "`n🔓 Opening all NetworkBuster ports..." -ForegroundColor Green
    foreach ($port in $ports) {
        $ruleName = "NetworkBuster_Port_$port"
        if (!(Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -DisplayName "NetworkBuster Port $port" -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow -Name $ruleName | Out-Null
            Write-Host "   ✅ Port $port opened" -ForegroundColor Green
        } else {
            Write-Host "   ℹ️  Port $port is already open" -ForegroundColor Cyan
        }
    }
}

function Close-Ports {
    Write-Host "`n🔒 Closing all NetworkBuster ports..." -ForegroundColor Red
    foreach ($port in $ports) {
        $ruleName = "NetworkBuster_Port_$port"
        if (Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue) {
            Remove-NetFirewallRule -Name $ruleName
            Write-Host "   🛑 Port $port closed" -ForegroundColor Yellow
        } else {
            Write-Host "   ℹ️  Port $port is already closed" -ForegroundColor Gray
        }
    }
}

if ($args.Count -eq 0) {
    Write-Host "`nNetworkBuster Port Manager" -ForegroundColor Cyan
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  .\manage_ports.ps1 -open   (Open all ports)"
    Write-Host "  .\manage_ports.ps1 -close  (Close all ports)"
    exit
}

if ($args[0] -eq "-open") { Open-Ports }
elseif ($args[0] -eq "-close") { Close-Ports }
else { Write-Host "Invalid argument. Use -open or -close." -ForegroundColor Red }
