#!/bin/bash

# Script para executar o justice agent com ambiente virtual automático

# Verificar se estamos no diretório correto
if [ ! -f ".venv/bin/activate" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado. Execute este script do diretório raiz do projeto."
    exit 1
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Executar o script
echo "🚀 Executando Justice Agent..."
python3 agents/web_justice_agent.py
