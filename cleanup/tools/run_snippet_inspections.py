#!/usr/bin/env python3
"""
Inspect snippet tokenization and measure assignments using project_template.
Run with: PYTHONPATH=. python3 tools/run_snippet_inspections.py
"""
import sys
from pathlib import Path
import project_template as pt
import music21

SNIPPET_DIR = Path("tools/snippets")

def extract_body_text(path: Path) -> str:
    return path.read_text()

def inspect_tokens_and_parts(snippet_text: str, name: str):
    body = snippet_text.strip()
    print(f"\n=== {name} ===")
    try:
        # Try to find the relative body for nicer tokenization (project_template expects full snippet)
        tokens = pt._get_tokens(body)
    except Exception as e:
        print(f"[tokenize error] {e}")
        tokens = []
    print("Tokens:", tokens)

    try:
        part = pt.parse_lilypond_snippet(body)
    except Exception as e:
        print(f"[parse error] {e}")
        return

    ts_list = list(part.recurse().getElementsByClass(music21.meter.TimeSignature))
    ts = ts_list[0] if ts_list else None
    measure_len = (ts.numerator * (4/ts.denominator)) if ts else 4.0
    print("Has TimeSignature:", bool(ts), " TS:", ts)
    running = 0.0
    for i, el in enumerate(part.flatten().notesAndRests, start=1):
        ql = el.quarterLength
        mnum = int(running // measure_len) + 1
        typename = type(el).__name__
        pitch = getattr(el, "pitch", None)
        pitches = getattr(el, "pitches", None)
        if pitches is not None:
            pstr = ",".join(p.nameWithOctave for p in pitches)
        elif pitch is not None:
            pstr = pitch.nameWithOctave
        else:
            pstr = "Rest"
        print(f"{i:02d}: offset~{running:.4f} ql={ql:.4f} -> measure {mnum}   {typename}({pstr})")
        running += ql
    print("total ql=", running)

def main():
    for p in sorted(SNIPPET_DIR.glob("*.ly")):
        text = extract_body_text(p)
        inspect_tokens_and_parts(text, p.name)

if __name__ == '__main__':
    main()
