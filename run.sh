#!/bin/bash
# Quick setup script for Mac/Linux - activates VENV and runs the app
# Usage: chmod +x run.sh && ./run.sh

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║       CyberFedDefender - Quick Start Script (Mac/Linux)       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate venv
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ VENV activated"

# Check if requirements are installed
echo ""
echo "Checking dependencies..."
python -m pip -q show flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    python -m pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Start the app
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Starting Flask development server...                          ║"
echo "║  Open browser to: http://localhost:5000                        ║"
echo "║  Press Ctrl+C to stop the server                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

python app.py
