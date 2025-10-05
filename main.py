# main.py - DEPRECATED
# 
# ⚠️  This file is deprecated as of October 3, 2025.
# 
# The orchestration logic has been moved to project_template.run_pipeline_from_file()
# to enable a more flexible and intuitive workflow.
#
# OLD WORKFLOW (deprecated):
#   python main.py first.py
#
# NEW WORKFLOW (recommended):
#   python first.py
#
# Each study file (first.py, second.py, third.py) is now self-executing.
# Simply run the file directly to generate PDF/MIDI outputs.
#
# This file is kept for backward compatibility but will be removed in a future version.

from pathlib import Path
import sys

def main(argv=None):
    """Deprecated main entry point - redirects to new workflow."""
    print("\n" + "="*60)
    print("⚠️  DEPRECATION WARNING")
    print("="*60)
    print("main.py is deprecated. Please use the new workflow:")
    print()
    print("  OLD: python main.py <study_file>")
    print("  NEW: python <study_file>")
    print()
    print("Example:")
    print("  python first.py   # Self-executing!")
    print("  python second.py")
    print("  python third.py")
    print("="*60)
    print()
    
    # For backward compatibility, still support the old workflow
    if argv is None:
        argv = sys.argv[1:]
    
    if len(argv) < 1:
        print("❌ Error: No input file specified")
        print("Usage: python main.py <study_file>")
        print()
        print("Or better yet, run the study file directly:")
        print("  python first.py")
        sys.exit(1)
    
    input_file = argv[0]
    print(f"Redirecting to new workflow...")
    print(f"Running: python {input_file}")
    print()
    
    # Use the new pipeline
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(input_file)

if __name__ == '__main__':
    main()