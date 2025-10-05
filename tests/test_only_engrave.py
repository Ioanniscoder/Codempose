import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import json
import subprocess

def test_only_engrave_json(tmp_path):
    # Build simple score_data JSON
    score = {
        'metadata': {'title': 'unit_test_score'},
        'parts': {'Main Melody': [
            {'type': 'note', 'pitches': [{'step':'e', 'alter':0, 'octave':4}], 'ql': 2.0},
            {'type': 'note', 'pitches': [{'step':'c', 'alter':0, 'octave':5}], 'ql': 2.0}
        ]}
    }
    j = tmp_path / 'score.json'
    j.write_text(json.dumps(score, ensure_ascii=False))
    # Run main.py with only-engrave
    p = subprocess.run(['python', 'main.py', '--input', str(j), '--only-engrave'], cwd=Path.cwd(), capture_output=True, text=True)
    print(p.stdout)
    assert p.returncode == 0
    # Expect an outputs/<stem>.ly file
    out_ly = Path('outputs') / f"{j.stem}.ly"
    assert out_ly.exists()
    # Clean up outputs created by the run
    try:
        for ext in ['.ly', '.pdf', '.midi', '.json']:
            f = Path('outputs') / f"{j.stem}{ext}"
            if f.exists():
                f.unlink()
    except Exception:
        pass
