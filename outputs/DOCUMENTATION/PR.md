Title: feat(engraver): verbatim-first heuristic, CLI overrides, tests and CI

Description:
This branch implements a conservative verbatim/manual .ly emission path that is selected by heuristic when the original input contains `\relative`, when the parser emitted warnings, or when per-note original tokens were preserved. The branch also:

- Adds CLI flags `--force-verbatim` and `--force-hybrid` (handled via score_data metadata)
- Adds a pytest (`tests/test_verbatim_route.py`) that verifies verbatim emission for `first.py`
- Adds GitHub Actions workflow that runs tests and a verbatim smoke generation
- Adds `scripts/generate_verbatim.sh` for local reproduction

Known issues / next steps:
- Hybrid Abjad path still needs hardening: improve `_build_abjad_pitch`, tighten verification, and add targeted tests for respelling cases.
- Consider expanding the verification to detect octave vs accidental mismatches and only fallback on semantic differences.

How to run locally:

1. Create a venv and install dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Run tests:

```bash
python -m pytest -q
```

3. Generate verbatim output for `first.py`:

```bash
./scripts/generate_verbatim.sh
```

If you prefer, paste this description into GitHub when creating a PR from branch `experimental/project_template_sanitizer_fix`.
