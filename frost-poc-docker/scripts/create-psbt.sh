#!/usr/bin/env bash
set -euo pipefail

INPUTS_JSON=$1
OUT_PSBT=$2

frost-cli create-psbt --inputs "$INPUTS_JSON" --out "$OUT_PSBT"
echo "✅ PSBT criado: $OUT_PSBT"