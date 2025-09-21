#!/usr/bin/env python3
"""Small composer helper: public API + CLI to create LilyPond and PDF outputs.

This module tries to use an external `make21` package if available; otherwise it
falls back to the parsing/engraving functions already in `project_template.py`.

Usage:
  python -m src.composer --melody "\\relative c' { e4 f g a }" --harmony "c,2 g,2"

It will write <output>.ly and invoke LilyPond (via Abjad) to produce the PDF.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional


try:
    import make21  # type: ignore
    HAVE_MAKE21 = True
except Exception:
    HAVE_MAKE21 = False


def create_score_from_snippets(melody_snippet: str, harmony_snippet: str, output_basename: str = "score") -> Path:
    """Create a LilyPond file and invoke engraving to produce a PDF.

    Returns the path to the generated PDF.
    """
    # Lazy import of project_template functions to reuse existing logic
    from project_template import parse_lilypond_snippet, engrave_with_abjad

    melody = parse_lilypond_snippet(melody_snippet)
    harmony = parse_lilypond_snippet(harmony_snippet)
    output_file = f"{output_basename}"
    engrave_with_abjad({"Melody": melody, "Harmony": harmony}, output_file)
    pdf_path = Path(output_file).with_suffix(".pdf")
    return pdf_path


def create_score_from_make21(obj, output_basename: str = "score") -> Path:
    """If Make21 is available, use it to create LilyPond input and then compile.

    This is a placeholder adapter that assumes Make21 can export LilyPond text.
    """
    if not HAVE_MAKE21:
        raise RuntimeError("make21 is not available in this environment")

    # This code path depends on the real Make21 API. Implementers should
    # replace the following with actual Make21 calls.
    lily_text = make21.to_lilypond(obj)  # type: ignore
    ly_path = Path(output_basename).with_suffix(".ly")
    ly_path.write_text(lily_text)
    # Attempt to invoke lilypond via system; let Abjad handle compiling if needed.
    # For now, return the expected PDF path.
    return ly_path.with_suffix(".pdf")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="composer")
    parser.add_argument("--melody", help="LilyPond snippet for melody", default="\\relative c' { e4 f g a <c e g>2. r4 }")
    parser.add_argument("--harmony", help="LilyPond snippet for harmony", default="c,2 g,2 <c e g>1")
    parser.add_argument("--output", help="Output basename (no extension)", default="relative_score")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)
    if HAVE_MAKE21:
        logging.info("Using Make21 to create score")
        # Example: convert some Make21 object; here we don't have one so fallback
        try:
            pdf = create_score_from_make21(None, args.output)
            logging.info(f"Generated PDF: {pdf}")
            return 0
        except Exception as exc:
            logging.warning("Make21 path failed, falling back: %s", exc)

    pdf = create_score_from_snippets(args.melody, args.harmony, args.output)
    logging.info(f"Generated PDF: {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
