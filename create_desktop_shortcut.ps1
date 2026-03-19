
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.IO.Path]::Combine($env:USERPROFILE, "Desktop")
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\NetworkBuster Manager.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\networkbuster_startup.bat"
$Shortcut.WorkingDirectory = "$PSScriptRoot"
$Shortcut.WindowStyle = 1
$Shortcut.Description = "NetworkBuster All-in-One Manager"
# Use a generic system icon if needed, but Python/Batch default is fine
$Shortcut.Save()

Write-Host "`n✅ Desktop shortcut 'NetworkBuster Manager' created successfully!" -ForegroundColor Green
