#!/usr/bin/env python3
"""Debug music21 TinyNotation parsing."""

import music21

# Test the TinyNotation string from lily_to_tiny
tiny_string = "6/4 e,2 b-,4 c2 r4 e2 f#4 e2 r4 b2. f'2. e'2. c'2. e'2 b'2 c''2"

print("TinyNotation string:", tiny_string)
print("\n" + "="*60)

# Parse with music21
tiny_obj = music21.converter.parse(f"tinynotation: {tiny_string}")

print("\nParsed stream:")
tiny_obj.show('text')

print("\n" + "="*60)
print("\nNotes and Rests:")
for i, el in enumerate(tiny_obj.flatten().notesAndRests):
    if hasattr(el, 'pitch'):
        print(f"{i}: {el.nameWithOctave} ({el.quarterLength})")
    else:
        print(f"{i}: Rest ({el.quarterLength})")
