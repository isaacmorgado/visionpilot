#!/bin/bash
# Setup script for Autonomous Computer Control System
# Run this script to set up the development environment

set -e

echo "=================================================="
echo "  Autonomous Computer Control System - Setup"
echo "=================================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

echo "Detected Python version: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "Error: Python 3.10+ is required"
    exit 1
fi
echo "✓ Python version OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists"
else
    python3 -m venv venv
    echo "  ✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "  ✓ Activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q
echo "  ✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "  ✓ Dependencies installed"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p screenshots logs
echo "  ✓ screenshots/ created"
echo "  ✓ logs/ created"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "  ✓ .env created"
    echo ""
    echo "  ⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
else
    echo ".env file already exists"
fi
echo ""

# Test imports
echo "Testing imports..."
python3 -c "
from src import (
    ComputerUseAgent,
    AgentConfig,
    ComputerController,
    ScreenCapture,
    AppleScriptRunner
)
print('  ✓ All imports successful')
"
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ] && ! grep -q "ANTHROPIC_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set"
    echo "   Set it with: export ANTHROPIC_API_KEY='your-key'"
    echo "   Or add it to the .env file"
else
    echo "✓ ANTHROPIC_API_KEY appears to be configured"
fi
echo ""

echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Grant macOS permissions (if not already done):"
echo "     - System Preferences → Security & Privacy → Privacy"
echo "     - Enable Accessibility for your terminal"
echo "     - Enable Screen Recording for your terminal"
echo ""
echo "  3. Test the installation:"
echo "     python -m src.cli info"
echo "     python -m src.cli test-permissions"
echo ""
echo "  4. Run your first task:"
echo "     python -m src.cli run 'Open Safari'"
echo ""
