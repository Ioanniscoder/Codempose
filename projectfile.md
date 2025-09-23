# Projectfile — Codempose

Short status, actionable todos, and run instructions for the repository.

## Status (as of commit)
- Devcontainer: configured and ready (includes LilyPond and git-lfs).
- Parser: `project_template.py` accepts a small LilyPond subset (notes, chords, \relative, simple dotted durations) and tinyNotation support exists.
- Engraver: converts music21 Parts → Abjad Voices → writes `.ly` and runs `lilypond`. Outputs now go to `outputs/` by default.
- Example composition: `first.py` demonstrates snippet-driven input, programmatic insertion examples, and an auto-harmony generator.
- Primer: `template_primer.txt` restored and documents supported snippets and tinyNotation examples.

## Quick run
1. Open in Codespaces (or VS Code devcontainer) and ensure the container is built.
2. Run the example generator:

```bash
python3 first.py
```

3. Inspect generated artifacts in `outputs/` (e.g. `outputs/first_score.pdf`). The devcontainer helper starts a tiny HTTP server on port `8888` so you can view files via the forwarded port.

## Todo (short-term)
- Implement tuplet handling for fractional durations (accurate 4/3, 2/3 etc.) — currently durations are approximated.
- Add an `--output-dir` CLI flag to `first.py` and `project_template.py` to override the default `outputs/`.
- Add a small CLI `--preview` flag to write temporary outputs for quick iteration.

## Todo (medium-term)
- Add per-staff `midi_programs` mapping and ensure LilyPond instrument names are robust.
- Add unit tests for `parse_lilypond_snippet` and `ql_to_lily_duration_string` (pytest).
- Add a Makefile or convenience scripts for build/test flows and a GitHub Actions workflow to validate examples.

## Notes on editing
- Do not modify `.txt` primer files without explicit approval — they are part of the learning material.
- Generated outputs are in `outputs/` and ignored by Git to keep the repo clean.

## Contacts / next steps
- If you want, I can implement the tuplet support next (recommended) or add the `--output-dir` flag — tell me which and I will implement, test, and commit.
