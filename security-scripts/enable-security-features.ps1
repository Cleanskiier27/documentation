<#
.SYNOPSIS
    Enables GitHub security features for all NetworkBuster repositories.

.DESCRIPTION
    Uses the GitHub CLI (gh) to enable vulnerability alerts and security
    advisories on all NetworkBuster repositories, and prints manual
    instructions for features that require UI configuration (e.g., push
    protection / secret scanning).

.NOTES
    Prerequisites : GitHub CLI (gh) must be installed and authenticated.
    PowerShell    : 5.1+
#>

$ErrorActionPreference = "Stop"

# ── Configuration ─────────────────────────────────────────────────────────────
$Repositories = @(
    "Cleanskiier27/documentation",
    "Cleanskiier27/nasa-waste-calc",
    "Cleanskiier27/artemis-r-navigation"
)

# ── Helpers ───────────────────────────────────────────────────────────────────
function Write-Section  { param($msg) Write-Host "`n$('─' * 60)" -ForegroundColor Gray;  Write-Host " $msg" -ForegroundColor Cyan;  Write-Host "$('─' * 60)" -ForegroundColor Gray }
function Write-Step     { param($n,$msg) Write-Host "`n  [$n] $msg" -ForegroundColor Yellow }
function Write-OK       { param($msg) Write-Host "      ✅  $msg" -ForegroundColor Green }
function Write-Warn     { param($msg) Write-Host "      ⚠️   $msg" -ForegroundColor Yellow }
function Write-Err      { param($msg) Write-Host "      ❌  $msg" -ForegroundColor Red }
function Write-Info     { param($msg) Write-Host "      $msg" -ForegroundColor White }
function Write-FilePath { param($msg) Write-Host "      $msg" -ForegroundColor Magenta }

# ── Banner ────────────────────────────────────────────────────────────────────
Write-Host @"

  ███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗████████╗██╗   ██╗
  ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
  ███████╗█████╗  ██║     ██║   ██║██████╔╝██║   ██║    ╚████╔╝
  ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║     ╚██╔╝
  ███████║███████╗╚██████╗╚██████╔╝██║  ██║██║   ██║      ██║
  ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝

        GitHub Security Features — NetworkBuster Repos
"@ -ForegroundColor Cyan

# ── Pre-flight checks ─────────────────────────────────────────────────────────
Write-Section "Pre-flight Checks"

Write-Step 1 "Checking GitHub CLI installation..."
try {
    $ghVersion = gh --version 2>&1 | Select-Object -First 1
    Write-OK "GitHub CLI found: $ghVersion"
} catch {
    Write-Err "GitHub CLI (gh) not found. Install from https://cli.github.com/"
    exit 1
}

Write-Step 2 "Verifying GitHub CLI authentication..."
try {
    $ghStatus = gh auth status 2>&1
    Write-OK "GitHub CLI is authenticated."
} catch {
    Write-Warn "Not authenticated. Launching gh auth login..."
    gh auth login
}

# ── Enable features for each repository ───────────────────────────────────────
Write-Section "Enabling Security Features"

$stepNum = 3
foreach ($repo in $Repositories) {
    Write-Host "`n  Repository: " -NoNewline -ForegroundColor White
    Write-Host $repo -ForegroundColor Magenta

    # Vulnerability alerts
    Write-Step $stepNum "Enabling vulnerability alerts on $repo..."
    $stepNum++
    try {
        $response = gh api "repos/$repo/vulnerability-alerts" --method PUT 2>&1
        if ($LASTEXITCODE -ne 0) { throw $response }
        Write-OK "Vulnerability alerts enabled."
    } catch {
        Write-Err "Failed to enable vulnerability alerts: $_"
    }

    # Automated security fixes (Dependabot)
    Write-Step $stepNum "Enabling automated security fixes on $repo..."
    $stepNum++
    try {
        $response = gh api "repos/$repo/automated-security-fixes" --method PUT 2>&1
        if ($LASTEXITCODE -ne 0) { throw $response }
        Write-OK "Automated security fixes (Dependabot) enabled."
    } catch {
        Write-Warn "Automated security fixes not available or already enabled: $_"
    }
}

# ── Manual instructions for push protection ────────────────────────────────────
Write-Section "Push Protection & Secret Scanning — Manual Steps"

Write-Host @"

  GitHub Secret Scanning and Push Protection require UI configuration.
  Complete the following steps for EACH repository:

"@ -ForegroundColor White

foreach ($repo in $Repositories) {
    Write-Host "  ── $repo ──" -ForegroundColor Yellow
    Write-FilePath "      https://github.com/$repo/settings/security_analysis"
    Write-Host ""
    Write-Host "      Enable ALL of the following toggles:" -ForegroundColor White
    Write-Host "        ✅  Dependency graph" -ForegroundColor Green
    Write-Host "        ✅  Dependabot alerts" -ForegroundColor Green
    Write-Host "        ✅  Dependabot security updates" -ForegroundColor Green
    Write-Host "        ✅  Secret scanning" -ForegroundColor Green
    Write-Host "        ✅  Push protection" -ForegroundColor Green
    Write-Host ""
}

# ── Security advisories ────────────────────────────────────────────────────────
Write-Section "Security Advisories"

Write-Host @"

  Security Advisories allow you to privately discuss, fix, and disclose
  security vulnerabilities. They are enabled per-repository in the UI:

"@ -ForegroundColor White

foreach ($repo in $Repositories) {
    Write-FilePath "      https://github.com/$repo/security/advisories/new"
}

# ── Final summary ──────────────────────────────────────────────────────────────
Write-Section "Security Features Summary"

Write-Host @"

  ✅  Vulnerability alerts enabled via API for all repos
  ✅  Dependabot automated fixes requested for all repos

  MANUAL ACTION REQUIRED:
  → Visit each repository's Security Analysis settings page (URLs above)
  → Enable Secret Scanning + Push Protection in the UI

  After enabling push protection, any future git push containing a
  detected secret will be BLOCKED before it reaches GitHub. 🔒

"@ -ForegroundColor Green
