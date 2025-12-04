"""
CHORD TEST: Automated Regression Guard for Chord Parsing
==========================================================

This minimal test file validates the critical two-stage chord parsing process.
It serves as an automated regression guard to ensure chord parsing never breaks.

CRITICAL DEPENDENCIES:
1. Stage 1: LilyPond → TinyNotation (establishes chord base note octave)
2. Stage 2: TinyNotation → music21 (resolves all chord notes relative to each other)

This file is intentionally minimal - it contains ONLY chord-related features to
provide fast, focused validation.
"""

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Dict
from lilypond_parser import parse_lilypond_to_data
from music_data import extract_data_from_part, data_to_part
from score_builder import build_score_from_blueprint
from project_template import engrave_with_abjad, export_to_musicxml


# ============================================================================
# COMPOSER'S WORKSPACE
# ============================================================================

# Metadata
TITLE = "Chord Parsing Test"
COMPOSER = "Automated Test Suite"

# ----------------------------------------------------------------------------
# STATION 1: COMPOSING INPUT
# ----------------------------------------------------------------------------

# Test 1: Simple triads in different octaves
SIMPLE_CHORDS_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    <c e g>2 <d f a>2 |
    <e g b>2 <f a c>2
}
"""

# Test 2: Chords with accidentals
ACCIDENTAL_CHORDS_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    <c ees g>2 <d fis a>2 |
    <e gis b>2 <f aes c>2
}
"""

# Test 3: Chords in different octave ranges (critical for relative octave logic)
OCTAVE_CHORDS_LILY = r"""
\relative c, {
    \time 4/4
    \key c \major
    <c e g>2 <c' e g>2 |
    <c, e g>2 <c'' e g>2
}
"""

# Test 4: Mixed chord sizes (triads, seventh chords)
MIXED_CHORDS_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    <c e g>4 <c e g b>4 <d f a c>2 |
    <e g>4 <f a c e>4 <g b d>2
}
"""

# ----------------------------------------------------------------------------
# STATION 2: VALIDATING & GENERATED INPUT
# ----------------------------------------------------------------------------

# Expected TinyNotation strings (for validation)
SIMPLE_CHORDS_TINY = "tinynotation: 4/4 <c e g>2 <d f a>2 <e g b>2 <f a c>2"
ACCIDENTAL_CHORDS_TINY = "tinynotation: 4/4 <c e- g>2 <d f# a>2 <e g# b>2 <f a- c>2"
OCTAVE_CHORDS_TINY = "tinynotation: 4/4 <c e g>2 <c' e g>2 <c, e g>2 <c'' e g>2"
MIXED_CHORDS_TINY = "tinynotation: 4/4 <c e g>4 <c e g b>4 <d f a c>2 <e g>4 <f a c e>4 <g b d>2"

# ----------------------------------------------------------------------------
# STATION 3: STRUCTURING INPUT
# ----------------------------------------------------------------------------

# Simple single-staff blueprint for testing
VOICE_STAVE_DEF = "ChordStaff"

VOICE_STAVE_DATA = """
    SIMPLE_CHORDS;
    ACCIDENTAL_CHORDS;
    OCTAVE_CHORDS;
    MIXED_CHORDS
"""


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_chord_parsing_tests() -> Dict[str, Dict]:
    """
    Execute chord parsing validation tests.
    
    Returns:
        score_data dictionary with all chord tests
    """
    print("\n" + "="*70)
    print("CHORD PARSING REGRESSION TEST")
    print("="*70)
    
    test_results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # ========================================================================
    # TEST 1: Simple Chords
    # ========================================================================
    
    print("\n[TEST 1: Simple Triads]")
    try:
        parsed = parse_lilypond_to_data(SIMPLE_CHORDS_LILY, part_name='SimpleChords')
        events = parsed.get('parts', {}).get('SimpleChords', [])
        
        # Validate: Should have 4 chord events
        chord_events = [e for e in events if e.get('type') == 'chord']
        assert len(chord_events) == 4, f"Expected 4 chords, got {len(chord_events)}"
        
        # Validate: Each chord should have 3 pitches (triads)
        for i, chord in enumerate(chord_events):
            pitches = chord.get('pitches', [])
            assert len(pitches) == 3, f"Chord {i+1}: Expected 3 pitches, got {len(pitches)}"
        
        # Validate: First chord should be C major (C5, E5, G5 - \relative c' means C5)
        first_chord = chord_events[0]['pitches']
        assert first_chord[0]['step'] == 'C' and first_chord[0]['octave'] == 5, f"Expected C5, got {first_chord[0]}"
        assert first_chord[1]['step'] == 'E' and first_chord[1]['octave'] == 5, f"Expected E5, got {first_chord[1]}"
        assert first_chord[2]['step'] == 'G' and first_chord[2]['octave'] == 5, f"Expected G5, got {first_chord[2]}"
        
        simple_chords_events = events
        test_results['passed'].append('Simple Triads')
        print("   ✅ PASSED: Simple triads parsed correctly")
        print(f"      • 4 chord events detected")
        print(f"      • First chord: {[p['step']+str(p['octave']) for p in first_chord]}")
        
    except AssertionError as e:
        test_results['failed'].append(f'Simple Triads: {e}')
        print(f"   ❌ FAILED: {e}")
        simple_chords_events = []
    except Exception as e:
        test_results['failed'].append(f'Simple Triads: {e}')
        print(f"   ❌ ERROR: {e}")
        simple_chords_events = []
    
    # ========================================================================
    # TEST 2: Chords with Accidentals
    # ========================================================================
    
    print("\n[TEST 2: Chords with Accidentals]")
    try:
        parsed = parse_lilypond_to_data(ACCIDENTAL_CHORDS_LILY, part_name='AccidentalChords')
        events = parsed.get('parts', {}).get('AccidentalChords', [])
        
        chord_events = [e for e in events if e.get('type') == 'chord']
        assert len(chord_events) == 4, f"Expected 4 chords, got {len(chord_events)}"
        
        # Validate: First chord should have E-flat (alter=-1)
        first_chord = chord_events[0]['pitches']
        assert first_chord[1]['step'] == 'E' and first_chord[1]['alter'] == -1
        
        # Validate: Second chord should have F-sharp (alter=1)
        second_chord = chord_events[1]['pitches']
        assert second_chord[1]['step'] == 'F' and second_chord[1]['alter'] == 1
        
        accidental_chords_events = events
        test_results['passed'].append('Accidental Chords')
        print("   ✅ PASSED: Accidentals parsed correctly")
        print(f"      • E-flat detected: alter={first_chord[1]['alter']}")
        print(f"      • F-sharp detected: alter={second_chord[1]['alter']}")
        
    except AssertionError as e:
        test_results['failed'].append(f'Accidental Chords: {e}')
        print(f"   ❌ FAILED: {e}")
        accidental_chords_events = []
    except Exception as e:
        test_results['failed'].append(f'Accidental Chords: {e}')
        print(f"   ❌ ERROR: {e}")
        accidental_chords_events = []
    
    # ========================================================================
    # TEST 3: Octave Range Handling
    # ========================================================================
    
    print("\n[TEST 3: Octave Range Handling]")
    try:
        parsed = parse_lilypond_to_data(OCTAVE_CHORDS_LILY, part_name='OctaveChords')
        events = parsed.get('parts', {}).get('OctaveChords', [])
        
        chord_events = [e for e in events if e.get('type') == 'chord']
        assert len(chord_events) == 4, f"Expected 4 chords, got {len(chord_events)}"
        
        # Validate: First chord should be C3
        chord1 = chord_events[0]['pitches']
        assert chord1[0]['octave'] == 3, f"Chord 1: Expected octave 3, got {chord1[0]['octave']}"
        
        # Validate: Second chord should be C4 (one octave up)
        chord2 = chord_events[1]['pitches']
        assert chord2[0]['octave'] == 4, f"Chord 2: Expected octave 4, got {chord2[0]['octave']}"
        
        # Validate: Third chord should be C3 (back down)
        chord3 = chord_events[2]['pitches']
        assert chord3[0]['octave'] == 3, f"Chord 3: Expected octave 3, got {chord3[0]['octave']}"
        
        # Validate: Fourth chord should be C5 (two octaves up from third)
        chord4 = chord_events[3]['pitches']
        assert chord4[0]['octave'] == 5, f"Chord 4: Expected octave 5, got {chord4[0]['octave']}"
        
        octave_chords_events = events
        test_results['passed'].append('Octave Range')
        print("   ✅ PASSED: Octave ranges handled correctly")
        print(f"      • Octaves: {chord1[0]['octave']} → {chord2[0]['octave']} → {chord3[0]['octave']} → {chord4[0]['octave']}")
        
    except AssertionError as e:
        test_results['failed'].append(f'Octave Range: {e}')
        print(f"   ❌ FAILED: {e}")
        octave_chords_events = []
    except Exception as e:
        test_results['failed'].append(f'Octave Range: {e}')
        print(f"   ❌ ERROR: {e}")
        octave_chords_events = []
    
    # ========================================================================
    # TEST 4: Mixed Chord Sizes
    # ========================================================================
    
    print("\n[TEST 4: Mixed Chord Sizes]")
    try:
        parsed = parse_lilypond_to_data(MIXED_CHORDS_LILY, part_name='MixedChords')
        events = parsed.get('parts', {}).get('MixedChords', [])
        
        chord_events = [e for e in events if e.get('type') == 'chord']
        assert len(chord_events) == 6, f"Expected 6 chords, got {len(chord_events)}"
        
        # Validate: Chord sizes
        expected_sizes = [3, 4, 4, 2, 4, 3]  # triads, seventh, dyad, seventh, triad
        for i, (chord, expected_size) in enumerate(zip(chord_events, expected_sizes)):
            actual_size = len(chord['pitches'])
            assert actual_size == expected_size, f"Chord {i+1}: Expected {expected_size} pitches, got {actual_size}"
        
        mixed_chords_events = events
        test_results['passed'].append('Mixed Chord Sizes')
        print("   ✅ PASSED: Mixed chord sizes handled correctly")
        print(f"      • Chord sizes: {[len(c['pitches']) for c in chord_events]}")
        
    except AssertionError as e:
        test_results['failed'].append(f'Mixed Chord Sizes: {e}')
        print(f"   ❌ FAILED: {e}")
        mixed_chords_events = []
    except Exception as e:
        test_results['failed'].append(f'Mixed Chord Sizes: {e}')
        print(f"   ❌ ERROR: {e}")
        mixed_chords_events = []
    
    # ========================================================================
    # ASSEMBLE FINAL SCORE (if all tests passed)
    # ========================================================================
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    
    if test_results['failed']:
        print("\n❌ FAILED TESTS:")
        for failure in test_results['failed']:
            print(f"   • {failure}")
        raise AssertionError("Chord parsing tests failed - see details above")
    
    print("\n✅ ALL CHORD PARSING TESTS PASSED")
    
    # Build snippet library
    SNIPPETS = {
        'SIMPLE_CHORDS': simple_chords_events,
        'ACCIDENTAL_CHORDS': accidental_chords_events,
        'OCTAVE_CHORDS': octave_chords_events,
        'MIXED_CHORDS': mixed_chords_events,
    }
    
    # Assemble score
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'}
    }
    
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
    
    return score_data


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run tests
        score_data = run_chord_parsing_tests()
        
        # Generate outputs
        print("\n" + "="*70)
        print("GENERATING OUTPUT FILES")
        print("="*70)
        
        engrave_with_abjad(score_data, 'chord_test', source_file=__file__)
        print("✅ Successfully compiled chord_test.pdf and .midi")
        
        export_to_musicxml(score_data, 'chord_test')
        print("✅ Successfully exported chord_test.musicxml")
        
        print("\n" + "="*70)
        print("✅ CHORD PARSING VALIDATION COMPLETE")
        print("="*70)
        print("\nGenerated files:")
        print("  • outputs/chord_test.ly")
        print("  • outputs/chord_test.pdf")
        print("  • outputs/chord_test.midi")
        print("  • outputs/chord_test.musicxml")
        print()
        
        sys.exit(0)
        
    except AssertionError as e:
        print("\n" + "="*70)
        print("❌ CHORD PARSING TESTS FAILED")
        print("="*70)
        print(f"\nError: {e}")
        print("\nThis indicates a regression in the chord parsing logic.")
        print("Review the two-stage parsing process:")
        print("  1. relative_octave_logic.py - Base note octave resolution")
        print("  2. lilypond_parser.py - All chord notes resolution")
        print()
        sys.exit(1)
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ UNEXPECTED ERROR")
        print("="*70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
