"""
Path helper for Codempose study files.

This module ensures study files can import core Codempose modules
regardless of where they are executed from.

Usage in study files:
    import _study_path  # Add this at the very top
    from project_template import run_pipeline_from_file
    
The import works from:
- studies/ directory: python first.py
- root directory: python studies/first.py
- any location: python /path/to/studies/first.py
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
    print(f"  2. {str(root_dir)} (backward compatibility)")
    print("\nCore modules available:")
    
    try:
        import project_template
        print("  ✓ project_template")
    except ImportError as e:
        print(f"  ✗ project_template: {e}")
    
    try:
        import lilypond_parser
        print("  ✓ lilypond_parser")
    except ImportError as e:
        print(f"  ✗ lilypond_parser: {e}")
    
    try:
        import music_data
        print("  ✓ music_data")
    except ImportError as e:
        print(f"  ✗ music_data: {e}")
