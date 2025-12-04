#!/bin/bash
# Create lean release tarball of Codempose workspace
# Includes: root files, src/, studies/OLD/, outputs/TEMPLATES/, DOCUMENTATION/

set -e

TARBALL_NAME="codempose-release-$(date +%Y%m%d-%H%M%S).tar.gz"
TEMP_DIR=$(mktemp -d)
BUILD_DIR="$TEMP_DIR/Codempose"

echo "=========================================="
echo "Creating Codempose Release Tarball"
echo "=========================================="
echo ""

# Create build directory
mkdir -p "$BUILD_DIR"

echo "📦 Copying essential files..."

# Root files (only essentials)
echo "  → Root files..."
cp generate_study.py "$BUILD_DIR/"
cp fix_browser.sh "$BUILD_DIR/"
cp fix_devcontainer.sh "$BUILD_DIR/"
[ -f .gitignore ] && cp .gitignore "$BUILD_DIR/"
[ -f README.md ] && cp README.md "$BUILD_DIR/"
[ -f requirements.txt ] && cp requirements.txt "$BUILD_DIR/"
[ -f install.sh ] && cp install.sh "$BUILD_DIR/"
[ -f Dockerfile ] && cp Dockerfile "$BUILD_DIR/"

# src/ directory (all active code)
echo "  → src/ directory..."
cp -r src "$BUILD_DIR/"
# Clean pycache
find "$BUILD_DIR/src" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR/src" -type f -name "*.pyc" -exec rm -f {} + 2>/dev/null || true

# studies/ structure
echo "  → studies/ directory..."
mkdir -p "$BUILD_DIR/studies"
cp studies/_study_path.py "$BUILD_DIR/studies/"
cp studies/__init__.py "$BUILD_DIR/studies/"
[ -f studies/README.md ] && cp studies/README.md "$BUILD_DIR/studies/"

# studies/OLD/ (archived studies)
echo "  → studies/OLD/ directory..."
cp -r studies/OLD "$BUILD_DIR/studies/"

# outputs/ structure
echo "  → outputs/ directory..."
mkdir -p "$BUILD_DIR/outputs"
[ -f outputs/.manifest ] && cp outputs/.manifest "$BUILD_DIR/outputs/"
[ -f outputs/.ok ] && cp outputs/.ok "$BUILD_DIR/outputs/"

# outputs/TEMPLATES/ (reference materials)
echo "  → outputs/TEMPLATES/ directory..."
cp -r outputs/TEMPLATES "$BUILD_DIR/outputs/"

# outputs/DOCUMENTATION/ (generated docs)
echo "  → outputs/DOCUMENTATION/ directory..."
if [ -d outputs/DOCUMENTATION ]; then
    cp -r outputs/DOCUMENTATION "$BUILD_DIR/outputs/"
fi

# DOCUMENTATION/ (project docs - includes all release notes and guides)
echo "  → DOCUMENTATION/ directory..."
cp -r DOCUMENTATION "$BUILD_DIR/"

# tests/ directory (test suite)
echo "  → tests/ directory..."
cp -r tests "$BUILD_DIR/"
# Clean pycache
find "$BUILD_DIR/tests" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR/tests" -type f -name "*.pyc" -exec rm -f {} + 2>/dev/null || true

echo ""
echo "🧹 Cleaning up..."
# Remove any remaining pycache
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -type f -name "*.pyc" -exec rm -f {} + 2>/dev/null || true

echo ""
echo "📊 Directory structure:"
cd "$TEMP_DIR"
tree -L 2 -I "__pycache__|*.pyc" Codempose/ || ls -R Codempose/

echo ""
echo "📦 Creating tarball..."
tar -czf "/workspaces/Codempose/$TARBALL_NAME" Codempose/

echo ""
echo "✅ Tarball created: $TARBALL_NAME"
ls -lh "/workspaces/Codempose/$TARBALL_NAME"

echo ""
echo "📂 Contents:"
tar -tzf "/workspaces/Codempose/$TARBALL_NAME" | head -50
echo "   ... (use 'tar -tzf $TARBALL_NAME | less' to see all)"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "=========================================="
echo "✅ Release tarball ready!"
echo "=========================================="
