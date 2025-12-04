#!/usr/bin/env python3
"""
Debug script to test transformation chain end-to-end
"""

import sys
sys.path.insert(0, '/workspaces/Codempose/src')

from lilypond_parser import parse_lilypond_to_data
from music_data import data_to_part, part_to_data
import music21

# Simple test case
test_lily = r"""
\relative c'' {
    d4 fis8 g
}
""".strip()

print("=" * 70)
print("DEBUGGING TRANSFORMATION CHAIN")
print("=" * 70)
print()

# Step 1: Parse
print("Step 1: Parse LilyPond")
print(f"  Input: {test_lily}")
result = parse_lilypond_to_data(test_lily, "Test")
part_name = list(result['parts'].keys())[0]
events = result['parts'][part_name]

print(f"\n  Parsed events:")
for ev in events:
    if ev['type'] == 'note':
        print(f"    {ev['step']}{ev['octave']} ql={ev['ql']}")

# Step 2: Convert to music21
print("\nStep 2: Convert to music21.Part")
part = data_to_part(events, {})
print(f"  Part has {len(part.flatten().notesAndRests)} elements")
for note in part.flatten().notes:
    print(f"    music21 Note: {note.nameWithOctave} ql={note.quarterLength}")

# Step 3: Transpose
print("\nStep 3: Transpose up Perfect 4th (P4)")
print("  Expected: D6→G6, F#6→B6, G6→C7")
transposed_part = part.transpose('P4')
print(f"  Transposed part has {len(transposed_part.flatten().notesAndRests)} elements")
for note in transposed_part.flatten().notes:
    print(f"    music21 Note: {note.nameWithOctave} ql={note.quarterLength}")

# Step 4: Extract back to events
print("\nStep 4: Extract back to events")
transposed_events = part_to_data(transposed_part)
print(f"  Extracted events:")
for ev in transposed_events:
    if ev['type'] == 'note':
        print(f"    {ev['step']}{ev['octave']} ql={ev['ql']}")

print()
print("=" * 70)
print("CONCLUSION:")
original_pitches = [(ev['step'], ev['octave']) for ev in events if ev['type'] == 'note']
transposed_pitches = [(ev['step'], ev['octave']) for ev in transposed_events if ev['type'] == 'note']

print(f"  Original:   {original_pitches}")
print(f"  Transposed: {transposed_pitches}")

# Check if transformation is correct
expected = [('G', 6), ('B', 6), ('C', 7)]
if transposed_pitches == expected:
    print("  ✅ TRANSFORMATION CORRECT!")
else:
    print(f"  ❌ TRANSFORMATION WRONG! Expected: {expected}")
