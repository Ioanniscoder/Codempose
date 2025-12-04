"""
Test Suite for Grace Note Support
==================================

Tests the grace note implementation using the ~prefix notation.

Grace Note Syntax: ~d16 c4
- Grace note d (16th) before main note c (quarter)
- Grace note has ql=0.0 (doesn't count toward measure)
- Main note keeps full duration

This is the zero-duration (acciaccatura) style.
"""

from lilypond_parser import parse_lilypond_to_data


def test_simple_grace_note():
    """Test basic grace note before a note."""
    print("="*70)
    print("TEST 1: Simple Grace Note (~d16 c4)")
    print("="*70)
    
    snippet = r"\relative c' { ~d16 c4 e4 g4 }"
    
    print(f"\nInput: {snippet}")
    print(f"\nExpected: Grace D4 (ql=0.0), C4 (ql=1.0), E4 (ql=1.0), G4 (ql=1.0)")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            is_grace = event.get('is_grace', False)
            grace_marker = " [GRACE]" if is_grace else ""
            orig = event.get('original_token', '?')
            print(f"   {i+1}. {step}{octave} (ql={ql:.3f}){grace_marker} ← {orig}")
    
    # Verify
    assert len(events) == 4, f"Expected 4 events, got {len(events)}"
    
    # Check grace note
    assert events[0]['is_grace'] == True, "First note should be grace note"
    assert events[0]['ql'] == 0.0, f"Grace note should have ql=0.0, got {events[0]['ql']}"
    assert events[0]['step'] == 'D', "Grace note should be D"
    
    # Check main notes
    assert events[1]['is_grace'] == False, "Second note should not be grace"
    assert events[1]['ql'] == 1.0, f"C4 should have ql=1.0, got {events[1]['ql']}"
    
    # Check measure total (excluding grace notes)
    measure_total = sum(e['ql'] for e in events if not e.get('is_grace', False))
    print(f"\n✓ Measure total (excluding grace): {measure_total} QL")
    assert measure_total == 3.0, f"Measure should total 3.0 QL, got {measure_total}"
    
    print(f"\n✅ Simple grace note works correctly!")


def test_multiple_grace_notes():
    """Test multiple grace notes in sequence."""
    print("\n" + "="*70)
    print("TEST 2: Multiple Grace Notes (~g8 ~a8 c4)")
    print("="*70)
    
    snippet = r"\relative c' { ~g8 ~a8 c4 d4 e4 }"
    
    print(f"\nInput: {snippet}")
    print(f"\nExpected: Grace G (ql=0.0), Grace A (ql=0.0), C4 (ql=1.0), D4 (ql=1.0), E4 (ql=1.0)")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            is_grace = event.get('is_grace', False)
            grace_marker = " [GRACE]" if is_grace else ""
            print(f"   {i+1}. {step}{octave} (ql={ql:.3f}){grace_marker}")
    
    # Verify
    assert len(events) == 5, f"Expected 5 events, got {len(events)}"
    assert events[0]['is_grace'] == True, "First note should be grace"
    assert events[1]['is_grace'] == True, "Second note should be grace"
    assert events[2]['is_grace'] == False, "Third note should not be grace"
    
    # Check measure total
    measure_total = sum(e['ql'] for e in events if not e.get('is_grace', False))
    print(f"\n✓ Measure total (excluding graces): {measure_total} QL")
    assert measure_total == 3.0, f"Measure should total 3.0 QL, got {measure_total}"
    
    print(f"\n✅ Multiple grace notes work correctly!")


def test_grace_note_with_accidental():
    """Test grace note with accidental."""
    print("\n" + "="*70)
    print("TEST 3: Grace Note with Accidental (~fis16 g4)")
    print("="*70)
    
    snippet = r"\relative c' { ~fis16 g4 a4 b4 }"
    
    print(f"\nInput: {snippet}")
    print(f"\nExpected: Grace F#4 (ql=0.0), G4 (ql=1.0), A4 (ql=1.0), B4 (ql=1.0)")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            alter = event.get('alter', 0)
            ql = event['ql']
            is_grace = event.get('is_grace', False)
            grace_marker = " [GRACE]" if is_grace else ""
            alter_str = {1: '#', -1: 'b', 0: ''}.get(alter, f'({alter})')
            print(f"   {i+1}. {step}{alter_str}{octave} (ql={ql:.3f}){grace_marker}")
    
    # Verify
    assert events[0]['is_grace'] == True, "First note should be grace"
    assert events[0]['step'] == 'F', "Grace note should be F"
    assert events[0]['alter'] == 1, "Grace note should be sharp"
    assert events[0]['ql'] == 0.0, "Grace note should have ql=0.0"
    
    print(f"\n✅ Grace note with accidental works correctly!")


def test_grace_note_across_bar():
    """Test grace note at beginning of new measure."""
    print("\n" + "="*70)
    print("TEST 4: Grace Note Across Bar Line")
    print("="*70)
    
    snippet = r"\relative c' { \time 2/4 c4 d4 | ~e8 f4 g8 }"
    
    print(f"\nInput: {snippet}")
    print(f"\nExpected: C4, D4, | Grace E, F4, G8")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            is_grace = event.get('is_grace', False)
            grace_marker = " [GRACE]" if is_grace else ""
            print(f"   {i+1}. {step}{octave} (ql={ql:.3f}){grace_marker}")
    
    # Find the grace note
    grace_notes = [e for e in events if e.get('is_grace', False)]
    assert len(grace_notes) == 1, f"Should have 1 grace note, found {len(grace_notes)}"
    assert grace_notes[0]['step'] == 'E', "Grace note should be E"
    
    print(f"\n✅ Grace note across bar line works correctly!")


def test_no_grace_notes():
    """Test that regular notes without grace prefix work normally."""
    print("\n" + "="*70)
    print("TEST 5: Regular Notes (No Grace Notes)")
    print("="*70)
    
    snippet = r"\relative c' { c4 d4 e4 f4 }"
    
    print(f"\nInput: {snippet}")
    print(f"\nExpected: All notes have is_grace=False and normal durations")
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events:")
    for i, event in enumerate(events):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            is_grace = event.get('is_grace', False)
            print(f"   {i+1}. {step}{octave} (ql={ql:.3f}) is_grace={is_grace}")
    
    # Verify no grace notes
    grace_count = sum(1 for e in events if e.get('is_grace', False))
    assert grace_count == 0, f"Should have 0 grace notes, found {grace_count}"
    
    # All notes should have normal duration
    for event in events:
        assert event['ql'] == 1.0, f"All notes should be quarter notes (1.0 QL)"
    
    print(f"\n✅ Regular notes work correctly (no false grace notes)!")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == '__main__':
    print("\n" + "🎵"*35)
    print("GRACE NOTE SUPPORT TEST SUITE")
    print("🎵"*35)
    
    try:
        test_simple_grace_note()
        test_multiple_grace_notes()
        test_grace_note_with_accidental()
        test_grace_note_across_bar()
        test_no_grace_notes()
        
        print("\n" + "="*70)
        print("✅ All grace note tests passed!")
        print("="*70)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
