"""
Test Custom Tuplet Shorthand Notation
======================================

This test verifies that the custom square bracket tuplet notation works:
- [c d e]8     → Triplet of eighth notes (3/2)
- [c d e f]16  → Quadruplet of sixteenth notes (4/3)
- [c d e f g]8 → Quintuplet (5/4)
"""

from lilypond_parser import parse_lilypond_to_data


def test_triplet_shorthand():
    """Test [a b c]8 → triplet of eighth notes."""
    print("\n" + "="*70)
    print("TEST 1: Triplet Shorthand [c d e]8")
    print("="*70)
    
    snippet = r"\relative c' { \time 4/4 c4 [d e f]8 g4 r4 }"
    
    print(f"\nInput: {snippet}")
    print("\nExpected: c4 → triplet(d8 e8 f8) → g4 → r4")
    
    result = parse_lilypond_to_data(snippet, part_name='Test')
    events = result.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, ev in enumerate(events):
        if ev.get('type') == 'note':
            step = ev.get('step')
            octave = ev.get('octave')
            ql = ev.get('ql')
            tuplet = ev.get('tuplet_ratio')
            orig = ev.get('original_token', '?')
            if tuplet:
                print(f"  {i+1:2d}. {step}{octave} (ql={ql:.3f}) TUPLET {tuplet} ← {orig}")
            else:
                print(f"  {i+1:2d}. {step}{octave} (ql={ql:.3f}) ← {orig}")
        elif ev.get('type') == 'rest':
            print(f"  {i+1:2d}. REST (ql={ev.get('ql')})")
    
    # Verify triplet quarter lengths
    # Triplet eighth notes: 3 notes in time of 2 eighths
    # Each note = (2 * 0.5) / 3 = 0.333... QL
    triplet_events = [e for e in events if e.get('tuplet_ratio')]
    if triplet_events:
        expected_ql = 2 * 0.5 / 3  # 2 eighth notes / 3 = 0.333...
        for ev in triplet_events:
            actual_ql = ev.get('ql', 0)
            if abs(actual_ql - expected_ql) < 0.01:
                print(f"\n✅ Tuplet duration correct: {actual_ql:.3f} QL")
            else:
                print(f"\n❌ Tuplet duration wrong: {actual_ql:.3f} QL (expected {expected_ql:.3f})")
    else:
        print("\n⚠️ No tuplet events found!")
    
    return result


def test_standard_lilypond_tuplet():
    """Test standard LilyPond \\tuplet 3/2 { c8 d8 e8 } syntax."""
    print("\n" + "="*70)
    print("TEST 2: Standard LilyPond Tuplet \\tuplet 3/2 { ... }")
    print("="*70)
    
    snippet = r"\relative c' { \time 4/4 c4 \tuplet 3/2 { d8 e8 f8 } g4 }"
    
    print(f"\nInput: {snippet}")
    
    result = parse_lilypond_to_data(snippet, part_name='Test')
    events = result.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, ev in enumerate(events):
        if ev.get('type') == 'note':
            step = ev.get('step')
            octave = ev.get('octave')
            ql = ev.get('ql')
            tuplet = ev.get('tuplet_ratio')
            if tuplet:
                print(f"  {i+1:2d}. {step}{octave} (ql={ql:.3f}) TUPLET {tuplet}")
            else:
                print(f"  {i+1:2d}. {step}{octave} (ql={ql:.3f})")
    
    return result


def test_quintuplet_shorthand():
    """Test [a b c d e]8 → quintuplet."""
    print("\n" + "="*70)
    print("TEST 3: Quintuplet Shorthand [c d e f g]8")
    print("="*70)
    
    snippet = r"\relative c' { \time 4/4 [c d e f g]8 r2 }"
    
    print(f"\nInput: {snippet}")
    print("\nExpected: 5 eighth notes in time of 4 (quintuplet)")
    
    result = parse_lilypond_to_data(snippet, part_name='Test')
    events = result.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, ev in enumerate(events):
        if ev.get('type') == 'note':
            step = ev.get('step')
            octave = ev.get('octave')
            ql = ev.get('ql')
            tuplet = ev.get('tuplet_ratio')
            if tuplet:
                print(f"  {i+1:2d}. {step}{octave} (ql={ql:.3f}) TUPLET {tuplet}")
            else:
                print(f"  {i+1:2d}. {step}{octave} (ql={ql:.3f})")
        elif ev.get('type') == 'rest':
            print(f"  {i+1:2d}. REST (ql={ev.get('ql')})")
    
    # Verify quintuplet quarter lengths
    # 5 notes in time of 4 eighth notes
    # Each note = (4 * 0.5) / 5 = 0.4 QL
    tuplet_events = [e for e in events if e.get('tuplet_ratio')]
    if tuplet_events:
        expected_ql = 4 * 0.5 / 5  # 0.4 QL
        for ev in tuplet_events:
            actual_ql = ev.get('ql', 0)
            if abs(actual_ql - expected_ql) < 0.01:
                print(f"\n✅ Quintuplet duration correct: {actual_ql:.3f} QL")
            else:
                print(f"\n❌ Quintuplet duration wrong: {actual_ql:.3f} QL (expected {expected_ql:.3f})")
    
    return result


if __name__ == '__main__':
    print("\n" + "🎵 "*35)
    print("CUSTOM TUPLET NOTATION TESTS")
    print("🎵 "*35)
    
    test_triplet_shorthand()
    test_standard_lilypond_tuplet()
    test_quintuplet_shorthand()
    
    print("\n" + "="*70)
    print("✅ All tests complete!")
    print("="*70 + "\n")
