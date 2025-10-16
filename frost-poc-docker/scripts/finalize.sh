#!/usr/bin/env bash
set -euo pipefail

SIGNED_PSBT=$1
OUT_TX=$2

frost-cli finalize-psbt --psbt "$SIGNED_PSBT" --out "$OUT_TX"
echo "✅ Transação finalizada: $OUT_TX"