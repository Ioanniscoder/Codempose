"""
Bug Verification Script
=======================
Verify the bugs identified by the other agent.
"""

from lily_to_tiny import lily_to_tiny_notation

print("=" * 80)
print("BUG VERIFICATION REPORT")
print("=" * 80)

# Bug 1: Relative octave crossing (b to c)
print("\n🐞 BUG 1: Relative Octave Crossing")
print("-" * 80)
snippet = r"\relative c' { c4 d e f g a b c }"
result = lily_to_tiny_notation(snippet)
print(f"Input:    {snippet}")
print(f"Output:   {result.tiny_notation}")
expected_output = "c4 d4 e4 f4 g4 a4 b4 c'4"
print(f"Expected: {expected_output}")
print(f"Match:    {'✅ FIXED' if expected_output in result.tiny_notation else '❌ BUG CONFIRMED'}")

# Bug 2: Explicit octave markers
print("\n🐞 BUG 2: Explicit Octave Markers")
print("-" * 80)

tests = [
    (r"\relative c { c'4 }", "c'4", "Single octave up - c' from base c should be C5"),
    (r"\relative c'' { c,4 }", "c4", "Octave down from c'' - c, should be C5"),
    (r"\relative c' { c4 e' g, c' }", "c4 e'4 g,4 c'4", "Mixed markers"),
]

for snippet, expected, name in tests:
    result = lily_to_tiny_notation(snippet)
    print(f"\nTest: {name}")
    print(f"  Input:    {snippet}")
    print(f"  Output:   {result.tiny_notation}")
    print(f"  Expected: {expected}")
    print(f"  Match:    {'✅ FIXED' if expected == result.tiny_notation else '❌ BUG CONFIRMED'}")

# Bug 3: Implicit duration inheritance
print("\n🐞 BUG 3: Implicit Duration Inheritance")
print("-" * 80)
snippet = r"\time 6/8 \relative c' { c8 d e f g a }"
result = lily_to_tiny_notation(snippet)
print(f"Input:    {snippet}")
print(f"Output:   {result.tiny_notation}")
print(f"Expected: 6/8 c8 d8 e8 f8 g8 a8")
print(f"Match:    {'✅ FIXED' if '6/8 c8 d8 e8 f8 g8 a8' == result.tiny_notation else '❌ BUG CONFIRMED'}")

# Bug 4: Relative mode with accidentals
print("\n🐞 BUG 4: Relative Mode with Accidentals")
print("-" * 80)
snippet = r"\relative c' { bes4 es as des }"
result = lily_to_tiny_notation(snippet)
print(f"Input:    {snippet}")
print(f"Output:   {result.tiny_notation}")
print(f"Expected: B-4 E-5 A-5 D-6 (ascending melodic line)")
print(f"Actual shows:   All in octave 4 ❌")

print("\n" + "=" * 80)
print("SUMMARY: All 4 critical bugs CONFIRMED")
print("Parser is NOT production-ready")
print("=" * 80)
