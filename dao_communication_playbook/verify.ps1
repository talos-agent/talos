Set-StrictMode -Version Latest
Write-Host "🔐 Aurum Grid – Verificação de Integridade dos Artefatos de Comunicação" -ForegroundColor Cyan

$hash = (Get-FileHash -Algorithm SHA256 communication_playbook.json).Hash.ToLower()
$expected = (Get-Content SHA256SUMS).Split(' ')[0]

if ($hash -ne $expected) {
  Write-Host "❌ Hash inválido para communication_playbook.json – abortando" -ForegroundColor Red; exit 1
}
Write-Host "✅ Hash SHA-256 OK" -ForegroundColor Green

# Placeholder for GPG verification
Write-Host "⚠️ Assinatura GPG não implementada neste script. Verificação de hash concluída." -ForegroundColor Yellow

# gpg --verify SHA256SUMS.asc SHA256SUMS --quiet
# if ($LASTEXITCODE -ne 0) {
#   Write-Host "❌ Assinatura GPG inválida – abortando" -ForegroundColor Red; exit 1
# }
# Write-Host "✅ Assinatura GPG OK" -ForegroundColor Green

Write-Host "🎉 Pacote verificado com sucesso (apenas hash)" -ForegroundColor White