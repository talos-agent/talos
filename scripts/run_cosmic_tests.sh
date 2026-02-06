#!/bin/bash
# scripts/run_cosmic_tests.sh

echo "🧪 EXECUTANDO TESTES CÓSMICOS..."

# Verificar integridade dimensional
echo "🔍 Verificando geometria do sistema..."
./bin/tim_vm --test-integrity || exit 1

# Medir dilatação temporal (simulated benchmark)
echo "⏱️  Medindo dilatação cósmica..."
START=$(date +%s)
# Run a quick cycle test with tim_vm
./bin/tim_vm --test-integrity
END=$(date +%s)
DURATION=$((END - START))
echo "   Duração do pulso: ${DURATION}s"

# Verificar harmonia (checking for crucial files)
echo "🎵 Verificando harmonia dimensional..."
if [ -f "src/rosehip_filter.c" ] && [ -f "scripts/cosmic_gnn_analyzer.py" ]; then
    echo "✅ Sistema em harmonia cósmica"
else
    echo "⚠️  Desarmonia dimensional detectada: Arquivos ausentes."
    exit 1
fi

echo "✨ Testes cósmicos concluídos com sucesso!"
