#!/usr/bin/env bash
set -e
echo "🔐 Aurum Grid – Verificação de Integridade dos Artefatos de Comunicação"
if ! sha256sum -c SHA256SUMS --quiet; then
  echo "❌ Hash inválido para communication_playbook.json – abortando"; exit 1
fi
echo "✅ Hash SHA-256 OK"

# Placeholder for GPG verification
echo "⚠️ Assinatura GPG não implementada neste script. Verificação de hash concluída."

# if ! gpg --verify SHA256SUMS.asc SHA256SUMS --quiet; then
#   echo "❌ Assinatura GPG inválida – abortando"; exit 1
# fi
# echo "✅ Assinatura GPG OK"

echo "🎉 Pacote verificado com sucesso (apenas hash)"