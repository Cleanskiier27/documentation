# NetworkBuster — Register All Services as Windows Scheduled Tasks
# Run this script as Administrator to auto-start everything on login

param(
    [switch]$Remove  # Pass -Remove to unregister all tasks
)

$ErrorActionPreference = 'Stop'
$NodePath   = "C:\networkbuster-session-20260405-data\node.exe"
$ScriptRoot = "C:\networkbuster-session-20260405-data\networkbuster-session-20260405-data"
$TaskGroup  = "NetworkBuster"

$tasks = @(
    @{ Name="NB-WebServer";     Desc="NetworkBuster Web Server (port 3000)";        Script="server-universal.js";          Port=3000 },
    @{ Name="NB-APIServer";     Desc="NetworkBuster API Server (port 3001)";         Script="api/server-universal.js";      Port=3001 },
    @{ Name="NB-AudioServer";   Desc="NetworkBuster Audio Server (port 3002)";       Script="server-audio.js";              Port=3002 },
    @{ Name="NB-RetrievalLab";  Desc="NetworkBuster Lab A - Retrieval Agent (4010)"; Script="labs/agent-retrieval.js";      Port=4010 },
    @{ Name="NB-MissionIntel";  Desc="NetworkBuster Lab B - Mission Intel (4011)";   Script="labs/agent-mission-intel.js";  Port=4011 },
    @{ Name="NB-NetScanner";    Desc="NetworkBuster Lab C - Network Scanner (4012)"; Script="labs/agent-network-scan.js";   Port=4012 }
)

if ($Remove) {
    Write-Host "`n Removing all NetworkBuster scheduled tasks..." -ForegroundColor Yellow
    foreach ($t in $tasks) {
        if (Get-ScheduledTask -TaskName $t.Name -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $t.Name -Confirm:$false
            Write-Host "  [REMOVED] $($t.Name)" -ForegroundColor Red
        }
    }
    Write-Host "`nAll tasks removed.`n" -ForegroundColor Yellow
    exit 0
}

# --- Check admin ---
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "`n[ERROR] Please run this script as Administrator.`n" -ForegroundColor Red
    exit 1
}

Write-Host "`n NetworkBuster — Registering $($tasks.Count) services as Scheduled Tasks" -ForegroundColor Cyan
Write-Host " Trigger: At user logon | Run hidden in background`n"

foreach ($t in $tasks) {
    $scriptFile = Join-Path $ScriptRoot $t.Script

    # Skip if lab file doesn't exist yet
    if (-not (Test-Path $scriptFile)) {
        Write-Host "  [SKIP] $($t.Name) — script not found: $($t.Script)" -ForegroundColor DarkGray
        continue
    }

    # Remove existing task first
    if (Get-ScheduledTask -TaskName $t.Name -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $t.Name -Confirm:$false
    }

    $action  = New-ScheduledTaskAction `
        -Execute $NodePath `
        -Argument $scriptFile `
        -WorkingDirectory $ScriptRoot

    $trigger = New-ScheduledTaskTrigger -AtLogOn

    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1) `
        -MultipleInstances IgnoreNew

    $principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -RunLevel Limited `
        -LogonType Interactive

    Register-ScheduledTask `
        -TaskName    $t.Name `
        -TaskPath    "\$TaskGroup\" `
        -Description $t.Desc `
        -Action      $action `
        -Trigger     $trigger `
        -Settings    $settings `
        -Principal   $principal `
        -Force | Out-Null

    Write-Host "  [REGISTERED] $($t.Name) → port $($t.Port)" -ForegroundColor Green
}

Write-Host @"

 All tasks registered under Task Scheduler → '$TaskGroup' folder.
 They will auto-start at next login.

 To start them NOW without rebooting, run:
   Start-ScheduledTask -TaskName 'NB-WebServer'
   Start-ScheduledTask -TaskName 'NB-APIServer'
   Start-ScheduledTask -TaskName 'NB-AudioServer'

 To remove all tasks, run:
   .\register-tasks.ps1 -Remove

 Or view them in: Task Scheduler → Task Scheduler Library → NetworkBuster

"@ -ForegroundColor Cyan
