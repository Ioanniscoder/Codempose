#!/bin/bash
# Build standalone Codempose executable using PyInstaller
# 
# This script creates a self-contained executable for seventh.py
# that can be distributed and run without Python installation.
#
# Requirements:
#   - PyInstaller: pip install pyinstaller
#   - All Codempose modules in current directory
#
# Usage:
#   ./build_standalone.sh
#
# Output:
#   dist/codempose-seventh (executable)

set -e  # Exit on error

echo "============================================================"
echo "🔨 Building Codempose Standalone Executable"
echo "============================================================"
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Build executable
echo "🔧 Building executable..."
echo ""

pyinstaller --onefile \
  --name=codempose-seventh \
  --add-data="project_template.py:." \
  --add-data="music_data.py:." \
  --add-data="lilypond_parser.py:." \
  --add-data="lily_tokenizer.py:." \
  --add-data="lily_token_parser.py:." \
  --add-data="lily_to_tiny.py:." \
  --add-data="relative_octave_logic.py:." \
  --add-data="data_structures.py:." \
  --add-data="composition_shorthand.py:." \
  --hidden-import=music21 \
  --hidden-import=abjad \
  --hidden-import=fractions \
  --hidden-import=pathlib \
  --hidden-import=subprocess \
  --clean \
  seventh.py

echo ""
echo "============================================================"
echo "✅ Build Complete!"
echo "============================================================"
echo ""
echo "📦 Executable created: dist/codempose-seventh"
echo ""

# Get file size
if [ -f "dist/codempose-seventh" ]; then
    SIZE=$(ls -lh dist/codempose-seventh | awk '{print $5}')
    echo "📊 File size: $SIZE"
    echo ""
    
    # Make executable
    chmod +x dist/codempose-seventh
    
    echo "🧪 Testing executable..."
    echo ""
    
    # Test run (create outputs directory first)
    mkdir -p outputs
    cd dist
    ./codempose-seventh
    cd ..
    
    echo ""
    echo "============================================================"
    echo "✅ Test Successful!"
    echo "============================================================"
    echo ""
    echo "Generated files:"
    ls -lh outputs/seventh.* 2>/dev/null || echo "  (Check outputs/ directory)"
    echo ""
    echo "📋 To distribute:"
    echo "  1. Copy dist/codempose-seventh to target system"
    echo "  2. Ensure LilyPond is installed: sudo apt install lilypond"
    echo "  3. Run: ./codempose-seventh"
    echo ""
    echo "📋 To create distribution package:"
    echo "  tar -czf codempose-seventh-standalone.tar.gz -C dist codempose-seventh"
    echo ""
else
    echo "❌ Build failed - executable not found"
    exit 1
fi
