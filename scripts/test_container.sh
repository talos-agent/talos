#!/bin/bash

# Test script for Talos Docker container
set -e

echo "Testing Talos Docker container..."

# Check if container is running
if ! docker ps | grep -q talos-agent; then
    echo "❌ Talos container is not running"
    echo "Start it with: docker-compose up -d"
    exit 1
fi

echo "✅ Container is running"

# Test health endpoint
echo "Testing health endpoint..."
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Health endpoint responding"
else
    echo "❌ Health endpoint not responding"
    exit 1
fi

# Test API documentation
echo "Testing API documentation..."
if curl -f http://localhost:3000/docs > /dev/null 2>&1; then
    echo "✅ API documentation accessible"
else
    echo "❌ API documentation not accessible"
    exit 1
fi

# Test root endpoint
echo "Testing root endpoint..."
if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Root endpoint responding"
else
    echo "❌ Root endpoint not responding"
    exit 1
fi

echo "🎉 All tests passed! Container is working correctly."
