#!/bin/bash
echo "=== DIAGNOSTIC OUTPUT ==="
echo "Current directory:"
pwd
echo ""
echo "PYTHONPATH:"
echo "$PYTHONPATH"
echo ""
echo "Python sys.path:"
python3 -c "import sys; print('\n'.join(sys.path))"
echo ""
echo "Looking for local modules:"
ls -la /workspaces/Codempose/*.py | grep -E "(voice_documentation|lily_converter|tenth)" || echo "Files not found"
echo ""
echo "Git status of those files:"
cd /workspaces/Codempose
git ls-files | grep -E "(voice_documentation|lily_converter|tenth)" || echo "Not in git"
echo ""
echo "Trying to import (this will show the exact error):"
python3 -c "import voice_documentation" 2>&1
echo ""
echo "=== END DIAGNOSTIC ==="