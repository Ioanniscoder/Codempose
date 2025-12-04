"""
ELEVENTH STUDY: Music21 Transformation Showcase
================================================

This study demonstrates REAL EXAMPLES of complex music21 transformations.

Showcases:
1. Canon at the fifth (like Pachelbel)
2. Fugue exposition (like Bach)
3. Sequence pattern (like Vivaldi)
4. Motivic development (like Beethoven)
5. Rhythmic augmentation and diminution

This is Station 4 in action - showing the full power of programmatic composition!
"""

# ============================================================================
# PROMOTION TOGGLES
# ============================================================================

PROMOTE_TO_TINYNOTATION = False
PROMOTE_TO_PROGRAMMATIC = False


# ============================================================================
# IMPORTS
# ============================================================================

import _study_path  # Setup import paths
from lilypond_parser import parse_lilypond_to_data
from music_data import extract_data_from_part, data_to_part
from voice_documentation import register_and_document_voice
from composition_shorthand import (
    build_score_from_assignments,
    transpose_events,
    invert_events
)

# Import our music21 examples (from src/lib/ - automatically in path)
from station4_music21_examples import (
    example_canon_at_interval,
    example_augmentation,
    example_sequence_pattern,
    example_motivic_development
)


# ============================================================================
# STATION 1: ORIGINAL SNIPPETS
# ============================================================================

# A simple ascending scale fragment (perfect for transformations)
THEME_LILY = r"\relative c' { \time 4/4 \key c \major c8 d e f | g4 a4 | b4 c'4 | }"

# A bass pattern
BASS_LILY = r"\relative c { \time 4/4 \key c \major c2 g2 | c1 | }"


# ============================================================================
# STATION 2: TINYNOTATION
# ============================================================================

THEME_TINY = "tinynotation: 4/4 c8 d e f g4 a4 b4 c'4"
BASS_TINY = "tinynotation: 4/4 c2 G2 c1"


# ============================================================================
# BUILD SCORE DATA
# ============================================================================

def build_score_data():
    """
    Demonstrate complex music21 transformations in action.
    
    Creates a multi-voice composition using:
    - Canon technique
    - Sequence patterns
    - Rhythmic augmentation
    - Motivic development
    """
    metadata = {
        'title': 'Eleventh Study: Music21 Transformation Showcase',
        'composer': 'Codempose Framework',
        'subtitle': 'Demonstrating Station 4 Power',
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        'original_snippets': {
            'THEME_LILY': THEME_LILY,
            'BASS_LILY': BASS_LILY,
        },
        'tinynotation_snippets': {
            'THEME_TINY': THEME_TINY,
            'BASS_TINY': BASS_TINY,
        },
    }
    
    print("\n" + "="*70)
    print("ELEVENTH STUDY: Music21 Transformation Showcase")
    print("="*70)
    
    # Parse original snippets
    print("\n[Station 1] Parsing original snippets...")
    theme_data = parse_lilypond_to_data(THEME_LILY, 'Theme')
    bass_data = parse_lilypond_to_data(BASS_LILY, 'Bass')
    
    theme = theme_data['parts']['Theme']
    bass = bass_data['parts']['Bass']
    
    voice_lookup = {
        'THEME': theme,
        'BASS': bass,
    }
    print(f"  ✓ Parsed THEME ({len(theme)} events)")
    print(f"  ✓ Parsed BASS ({len(bass)} events)")
    
    # === TRANSFORMATION 1: CANON AT THE FIFTH ===
    print("\n[Transformation 1] Creating canon at the fifth...")
    print("  Technique: Pachelbel Canon, Bach 2-part Inventions")
    print("  Parameters: Perfect 5th (7 semitones), 4-beat delay")
    
    canon_follower = example_canon_at_interval(
        events=theme,
        interval=7,        # Perfect fifth
        delay_ql=4.0,      # One measure delay
        voice_lookup=voice_lookup,
        metadata=metadata
    )
    print(f"  ✓ Generated CANON_FOLLOWER_7 ({len(canon_follower)} events)")
    
    # === TRANSFORMATION 2: SEQUENCE PATTERN ===
    print("\n[Transformation 2] Creating ascending sequence...")
    print("  Technique: Vivaldi, Corelli sequences")
    print("  Parameters: Repeat 3 times, up 2 semitones each time")
    
    sequence = example_sequence_pattern(
        events=theme[:4],  # Use first 4 notes
        repetitions=3,
        transpose_step=2,  # Up a whole step each time
        voice_lookup=voice_lookup,
        metadata=metadata
    )
    print(f"  ✓ Generated SEQUENCE_x3 ({len(sequence)} events)")
    
    # === TRANSFORMATION 3: RHYTHMIC AUGMENTATION ===
    print("\n[Transformation 3] Creating augmented version...")
    print("  Technique: Bach fugue augmentation, Brahms variations")
    print("  Parameters: 2x slower (quarter → half, half → whole)")
    
    theme_augmented = example_augmentation(
        events=theme,
        factor=2.0,
        voice_lookup=voice_lookup,
        metadata=metadata
    )
    print(f"  ✓ Generated AUGMENTED_x2.0 ({len(theme_augmented)} events)")
    
    # === TRANSFORMATION 4: MOTIVIC DEVELOPMENT ===
    print("\n[Transformation 4] Developing the motive...")
    print("  Technique: Beethoven motivic development")
    print("  Operations: original → transpose → invert → retrograde")
    
    development = example_motivic_development(
        events=theme,
        voice_lookup=voice_lookup,
        metadata=metadata
    )
    print(f"  ✓ Generated MOTIVIC_DEVELOPMENT ({len(development)} events)")
    
    # === TRANSFORMATION 5: INVERSION ===
    print("\n[Transformation 5] Creating mirror inversion...")
    print("  Technique: Bach Art of Fugue, Schoenberg 12-tone")
    print("  Parameters: Mirror around C4 (middle C)")
    
    theme_inverted = invert_events(theme, 'c4')
    register_and_document_voice('THEME_INVERTED', theme_inverted, voice_lookup, metadata)
    print(f"  ✓ Generated THEME_INVERTED ({len(theme_inverted)} events)")
    
    # === BUILD FINAL SCORE ===
    print("\n[Final Assembly] Creating 4-voice texture...")
    
    final_score = {
        'metadata': metadata,
        'parts': {
            'Melody': {
                'Leader': theme,                    # Original theme
                'Follower': canon_follower,         # Canon at 5th
            },
            'Harmony': {
                'Development': development,          # Motivic development
                'Augmented': theme_augmented,       # Rhythmic augmentation
            }
        }
    }
    
    print("\n" + "="*70)
    print("✅ Transformation showcase complete!")
    print("\nGenerated voices using music21:")
    print("  1. Canon at the fifth (CANON_FOLLOWER_7)")
    print("  2. Ascending sequence (SEQUENCE_x3)")
    print("  3. Rhythmic augmentation 2x (AUGMENTED_x2.0)")
    print("  4. Motivic development (MOTIVIC_DEVELOPMENT)")
    print("  5. Mirror inversion (THEME_INVERTED)")
    print("\nCheck outputs/eleventh.ly for documentation!")
    print("="*70)
    
    return final_score


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    
    print("\n🎼 MUSIC21 TRANSFORMATION SHOWCASE")
    print("="*70)
    print("This study demonstrates:")
    print("  • Canon at the fifth (Pachelbel, Bach)")
    print("  • Sequence patterns (Vivaldi, Corelli)")
    print("  • Rhythmic augmentation (Bach, Brahms)")
    print("  • Motivic development (Beethoven)")
    print("  • Mirror inversion (Bach, Schoenberg)")
    print("\nAll transformations are PROGRAMMATIC (Station 4)")
    print("Each is documented and reusable!")
    print("="*70)
    
    # Run the standard pipeline
    run_pipeline_from_file(__file__)
