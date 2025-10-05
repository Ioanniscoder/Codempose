#!/usr/bin/env python3
"""Test the new TinyNotation string."""

import music21

tiny_string = "6/4 E2 B-4 c2 r4 e2 f#4 e2 r4 b2. f'2. e'2. c'2. e'2 b'2 c''2"

print("TinyNotation:", tiny_string)
print("\n" + "="*60)

obj = music21.converter.parse(f"tinynotation: {tiny_string}")

print("\nNotes and Rests:")
for i, el in enumerate(obj.flatten().notesAndRests):
    if hasattr(el, 'pitch'):
        print(f"{i}: {el.nameWithOctave} (QL={el.quarterLength})")
    else:
        print(f"{i}: Rest (QL={el.quarterLength})")

print("\n" + "="*60)
print("\nExpected sequence from LilyPond:")
print("E3, B♭3, C4, Rest, E4, F#4, E4, Rest, B4, F5, E5, C5, E5, B5, C6")
