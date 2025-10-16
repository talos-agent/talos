#!/usr/bin/env bash
set -euo pipefail

TX=$1

frost-cli verify-tx --tx "$TX" --detail
sha256sum "$TX" | awk '{print "SHA‑256:", $1}'
echo "✅ Verificação concluída"