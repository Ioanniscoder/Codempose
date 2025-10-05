import os
from pathlib import Path

import project_template as pt
from lilypond_parser import parse_lilypond_to_data
from music_data import data_to_part, extract_data_from_part


def test_first_pipeline_creates_outputs(tmp_path):
    """Integration-style test: parse a Lily snippet, apply a transform,
    and call the decoupled engraver. Verify output files are written.
    """
    # Use a representative snippet similar to the snapshot header in first.py
    lily = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 | b2. f'2. | e2. c2. | e2 b2 c2 }"

    # Parse into canonical data dict
    score_data = parse_lilypond_to_data(lily, part_name="Main Melody")
    assert 'parts' in score_data and 'Main Melody' in score_data['parts']

    # Rebuild a music21 Part, perform a small transform (transpose P5), and
    # re-extract events into the score_data under a new part name.
    part = data_to_part(score_data['parts']['Main Melody'], score_data.get('metadata'))
    tpart = part.transpose('P5')
    new_events = extract_data_from_part(tpart)
    score_data = {"metadata": score_data.get('metadata', {}), 'parts': {'Transposed Melody': new_events}}

    # Ensure outputs dir exists in the test workspace and call engraver
    outdir = Path('outputs')
    if outdir.exists():
        # remove any stale test artifacts for a clean run
        for p in outdir.iterdir():
            if p.is_file() and p.suffix in {'.ly', '.pdf', '.midi', '.json'}:
                try:
                    p.unlink()
                except Exception:
                    pass
    else:
        outdir.mkdir(parents=True)

    # Call the decoupled engraver (this will write outputs/<basename>.ly and attempt to run lilypond)
    basename = 'test_first_score'
    pt.engrave_with_abjad(score_data, basename)

    # Check that at least a .ly file and .json were produced (engraver writes .ly and .json)
    ly = outdir / f"{basename}.ly"
    assert ly.exists(), f"Expected {ly} to be created"

    jsonf = outdir / f"{basename}.json"
    # The JSON creation may be best-effort; ensure file exists or engraving produced a .midi/.pdf
    exists_json = jsonf.exists()
    exists_pdf = (outdir / f"{basename}.pdf").exists()
    exists_midi = (outdir / f"{basename}.midi").exists()
    assert exists_json or exists_pdf or exists_midi, "Expected at least one of .json/.pdf/.midi to be created"
