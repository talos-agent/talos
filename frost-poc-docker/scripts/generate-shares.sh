#!/usr/bin/env bash
set -euo pipefail

TOTAL=$1
THRESHOLD=$2
OUTDIR=$3

mkdir -p "$OUTDIR"
frost-cli gen-shares --total "$TOTAL" --threshold "$THRESHOLD" --out "$OUTDIR"
echo "✅ Shares geradas em $OUTDIR"