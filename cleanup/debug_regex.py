#!/usr/bin/env python3
import re

# Test the regex pattern directly
token_pattern = r'''
    __TUPLET_\d+__                   # Tuplet placeholder
    |
    <[^>]+>\d*\.?\([^)]*\)?~?        # Chords: <c e g>4(mods)~ with optional container + tie
    |
    ~?(?:heses|ces|eses|ases|des|fes)  # Grace note prefix + D/F/other + es (always combined)
    [',]*\d*\.?\([^)]*\)?~?          # Octave markers, duration, suffix container, tie
    |
    ~?(?:es|as)                      # Grace note prefix + Standalone E-flat or A-flat
    (?![a-z])                        # NOT followed by another letter (negative lookahead)
    [',]*\d*\.?\([^)]*\)?~?          # Octave markers, duration, suffix container, tie
    |
    ~?[a-gr]                         # Grace note prefix + Note/rest letter
    (?:isis|ises|eses|is|es|bmol|mol|\#|b)?   # Accidental suffix (including localized bmol/mol)
    [',]*\d*\.?\([^)]*\)?~?          # Octave markers, duration, suffix container, tie
'''

test_strings = [
    "c4(.)",
    "~g16",
    "a2(f)",
    "~g16 a2(f)",
    "a2(p, >)~",
]

for test_str in test_strings:
    matches = re.findall(token_pattern, test_str, re.VERBOSE)
    print(f"Input: '{test_str}'")
    print(f"Matches: {matches}")
    print()
