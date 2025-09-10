#!/bin/bash
# Startup script for Talos server with database migrations

set -e

echo "Starting Talos server..."

# Run database migrations
echo "Running database migrations..."
python -m talos migrations upgrade

# Start the FastAPI server
echo "Starting FastAPI server..."
python -m talos.cli.server
