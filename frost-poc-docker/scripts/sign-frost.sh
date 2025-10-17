#!/usr/bin/env bash
set -euo pipefail

UNSIGNED_PSBT=$1
SHARES_DIR=$2
OUT_PSBT=$3

# Seleciona 3 shares aleatórias
SHARES=$(ls "$SHARES_DIR" | shuf -n 3 | tr '\n' ' ')
frost-cli sign-psbt --psbt "$UNSIGNED_PSBT" --shares $SHARES --out "$OUT_PSBT"
echo "✅ PSBT parcialmente assinado: $OUT_PSBT"