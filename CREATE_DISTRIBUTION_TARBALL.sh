#!/bin/bash
# Create complete distribution tarball of Codempose
# Updated: November 2025 - Includes Station 2 Snippet Library feature

set -e

# Fixed filename (no timestamp)
TARBALL_NAME="codempose_complete_distribution.tar.gz"

echo "=========================================="
echo "Creating Codempose Complete Distribution"
echo "=========================================="
echo "Filename: $TARBALL_NAME (will overwrite existing)"
echo ""

echo "📦 Preparing files..."

# Create temporary exclusion list
cat > /tmp/tar_exclude_$$.txt << 'EXCLUDE'
.git
.venv
__pycache__
*.pyc
.pytest_cache
.devcontainer
.vscode
.backups
.safety_backup_before_restore
backup
cleanup
Gemini
parser_project
outputs/*.ly
outputs/*.pdf
outputs/*.midi
outputs/*.musicxml
outputs/102th.py
codempose_complete_distribution.tar.gz
codempose_complete_distribution_*.tar.gz
codempose-release-*.tar.gz
EXCLUDE

echo "🗜️  Creating tarball with core distribution..."
tar -czf "$TARBALL_NAME" \
    --exclude-from=/tmp/tar_exclude_$$.txt \
    --transform 's,^,Codempose/,' \
    src/ \
    studies/*.py \
    studies/_study_path.py \
    studies/__init__.py \
    studies/README.md \
    studies/OLD/ \
    tests/ \
    outputs/TEMPLATES/ \
    outputs/DOCUMENTATION/ \
    DOCUMENTATION/ \
    generate_study.py \
    setup_paths.py \
    requirements.txt \
    install.sh \
    install_windows.bat \
    fix_windows_install.py \
    README.md \
    SETUP.md \
    INSTALL_WINDOWS.md \
    WINDOWS_README.md \
    UPDATES_2025_10_24.md \
    Dockerfile \
    fix_browser.sh \
    fix_devcontainer.sh \
    .gitignore 2>/dev/null || true

# Cleanup
rm -f /tmp/tar_exclude_$$.txt

echo ""
echo "✅ Tarball created: $TARBALL_NAME"
ls -lh "$TARBALL_NAME"

echo ""
echo "📊 Contents summary:"
tar -tzf "$TARBALL_NAME" | head -50
echo "   ... (total $(tar -tzf "$TARBALL_NAME" | wc -l) files)"

echo ""
echo "🔍 Key features in this distribution:"
echo "   ✓ Station 2 Snippet Library (editable LilyPond output)"
echo "   ✓ Blueprint String Framework"
echo "   ✓ Transformation caching system"
echo "   ✓ Auto-parsing from VOICE_STAVE_DATA"
echo "   ✓ Multi-part transformation suffix model"
echo "   ✓ Absolute LilyPond notation converter"
echo "   ✓ Windows installation support (INSTALL_WINDOWS.md)"
echo "   ✓ Automated fix script (fix_windows_install.py)"

echo ""
echo "=========================================="
echo "✅ Distribution ready!"
echo "=========================================="
