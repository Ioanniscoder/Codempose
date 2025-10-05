"""
Demonstration of ParseResult usage - simulates the final parser output.

This is NOT the actual parser (we haven't built that yet), but rather
a hand-crafted example showing what the parser will eventually produce.

Run this to see what the final output format will look like.
"""

from data_structures import ParseResult, TokenInfo


def demo_simple_conversion():
    """Simulate parsing a simple melody."""
    print("\n" + "="*70)
    print("DEMO 1: Simple C Major Scale")
    print("="*70)
    
    # Simulate: \relative c' { c4 d e f g a b c }
    result = ParseResult(
        tiny_notation="4/4 C4 D4 E4 F4 G4 A4 B4 C5",
        tokens=[
            TokenInfo("c4", "C4", 0, pitch_leap=None),
            TokenInfo("d4", "D4", 1, pitch_leap=2),
            TokenInfo("e4", "E4", 2, pitch_leap=2),
            TokenInfo("f4", "F4", 3, pitch_leap=1),
            TokenInfo("g4", "G4", 4, pitch_leap=2),
            TokenInfo("a4", "A4", 5, pitch_leap=2),
            TokenInfo("b4", "B4", 6, pitch_leap=2),
            TokenInfo("c4", "C5", 7, pitch_leap=1),
        ],
        directives={"time": "4/4"},
        success=True
    )
    
    print(f"\n✓ TinyNotation output:\n  {result.tiny_notation}\n")
    print(result.format_review())
    
    return result


def demo_with_warnings():
    """Simulate parsing with localized accidentals and large leaps."""
    print("\n" + "="*70)
    print("DEMO 2: Real-World Example with Warnings")
    print("="*70)
    
    # Simulate: \relative e { \time 6/4 e2 bmol4 c2 r4 }
    result = ParseResult(
        tiny_notation="6/4 E2 Bb4 C2 r4",
        tokens=[
            TokenInfo("e2", "E2", 0, pitch_leap=None),
            TokenInfo(
                "bmol4", 
                "Bb4", 
                1, 
                pitch_leap=-5,
                warnings=["Localized accidental 'bmol' - consider using 'bes' or 'b-'"]
            ),
            TokenInfo("c2", "C2", 2, pitch_leap=13),  # Large leap!
            TokenInfo("r4", "r4", 3, pitch_leap=None),
        ],
        directives={
            "time": "6/4",
            "key": "c major",
            "tempo": "4=90"
        },
        warnings=[],
        success=True
    )
    
    print(f"\n✓ TinyNotation output:\n  {result.tiny_notation}\n")
    print(f"📊 Flagged tokens: {len(result.flagged_tokens())}\n")
    print(result.format_review())
    
    # Show inline annotation
    print(f"\n✓ Inline annotated format:\n  {result.format_inline_annotated()}\n")
    
    return result


def demo_json_export():
    """Demonstrate JSON export capability."""
    print("\n" + "="*70)
    print("DEMO 3: JSON Export for External Tools")
    print("="*70)
    
    result = ParseResult(
        tiny_notation="4/4 C4 Bb4",
        tokens=[
            TokenInfo("c4", "C4", 0),
            TokenInfo("bmol4", "Bb4", 1, warnings=["Localized accidental"]),
        ],
        directives={"time": "4/4"}
    )
    
    import json
    json_output = json.dumps(result.to_dict(), indent=2)
    print(json_output)
    
    return result


def demo_failure_case():
    """Simulate a parse that encountered problems."""
    print("\n" + "="*70)
    print("DEMO 4: Failed Parse with Global Warnings")
    print("="*70)
    
    result = ParseResult(
        tiny_notation="",
        tokens=[],
        warnings=[
            "Unable to parse LilyPond input",
            "Expected '\\relative' directive but found none"
        ],
        success=False
    )
    
    print(result.format_review())
    print(f"\n❌ Parse failed: {result.success}")
    
    return result


def demo_edge_cases():
    """Test various edge cases."""
    print("\n" + "="*70)
    print("DEMO 5: Edge Cases")
    print("="*70)
    
    # Large leap
    result = ParseResult(
        tiny_notation="4/4 C4 C7",
        tokens=[
            TokenInfo("c4", "C4", 0),
            TokenInfo("c'''4", "C7", 1, pitch_leap=36),  # 3 octaves!
        ],
        directives={"time": "4/4"}
    )
    
    print("Edge Case: Extreme octave leap (3 octaves)")
    print(result.format_review())
    
    flagged = result.flagged_tokens()
    if flagged:
        print(f"\n⚠️  Found {len(flagged)} flagged token(s):")
        for token in flagged:
            print(f"  • {token.original} → {token.converted} (leap: {token.pitch_leap} semitones)")


def run_all_demos():
    """Run all demonstrations."""
    print("\n" + "🎵"*35)
    print(" "*20 + "ParseResult Demo Suite")
    print("🎵"*35)
    
    demos = [
        demo_simple_conversion,
        demo_with_warnings,
        demo_json_export,
        demo_failure_case,
        demo_edge_cases
    ]
    
    results = []
    for demo_func in demos:
        result = demo_func()
        results.append(result)
        input("\n[Press Enter to continue to next demo...]")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total demos run: {len(results)}")
    print(f"Successful parses: {sum(1 for r in results if r.success)}")
    print(f"Demos with warnings: {sum(1 for r in results if r.has_warnings())}")
    print(f"Total flagged tokens: {sum(len(r.flagged_tokens()) for r in results)}")
    print("\n✅ All data structure features demonstrated successfully!")


if __name__ == '__main__':
    # Quick test mode (no pauses)
    import sys
    if '--quick' in sys.argv:
        demo_simple_conversion()
        demo_with_warnings()
        demo_json_export()
        demo_failure_case()
        demo_edge_cases()
    else:
        # Interactive mode
        run_all_demos()
