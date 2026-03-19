
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.IO.Path]::Combine($env:USERPROFILE, "Desktop")
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\NetworkBuster Terminal.lnk")
$Shortcut.TargetPath = "powershell.exe"
# Properly escape quotes for the command argument
$cmd = ". .\nb.ps1; nb-help; cd '$PSScriptRoot'"
$Shortcut.Arguments = "-NoExit -Command ""$cmd"""
$Shortcut.WorkingDirectory = "$PSScriptRoot"
$Shortcut.IconLocation = "powershell.exe, 0"
$Shortcut.Description = "NetworkBuster CLI Terminal"
$Shortcut.Save()

Write-Host "`n✅ Desktop shortcut 'NetworkBuster Terminal' created successfully!" -ForegroundColor Green
Write-Host "💡 This terminal pre-loads 'nb' commands (nb-start, nb-status, etc.)" -ForegroundColor Cyan
