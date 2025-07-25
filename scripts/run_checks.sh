#!/bin/bash

# This script runs ruff, mypy, and pytest, similar to the CI.

# Exit immediately if a command exits with a non-zero status.
set -e

# Install dependencies if the virtual environment doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install "uv==0.2.22"
    uv pip install -e .[dev]
else
    source .venv/bin/activate
fi

# Run isort
echo "Running isort..."
uv run isort .

# Run ruff
echo "Running ruff..."
uv run ruff format .
uv run ruff check .

# Run mypy
echo "Running mypy..."
uv run mypy src

# Run pytest
echo "Running pytest..."
uv run pytest
