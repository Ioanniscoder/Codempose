#!/usr/bin/env python3
"""Debug script to test the parser and see what it extracts."""

from lilypond_parser import parse_lilypond_to_data
import json

lily_string = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 | b2. f'2. | e2. c2. | e2 b2 c2 }"

print("Input:", lily_string)
print("\n" + "="*60)

result = parse_lilypond_to_data(lily_string, 'Melody')

print("\nMetadata:")
print(json.dumps(result['metadata'], indent=2))

print("\nFirst 10 events:")
for i, event in enumerate(result['parts']['Melody'][:10]):
    print(f"  {i}: {event}")

print("\n" + "="*60)
