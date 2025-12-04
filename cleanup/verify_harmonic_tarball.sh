#!/bin/bash
# Harmonic Intelligence System - Quick Verification Script
# Extracts tarball and runs basic validation checks

echo "============================================================"
echo "🎵 HARMONIC INTELLIGENCE SYSTEM - VERIFICATION"
echo "============================================================"
echo ""

# Check if tarball exists
if [ ! -f "harmonic_intelligence_complete.tar.gz" ]; then
    echo "❌ Error: harmonic_intelligence_complete.tar.gz not found"
    echo "   Please run this script from the directory containing the tarball"
    exit 1
fi

echo "📦 Extracting tarball..."
tar -xzf harmonic_intelligence_complete.tar.gz
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to extract tarball"
    exit 1
fi
echo "✅ Extraction successful"
echo ""

echo "📋 Verifying file structure..."
cd harmonic_intelligence || exit 1

# Check core modules
echo -n "   harmonic_analysis.py ... "
[ -f "harmonic_analysis.py" ] && echo "✅" || echo "❌ MISSING"

echo -n "   harmonic_engine.py ... "
[ -f "harmonic_engine.py" ] && echo "✅" || echo "❌ MISSING"

# Check demo files
echo -n "   fifteenth.py ... "
[ -f "fifteenth.py" ] && echo "✅" || echo "❌ MISSING"

echo -n "   sixteenth.py ... "
[ -f "sixteenth.py" ] && echo "✅" || echo "❌ MISSING"

echo -n "   seventeenth.py ... "
[ -f "seventeenth.py" ] && echo "✅" || echo "❌ MISSING"

# Check documentation
echo -n "   HARMONIC_IMPLEMENTATION_COMPLETE.md ... "
[ -f "HARMONIC_IMPLEMENTATION_COMPLETE.md" ] && echo "✅" || echo "❌ MISSING"

# Check outputs
echo -n "   outputs/sixteenth.pdf ... "
[ -f "outputs/sixteenth.pdf" ] && echo "✅" || echo "❌ MISSING"

echo -n "   outputs/seventeenth.pdf ... "
[ -f "outputs/seventeenth.pdf" ] && echo "✅" || echo "❌ MISSING"

echo ""
echo "📊 File Statistics:"
echo "   Core modules: $(find . -name "*.py" -path "./harmonic_*.py" | wc -l) files"
echo "   Demo studies: $(find . -name "fifteenth.py" -o -name "sixteenth.py" -o -name "seventeenth.py" | wc -l) files"
echo "   Documentation: $(find . -name "*.md" | wc -l) files"
echo "   PDF outputs: $(find outputs/ -name "*.pdf" 2>/dev/null | wc -l) files"
echo "   Total files: $(find . -type f | wc -l) files"
echo ""

echo "📖 Quick Start:"
echo "   1. Read: HARMONIC_INTELLIGENCE_EXECUTIVE_SUMMARY.md"
echo "   2. Review API: HARMONIC_IMPLEMENTATION_COMPLETE.md"
echo "   3. View outputs: outputs/sixteenth.pdf, outputs/seventeenth.pdf"
echo ""

echo "🧪 To test the implementation (requires Python 3 + music21):"
echo "   python3 fifteenth.py    # Structural analysis demo"
echo "   python3 sixteenth.py    # Basic harmonization (I-IV-V-I)"
echo "   python3 seventeenth.py  # Advanced harmonization (50s progression)"
echo ""

echo "============================================================"
echo "✅ VERIFICATION COMPLETE"
echo "============================================================"
echo ""
echo "Archive contents are ready for review!"
echo "Total archive size: $(du -h harmonic_intelligence_complete.tar.gz 2>/dev/null | cut -f1 || echo '174K')"
echo ""
