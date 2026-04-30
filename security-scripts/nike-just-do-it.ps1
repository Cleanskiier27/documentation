<#
.SYNOPSIS
    Master security automation script — runs all NetworkBuster security tasks.

.DESCRIPTION
    All-in-one orchestrator that:
      1. Rotates Azure Container Registry credentials
      2. Enables GitHub security features on all repos
      3. Updates .gitignore with credential exclusion patterns

    Git history cleanup is intentionally excluded from this script.

.NOTES
    Prerequisites : Azure CLI (az) and GitHub CLI (gh) must be installed.
    PowerShell    : 5.1+
#>

$ErrorActionPreference = "Stop"

# ── Helpers ───────────────────────────────────────────────────────────────────
function Write-Section  { param($msg) Write-Host "`n$('─' * 60)" -ForegroundColor Gray;  Write-Host " $msg" -ForegroundColor Cyan;  Write-Host "$('─' * 60)" -ForegroundColor Gray }
function Write-OK       { param($msg) Write-Host "      ✅  $msg" -ForegroundColor Green }
function Write-Warn     { param($msg) Write-Host "      ⚠️   $msg" -ForegroundColor Yellow }
function Write-Err      { param($msg) Write-Host "      ❌  $msg" -ForegroundColor Red }
function Write-Info     { param($msg) Write-Host "      $msg" -ForegroundColor White }

# ── ASCII Banner ───────────────────────────────────────────────────────────────
Write-Host @"

 ███╗   ██╗██╗██╗  ██╗███████╗    ██╗██╗   ██╗███████╗████████╗
 ████╗  ██║██║██║ ██╔╝██╔════╝    ██║██║   ██║██╔════╝╚══██╔══╝
 ██╔██╗ ██║██║█████╔╝ █████╗      ██║██║   ██║███████╗   ██║
 ██║╚██╗██║██║██╔═██╗ ██╔══╝ ██   ██║██║   ██║╚════██║   ██║
 ██║ ╚████║██║██║  ██╗███████╗╚█████╔╝╚██████╔╝███████║   ██║
 ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚══════╝ ╚════╝  ╚═════╝ ╚══════╝   ╚═╝

  ██████╗  ██████╗     ██╗████████╗
  ██╔══██╗██╔═══██╗    ██║╚══██╔══╝
  ██║  ██║██║   ██║    ██║   ██║
  ██║  ██║██║   ██║    ██║   ██║
  ██████╔╝╚██████╔╝    ██║   ██║
  ╚═════╝  ╚═════╝     ╚═╝   ╚═╝

         NetworkBuster — Complete Security Automation
"@ -ForegroundColor Cyan

Write-Host "  Just do it. — Nike" -ForegroundColor Gray
Write-Host ""

# ── Safety confirmation ────────────────────────────────────────────────────────
Write-Section "Safety Confirmation"

Write-Host @"

  This master script will run the following operations IN SEQUENCE:

    [1] Rotate Azure Container Registry credentials (password1 + password2)
    [2] Enable GitHub security features on all NetworkBuster repos
    [3] Update .gitignore with credential exclusion patterns

  ⚠️  Step 1 will IMMEDIATELY invalidate existing ACR passwords.
  ⚠️  Update your GitHub Secrets before running any CI/CD pipelines.

  Note: Git history cleanup is NOT included in this script.
        Run that manually if required.

"@ -ForegroundColor White

$confirm = Read-Host "  Type JUST-DO-IT to proceed with ALL operations"
if ($confirm -ne "JUST-DO-IT") {
    Write-Warn "Master script cancelled. No changes were made."
    exit 0
}

# Track overall success
$results = [ordered]@{}
$scriptDir = $PSScriptRoot

# ── Step 1: Rotate Azure credentials ──────────────────────────────────────────
Write-Section "Step 1 of 3 — Rotating Azure Credentials"

$rotateScript = Join-Path $scriptDir "rotate-azure-credentials.ps1"
if (-not (Test-Path $rotateScript)) {
    Write-Err "rotate-azure-credentials.ps1 not found in $scriptDir"
    $results["Rotate Azure Credentials"] = "❌ Script not found"
} else {
    try {
        & $rotateScript
        $results["Rotate Azure Credentials"] = "✅ Completed"
        Write-OK "Credential rotation finished."
    } catch {
        Write-Err "Credential rotation failed: $_"
        $results["Rotate Azure Credentials"] = "❌ Failed: $_"
    }
}

# ── Step 2: Enable GitHub security features ────────────────────────────────────
Write-Section "Step 2 of 3 — Enabling GitHub Security Features"

$securityScript = Join-Path $scriptDir "enable-security-features.ps1"
if (-not (Test-Path $securityScript)) {
    Write-Err "enable-security-features.ps1 not found in $scriptDir"
    $results["Enable GitHub Security Features"] = "❌ Script not found"
} else {
    try {
        & $securityScript
        $results["Enable GitHub Security Features"] = "✅ Completed"
        Write-OK "Security features enabled."
    } catch {
        Write-Err "Enable security features failed: $_"
        $results["Enable GitHub Security Features"] = "❌ Failed: $_"
    }
}

# ── Step 3: Update .gitignore ──────────────────────────────────────────────────
Write-Section "Step 3 of 3 — Updating .gitignore"

$gitignoreScript = Join-Path $scriptDir "update-gitignore.ps1"
if (-not (Test-Path $gitignoreScript)) {
    Write-Err "update-gitignore.ps1 not found in $scriptDir"
    $results["Update .gitignore"] = "❌ Script not found"
} else {
    try {
        & $gitignoreScript
        $results["Update .gitignore"] = "✅ Completed"
        Write-OK ".gitignore updated."
    } catch {
        Write-Err ".gitignore update failed: $_"
        $results["Update .gitignore"] = "❌ Failed: $_"
    }
}

# ── Final summary ──────────────────────────────────────────────────────────────
Write-Section "Final Success Summary"

Write-Host ""
foreach ($key in $results.Keys) {
    Write-Host "  $($results[$key])  $key" -ForegroundColor $(if ($results[$key] -like "✅*") { "Green" } else { "Red" })
}

$allSucceeded = ($results.Values | Where-Object { $_ -notlike "✅*" }).Count -eq 0

if ($allSucceeded) {
    Write-Host @"

  🎉  ALL OPERATIONS COMPLETED SUCCESSFULLY!

  What you MUST do next:
    1. Open the azure-credentials-*.json file saved by Step 1.
    2. Update GitHub Secrets in ALL three repositories with the new passwords.
    3. DELETE the azure-credentials-*.json file from disk.
    4. Trigger a test CI/CD pipeline run to verify everything works.
    5. Complete the manual Secret Scanning / Push Protection steps in GitHub UI.

  Stay safe. Stay secure. Just do it. 🚀

"@ -ForegroundColor Green
} else {
    Write-Host @"

  ⚠️  Some operations failed. Review errors above and re-run the
      individual scripts manually to complete the remaining steps.

"@ -ForegroundColor Yellow
}
