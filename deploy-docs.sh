#!/usr/bin/env bash
# --------------------------------------------------------------------------
#  Docsify Auto-Deploy  –  PowerShell & Bash  –  https://github.com/uniaolives/agi
#  Uso:  bash deploy-docs-unified  ou  pwsh -File deploy-docs-unified.ps1
# --------------------------------------------------------------------------
set -euo pipefail
##############  BASH SECTION  ###############################################
if [ -n "${BASH_VERSION:-}" ]; then
LOG_FILE="deploy-log-$(date +%F_%H-%M-%S).txt"
echo "🚀 Iniciando deploy Docsify (Bash)" | tee -a "$LOG_FILE"

# Detecta branch
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
echo "✅ Branch detectada: $BRANCH" | tee -a "$LOG_FILE"

# Stash / checkout / add
git stash push -m "Pre-deploy stash" &>>"$LOG_FILE" || true
git checkout "$BRANCH" &>>"$LOG_FILE"

git add docs/
if git diff --cached --quiet; then
  echo "ℹ️  Sem mudanças para enviar." | tee -a "$LOG_FILE"
  exit 0
fi

# Dry-run
if [[ "${1:-}" == "--dry-run" ]]; then
  echo "🔍 DryRun ativado — nenhuma alteração será enviada." | tee -a "$LOG_FILE"
  git diff --cached | tee -a "$LOG_FILE"
  exit 0
fi

# Commit + push
git commit -m "docs: auto-deploy $(date '+%Y-%m-%d %H:%M:%S')" &>>"$LOG_FILE"
git push origin "$BRANCH" &>>"$LOG_FILE"

echo "✅ Deploy concluído! Logs em: $LOG_FILE"
exit 0
fi
##############  POWERSHELL SECTION  #########################################
if ($PSCommandPath) {
$logFile = "deploy-log-$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').txt"
Write-Host "🚀 Iniciando deploy Docsify (PowerShell)" -ForegroundColor Cyan

$branch = git rev-parse --abbrev-ref HEAD 2>$null
if (-not $branch) { $branch = "main" }
Write-Host "✅ Branch detectada: $branch" -ForegroundColor Green

git stash push -m "Pre-deploy stash" | Out-File -Append $logFile
git checkout $branch | Out-File -Append $logFile

git add docs/
if ((git diff --cached --quiet) -eq 0) {
  Write-Host "ℹ️  Sem mudanças para enviar." -ForegroundColor Yellow
  exit 0
}

if ($args[0] -eq "--dry-run") {
  Write-Host "🔍 DryRun ativado — nenhuma alteração será enviada." -ForegroundColor Magenta
  git diff --cached | Tee-Object -FilePath $logFile
  exit 0
}

git commit -m "docs: auto-deploy $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -Append $logFile
git push origin $branch | Out-File -Append $logFile

Write-Host "✅ Deploy concluído! Logs em: $logFile" -ForegroundColor Green
exit 0
}
