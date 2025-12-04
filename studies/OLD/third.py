"""Template study file: richer `first.py` used as a starting point for
experimentation and tests.

This module exposes a primary LilyPond snippet constant (used by
`main.py` when present) and also provides helpers that build a
music21.Part so tests can import and call `build_part()` directly.

Design goals:
- Keep the file safe to import (no destructive side-effects).
- Provide several example snippets (LilyPond and tinyNotation).
- Provide `build_part()` which returns a music21.Part (used by
  `main.py` when the study module exposes a `build_part()` function).
- Provide a small example `add_harmony()` helper that demonstrates
  how to Huur transform the Part with music21 objects.

Later the file can be installed (promoted) by an installer that
replaces the working template; until then it remains read-only.
"""

import _study_path  # Auto-path setup for study files
from typing import Dict, Optional

# Primary human-facing LilyPond snippet. `main.py` will prefer this
# when present. Keep this concise and representative.
SOURCE_MELODY_LILY = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 | b2. f'2. | e2. c2. | e2 b2 c2 }"

# A small set of test snippets (both LilyPond and tinyNotation) that
# are useful during development and automated tests.
ALTERNATE_SNIPPETS: Dict[str, str] = {
	'simple_lily': r"\relative c' { c4 d e f | g a b c }",
	'melody_variant': r"\relative g' { e4 fs g a | b c d e }",
	'tiny_example': "c4 d8 e f2 g4 a b c'",  # tinyNotation snippet
}

# A short harmony snippet used by the example transform below.
HARMONY_SNIPPET = r"<e g b>2 <f a c'>2"

# Default output basename (main.py will override when --output passed).
OUTPUT_BASENAME = 'first_score'


def get_snippets() -> Dict[str, str]:
	"""Return a dictionary of available snippets for interactive use.

	This helper is convenient when you import the study module in a
	REPL to inspect or to pick an example to build.
	"""
	d = {'primary': SOURCE_MELODY_LILY}
	d.update(ALTERNATE_SNIPPETS)
	return d


def build_part(snippet: Optional[str] = None):
	"""Build and return a music21.stream.Part from a snippet.

	Behavior:
	- If `snippet` is None, use `SOURCE_MELODY_LILY`.
	- If `snippet` matches a key in `ALTERNATE_SNIPPETS`, use that
	  stored snippet (tinyNotation or LilyPond style strings).
	- Parsing is delegated to the existing pipeline helpers so the
	  canonical data dict path is exercised.

	Returns:
		music21.stream.Part
	"""
	# Local import to avoid heavy startup cost when the file is merely
	# inspected. These project helpers are available in the workspace.
	from lilypond_parser import parse_lilypond_to_data
	from music_data import data_to_part

	use = snippet or SOURCE_MELODY_LILY
	# If user passed a known key, resolve it
	if isinstance(use, str) and use in ALTERNATE_SNIPPETS:
		use = ALTERNATE_SNIPPETS[use]

	# Use the robust parser implemented in this repository which
	# returns the canonical data dict (metadata + parts)
	score_data = parse_lilypond_to_data(use, part_name='Main Melody')
	events = score_data.get('parts', {}).get('Main Melody')
	if events is None:
		raise RuntimeError('Parser did not return events for Main Melody')

	# Convert canonical events to a music21 Part
	part = data_to_part(events, metadata=score_data.get('metadata'))

	# Example: attach parser diagnostics (if any) to the Part for
	# callers to inspect programmatically.
	warnings = score_data.get('metadata', {}).get('warnings') or []
	suggestions = score_data.get('metadata', {}).get('suggestions') or []
	# Attach as attributes (non-persistent) so calling code can see them
	setattr(part, '_parse_warnings', warnings)
	setattr(part, '_parse_suggestions', suggestions)

	return part


def add_harmony(base_part, harmony_snippet: Optional[str] = None):
	"""Return a new music21.Score with the base part and a simple
	harmony part (derived from a short snippet).

	This demonstrates how one might programmatically construct a
	multi-part Score from the parsed melody.
	"""
	from music21 import stream

	harmony_snip = harmony_snippet or HARMONY_SNIPPET
	try:
		# Use the same pipeline path to parse the harmony snippet
		from lilypond_parser import parse_lilypond_to_data
		from music_data import data_to_part

		hd = parse_lilypond_to_data(harmony_snip, part_name='Harmony')
		h_events = hd.get('parts', {}).get('Harmony', [])
		harmony_part = data_to_part(h_events, metadata=hd.get('metadata'))
	except Exception:
		# If parsing fails, build a small placeholder part
		harmony_part = stream.Part()

	score = stream.Score()
	score.append(base_part)
	score.append(harmony_part)
	return score


if __name__ == '__main__':
	# Minimal interactive helper when executed directly: list snippets
	print('first.py (template): available snippets:')
	for k in get_snippets().keys():
		print(' -', k)

SOURCE_MELODY_LILY = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 | b2. f'2. | e2. c2. | e2 b2 c2 }"
HARMONY_SNIPPET = r"e2 b2 <e g b>2"
OUTPUT_BASENAME = 'first_score'


def build_score_data():
    """Build score_data from SOURCE_MELODY_LILY for main.py."""
    # Temporary simple data
    return {
        'metadata': {'title': 'test'},
        'parts': {
            'Main Melody': [
                {'type': 'note', 'step': 'c', 'alter': 0, 'octave': 4, 'ql': 1.0},
                {'type': 'note', 'step': 'd', 'alter': 0, 'octave': 4, 'ql': 1.0},
                {'type': 'note', 'step': 'e', 'alter': 0, 'octave': 4, 'ql': 1.0}
            ]
        }
    }


# Self-executing entry point - enables direct execution with: python third.py
if __name__ == '__main__':
	from project_template import run_pipeline_from_file
	run_pipeline_from_file(__file__)

