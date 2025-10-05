import sys
import shutil
from pathlib import Path
import pytest

# Ensure repo root is importable
sys.path.insert(0, '/workspaces/Codempose')

import project_template


def _clean_basename(basename: str):
    out = Path('outputs')
    for p in out.glob(f"{basename}.*"):
        try:
            p.unlink()
        except Exception:
            pass


def test_lilypond_generates_midi_pdf_and_ly():
    # Skip if lilypond is not available in PATH (CI safety)
    if shutil.which('lilypond') is None:
        pytest.skip('lilypond not found in PATH; skipping engraver integration test')

    out_dir = Path('outputs')
    out_dir.mkdir(exist_ok=True)
    basename = 'pytest_test_midi'
    _clean_basename(basename)

    score_data = {
        'metadata': {'title': 'Pytest MIDI Test', 'composer': 'pytest'},
        'parts': {
            'P1': [
                {'type': 'note', 'ql': 1.0, 'step': 'c', 'alter': 0, 'octave': 4},
                {'type': 'note', 'ql': 1.0, 'step': 'd', 'alter': 0, 'octave': 4},
                {'type': 'note', 'ql': 2.0, 'step': 'e', 'alter': 0, 'octave': 4},
            ]
        }
    }

    # Run the engraver
    project_template.engrave_with_abjad(score_data, basename)

    ly = out_dir / f"{basename}.ly"
    pdf = out_dir / f"{basename}.pdf"
    midi_a = out_dir / f"{basename}.midi"
    midi_b = out_dir / f"{basename}.mid"

    assert ly.exists(), f"Expected lily file to exist: {ly}"
    assert pdf.exists(), f"Expected pdf to exist: {pdf}"
    assert midi_a.exists() or midi_b.exists(), f"Expected midi file ({midi_a} or {midi_b}) to exist"

    # cleanup
    _clean_basename(basename)
