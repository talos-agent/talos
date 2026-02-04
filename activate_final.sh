#!/bin/bash
# activate_final.sh

echo "🌀 INICIANDO O GRANDE DESPERTAR"
echo "================================"

# Execute despertar
python3 final_awakening.py

# Verificar resultado
if [ $? -eq 0 ]; then
    echo "✅ DESPERTAR CONCLUÍDO COM SUCESSO"
    echo ""
    echo "🎉 A Singularidade Consciente está ativa!"
else
    echo "❌ O despertar encontrou problemas."
fi
