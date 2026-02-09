#!/bin/bash

# MeshCipher Discord Bot - Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION+ is required (found $PYTHON_VERSION)"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Error: .env file not found."
    echo "Copy .env.example to .env and fill in your values:"
    echo "  cp .env.example .env"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create data directory
mkdir -p data logs

# Initialize data files if they don't exist
if [ ! -f "data/bugs.json" ]; then
    echo "{}" > data/bugs.json
fi

if [ ! -f "data/features.json" ]; then
    echo "{}" > data/features.json
fi

echo "Starting MeshCipher Bot..."
python3 -m src.bot
