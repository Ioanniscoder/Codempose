# Quick Windows Fix Script
# Run this if you get "ModuleNotFoundError: No module named '_study_path'"

import os
import sys
from pathlib import Path

def fix_windows_installation():
    """Fix common Windows installation issues."""
    
    print("=" * 50)
    print("Codempose Windows Installation Fixer")
    print("=" * 50)
    print()
    
    # Get the Codempose root directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"Working directory: {script_dir}")
    print()
    
    issues_found = []
    issues_fixed = []
    
    # Check 1: Verify _study_path.py exists
    print("[1/4] Checking studies/_study_path.py...")
    study_path_file = script_dir / "studies" / "_study_path.py"
    
    if not study_path_file.exists():
        issues_found.append("studies/_study_path.py is missing")
        print("  ❌ MISSING - Creating from template...")
        
        # Create the file
        study_path_content = """import sys
from pathlib import Path

# Add parent directory to path so we can import from src/
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
"""
        study_path_file.write_text(study_path_content)
        issues_fixed.append("Created studies/_study_path.py")
        print("  ✅ Created")
    else:
        print("  ✅ OK")
    
    # Check 2: Remove hidden/system attributes (Windows)
    if sys.platform == 'win32':
        print("[2/4] Removing Windows hidden/system attributes...")
        critical_files = [
            "studies/_study_path.py",
            "studies/__init__.py",
            "src/__init__.py"
        ]
        
        for file_path in critical_files:
            full_path = script_dir / file_path
            if full_path.exists():
                try:
                    # Remove read-only, hidden, system attributes
                    os.system(f'attrib -h -s -r "{full_path}" 2>nul')
                    print(f"  ✅ Fixed: {file_path}")
                except Exception as e:
                    print(f"  ⚠️  Could not fix {file_path}: {e}")
    else:
        print("[2/4] Skipping (not Windows)")
    
    # Check 3: Verify all __init__.py files exist
    print("[3/4] Checking __init__.py files...")
    init_files = [
        "src/__init__.py",
        "src/lib/__init__.py", 
        "studies/__init__.py",
        "tests/__init__.py"
    ]
    
    for init_path in init_files:
        full_path = script_dir / init_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not full_path.exists():
            full_path.write_text("# Python package marker\n")
            issues_fixed.append(f"Created {init_path}")
            print(f"  ✅ Created: {init_path}")
        else:
            print(f"  ✅ OK: {init_path}")
    
    # Check 4: Test imports
    print("[4/4] Testing imports...")
    try:
        # Add to path
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        
        # Test import _study_path
        from studies import _study_path
        print("  ✅ studies._study_path imported")
        
        # Test import score_builder
        from src import score_builder
        print("  ✅ src.score_builder imported")
        
    except ImportError as e:
        issues_found.append(f"Import failed: {e}")
        print(f"  ❌ Import failed: {e}")
    
    # Summary
    print()
    print("=" * 50)
    print("Summary")
    print("=" * 50)
    
    if issues_fixed:
        print("\n✅ Issues Fixed:")
        for fix in issues_fixed:
            print(f"  • {fix}")
    
    if issues_found:
        print("\n❌ Issues Found (manual fix needed):")
        for issue in issues_found:
            print(f"  • {issue}")
        print()
        print("Please re-extract the distribution tarball.")
        print("See INSTALL_WINDOWS.md for detailed instructions.")
        return False
    else:
        print("\n✅ All checks passed!")
        print("\nYou can now run studies:")
        print("  python studies/eightyfirst.py")
        print("  python studies/102th.py")
        return True

if __name__ == "__main__":
    try:
        success = fix_windows_installation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
