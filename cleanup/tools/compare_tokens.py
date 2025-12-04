#!/usr/bin/env python3
"""Compare original LilyPond snippet tokens to the tokens emitted from
music21 parsing + token emission used by the template.

Usage: python3 tools/compare_tokens.py

This script imports `first.py` to get MELODY_SNIPPET and uses
`project_template` helpers to create both token lists and prints a
simple line-based diff.
"""
from project_template import _get_tokens, parse_lilypond_snippet, emit_lily_tokens_from_part, _normalize_lily_for_abjad
from first import MELODY_SNIPPET
import re


def extract_body(snippet: str) -> str:
    m = re.search(r"\{(.*)\}", snippet, re.DOTALL)
    return m.group(1).strip() if m else snippet


def filter_music_tokens(tokens):
    # Remove directives (\time, \key, \tempo, \major/minor) and barlines
    out = [t for t in tokens if not (t.startswith('\\') or t == '|')]
    return out


def strip_octaves(tok: str) -> str:
    # remove octave marks (apostrophes and commas)
    return re.sub(r"[,']", "", tok)


def normalize_token_for_compare(tok: str) -> str:
    # Normalize accidentals via the same normalizer used earlier
    try:
        t = _normalize_lily_for_abjad(tok)
    except Exception:
        t = tok
    # strip octave marks for comparison so we compare step+acc+dur
    return strip_octaves(t)


orig = MELODY_SNIPPET
print('Original snippet:')
print(orig)

# Extract body and tokenize
body = extract_body(orig)
# Remove common directives so their arguments (e.g. the 'c' in '\key c')
# are not treated as note tokens by the tokenizer during comparison.
body_clean = body
body_clean = re.sub(r"\\time\s+\d+/\d+", "", body_clean, flags=re.IGNORECASE)
body_clean = re.sub(r"\\key\s+[a-gA-G][^\s]*\s+(?:major|minor)?", "", body_clean, flags=re.IGNORECASE)
body_clean = re.sub(r"\\tempo\s+[^\s]+", "", body_clean, flags=re.IGNORECASE)
norm_body = _normalize_lily_for_abjad(body_clean)
orig_body_tokens = _get_tokens(norm_body)
orig_music_tokens = filter_music_tokens(orig_body_tokens)
print('\nOriginal music tokens (body):')
print(orig_music_tokens)

# Parse and re-emit tokens from the parsed Part
part = parse_lilypond_snippet(orig)
emitted = emit_lily_tokens_from_part(part)
print('\nEmitted token stream:')
print(emitted)

emitted_tokens = emitted.split()
emitted_tokens = filter_music_tokens(emitted_tokens)
print('\nEmitted music tokens:')
print(emitted_tokens)

# Normalize both lists for comparison
orig_norm = [normalize_token_for_compare(t) for t in orig_music_tokens]
emit_norm = [normalize_token_for_compare(t) for t in emitted_tokens]

print('\nNormalized original tokens:')
print(orig_norm)
print('\nNormalized emitted tokens:')
print(emit_norm)

print('\nDifferences (index, orig -> emit):')
for i, (a, b) in enumerate(zip(orig_norm, emit_norm)):
    if a != b:
        print(f"[{i}] {a!r} -> {b!r}")

if len(orig_norm) != len(emit_norm):
    print('\nToken counts differ:')
    print(' orig:', len(orig_norm))
    print(' emit:', len(emit_norm))
    if len(orig_norm) > len(emit_norm):
        print('orig tail:', orig_norm[len(emit_norm):])
    else:
        print('emit tail:', emit_norm[len(orig_norm):])
