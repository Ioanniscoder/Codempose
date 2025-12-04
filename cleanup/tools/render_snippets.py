#!/usr/bin/env python3
"""Render each snippet in tools/snippets/*.ly into its own PDF using the
project template. Outputs are written to outputs/snippet_<name>.*

Run with: PYTHONPATH=. python3 tools/render_snippets.py
"""
from pathlib import Path
import project_template as pt

SNIPPET_DIR = Path('tools/snippets')
OUT_DIR = Path('outputs')
OUT_DIR.mkdir(parents=True, exist_ok=True)

snippets = sorted(SNIPPET_DIR.glob('*.ly'))
if not snippets:
    print('No snippets found in tools/snippets/')
    raise SystemExit(1)

for p in snippets:
    name = p.stem
    text = p.read_text()
    print(f'Parsing snippet {p.name}...')
    try:
        part = pt.parse_lilypond_snippet(text)
    except Exception as e:
        print(f'  parse error: {e}')
        continue
    outbasename = OUT_DIR / f'snippet_{name}'
    print(f'  engraving -> {outbasename}.pdf')
    try:
        # engrave single part as its own score; do not prune other outputs
        pt.engrave_with_abjad({name: part}, str(outbasename), prune_other=False, force=True)
    except Exception as e:
        print(f'  engraving error: {e}')

print('\nDone. Generated PDFs (if LilyPond succeeded) in outputs/:')
for f in sorted(OUT_DIR.glob('snippet_*.pdf')):
    print(' -', f.name)
