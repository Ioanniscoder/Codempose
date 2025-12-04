#!/usr/bin/env python3
from lilypond_parser import parse_lilypond_to_data

# Test 1: Grace note with dynamic
print("Test 1: Grace note with dynamic")
result = parse_lilypond_to_data(r"\relative c' { ~g16 a2(f) }")
events = result['parts']['Part 1']
print(f'Number of events: {len(events)}')
for i, e in enumerate(events):
    print(f'Event {i}: step={e.get("step")}, ql={e.get("ql")}, is_grace={e.get("is_grace")}, dynamics={e.get("dynamics")}')
print()

# Test 2: Tied notes with modifiers
print("Test 2: Tied notes with modifiers")
result = parse_lilypond_to_data(r"\relative c' { a2(p, >)~ a2 }")
events = result['parts']['Part 1']
print(f'Number of events: {len(events)}')
for i, e in enumerate(events):
    print(f'Event {i}: step={e.get("step")}, ql={e.get("ql")}, dynamics={e.get("dynamics")}, articulations={e.get("articulations")}')
print()

# Test 3: Multiple notes
print("Test 3: Multiple notes with various modifiers")
result = parse_lilypond_to_data(r"\relative c' { c4(.) d4(p) e4(motif1) f4 }")
events = result['parts']['Part 1']
print(f'Number of events: {len(events)}')
for i, e in enumerate(events):
    print(f'Event {i}: step={e.get("step")}, articulations={e.get("articulations")}, dynamics={e.get("dynamics")}, tracker={e.get("tracker")}')
