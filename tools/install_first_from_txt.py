"""
Safe installer for first.py

This script atomically installs `first.py` from `first.py.txt` after
performing basic validation. It is intended to be a safe, explicit
replacement workflow to avoid accidental self-modifying runs.

Features:
- Syntax-check the candidate file (`compile()`)
- Optionally run the project's test suite (`pytest`) before install
- Create a timestamped backup of the existing `first.py` in `archive/`
- Atomically write a temp file, fsync, then os.replace() into place
- Set installed `first.py` to read-only (0444) to avoid accidental edits

Usage:
  python tools/install_first_from_txt.py [--yes] [--no-tests]

By default the script will run the test-suite. Use --no-tests to skip.
Use --yes to skip interactive confirmation.
"""

from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path


def run_tests() -> bool:
    """Run pytest in the repository root. Returns True if tests pass."""
    print("Running pytest to validate the project before install...")
    try:
        # Use the venv python to run pytest (if available via sys.executable)
        res = subprocess.run([sys.executable, '-m', 'pytest', '-q'], cwd=str(Path.cwd()))
        return res.returncode == 0
    except FileNotFoundError:
        print("pytest not found; skipping tests")
        return True
    except Exception as exc:
        print(f"Error running tests: {exc}")
        return False


def prompt_yes_no(msg: str) -> bool:
    resp = input(msg + ' [y/N]: ').strip().lower()
    return resp in ('y', 'yes')


def install(first_txt: Path, dest_py: Path, run_tests_flag: bool = True, assume_yes: bool = False) -> int:
    """Perform installation. Returns 0 on success, non-zero on failure."""
    if not first_txt.exists():
        print(f"Source file not found: {first_txt}")
        return 2

    content = first_txt.read_text(encoding='utf8')

    # Basic syntax check
    try:
        compile(content, str(first_txt), 'exec')
    except SyntaxError as e:
        print(f"Syntax error in {first_txt}: {e}")
        return 3

    # Optionally run tests
    if run_tests_flag:
        ok = run_tests()
        if not ok:
            print("Tests failed. Aborting installation by default.")
            if not assume_yes and not prompt_yes_no("Proceed with install despite failing tests?"):
                return 4

    # Confirmation
    if not assume_yes:
        print(f"About to install {first_txt} -> {dest_py}")
        if not prompt_yes_no("Continue with installation?"):
            print("Aborted by user.")
            return 5

    # Prepare tmp file
    tmp = dest_py.with_suffix('.py.tmp')
    try:
        with tmp.open('w', encoding='utf8') as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
    except Exception as e:
        print(f"Error writing temporary file {tmp}: {e}")
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass
        return 6

    # Backup existing dest into archive if present
    archive_dir = Path('archive')
    archive_dir.mkdir(parents=True, exist_ok=True)
    backup_name = None
    if dest_py.exists():
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        backup_name = archive_dir / f"first_installed_{ts}.py"
        try:
            os.replace(str(dest_py), str(backup_name))
            print(f"Backed up existing {dest_py} -> {backup_name}")
        except Exception as e:
            print(f"Warning: could not backup existing {dest_py}: {e}")

    # Move tmp -> dest atomically
    try:
        os.replace(str(tmp), str(dest_py))
    except Exception as e:
        print(f"Error installing {dest_py}: {e}")
        # Try to restore backup if present
        if backup_name and backup_name.exists():
            try:
                os.replace(str(backup_name), str(dest_py))
                print("Restored backup to dest after failed install.")
            except Exception as e2:
                print(f"Failed to restore backup: {e2}")
        return 7

    # Make installed file read-only for safety
    try:
        os.chmod(str(dest_py), 0o444)
    except Exception as e:
        print(f"Warning: could not set read-only permissions on {dest_py}: {e}")

    print(f"Installed {dest_py} successfully.")
    if backup_name:
        print(f"Previous file archived as: {backup_name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install first.py from first.py.txt safely")
    parser.add_argument('--no-tests', dest='run_tests', action='store_false', help='Skip running pytest before install')
    parser.add_argument('--yes', '-y', action='store_true', help='Assume yes to prompts')
    args = parser.parse_args(argv)

    first_txt = Path('first.py.txt')
    dest = Path('first.py')

    return install(first_txt, dest, run_tests_flag=args.run_tests, assume_yes=args.yes)


if __name__ == '__main__':
    sys.exit(main())
