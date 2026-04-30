<#
.SYNOPSIS
    Updates .gitignore in all NetworkBuster repositories with security patterns.

.DESCRIPTION
    Adds comprehensive credential, key, and environment-variable exclusion
    patterns to the .gitignore file at the root of the current git repository,
    then commits and pushes the change automatically.

.NOTES
    Prerequisites : Git must be installed and the current directory must be
                    the root of a git repository.
    PowerShell    : 5.1+
#>

$ErrorActionPreference = "Stop"

# ── Patterns to add ───────────────────────────────────────────────────────────
$SecurityPatterns = @"

# ── Security patterns added $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ──────────
# Credential and secret files
*secret*
*credential*
*password*
*.key
*.pem

# Azure deployment artifacts
deployment-output.json
azure-credentials*.json
.azure/

# Environment variables
.env
.env.*
!.env.example
config.local.*

# SSH keys
id_rsa
id_rsa.pub
id_ed25519
id_ed25519.pub
*.ppk

# AWS credentials
.aws/credentials
.aws/config
credentials.csv

# General sensitive output files
*.token
*.secret
*.pfx
*.p12
"@

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

   ██████╗ ██╗████████╗██╗ ██████╗ ███╗   ██╗ ██████╗ ██████╗ ███████╗
  ██╔════╝ ██║╚══██╔══╝██║██╔════╝ ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
  ██║  ███╗██║   ██║   ██║██║  ███╗██╔██╗ ██║██║   ██║██████╔╝█████╗
  ██║   ██║██║   ██║   ██║██║   ██║██║╚██╗██║██║   ██║██╔══██╗██╔══╝
  ╚██████╔╝██║   ██║   ██║╚██████╔╝██║ ╚████║╚██████╔╝██║  ██║███████╗
   ╚═════╝ ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝

              .gitignore Security Update — NetworkBuster
"@ -ForegroundColor Cyan

# ── Pre-flight checks ─────────────────────────────────────────────────────────
Write-Section "Pre-flight Checks"

Write-Step 1 "Checking git installation..."
try {
    $gitVersion = git --version 2>&1
    Write-OK "Git found: $gitVersion"
} catch {
    Write-Err "Git not found. Please install git and try again."
    exit 1
}

Write-Step 2 "Verifying current directory is a git repository..."
try {
    $repoRoot = git rev-parse --show-toplevel 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Not a git repository." }
    Write-OK "Repository root: $repoRoot"
} catch {
    Write-Err "Not inside a git repository. Navigate to the repo root first."
    exit 1
}

$gitignorePath = Join-Path $repoRoot ".gitignore"

# ── Check existing .gitignore ──────────────────────────────────────────────────
Write-Section "Checking Existing .gitignore"

Write-Step 3 "Looking for existing .gitignore at $gitignorePath..."
if (Test-Path $gitignorePath) {
    $existing = Get-Content $gitignorePath -Raw
    Write-OK ".gitignore found ($([math]::Round(($existing.Length / 1KB), 1)) KB)."

    # Check if patterns already present (look for the unique marker added by this script)
    if ($existing -match "Security patterns added") {
        Write-Warn "Security patterns appear to already be present in .gitignore."
        $overwrite = Read-Host "  Add patterns again anyway? (yes/no)"
        if ($overwrite -ne "yes") {
            Write-Info "Skipping .gitignore update."
            exit 0
        }
    }
} else {
    Write-Warn ".gitignore not found. A new one will be created."
    $existing = ""
}

# ── Append patterns ────────────────────────────────────────────────────────────
Write-Section "Updating .gitignore"

Write-Step 4 "Appending security patterns..."
Add-Content -Path $gitignorePath -Value $SecurityPatterns -Encoding UTF8
Write-OK "Security patterns added to .gitignore."
Write-FilePath "      $gitignorePath"

Write-Host "`n  Patterns added:" -ForegroundColor White
$SecurityPatterns -split "`n" | Where-Object { $_ -and $_ -notmatch "^#" -and $_.Trim() } | ForEach-Object {
    Write-Host "    $_" -ForegroundColor Gray
}

# ── Commit and push ────────────────────────────────────────────────────────────
Write-Section "Committing and Pushing"

Write-Step 5 "Staging .gitignore..."
git add .gitignore | Out-Null
Write-OK ".gitignore staged."

Write-Step 6 "Committing..."
$commitMsg = "security: update .gitignore with credential exclusion patterns"
git commit -m $commitMsg | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Nothing to commit — patterns may already be tracked. Continuing."
} else {
    Write-OK "Committed: `"$commitMsg`""
}

Write-Step 7 "Pushing to origin..."
try {
    git push | Out-Null
    Write-OK "Changes pushed to origin successfully."
} catch {
    Write-Err "Push failed: $_"
    Write-Warn "You may need to pull first or push manually: git push origin"
}

# ── Final summary ──────────────────────────────────────────────────────────────
Write-Section "Update Complete"

Write-Host @"

  ✅  .gitignore updated with comprehensive security patterns
  ✅  Changes committed and pushed

  These patterns now prevent accidental commits of:
    • Secret / credential / password files
    • Azure deployment artifacts (.azure/, deployment-output.json)
    • Environment variable files (.env, .env.*)
    • SSH private keys (id_rsa, *.pem, *.ppk)
    • AWS credential files
    • Generic token and certificate files

  REMINDER: .gitignore only protects FUTURE commits.
  Files already tracked must be removed with:
    git rm --cached <filename>

"@ -ForegroundColor Green
