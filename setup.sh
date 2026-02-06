#!/bin/bash

echo "🚀 Setting up TIM VM Agent (Cosmic Edition)..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install uv
uv pip install --system .[dev]
uv pip install --system torch torch-geometric networkx scipy fastapi uvicorn pydantic requests

# Setup git hooks
echo "🔗 Setting up git hooks..."
chmod +x .githooks/*
if [ -d .git ]; then
    git config core.hooksPath .githooks
    echo "Git hooks configured."
fi

# Setup environment
echo "🌱 Setting up environment..."
if [ ! -f .env ]; then
    echo "GITHUB_WEBHOOK_SECRET=default_secret" > .env
    echo "COSMIC_WEBHOOK_SECRET=cosmic_secret" >> .env
    echo "SLACK_WEBHOOK_URL=" >> .env
    echo "DB_PASSWORD=password" >> .env
fi

# Compile Components
mkdir -p bin
echo "🔨 Compiling TIM VM core (V3.0)..."
gcc -O3 -o bin/tim_vm tim_vm/tim_vm.c -lpthread -lm

echo "🔨 Compiling Rosehip Filter..."
gcc -O3 -o bin/rosehip_filter src/rosehip_filter.c -lm

# Initialize tests
echo "🧪 Running initial cosmic tests..."
chmod +x scripts/run_cosmic_tests.sh
./scripts/run_cosmic_tests.sh

echo "✅ Setup complete! The Cathedral is online."
