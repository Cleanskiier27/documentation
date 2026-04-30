# 🔒 NetworkBuster — Security Automation Scripts

A suite of PowerShell scripts to automate security operations for the NetworkBuster infrastructure: rotating exposed Azure credentials and hardening all GitHub repositories.

---

## 📁 Scripts Overview

| Script | Purpose |
|---|---|
| [`nike-just-do-it.ps1`](#nike-just-do-itps1) | **Master script** — runs all operations in sequence |
| [`rotate-azure-credentials.ps1`](#rotate-azure-credentialsps1) | Rotates Azure Container Registry passwords |
| [`enable-security-features.ps1`](#enable-security-featuresps1) | Enables GitHub security features on all repos |
| [`update-gitignore.ps1`](#update-gitignoreps1) | Updates `.gitignore` with credential exclusion patterns |

---

## ✅ Prerequisites

| Tool | Install Link | Check |
|---|---|---|
| **Azure CLI** (`az`) | https://aka.ms/installazurecliwindows | `az --version` |
| **GitHub CLI** (`gh`) | https://cli.github.com/ | `gh --version` |
| **PowerShell 5.1+** | Built-in on Windows 10/11 | `$PSVersionTable.PSVersion` |
| **Git** | https://git-scm.com/ | `git --version` |

Authenticate before running:

```powershell
# Azure
az login
az account set --subscription cdb580bc-e2e9-4866-aac2-aa86f0a25cb3

# GitHub
gh auth login
```

---

## 🚀 How to Use

### Quick Start (All-in-One)

```powershell
cd security-scripts
.\nike-just-do-it.ps1
```

Type `JUST-DO-IT` when prompted to confirm, and all three operations will run in sequence.

---

### Individual Scripts

#### `rotate-azure-credentials.ps1`

Rotates both `password1` and `password2` for the `networkbusterlo25gft5nqwzg` Azure Container Registry.

```powershell
.\rotate-azure-credentials.ps1
```

**What it does:**
1. Logs into Azure and sets the correct subscription.
2. Displays the current credentials (masked, first 10 chars only).
3. Prompts for confirmation — type `YES` to proceed.
4. Rotates `password1`, then `password2`.
5. Displays the new credentials (masked).
6. Saves full credentials to `azure-credentials-<timestamp>.json`.
7. Prints GitHub Secrets update URLs for all three repos.
8. Tests the new credentials with `az acr login`.

---

#### `enable-security-features.ps1`

Enables vulnerability alerts and Dependabot on all NetworkBuster repositories via the GitHub API.

```powershell
.\enable-security-features.ps1
```

**What it does:**
1. Checks that GitHub CLI is installed and authenticated.
2. Enables vulnerability alerts on each repo via `gh api`.
3. Enables Dependabot automated security fixes on each repo.
4. Prints manual instructions for enabling Secret Scanning and Push Protection in the GitHub UI.

> **Note:** Secret Scanning and Push Protection must be enabled manually in each repository's Settings → Security Analysis page.

---

#### `update-gitignore.ps1`

Adds credential and secret exclusion patterns to the `.gitignore` of the current repository, then commits and pushes.

```powershell
# Run from the root of a git repository
cd path\to\your\repo
.\path\to\security-scripts\update-gitignore.ps1
```

**Patterns added:**
```
*secret*
*credential*
*password*
*.key
*.pem
deployment-output.json
azure-credentials*.json
.azure/
.env
.env.*
!.env.example
config.local.*
id_rsa / id_ed25519 (SSH keys)
.aws/credentials (AWS)
*.token / *.pfx / *.p12
```

---

#### `nike-just-do-it.ps1`

Master orchestrator — runs all three scripts in sequence.

```powershell
.\nike-just-do-it.ps1
```

**Steps:**
1. Rotate Azure credentials → `rotate-azure-credentials.ps1`
2. Enable GitHub security features → `enable-security-features.ps1`
3. Update `.gitignore` → `update-gitignore.ps1`

Prints a final summary showing the status of each step.

> **Note:** Git history cleanup is intentionally **not** included. See the [troubleshooting](#-troubleshooting) section if you need to purge sensitive data from git history.

---

## ⚠️ Safety Warnings

- **Rotating ACR credentials immediately invalidates the old passwords.** Any service using the old passwords (CI/CD pipelines, Docker logins) will fail until you update GitHub Secrets.
- **The saved `azure-credentials-*.json` file contains plaintext passwords.** Delete it as soon as you have updated all GitHub Secrets.
- **`.gitignore` only protects future commits.** Files already tracked by git must be removed with `git rm --cached <filename>` and the history should be cleaned if they contained secrets.
- **Never commit the `azure-credentials-*.json` output file.** It is matched by the pattern added to `.gitignore` by `update-gitignore.ps1`.

---

## 🔐 Credential Rotation Checklist

```
IMMEDIATE (run these scripts):
☐ Rotate ACR password1
☐ Rotate ACR password2

WITHIN 1 HOUR:
☐ Update AZURE_REGISTRY_USERNAME in GitHub Secrets (all 3 repos)
☐ Update AZURE_REGISTRY_PASSWORD in GitHub Secrets (all 3 repos)
☐ Delete azure-credentials-*.json from disk
☐ Trigger test CI/CD run to verify new credentials work

WITHIN 24 HOURS:
☐ Enable Secret Scanning in GitHub UI (all 3 repos)
☐ Enable Push Protection in GitHub UI (all 3 repos)
☐ Update .gitignore (run update-gitignore.ps1)
☐ Review Azure Activity Logs for unauthorized access
☐ Rotate Vercel tokens if exposed
```

### GitHub Secrets Update URLs

| Repository | Secrets URL |
|---|---|
| `Cleanskiier27/documentation` | https://github.com/Cleanskiier27/documentation/settings/secrets/actions |
| `Cleanskiier27/nasa-waste-calc` | https://github.com/Cleanskiier27/nasa-waste-calc/settings/secrets/actions |
| `Cleanskiier27/artemis-r-navigation` | https://github.com/Cleanskiier27/artemis-r-navigation/settings/secrets/actions |

**Secrets to update:**

| Secret Name | Value |
|---|---|
| `AZURE_REGISTRY_USERNAME` | `networkbusterlo25gft5nqwzg` |
| `AZURE_REGISTRY_PASSWORD` | *(new password from rotation script)* |
| `AZURE_REGISTRY_SERVER` | `networkbusterlo25gft5nqwzg.azurecr.io` |

---

## ✔️ Post-Rotation Verification Steps

```powershell
# 1. Confirm new credentials work
az acr login --name networkbusterlo25gft5nqwzg

# 2. Check Azure Activity Logs for unauthorized access
az monitor activity-log list `
  --resource-group networkbuster-rg `
  --start-time (Get-Date).AddDays(-7).ToString("yyyy-MM-dd") `
  --output table

# 3. List images in the registry
az acr repository list --name networkbusterlo25gft5nqwzg --output table

# 4. Verify GitHub Actions can push (trigger a CI run)
# Push a dummy commit to trigger the pipeline and check it succeeds
```

---

## 🛠️ Troubleshooting

### `az login` opens a browser but hangs
```powershell
az login --use-device-code
```

### `gh auth login` fails
```powershell
gh auth login --web
# OR using a Personal Access Token:
$env:GH_TOKEN = "your-pat-here"
gh auth status
```

### ACR login test fails with "Docker daemon not running"
The credential rotation itself succeeded. The Docker login test requires Docker Desktop to be running.
```powershell
# Test using token only (no Docker required)
az acr login --name networkbusterlo25gft5nqwzg --expose-token
```

### git push fails in `update-gitignore.ps1`
```powershell
git pull --rebase
git push
```

### Purging sensitive data from git history (manual step)
```powershell
# Run ONLY if you need to remove a file from all historical commits
git filter-branch --force --index-filter `
  "git rm --cached --ignore-unmatch _03-exposed-secrets.md" `
  --prune-empty --tag-name-filter cat -- --all

git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (rewrites history — coordinate with all collaborators first)
git push origin --force --all
git push origin --force --tags
```

---

## 📞 Support

For issues with these scripts, open an issue in [Cleanskiier27/documentation](https://github.com/Cleanskiier27/documentation/issues).
