#!/usr/bin/env python3
from lilypond_parser import parse_lilypond_to_data

# Test tie merging
print("Test: Tied notes with modifiers")
result = parse_lilypond_to_data(r"\relative c' { a2(p, themeA, >) a2~ a2(f) r4 }")
events = result['parts']['Part 1']

for i, e in enumerate(events):
    print(f"Event {i}: step={e.get('step')}, ql={e.get('ql')}, dynamics={e.get('dynamics')}, tracker={e.get('tracker')}, articulations={e.get('articulations')}, original={e.get('original_token')}")
