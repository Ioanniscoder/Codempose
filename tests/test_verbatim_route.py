import subprocess
from pathlib import Path


def test_verbatim_route_creates_ly_with_header(tmp_path):
    # Run the main script with the example input 'first.py' (repo root)
    # and force verbatim to ensure deterministic behavior.
    repo_root = Path(__file__).resolve().parents[1]
    out_basename = 'first'
    cmd = [str(repo_root / '.venv' / 'bin' / 'python'), str(repo_root / 'main.py'), '--input', str(repo_root / 'first.py'), '--force-verbatim']
    proc = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    assert proc.returncode == 0, f"main.py failed: stdout={proc.stdout}\nstderr={proc.stderr}"
    ly_path = repo_root / 'outputs' / f"{out_basename}.ly"
    assert ly_path.exists(), f"Expected {ly_path} to exist"
    text = ly_path.read_text(encoding='utf8')
    # The original snippet should appear in the header comments
    assert '% === Original snippet (from metadata) ===' in text
    # Basic sanity: contains \score and \new Staff
    assert '\\score' in text
    assert '\\new Staff' in text
