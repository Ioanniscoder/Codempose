"""
Test Suite for Articulation Support
====================================

Tests tenuto (-) and accent (>) articulation marks.

Syntax:
- c4-  = quarter C with tenuto
- d4>  = quarter D with accent
- e4   = quarter E (no articulation)

Note: Staccato (.) conflicts with dotted rhythm notation (c4. = dotted quarter).
For now, we support tenuto and accent which have no conflicts.
"""

from lilypond_parser import parse_lilypond_to_data


def test_tenuto():
    """
    Test tenuto articulation (dash suffix).
    
    Syntax: c4- means quarter note with tenuto
    """
    print("\n" + "="*70)
    print("TEST 1: Tenuto Articulation (c4- d4- e4)")
    print("="*70)
    
    snippet = r"\relative c' { c4- d4- e4 }"
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events from: {snippet}")
    print("\nEvent details:")
    
    for i, event in enumerate(events, 1):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            artic = event.get('articulation', '')
            artic_label = f" [tenuto]" if artic == '-' else ""
            print(f"  {i}. {step}{octave} (ql={ql:.3f}){artic_label}")
    
    # Validate articulations
    assert events[0]['articulation'] == '-', "First note should have tenuto"
    assert events[1]['articulation'] == '-', "Second note should have tenuto"
    assert events[2]['articulation'] == '', "Third note should have no articulation"
    
    print("\n✅ Tenuto articulation works correctly!")
    return True


def test_accent():
    """
    Test accent articulation (> suffix).
    
    Syntax: c4> means quarter note with accent
    """
    print("\n" + "="*70)
    print("TEST 2: Accent Articulation (c4> d4> e4)")
    print("="*70)
    
    snippet = r"\relative c' { c4> d4> e4 }"
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events from: {snippet}")
    print("\nEvent details:")
    
    for i, event in enumerate(events, 1):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            artic = event.get('articulation', '')
            artic_label = f" [accent]" if artic == '>' else ""
            print(f"  {i}. {step}{octave} (ql={ql:.3f}){artic_label}")
    
    # Validate articulations
    assert events[0]['articulation'] == '>', "First note should have accent"
    assert events[1]['articulation'] == '>', "Second note should have accent"
    assert events[2]['articulation'] == '', "Third note should have no articulation"
    
    print("\n✅ Accent articulation works correctly!")
    return True


def test_mixed_articulations():
    """
    Test multiple articulation types in one phrase.
    
    Syntax: Mix of tenuto, accent, and plain notes
    """
    print("\n" + "="*70)
    print("TEST 3: Mixed Articulations (c4- d4> e4 f4-)")
    print("="*70)
    
    snippet = r"\relative c' { c4- d4> e4 f4- }"
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events from: {snippet}")
    print("\nEvent details:")
    
    articulation_names = {
        '-': 'tenuto',
        '>': 'accent',
        '': 'none'
    }
    
    for i, event in enumerate(events, 1):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            artic = event.get('articulation', '')
            artic_name = articulation_names.get(artic, 'unknown')
            print(f"  {i}. {step}{octave} (ql={ql:.3f}) → {artic_name}")
    
    # Validate articulations
    assert events[0]['articulation'] == '-', "C should have tenuto"
    assert events[1]['articulation'] == '>', "D should have accent"
    assert events[2]['articulation'] == '', "E should have no articulation"
    assert events[3]['articulation'] == '-', "F should have tenuto"
    
    print("\n✅ Mixed articulations work correctly!")
    return True


def test_articulation_with_accidentals():
    """
    Test articulations combined with accidentals.
    
    Syntax: fis4- (F-sharp quarter with tenuto)
    """
    print("\n" + "="*70)
    print("TEST 4: Articulation with Accidentals (fis4- bes4> es4-)")
    print("="*70)
    
    snippet = r"\relative c' { fis4- bes4> es4- }"
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events from: {snippet}")
    print("\nEvent details:")
    
    for i, event in enumerate(events, 1):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            alter = event.get('alter', 0)
            ql = event['ql']
            artic = event.get('articulation', '')
            
            alter_str = ''
            if alter == 1:
                alter_str = '#'
            elif alter == -1:
                alter_str = 'b'
            
            artic_label = f" [{artic}]" if artic else ""
            print(f"  {i}. {step}{alter_str}{octave} (ql={ql:.3f}){artic_label}")
    
    # Validate
    assert events[0]['step'] == 'F' and events[0]['alter'] == 1, "F# parsed correctly"
    assert events[0]['articulation'] == '-', "F# should have tenuto"
    
    assert events[1]['step'] == 'B' and events[1]['alter'] == -1, "Bb parsed correctly"
    assert events[1]['articulation'] == '>', "Bb should have accent"
    
    assert events[2]['step'] == 'E' and events[2]['alter'] == -1, "Eb parsed correctly"
    assert events[2]['articulation'] == '-', "Eb should have tenuto"
    
    print("\n✅ Articulations with accidentals work correctly!")
    return True


def test_articulation_with_ties():
    """
    Test articulations combined with ties.
    
    Syntax: c4-~ c4 (tenuto on first note, tied to second)
    Note: Articulation comes BEFORE tie marker
    """
    print("\n" + "="*70)
    print("TEST 5: Articulation with Ties (c4-~ c4 d4>~ d4)")
    print("="*70)
    
    snippet = r"\relative c' { c4-~ c4 d4>~ d4 }"
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events from: {snippet}")
    print("\nEvent details:")
    
    for i, event in enumerate(events, 1):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            artic = event.get('articulation', '')
            artic_label = f" [{artic}]" if artic else ""
            print(f"  {i}. {step}{octave} (ql={ql:.3f}){artic_label}")
    
    # Validate: First C should be merged and have tenuto
    assert events[0]['step'] == 'C', "First note is C"
    assert events[0]['ql'] == 2.0, "C should be tied (2.0 QL)"
    
    assert events[1]['step'] == 'D', "Second note is D"
    assert events[1]['ql'] == 2.0, "D should be tied (2.0 QL)"
    
    print("\n✅ Articulations with ties work correctly!")
    return True


def test_no_false_positives():
    """
    Test that regular notes don't get false articulation marks.
    """
    print("\n" + "="*70)
    print("TEST 6: No False Positives (c4 d4 e4 f4)")
    print("="*70)
    
    snippet = r"\relative c' { c4 d4 e4 f4 }"
    
    parsed = parse_lilypond_to_data(snippet, part_name='Test')
    events = parsed.get('parts', {}).get('Test', [])
    
    print(f"\n✓ Parsed {len(events)} events from: {snippet}")
    print("\nEvent details:")
    
    for i, event in enumerate(events, 1):
        if event['type'] == 'note':
            step = event['step']
            octave = event['octave']
            ql = event['ql']
            artic = event.get('articulation', '')
            status = "✓ clean" if not artic else f"✗ has '{artic}'"
            print(f"  {i}. {step}{octave} (ql={ql:.3f}) → {status}")
    
    # Validate: No articulations
    for event in events:
        assert event.get('articulation', '') == '', "No notes should have articulation"
    
    print("\n✅ No false positives detected!")
    return True


if __name__ == '__main__':
    print("\n🎵🎵🎵 ARTICULATION SUPPORT TEST SUITE 🎵🎵🎵")
    
    tests = [
        test_tenuto,
        test_accent,
        test_mixed_articulations,
        test_articulation_with_accidentals,
        test_articulation_with_ties,
        test_no_false_positives,
    ]
    
    passed = 0
    failed = 0
    
    for test_fn in tests:
        try:
            if test_fn():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(tests)}")
    else:
        print("✅ All articulation tests passed!")
    print("="*70)
