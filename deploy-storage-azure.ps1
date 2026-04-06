# NetworkBuster Azure Storage Deployment (PowerShell)
# This script deploys Azure Storage infrastructure for NetworkBuster
# Usage: .\deploy-storage-azure.ps1

param(
    [string]$SubscriptionId = "cdb580bc-e2e9-4866-aac2-aa86f0a25cb3",
    [string]$ResourceGroup = "networkbuster-rg",
    [string]$Location = "eastus",
    [string]$ProjectName = "networkbuster",
    [string]$StorageSku = "Standard_LRS",
    [string]$AccessTier = "Hot"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 NetworkBuster Azure Storage Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Resource Group: $ResourceGroup"
Write-Host "  Location: $Location"
Write-Host "  Project: $ProjectName"
Write-Host "  Subscription: $SubscriptionId"
Write-Host "  Storage SKU: $StorageSku"
Write-Host "  Access Tier: $AccessTier"
Write-Host ""

# Check Azure CLI
Write-Host "🔍 Checking Azure CLI installation..." -ForegroundColor Yellow
$azCliCheck = az --version 2>$null
if (-not $azCliCheck) {
    Write-Host "❌ Azure CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Azure CLI is available" -ForegroundColor Green

# Login to Azure
Write-Host ""
Write-Host "🔐 Checking Azure authentication..." -ForegroundColor Yellow
try {
    az account show | Out-Null
} catch {
    Write-Host "  Logging into Azure..." -ForegroundColor Cyan
    az login | Out-Null
}

# Set subscription
Write-Host "📋 Setting subscription..." -ForegroundColor Yellow
az account set --subscription $SubscriptionId

# Create resource group if needed
Write-Host "📁 Checking resource group..." -ForegroundColor Yellow
$rgExists = az group exists --name $ResourceGroup | ConvertFrom-Json
if (-not $rgExists) {
    Write-Host "  Creating resource group: $ResourceGroup" -ForegroundColor Cyan
    az group create `
        --name $ResourceGroup `
        --location $Location | Out-Null
} else {
    Write-Host "  ✅ Resource group already exists" -ForegroundColor Green
}

# Deploy storage infrastructure
Write-Host ""
Write-Host "💾 Deploying Azure Storage Infrastructure..." -ForegroundColor Cyan
Write-Host "  ├─ Storage Account" -ForegroundColor Cyan
Write-Host "  ├─ Blob Containers (7)" -ForegroundColor Cyan
Write-Host "  ├─ File Shares (1)" -ForegroundColor Cyan
Write-Host "  ├─ Tables (2)" -ForegroundColor Cyan
Write-Host "  └─ Queues (2)" -ForegroundColor Cyan
Write-Host ""

$deploymentName = "networkbuster-storage-$(Get-Date -Format 'yyyyMMddHHmmss')"

$deploymentOutput = az deployment group create `
    --resource-group $ResourceGroup `
    --template-file infra/storage.bicep `
    --parameters `
        location=$Location `
        projectName=$ProjectName `
        environment="prod" `
        storageSku=$StorageSku `
        accessTier=$AccessTier `
    --name $deploymentName `
    --query properties.outputs

# Parse outputs
$outputs = $deploymentOutput | ConvertFrom-Json

Write-Host ""
Write-Host "✅ Storage deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment Outputs:" -ForegroundColor Yellow
Write-Host "===================="
Write-Host ($outputs | ConvertTo-Json -Depth 10)
Write-Host ""

# Extract key values
$storageAccountName = $outputs.storageAccountName.value
$storageAccountKey = $outputs.storageAccountKey.value
$connectionString = $outputs.connectionString.value
$blobEndpoint = $outputs.blobEndpoint.value

Write-Host "🔑 Storage Access Information:" -ForegroundColor Yellow
Write-Host "  Account Name: $storageAccountName" -ForegroundColor Cyan
Write-Host "  Connection String: $($connectionString.Substring(0, 50))..." -ForegroundColor Cyan
Write-Host ""

# Save credentials securely
Write-Host "💾 Saving credentials to secure file..." -ForegroundColor Yellow
$credsFile = "storage-credentials.env"

$credsContent = @"
# NetworkBuster Azure Storage Credentials
# ⚠️ KEEP THIS FILE SECURE - DO NOT COMMIT TO GIT

AZURE_STORAGE_ACCOUNT_NAME=$storageAccountName
AZURE_STORAGE_ACCOUNT_KEY=$storageAccountKey
AZURE_STORAGE_CONNECTION_STRING=$connectionString
AZURE_STORAGE_RESOURCE_GROUP=$ResourceGroup

# Endpoints
AZURE_STORAGE_BLOB_ENDPOINT=$blobEndpoint
AZURE_STORAGE_FILE_ENDPOINT=$($outputs.fileEndpoint.value)
AZURE_STORAGE_TABLE_ENDPOINT=$($outputs.tableEndpoint.value)
AZURE_STORAGE_QUEUE_ENDPOINT=$($outputs.queueEndpoint.value)

# Containers
AZURE_STORAGE_CONTAINER_REALTIME=realtime-data
AZURE_STORAGE_CONTAINER_AI=ai-training-datasets
AZURE_STORAGE_CONTAINER_MODELS=ml-models
AZURE_STORAGE_CONTAINER_READER=immersive-reader-content
AZURE_STORAGE_CONTAINER_ANALYTICS=analytics-data
AZURE_STORAGE_CONTAINER_BLOG=blog-assets
AZURE_STORAGE_CONTAINER_BACKUPS=backups
"@

Set-Content -Path $credsFile -Value $credsContent
(Get-Item $credsFile).Attributes = 'Hidden'
Write-Host "  [OK] Credentials saved to: $credsFile (hidden)" -ForegroundColor Green
Write-Host ""

Write-Host "WARN: Add '$credsFile' to .gitignore" -ForegroundColor Yellow
Write-Host ""

# Display information
Write-Host "Blob Containers Created:" -ForegroundColor Yellow
Write-Host "  1. realtime-data          - Real-time visitor metrics" -ForegroundColor Cyan
Write-Host "  2. ai-training-datasets   - ML training datasets" -ForegroundColor Cyan
Write-Host "  3. ml-models              - Trained model artifacts" -ForegroundColor Cyan
Write-Host "  4. immersive-reader-content - Immersive reader data" -ForegroundColor Cyan
Write-Host "  5. analytics-data         - Analytics processing files" -ForegroundColor Cyan
Write-Host "  6. blog-assets            - Blog media and content" -ForegroundColor Cyan
Write-Host "  7. backups                - Backup archives" -ForegroundColor Cyan
Write-Host ""

Write-Host "File Shares Created:" -ForegroundColor Yellow
Write-Host "  1. cache (100 GB quota)    - Cache storage" -ForegroundColor Cyan
Write-Host ""

Write-Host "Tables Created:" -ForegroundColor Yellow
Write-Host "  1. VisitorMetrics         - Visitor tracking data" -ForegroundColor Cyan
Write-Host "  2. PerformanceMetrics     - Performance metrics" -ForegroundColor Cyan
Write-Host ""

Write-Host "Queues Created:" -ForegroundColor Yellow
Write-Host "  1. ai-training-jobs       - AI training job queue" -ForegroundColor Cyan
Write-Host "  2. data-processing        - Data processing queue" -ForegroundColor Cyan
Write-Host ""

Write-Host "Storage infrastructure deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update GitHub Secrets with storage credentials" -ForegroundColor Cyan
Write-Host "  2. Configure Container Apps to use storage" -ForegroundColor Cyan
Write-Host "  3. Update immersive reader to fetch from storage" -ForegroundColor Cyan
Write-Host "  4. Configure AI training pipeline with datasets" -ForegroundColor Cyan
Write-Host ""

# Offer to configure GitHub Secrets
$configSecrets = Read-Host "Configure GitHub Secrets now? (y/n)"
if ($configSecrets -eq 'y') {
    Write-Host ""
    Write-Host "Configuring GitHub Secrets..." -ForegroundColor Yellow
    
    try {
        gh secret set AZURE_STORAGE_ACCOUNT_NAME --body $storageAccountName
        gh secret set AZURE_STORAGE_ACCOUNT_KEY --body $storageAccountKey
        gh secret set AZURE_STORAGE_CONNECTION_STRING --body $connectionString
        Write-Host "  [OK] GitHub Secrets configured successfully" -ForegroundColor Green
    } catch {
        Write-Host "  WARN: Could not configure GitHub Secrets (gh CLI may not be installed)" -ForegroundColor Yellow
        Write-Host "     Run these commands manually:" -ForegroundColor Yellow
        Write-Host "     gh secret set AZURE_STORAGE_ACCOUNT_NAME --body '$storageAccountName'" -ForegroundColor Gray
        Write-Host "     gh secret set AZURE_STORAGE_ACCOUNT_KEY --body '$storageAccountKey'" -ForegroundColor Gray
        Write-Host "     gh secret set AZURE_STORAGE_CONNECTION_STRING --body '$connectionString'" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "[OK] Deployment complete!" -ForegroundColor Green
