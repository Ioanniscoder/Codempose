#!/usr/bin/env python3
"""Debug script to test lily_to_tiny conversion."""

from lily_to_tiny import lily_to_tiny_notation

lily_string = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 | b2. f'2. | e2. c2. | e2 b2 c2 }"

print("Input:", lily_string)
print("\n" + "="*60)

result = lily_to_tiny_notation(lily_string)

print(f"\nSuccess: {result.success}")
print(f"TinyNotation: {result.tiny_notation}")
print(f"\nDirectives: {result.directives}")
print(f"\nWarnings: {result.warnings}")

print("\nFirst 10 tokens:")
for i, token in enumerate(result.tokens[:10]):
    print(f"  {i}: {token.original:15s} -> {token.converted:15s}  {token.warnings}")

print("\n" + "="*60)
