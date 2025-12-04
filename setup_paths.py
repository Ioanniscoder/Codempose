"""
Setup script for Codempose distribution.
Run this once after extracting the tarball to configure paths.

Usage:
    python setup_paths.py
"""

import sys
from pathlib import Path

def setup_codempose_paths():
    """Create necessary path configuration files."""
    
    # Get the root directory (where this script is)
    root_dir = Path(__file__).parent.resolve()
    studies_dir = root_dir / 'studies'
    src_dir = root_dir / 'src'
    lib_dir = src_dir / 'lib'
    
    # Create _study_path.py if it doesn't exist
    study_path_file = studies_dir / '_study_path.py'
    
    study_path_content = '''"""
Path helper for Codempose study files.

This module ensures study files can import core Codempose modules
regardless of where they are executed from.

Usage in study files:
    import _study_path  # Add this at the very top
    from project_template import run_pipeline_from_file
"""

import sys
from pathlib import Path

# Get the directory containing this file (studies/)
study_dir = Path(__file__).parent.resolve()

# The root is one level up from studies/
root_dir = study_dir.parent

# Get the src/ directory where core modules live
src_dir = root_dir / 'src'

# Get the src/lib/ directory where importable libraries live
lib_dir = src_dir / 'lib'

# Add src/ to sys.path first (higher priority for imports)
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Add src/lib/ to sys.path (for template libraries)
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

# Also add root to sys.path for backward compatibility
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Diagnostic (only shown if running this file directly)
if __name__ == '__main__':
    print(f"Study directory: {study_dir}")
    print(f"Root directory: {root_dir}")
    print(f"Src directory: {src_dir}")
    print(f"sys.path updated:")
    print(f"  1. {str(src_dir)} (core modules)")
    print(f"  2. {str(lib_dir)} (library templates)")
    print(f"  3. {str(root_dir)} (root)")
'''
    
    # Create the file
    with open(study_path_file, 'w', encoding='utf-8') as f:
        f.write(study_path_content)
    
    print("✅ Codempose setup complete!")
    print()
    print(f"📁 Root directory: {root_dir}")
    print(f"📁 Source directory: {src_dir}")
    print(f"📁 Studies directory: {studies_dir}")
    print()
    print(f"✓ Created: {study_path_file}")
    print()
    print("Next steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run a test: python generate_study.py")
    print("  3. Or run a study: python studies/100th.py")
    print()
    
    # Verify paths exist
    if not src_dir.exists():
        print("⚠️  WARNING: src/ directory not found!")
        return False
    
    if not studies_dir.exists():
        print("⚠️  WARNING: studies/ directory not found!")
        return False
    
    return True

if __name__ == '__main__':
    success = setup_codempose_paths()
    sys.exit(0 if success else 1)
