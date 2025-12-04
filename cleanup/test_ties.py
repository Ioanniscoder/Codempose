"""
Test Suite for Tie Support
===========================

Tests the implementation of tie notation (c4~ c4) which connects
two notes of the same pitch into a single sustained sound.

Tie Rules:
- Ties connect notes of the SAME pitch (step + octave + accidental)
- Tied notes merge into a single event with combined duration
- Ties can chain across multiple notes: c4~ c4~ c2
- Pitch mismatch breaks the tie chain
- Rests break the tie chain
"""

from lilypond_parser import parse_lilypond_to_data


def test_simple_tie():
    """Test basic tie: two quarter notes tied = half note."""
    print("\n" + "="*70)
    print("TEST 1: Simple Tie (c4~ c4)")
    print("="*70)
    
    snippet = r"\relative c' { c4~ c4 d2 }"
    
    print(f"\nInput: {snippet}")
    print("\nExpected: C4 (ql=2.0 from tied quarters), D4 (ql=2.0)")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events, 1):
        if event.get('type') == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            orig = event.get('original_token', '?')
            print(f"   {i}. {step}{octave} (ql={ql:.3f}) ← {orig}")
        else:
            print(f"   {i}. {event.get('type').upper()} (ql={event['ql']})")
    
    # Verify tie worked
    assert len(events) == 2, f"Expected 2 events, got {len(events)}"
    
    c_event = events[0]
    assert c_event['step'] == 'C' and c_event['octave'] == 5, "First note should be C5"
    assert c_event['ql'] == 2.0, f"Tied C4~ c4 should be 2.0 QL, got {c_event['ql']}"
    
    d_event = events[1]
    assert d_event['step'] == 'D' and d_event['octave'] == 5, "Second note should be D5"
    assert d_event['ql'] == 2.0, f"D2 should be 2.0 QL, got {d_event['ql']}"
    
    print("\n✅ Simple tie works correctly!")


def test_tie_chain():
    """Test chained ties: c4~ c4~ c2 = whole note."""
    print("\n" + "="*70)
    print("TEST 2: Tie Chain (c4~ c4~ c2)")
    print("="*70)
    
    snippet = r"\relative c' { c4~ c4~ c2 }"
    
    print(f"\nInput: {snippet}")
    print("\nExpected: C4 (ql=4.0 from three tied notes)")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} event(s):")
    for i, event in enumerate(events, 1):
        if event.get('type') == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            orig = event.get('original_token', '?')
            print(f"   {i}. {step}{octave} (ql={ql:.3f}) ← {orig}")
    
    # Verify tie chain
    assert len(events) == 1, f"Expected 1 merged event, got {len(events)}"
    
    c_event = events[0]
    assert c_event['step'] == 'C' and c_event['octave'] == 5, "Note should be C5"
    assert c_event['ql'] == 4.0, f"Tied c4~ c4~ c2 should be 4.0 QL, got {c_event['ql']}"
    
    print("\n✅ Tie chain works correctly!")


def test_tie_across_bar():
    """Test tie across bar line (most common use case)."""
    print("\n" + "="*70)
    print("TEST 3: Tie Across Bar Line")
    print("="*70)
    
    snippet = r"\relative c' { \time 4/4 c2~ | c4 d4 e2 }"
    
    print(f"\nInput: {snippet}")
    print("\nExpected: C4 (ql=3.0, tied across bar), D4 (ql=1.0), E4 (ql=2.0)")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events, 1):
        if event.get('type') == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            orig = event.get('original_token', '?')
            print(f"   {i}. {step}{octave} (ql={ql:.3f}) ← {orig}")
    
    # Verify
    assert len(events) == 3, f"Expected 3 events, got {len(events)}"
    
    c_event = events[0]
    assert c_event['ql'] == 3.0, f"Tied c2~ c4 should be 3.0 QL, got {c_event['ql']}"
    
    print("\n✅ Tie across bar line works correctly!")


def test_tie_broken_by_different_pitch():
    """Test that tie breaks when pitch changes."""
    print("\n" + "="*70)
    print("TEST 4: Tie Broken by Pitch Mismatch")
    print("="*70)
    
    snippet = r"\relative c' { c4~ d4 e4 f4 }"
    
    print(f"\nInput: {snippet}")
    print("\nExpected: C4 (ql=1.0, tie broken), D4, E4, F4 - all quarter notes")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events, 1):
        if event.get('type') == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            orig = event.get('original_token', '?')
            print(f"   {i}. {step}{octave} (ql={ql:.3f}) ← {orig}")
    
    # Verify all notes are separate
    assert len(events) == 4, f"Expected 4 events, got {len(events)}"
    
    for event in events:
        assert event['ql'] == 1.0, f"All notes should be 1.0 QL, got {event['ql']}"
    
    print("\n✅ Tie correctly broken by pitch mismatch!")


def test_tie_broken_by_rest():
    """Test that tie breaks when a rest intervenes."""
    print("\n" + "="*70)
    print("TEST 5: Tie Broken by Rest")
    print("="*70)
    
    snippet = r"\relative c' { c4~ r4 c4 d4 }"
    
    print(f"\nInput: {snippet}")
    print("\nExpected: C4 (ql=1.0, tie broken), REST, C4, D4")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events, 1):
        if event.get('type') == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            orig = event.get('original_token', '?')
            print(f"   {i}. {step}{octave} (ql={ql:.3f}) ← {orig}")
        else:
            print(f"   {i}. REST (ql={event['ql']})")
    
    # Verify
    assert len(events) == 4, f"Expected 4 events, got {len(events)}"
    assert events[0]['ql'] == 1.0, f"First C should be 1.0 QL, got {events[0]['ql']}"
    assert events[1]['type'] == 'rest', "Second event should be rest"
    
    print("\n✅ Tie correctly broken by rest!")


def test_tie_with_accidentals():
    """Test ties with accidental matching."""
    print("\n" + "="*70)
    print("TEST 6: Tie with Accidentals")
    print("="*70)
    
    snippet = r"\relative c' { fis4~ fis4 f4~ f4 }"
    
    print(f"\nInput: {snippet}")
    print("\nExpected: F#4 (ql=2.0), F4 (ql=2.0)")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events, 1):
        if event.get('type') == 'note':
            step = event['step']
            octave = event['octave']
            alter = event.get('alter', 0)
            ql = event['ql']
            acc_str = {1: '#', -1: 'b', 0: ''}.get(alter, '')
            orig = event.get('original_token', '?')
            print(f"   {i}. {step}{acc_str}{octave} (ql={ql:.3f}) ← {orig}")
    
    # Verify
    assert len(events) == 2, f"Expected 2 events, got {len(events)}"
    
    fis_event = events[0]
    assert fis_event['alter'] == 1, "First note should be F#"
    assert fis_event['ql'] == 2.0, f"Tied fis4~ fis4 should be 2.0 QL, got {fis_event['ql']}"
    
    f_event = events[1]
    assert f_event['alter'] == 0, "Second note should be F natural"
    assert f_event['ql'] == 2.0, f"Tied f4~ f4 should be 2.0 QL, got {f_event['ql']}"
    
    print("\n✅ Ties with accidentals work correctly!")


if __name__ == '__main__':
    print("\n" + "🎵"*35)
    print("TIE SUPPORT TEST SUITE")
    print("🎵"*35)
    
    try:
        test_simple_tie()
        test_tie_chain()
        test_tie_across_bar()
        test_tie_broken_by_different_pitch()
        test_tie_broken_by_rest()
        test_tie_with_accidentals()
        
        print("\n" + "="*70)
        print("✅ All tie tests passed!")
        print("="*70)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
