#!/bin/bash
# Codempose Installation Script
# For Linux/macOS systems

set -e

echo "======================================================================="
echo "  CODEMPOSE INSTALLATION"
echo "======================================================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Check LilyPond
echo "Checking LilyPond..."
if ! command -v lilypond &> /dev/null; then
    echo "⚠️  LilyPond not found. Please install LilyPond 2.24 or later."
    echo "   Download from: http://lilypond.org/download.html"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    LILY_VERSION=$(lilypond --version | head -n 1)
    echo "✓ Found $LILY_VERSION"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --quiet --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install --quiet -r requirements.txt

echo ""
echo "======================================================================="
echo "  ✅ INSTALLATION COMPLETE"
echo "======================================================================="
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To generate your first study:"
echo "  python generate_study.py 1 'My First Study'"
echo ""
echo "To run a study:"
echo "  python studies/first.py"
echo ""
echo "Output files will be in: outputs/"
echo "======================================================================="
