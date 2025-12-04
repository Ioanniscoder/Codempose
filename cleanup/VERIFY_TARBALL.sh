#!/bin/bash
# Codempose Release Verification Script
# Tests that the tarball contains all essential components

set -e

echo "=========================================="
echo "Codempose Release Verification"
echo "=========================================="
echo ""

TARBALL="codempose-release-20251019-154528.tar.gz"

if [ ! -f "$TARBALL" ]; then
    echo "❌ Error: Tarball not found: $TARBALL"
    exit 1
fi

echo "✅ Tarball found: $TARBALL"
echo "   Size: $(ls -lh $TARBALL | awk '{print $5}')"
echo ""

echo "🔍 Verifying contents..."
echo ""

# Check critical files
CRITICAL_FILES=(
    "Codempose/README.md"
    "Codempose/generate_study.py"
    "Codempose/requirements.txt"
    "Codempose/src/score_builder.py"
    "Codempose/src/transformations.py"
    "Codempose/src/lily_converter.py"
    "Codempose/src/harmonic_engine.py"
    "Codempose/src/harmonic_analysis.py"
    "Codempose/DOCUMENTATION/HYBRID_SUFFIX_MODEL.md"
    "Codempose/DOCUMENTATION/CREATIVE_EXAMPLES_COMPLETE.md"
)

MISSING=0
for file in "${CRITICAL_FILES[@]}"; do
    if tar -tzf "$TARBALL" "$file" &>/dev/null; then
        echo "  ✅ $file"
    else
        echo "  ❌ MISSING: $file"
        MISSING=$((MISSING + 1))
    fi
done

echo ""

if [ $MISSING -gt 0 ]; then
    echo "❌ Verification FAILED: $MISSING critical files missing"
    exit 1
fi

echo "✅ All critical files present"
echo ""

# Check directories
echo "📂 Verifying directory structure..."
echo ""

CRITICAL_DIRS=(
    "Codempose/src"
    "Codempose/studies"
    "Codempose/studies/OLD"
    "Codempose/outputs/TEMPLATES"
    "Codempose/DOCUMENTATION"
    "Codempose/tests"
)

for dir in "${CRITICAL_DIRS[@]}"; do
    if tar -tzf "$TARBALL" | grep -q "^${dir}/"; then
        COUNT=$(tar -tzf "$TARBALL" | grep "^${dir}/" | wc -l)
        echo "  ✅ $dir ($COUNT files)"
    else
        echo "  ❌ MISSING: $dir"
        MISSING=$((MISSING + 1))
    fi
done

echo ""

if [ $MISSING -gt 0 ]; then
    echo "❌ Verification FAILED: $MISSING critical directories missing"
    exit 1
fi

echo "✅ All critical directories present"
echo ""

# Count files
echo "📊 File counts:"
TOTAL=$(tar -tzf "$TARBALL" | wc -l)
PY_FILES=$(tar -tzf "$TARBALL" | grep "\.py$" | wc -l)
MD_FILES=$(tar -tzf "$TARBALL" | grep "\.md$" | wc -l)
echo "  • Total files: $TOTAL"
echo "  • Python files: $PY_FILES"
echo "  • Markdown docs: $MD_FILES"
echo ""

# Check for new features
echo "🆕 Verifying new features..."
echo ""

NEW_FEATURES=(
    "HYBRID_SUFFIX_MODEL"
    "CREATIVE_EXAMPLES"
    "harmonize_part"
    "events_to_tinynotation"
)

FEATURE_MISSING=0
for feature in "${NEW_FEATURES[@]}"; do
    if tar -xzf "$TARBALL" -O | grep -q "$feature"; then
        echo "  ✅ Feature found: $feature"
    else
        echo "  ⚠️  Feature not found in tarball text: $feature"
        FEATURE_MISSING=$((FEATURE_MISSING + 1))
    fi
done

echo ""

# Summary
echo "=========================================="
if [ $MISSING -eq 0 ]; then
    echo "✅ VERIFICATION PASSED"
    echo "=========================================="
    echo ""
    echo "Tarball is complete and ready for distribution!"
    echo ""
    echo "📦 To extract:"
    echo "   tar -xzf $TARBALL"
    echo ""
    echo "🚀 To get started:"
    echo "   cd Codempose"
    echo "   pip install -r requirements.txt"
    echo "   python generate_study.py 1 \"My First Study\""
    echo "   python studies/first.py"
    echo ""
    echo "📖 Read RELEASE_NOTES_20251019.md for complete feature list"
    exit 0
else
    echo "❌ VERIFICATION FAILED"
    echo "=========================================="
    echo ""
    echo "Please check the missing files/directories above"
    exit 1
fi
