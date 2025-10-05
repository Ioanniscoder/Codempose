"""
Example Composition Using Hybrid Model
=======================================

This file demonstrates how to use both composition_shorthand.py and
advanced_transformations.py to create a complete musical composition.

This example follows the hybrid model:
- Use shorthand functions for simple operations
- Use programmatic functions for complex transformations
- Combine both approaches in build_score_data()
"""

from composition_shorthand import (
    from_roman_numerals,
    from_scale_degrees,
    augment,
    transpose_events
)

from advanced_transformations import (
    create_melodic_sequence,
    realize_figured_bass
)


def build_score_data():
    """
    Build a complete musical score using the hybrid model.
    
    This demonstrates both simple shorthand operations and
    complex programmatic transformations.
    """
    
    print("🎵 Building score with hybrid model...")
    
    # ═══════════════════════════════════════════════════════════════
    # PART 1: Use Shorthand for Simple Building Blocks
    # ═══════════════════════════════════════════════════════════════
    
    print("\n📝 Creating simple building blocks with shorthand...")
    
    # Create a simple melodic theme using scale degrees
    theme = from_scale_degrees(
        degree_str="1-3-5-4-3-2-1",
        key_str="C",
        rhythm_str="q-e-e-q-q-q-h"
    )
    print(f"  ✓ Created theme with {len(theme)} notes")
    
    # Create a countermelody in a different register
    countermelody = from_scale_degrees(
        degree_str="5-3-1-7-1",
        key_str="C",
        rhythm_str="h-q-q-q-h"
    )
    # Transpose down an octave for variety
    countermelody = transpose_events(countermelody, -12)
    print(f"  ✓ Created countermelody with {len(countermelody)} notes")
    
    # Create a harmonic progression using Roman numerals
    harmony = from_roman_numerals(
        progression_str="I-vi-IV-V-I",
        key_str="C",
        rhythm_str="w-w-w-w-w"
    )
    print(f"  ✓ Created harmonic progression with {len(harmony)} chords")
    
    # Create an augmented version of the theme for variation
    theme_slow = augment(theme, multiplier=2.0)
    print(f"  ✓ Created augmented theme (2x slower)")
    
    # ═══════════════════════════════════════════════════════════════
    # PART 2: Use Programmatic Functions for Complex Operations
    # ═══════════════════════════════════════════════════════════════
    
    print("\n🔧 Applying complex transformations programmatically...")
    
    # Create a melodic sequence (descending pattern)
    soprano_sequence = create_melodic_sequence(
        events=theme,
        interval_pattern=[-2, -2, -2],  # Descending by whole steps
        key='C major',
        preserve_rhythm=True
    )
    print(f"  ✓ Created melodic sequence with {len(soprano_sequence)} notes")
    
    # Create another sequence (ascending pattern)
    alto_sequence = create_melodic_sequence(
        events=countermelody,
        interval_pattern=[2, 2, -4],  # Up, up, down
        key='C major',
        preserve_rhythm=True
    )
    print(f"  ✓ Created second sequence with {len(alto_sequence)} notes")
    
    # Create a bass line and realize it with figured bass
    bass_line = from_scale_degrees(
        degree_str="1-6-4-5-1",
        key_str="C",
        rhythm_str="w-w-w-w-w"
    )
    # Transpose bass down an octave
    bass_line = transpose_events(bass_line, -12)
    
    # Realize the figured bass into 4 voices
    satb_voices = realize_figured_bass(
        bass_events=bass_line,
        figures="5/3 6 6/4 5/3 5/3"
    )
    print(f"  ✓ Realized figured bass into {len(satb_voices)} SATB voices")
    
    # ═══════════════════════════════════════════════════════════════
    # PART 3: Combine Everything into Final Score Structure
    # ═══════════════════════════════════════════════════════════════
    
    print("\n🎼 Assembling final score structure...")
    
    score_data = {
        'metadata': {
            'title': 'Hybrid Model Composition Example',
            'composer': 'Codempose Framework',
            'subtitle': 'Demonstrating Shorthand + Programmatic Approaches'
        },
        'parts': {
            'UpperVoices': {
                'Soprano': soprano_sequence,
                'Alto': alto_sequence
            },
            'LowerVoices': {
                'Tenor': satb_voices['Tenor'],
                'Bass': satb_voices['Bass']
            },
            'Accompaniment': {
                'Chords': harmony
            }
        }
    }
    
    print("  ✓ Score assembled successfully!")
    print(f"\n📊 Final score contains:")
    print(f"  - {len(score_data['parts'])} part groups")
    for part_name, voices in score_data['parts'].items():
        print(f"    • {part_name}: {list(voices.keys())}")
    
    return score_data


def display_score_summary(score_data):
    """Display a summary of the generated score."""
    print("\n" + "=" * 60)
    print("SCORE SUMMARY")
    print("=" * 60)
    
    metadata = score_data.get('metadata', {})
    print(f"\nTitle: {metadata.get('title', 'Untitled')}")
    print(f"Composer: {metadata.get('composer', 'Unknown')}")
    if 'subtitle' in metadata:
        print(f"Subtitle: {metadata['subtitle']}")
    
    print("\nParts:")
    for part_name, voices in score_data['parts'].items():
        print(f"\n  {part_name}:")
        for voice_name, events in voices.items():
            num_notes = sum(1 for e in events if e['type'] == 'note')
            num_rests = sum(1 for e in events if e['type'] == 'rest')
            num_chords = sum(1 for e in events if e['type'] == 'chord')
            total_ql = sum(e.get('ql', 0) for e in events)
            
            print(f"    - {voice_name}: {len(events)} events " +
                  f"({num_notes} notes, {num_rests} rests, {num_chords} chords, " +
                  f"{total_ql} ql total)")
    
    print("\n" + "=" * 60)


def main():
    """Main function to run the example composition."""
    print("\n" + "=" * 60)
    print("HYBRID MODEL COMPOSITION EXAMPLE")
    print("=" * 60)
    print("\nThis example demonstrates:")
    print("  1. Simple operations with composition_shorthand.py")
    print("  2. Complex transformations with advanced_transformations.py")
    print("  3. Combining both in a hybrid approach")
    print()
    
    # Build the score
    score_data = build_score_data()
    
    # Display summary
    display_score_summary(score_data)
    
    print("\n💡 Next steps:")
    print("  - Pass this score_data to engrave_with_abjad() to create a PDF")
    print("  - See ADVANCED_TRANSFORMATIONS_GUIDE.md for more examples")
    print("  - Experiment with different transformations and combinations")
    
    print("\n✅ Example completed successfully!\n")
    
    return score_data


if __name__ == '__main__':
    score = main()
