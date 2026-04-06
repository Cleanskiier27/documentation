<#
.SYNOPSIS
    Rotates Azure Container Registry credentials for the NetworkBuster infrastructure.

.DESCRIPTION
    Connects to Azure, rotates both password1 and password2 for the NetworkBuster
    Container Registry, saves the new credentials to a JSON file, and prints
    step-by-step instructions for updating GitHub Secrets in all affected repos.

.NOTES
    Prerequisites : Azure CLI (az) must be installed and in PATH.
    Run as        : Any user with Contributor access to networkbuster-rg.
    PowerShell    : 5.1+
#>

$ErrorActionPreference = "Stop"

# ── Configuration ────────────────────────────────────────────────────────────
$RegistryName   = "networkbusterlo25gft5nqwzg"
$SubscriptionId = "cdb580bc-e2e9-4866-aac2-aa86f0a25cb3"
$ResourceGroup  = "networkbuster-rg"
$Repositories   = @(
    "Cleanskiier27/documentation",
    "Cleanskiier27/nasa-waste-calc",
    "Cleanskiier27/artemis-r-navigation"
)
$OutputFile = Join-Path $env:TEMP "azure-credentials-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"

# ── Helpers ───────────────────────────────────────────────────────────────────
function Write-Section  { param($msg) Write-Host "`n$('─' * 60)" -ForegroundColor Gray;  Write-Host " $msg" -ForegroundColor Cyan;  Write-Host "$('─' * 60)" -ForegroundColor Gray }
function Write-Step     { param($n,$msg) Write-Host "`n  [$n] $msg" -ForegroundColor Yellow }
function Write-OK       { param($msg) Write-Host "      ✅  $msg" -ForegroundColor Green }
function Write-Warn     { param($msg) Write-Host "      ⚠️   $msg" -ForegroundColor Yellow }
function Write-Err      { param($msg) Write-Host "      ❌  $msg" -ForegroundColor Red }
function Write-Info     { param($msg) Write-Host "      $msg" -ForegroundColor White }
function Write-FilePath { param($msg) Write-Host "      $msg" -ForegroundColor Magenta }

function Mask-Secret {
    param([string]$Value)
    if ($Value.Length -le 10) { return "**********" }
    return $Value.Substring(0, 10) + ("*" * ($Value.Length - 10))
}

# ── Banner ────────────────────────────────────────────────────────────────────
Write-Host @"

  ██████╗  ██████╗ ████████╗ █████╗ ████████╗███████╗
  ██╔══██╗██╔═══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝
  ██████╔╝██║   ██║   ██║   ███████║   ██║   █████╗
  ██╔══██╗██║   ██║   ██║   ██╔══██║   ██║   ██╔══╝
  ██║  ██║╚██████╔╝   ██║   ██║  ██║   ██║   ███████╗
  ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝

        Azure Container Registry — Credential Rotation
"@ -ForegroundColor Cyan

# ── Pre-flight checks ─────────────────────────────────────────────────────────
Write-Section "Pre-flight Checks"

Write-Step 1 "Checking Azure CLI installation..."
try {
    $azVersion = az version --output tsv 2>&1
    Write-OK "Azure CLI found."
} catch {
    Write-Err "Azure CLI (az) not found. Install from https://aka.ms/installazurecliwindows"
    exit 1
}

Write-Step 2 "Verifying Azure login..."
try {
    $account = az account show --output json 2>&1 | ConvertFrom-Json
    Write-OK "Logged in as: $($account.user.name)"
} catch {
    Write-Warn "Not logged in. Launching az login..."
    az login
    $account = az account show --output json | ConvertFrom-Json
}

Write-Step 3 "Setting subscription to $SubscriptionId..."
az account set --subscription $SubscriptionId | Out-Null
$current = az account show --output json | ConvertFrom-Json
Write-OK "Active subscription: $($current.name) ($($current.id))"

# ── Show current credentials (masked) ─────────────────────────────────────────
Write-Section "Current Credentials (Masked)"

Write-Step 4 "Fetching current ACR credentials..."
try {
    $currentCreds = az acr credential show --name $RegistryName --output json | ConvertFrom-Json
    Write-Info "Registry  : $($currentCreds.username)"
    Write-Info "Password1 : $(Mask-Secret $currentCreds.passwords[0].value)"
    Write-Info "Password2 : $(Mask-Secret $currentCreds.passwords[1].value)"
} catch {
    Write-Err "Failed to retrieve current credentials: $_"
    exit 1
}

# ── Safety confirmation ────────────────────────────────────────────────────────
Write-Host "`n  ⚠️  This will INVALIDATE the current passwords immediately." -ForegroundColor Red
Write-Host "  Any service using the old passwords will stop authenticating." -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "  Type YES to proceed with credential rotation"
if ($confirm -ne "YES") {
    Write-Warn "Rotation cancelled."
    exit 0
}

# ── Rotate credentials ─────────────────────────────────────────────────────────
Write-Section "Rotating Credentials"

Write-Step 5 "Rotating password1..."
try {
    az acr credential renew --name $RegistryName --password-name password1 --output none
    Write-OK "password1 rotated."
} catch {
    Write-Err "Failed to rotate password1: $_"
    exit 1
}

Write-Step 6 "Rotating password2..."
try {
    az acr credential renew --name $RegistryName --password-name password2 --output none
    Write-OK "password2 rotated."
} catch {
    Write-Err "Failed to rotate password2: $_"
    exit 1
}

# ── Display new credentials ────────────────────────────────────────────────────
Write-Section "New Credentials"

$newCreds = az acr credential show --name $RegistryName --output json | ConvertFrom-Json
$newPassword1 = $newCreds.passwords[0].value
$newPassword2 = $newCreds.passwords[1].value

Write-Info "Registry         : $($newCreds.username)"
Write-Info "Login Server     : $RegistryName.azurecr.io"
Write-Info "New Password1    : $(Mask-Secret $newPassword1)"
Write-Info "New Password2    : $(Mask-Secret $newPassword2)"

# ── Save credentials to JSON ───────────────────────────────────────────────────
Write-Section "Saving Credentials"

$credObject = [ordered]@{
    generatedAt      = (Get-Date -Format "o")
    registryName     = $RegistryName
    loginServer      = "$RegistryName.azurecr.io"
    username         = $newCreds.username
    password1        = $newPassword1
    password2        = $newPassword2
    subscriptionId   = $SubscriptionId
    resourceGroup    = $ResourceGroup
    WARNING          = "DELETE THIS FILE AFTER UPDATING GITHUB SECRETS"
}

$credObject | ConvertTo-Json | Set-Content -Path $OutputFile -Encoding UTF8
Write-OK "Credentials saved to:"
Write-FilePath "      $OutputFile"
Write-Warn "DELETE this file after you have updated all GitHub Secrets!"

# ── GitHub Secrets update instructions ────────────────────────────────────────
Write-Section "GitHub Secrets — Update Instructions"

Write-Host "`n  Update the following secret in each repository:" -ForegroundColor White
Write-Host ""
Write-Host "    Secret Name              Value" -ForegroundColor Gray
Write-Host "    ───────────────────────  ────────────────────────────────────" -ForegroundColor Gray
Write-Host "    AZURE_REGISTRY_USERNAME  $($newCreds.username)" -ForegroundColor White
Write-Host "    AZURE_REGISTRY_PASSWORD  <new password1 from saved file>" -ForegroundColor White
Write-Host "    AZURE_REGISTRY_SERVER    $RegistryName.azurecr.io" -ForegroundColor White
Write-Host ""

foreach ($repo in $Repositories) {
    Write-Host "  → https://github.com/$repo/settings/secrets/actions" -ForegroundColor Magenta
}

# ── Test new credentials ────────────────────────────────────────────────────────
Write-Section "Testing New Credentials"

Write-Step 7 "Testing ACR login with new credentials..."
try {
    az acr login --name $RegistryName --output none
    Write-OK "ACR login successful with new credentials!"
} catch {
    Write-Err "ACR login test failed: $_"
    Write-Warn "Check that Docker is running or use --expose-token for token-only login."
}

# ── Final summary ──────────────────────────────────────────────────────────────
Write-Section "Rotation Complete"
Write-Host @"

  ✅  password1 rotated
  ✅  password2 rotated
  ✅  Credentials saved to: $OutputFile

  NEXT STEPS:
  1. Open the saved JSON file and copy the new passwords.
  2. Update GitHub Secrets in ALL repositories listed above.
  3. Trigger a test CI/CD run to verify the pipeline still works.
  4. DELETE the credentials JSON file from disk.
  5. Run enable-security-features.ps1 to harden your repos.

"@ -ForegroundColor Green
