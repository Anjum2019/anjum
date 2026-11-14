<#
.SYNOPSIS
    Fixes the "GH013: Push cannot contain secrets" rejection caused by
    AI Agent/.env being TRACKED in your local repo.

.DESCRIPTION
    Your VS Code git log shows the real problem: 'AI Agent/.env' is tracked in
    the index, so every commit re-includes it and every push is rejected with a
    new commit SHA. .gitignore cannot help while the file is tracked.

    This script:
      1. clears a stale .git\index.lock (if no git process is running)
      2. backs up your current branch
      3. collapses your unpushed commits into ONE clean commit
      4. removes AI Agent/.env from the index (the file stays on disk)
      5. verifies no gsk_ key remains, then pushes

.EXAMPLE
    cd "C:\AI Programming\anjum"
    powershell -ExecutionPolicy Bypass -File .\scripts\fix-push-windows.ps1

.EXAMPLE
    # do everything except the push, so you can inspect first
    powershell -ExecutionPolicy Bypass -File .\scripts\fix-push-windows.ps1 -NoPush
#>

param(
    [string]$SecretPath = "AI Agent/.env",
    [string]$Message    = "Update AI Agent work (.env untracked)",
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

function Write-Step($t) { Write-Host "`n==> $t" -ForegroundColor Cyan }
function Write-Ok($t)   { Write-Host "  ok  $t" -ForegroundColor Green }
function Write-Bad($t)  { Write-Host "  !!  $t" -ForegroundColor Red }

# ------------------------------------------------------------------ 0. sanity
$root = (& git rev-parse --show-toplevel) 2>$null
if (-not $root) { Write-Bad "Run this from inside your git repository."; exit 1 }
Write-Ok "Repository: $root"

& git rev-parse --verify origin/main *> $null
if ($LASTEXITCODE -ne 0) { Write-Bad "No origin/main. Run: git fetch origin"; exit 1 }

# --------------------------------------------------- 1. clear a stale lock file
$lock = Join-Path $root ".git\index.lock"
if (Test-Path $lock) {
    $gitProcs = Get-Process -Name git, git-remote-https -ErrorAction SilentlyContinue
    if ($gitProcs) {
        Write-Bad "index.lock exists AND git is running (PID $($gitProcs.Id -join ', '))."
        Write-Bad "Close VS Code's Source Control or wait for it to finish, then re-run."
        exit 1
    }
    Write-Step "Removing stale $lock"
    Remove-Item -Force $lock
    Write-Ok "Stale lock removed."
} else {
    Write-Ok "No index.lock present."
}

# ------------------------------------------------------------- 2. safety backup
$stamp  = Get-Date -Format "yyyyMMdd-HHmmss"
$branch = (& git rev-parse --abbrev-ref HEAD).Trim()
$backup = "backup/pre-env-fix-$stamp"
& git branch $backup HEAD
Write-Ok "Backup branch created: $backup  (undo with: git reset --hard $backup)"

$originMain = (& git rev-parse origin/main).Trim()
$unpushed   = (& git rev-list --count "origin/main..HEAD").Trim()
Write-Ok "origin/main = $($originMain.Substring(0,7));  $unpushed unpushed commit(s)"

# --------------------------------------- 3. make sure .gitignore covers .env
$gi = Join-Path $root ".gitignore"
if (-not (Test-Path $gi)) { New-Item -ItemType File -Path $gi | Out-Null }
$rules = @(".env", ".env.*", "!.env.example")
$existing = Get-Content $gi -ErrorAction SilentlyContinue
$missing  = $rules | Where-Object { $existing -notcontains $_ }
if ($missing) {
    Add-Content -Path $gi -Value $missing
    Write-Ok "Added ignore rules: $($missing -join ', ')"
} else {
    Write-Ok ".gitignore already ignores .env"
}

# ------------------------------- 4. collapse unpushed history into one commit
#    --soft keeps every file change staged and leaves the working tree alone.
Write-Step "Collapsing the $unpushed unpushed commit(s) into one clean commit"
& git reset --soft origin/main
if ($LASTEXITCODE -ne 0) { Write-Bad "git reset failed."; exit 1 }

# Drop the secret from the index. The file on disk is NOT deleted.
& git rm -r --cached --ignore-unmatch -- $SecretPath | Out-Null
Write-Ok "Untracked '$SecretPath' (file kept on disk)"

& git add -A
& git commit -q -m $Message
if ($LASTEXITCODE -ne 0) { Write-Bad "git commit failed - nothing to commit?"; exit 1 }
Write-Ok "Committed."

# ------------------------------------------------------------- 5. verify + push
Write-Step "Verifying no Groq key remains in what will be pushed"
$leaks = @()
$commits = & git rev-list "origin/main..HEAD"
foreach ($c in $commits) {
    $found = & git grep -a -I -nE "gsk_[A-Za-z0-9]{20,}" $c -- 2>$null
    if ($found) { $leaks += $found }
}
if ($leaks.Count -gt 0) {
    Write-Bad "Key still present - aborting before push:"
    $leaks | ForEach-Object { Write-Host "      $_" }
    Write-Bad "Restore with: git reset --hard $backup"
    exit 1
}
Write-Ok "No gsk_ key in any commit to be pushed."

$staged = (& git ls-files -- $SecretPath)
if ($staged) { Write-Bad "'$SecretPath' is still tracked."; exit 1 }
Write-Ok "'$SecretPath' is untracked."

& git merge-base --is-ancestor origin/main HEAD
if ($LASTEXITCODE -ne 0) { Write-Bad "Not a fast-forward. Restore: git reset --hard $backup"; exit 1 }
Write-Ok "Fast-forward push is safe."

if ($NoPush) {
    Write-Host "`nReady. Push when you are sure with:  git push origin main" -ForegroundColor Yellow
    exit 0
}

Write-Step "Pushing"
& git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Bad "Push was rejected. Restore your work with: git reset --hard $backup"
    exit 1
}

Write-Host ""
Write-Ok "Pushed. Your local work is on GitHub and .env stayed on your disk."
Write-Host ""
Write-Host "  REMINDER: revoke the exposed Groq key at https://console.groq.com/keys" -ForegroundColor Yellow
Write-Host "  The old key is still in this repo's public history on main." -ForegroundColor Yellow
