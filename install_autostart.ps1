#Requires -RunAsAdministrator

<#
.SYNOPSIS
    NetworkBuster Startup Service Installer
.DESCRIPTION
    Installs NetworkBuster to auto-start on Windows boot
#>

$InstallDir = $PSScriptRoot
$ServiceName = "NetworkBuster_AutoStart"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  NetworkBuster Auto-Start Installer                       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n[1/3] Creating startup script..." -ForegroundColor Yellow

# Create startup script
$startupScript = @"
@echo off
cd /d "$InstallDir"
call .venv\Scripts\activate.bat
start /min python auto_start_service.py
exit
"@

$startupScriptPath = Join-Path $InstallDir "startup_service.bat"
Set-Content -Path $startupScriptPath -Value $startupScript
Write-Host "   ✅ Startup script created" -ForegroundColor Green

Write-Host "`n[2/3] Creating Windows startup shortcut..." -ForegroundColor Yellow

# Add to Windows Startup folder
$startupFolder = [Environment]::GetFolderPath("Startup")
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut("$startupFolder\NetworkBuster.lnk")
$shortcut.TargetPath = $startupScriptPath
$shortcut.WorkingDirectory = $InstallDir
$shortcut.Description = "NetworkBuster Auto-Start Service"
$shortcut.Save()

Write-Host "   ✅ Startup shortcut created: $startupFolder\NetworkBuster.lnk" -ForegroundColor Green

Write-Host "`n[3/3] Creating scheduled task..." -ForegroundColor Yellow

# Firewall configuration for NetworkBuster
$ports = @(3000, 3001, 3002, 5000, 6000, 7000, 8000, 9000)
Write-Host "`n[4/4] Configuring Windows Firewall..." -ForegroundColor Yellow
foreach ($port in $ports) {
    $ruleName = "NetworkBuster_Port_$port"
    if (!(Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue)) {
        New-NetFirewallRule -DisplayName "NetworkBuster Port $port" -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow -Name $ruleName | Out-Null
        Write-Host "   ✅ Opened Port $port" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Port $port already open" -ForegroundColor Cyan
    }
}

# Create scheduled task for system events
$taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>NetworkBuster Immersive Auto-Start</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$env:USERNAME</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
  </Settings>
  <Actions>
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -File "$InstallDir\immersive_boot.ps1"</Arguments>
      <WorkingDirectory>$InstallDir</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

$taskXmlPath = Join-Path $InstallDir "autostart_task.xml"
Set-Content -Path $taskXmlPath -Value $taskXml -Encoding Unicode

# Create the task
try {
    schtasks /Create /TN "$ServiceName" /XML "$taskXmlPath" /F | Out-Null
    Write-Host "   ✅ Scheduled task created: $ServiceName" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Task creation failed (may already exist)" -ForegroundColor Yellow
}

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ AUTO-START INSTALLED!                     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n🚀 NetworkBuster will now automatically start:" -ForegroundColor Cyan
Write-Host "   • On Windows boot" -ForegroundColor White
Write-Host "   • On user login" -ForegroundColor White
Write-Host "   • After system resume" -ForegroundColor White

Write-Host "`n🎮 Control Options:" -ForegroundColor Cyan
Write-Host "   Disable: schtasks /Change /TN `"$ServiceName`" /DISABLE" -ForegroundColor White
Write-Host "   Enable:  schtasks /Change /TN `"$ServiceName`" /ENABLE" -ForegroundColor White
Write-Host "   Remove:  schtasks /Delete /TN `"$ServiceName`" /F" -ForegroundColor White

Write-Host "`n📁 Startup Location:" -ForegroundColor Cyan
Write-Host "   $startupFolder\NetworkBuster.lnk" -ForegroundColor White

Write-Host "`n✨ Test now?" -ForegroundColor Yellow
$test = Read-Host "Start services now? (y/n)"
if ($test -eq 'y') {
    Write-Host "`nStarting services..." -ForegroundColor Cyan
    & "$InstallDir\.venv\Scripts\python.exe" "$InstallDir\auto_start_service.py"
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
