"""
Test suite for composition_shorthand and advanced_transformations modules.

This file demonstrates the usage of both modules and verifies they work correctly.
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from composition_shorthand import (
    from_roman_numerals,
    from_scale_degrees,
    stretch_events,
    transpose_events,
    augment,
    diminish
)

from advanced_transformations import (
    create_melodic_sequence,
    realize_figured_bass,
    apply_modal_mixture
)


def test_from_roman_numerals():
    """Test Roman numeral chord generation."""
    print("\n=== Testing from_roman_numerals ===")
    
    # Test basic progression
    progression = from_roman_numerals(
        progression_str="I-V-vi-IV",
        key_str="C",
        rhythm_str="w-w-w-w"
    )
    
    print(f"Generated {len(progression)} chords")
    assert len(progression) == 4, "Should generate 4 chords"
    assert progression[0]['type'] == 'chord', "Should be chord events"
    assert progression[0]['ql'] == 4.0, "Whole note should be 4.0 ql"
    
    # Check first chord (I in C major = C-E-G)
    first_chord_pitches = progression[0]['pitches']
    print(f"First chord (I in C): {[p['step'] for p in first_chord_pitches]}")
    
    print("✓ from_roman_numerals test passed")
    return progression


def test_from_scale_degrees():
    """Test scale degree melody generation."""
    print("\n=== Testing from_scale_degrees ===")
    
    # Test basic scale
    melody = from_scale_degrees(
        degree_str="1-2-3-4-5-6-7-1",
        key_str="C",
        rhythm_str="q-q-q-q-q-q-q-h"
    )
    
    print(f"Generated {len(melody)} notes")
    assert len(melody) == 8, "Should generate 8 notes"
    assert melody[0]['type'] == 'note', "Should be note events"
    assert melody[0]['step'] == 'C', "First note in C major scale should be C"
    assert melody[0]['ql'] == 1.0, "Quarter note should be 1.0 ql"
    
    # Test with rest
    melody_with_rest = from_scale_degrees(
        degree_str="1-3-5-r-1",
        key_str="C",
        rhythm_str="q-q-q-q-h"
    )
    
    assert melody_with_rest[3]['type'] == 'rest', "Should have a rest"
    
    print(f"Melody notes: {[n['step'] if n['type'] == 'note' else 'R' for n in melody[:5]]}")
    print("✓ from_scale_degrees test passed")
    return melody


def test_stretch_events():
    """Test rhythmic augmentation and diminution."""
    print("\n=== Testing stretch_events ===")
    
    # Create a simple melody
    melody = from_scale_degrees("1-2-3", "C", "q-q-q")
    
    # Test augmentation
    augmented = augment(melody)
    assert augmented[0]['ql'] == 2.0, "Augmentation should double duration"
    print(f"Original ql: {melody[0]['ql']}, Augmented ql: {augmented[0]['ql']}")
    
    # Test diminution
    diminished = diminish(melody)
    assert diminished[0]['ql'] == 0.5, "Diminution should halve duration"
    print(f"Original ql: {melody[0]['ql']}, Diminished ql: {diminished[0]['ql']}")
    
    # Test custom stretch
    stretched = stretch_events(melody, 1.5)
    assert stretched[0]['ql'] == 1.5, "Should multiply by custom factor"
    
    print("✓ stretch_events test passed")
    return augmented


def test_transpose_events():
    """Test transposition."""
    print("\n=== Testing transpose_events ===")
    
    # Create a C major triad as melody
    melody = from_scale_degrees("1-3-5", "C", "q-q-q")
    
    # Transpose up a perfect fifth (7 semitones)
    transposed = transpose_events(melody, 7)
    
    print(f"Original first note: {melody[0]['step']}{melody[0]['octave']}")
    print(f"Transposed first note: {transposed[0]['step']}{transposed[0]['octave']}")
    
    # C transposed up a fifth should be G
    assert transposed[0]['step'] == 'G', "C + P5 should be G"
    
    print("✓ transpose_events test passed")
    return transposed


def test_create_melodic_sequence():
    """Test melodic sequencing."""
    print("\n=== Testing create_melodic_sequence ===")
    
    # Create a simple theme
    theme = from_scale_degrees("1-3-5", "C", "q-q-q")
    
    # Create a descending sequence
    sequence = create_melodic_sequence(
        events=theme,
        interval_pattern=[-2, -2],  # Down a step twice
        key='C major',
        preserve_rhythm=True
    )
    
    # Should have original + 2 transpositions = 9 notes total
    expected_length = len(theme) + (len(theme) * 2)
    print(f"Theme length: {len(theme)}, Sequence length: {len(sequence)}")
    assert len(sequence) == expected_length, f"Should have {expected_length} notes"
    
    print("✓ create_melodic_sequence test passed")
    return sequence


def test_realize_figured_bass():
    """Test figured bass realization."""
    print("\n=== Testing realize_figured_bass ===")
    
    # Create a simple bass line
    bass_line = from_scale_degrees("1-5-1", "C", "w-w-w")
    
    # Realize it
    voices = realize_figured_bass(
        bass_events=bass_line,
        figures="5/3 5/3 5/3"
    )
    
    # Should return a dictionary with SATB voices
    assert 'Soprano' in voices, "Should have Soprano voice"
    assert 'Alto' in voices, "Should have Alto voice"
    assert 'Tenor' in voices, "Should have Tenor voice"
    assert 'Bass' in voices, "Should have Bass voice"
    
    # All voices should have the same number of events
    assert len(voices['Soprano']) == len(bass_line), "All voices should match bass length"
    
    print(f"Generated {len(voices)} voices with {len(voices['Soprano'])} events each")
    print("✓ realize_figured_bass test passed")
    return voices


def test_complete_example():
    """Test a complete composition using both modules."""
    print("\n=== Testing Complete Example ===")
    
    # Shorthand: Create building blocks
    theme = from_scale_degrees("1-3-5-3-1", "C", "q-q-q-q-h")
    harmony = from_roman_numerals("I-IV-V-I", "C", "w-w-w-w")
    
    # Programmatic: Create complex transformations
    sequence = create_melodic_sequence(
        events=theme,
        interval_pattern=[-2, 2],
        key='C major'
    )
    
    # Build score structure
    score_data = {
        'metadata': {
            'title': 'Test Composition',
            'composer': 'Test Suite'
        },
        'parts': {
            'Melody': {
                'Theme': theme,
                'Sequence': sequence
            },
            'Harmony': {
                'Chords': harmony
            }
        }
    }
    
    print(f"Score has {len(score_data['parts'])} parts")
    print(f"  - Melody: {list(score_data['parts']['Melody'].keys())}")
    print(f"  - Harmony: {list(score_data['parts']['Harmony'].keys())}")
    
    print("✓ Complete example test passed")
    return score_data


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TRANSFORMATION MODULES TEST SUITE")
    print("=" * 60)
    
    try:
        # Test composition_shorthand functions
        test_from_roman_numerals()
        test_from_scale_degrees()
        test_stretch_events()
        test_transpose_events()
        
        # Test advanced_transformations functions
        test_create_melodic_sequence()
        test_realize_figured_bass()
        
        # Test complete integration
        test_complete_example()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe transformation modules are working correctly!")
        print("See ADVANCED_TRANSFORMATIONS_GUIDE.md for usage examples.")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
