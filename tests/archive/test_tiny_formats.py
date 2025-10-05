#!/usr/bin/env python3
"""Test different TinyNotation formats."""

import music21

test_cases = [
    "C2 D2 E2",  # Basic
    "c2 d2 e2",  # Lowercase
    "c'2 d'2 e'2",  # With apostrophes (LilyPond style)
    "c,2 d,2 e,2",  # With commas (LilyPond style)  
    "C42 D42 E42",  # With octave numbers  (wrong - 42 is duration)
]

for i, tiny in enumerate(test_cases, 1):
    print(f"\nTest {i}: {tiny}")
    try:
        obj = music21.converter.parse(f"tinynotation: {tiny}")
        notes = list(obj.flatten().notesAndRests)
        if notes:
            print(f"  First note: {notes[0].nameWithOctave if hasattr(notes[0], 'nameWithOctave') else notes[0]}")
        else:
            print(f"  No notes parsed")
    except Exception as e:
        print(f"  ERROR: {e}")
