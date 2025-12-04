"""Fifteenth study file - Structural Tone Analysis Demonstration.

This study demonstrates the Harmonic Intelligence System's ability to
identify structural vs. ornamental notes in a melody based on principles
from "Tonal Harmony" textbook.

Structural tones are melodic notes that:
- Fall on strong beats (beat 1, or beat 3 in 4/4)
- Have long durations (quarter note or longer)

Ornamental tones embellish the structural framework with passing tones,
neighbor tones, and other decorative elements.
"""

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

# Simple melody with mix of structural and ornamental tones
MELODY_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=120
    c4 d8 e8 f4 g4 |
    a2 g4 f4 |
    e4 d8 c8 d4 c4 |
    c1
}
""".strip()

# Alternative: More ornamental melody for testing
ORNAMENTAL_MELODY_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    c8 d8 e8 f8 g4 e4 |
    f8 g8 a8 g8 f4 d4 |
    e8 f8 g8 a8 g4 e4 |
    c1
}
""".strip()

TITLE = "Structural Tone Analysis Demo"
COMPOSER = "Harmonic Intelligence System"

# Toggle for different test melodies
USE_ORNAMENTAL_MELODY = False  # Set to True to test with more complex melody


# ============================================================================
# STATION 2: REAL-TIME VALIDATION
# ============================================================================
# (Automatic via LilyPond parser)


# ============================================================================
# STATION 3: HARMONIC ANALYSIS
# ============================================================================

def build_score_data():
    """
    Build score data with structural tone analysis.
    
    This function demonstrates the Harmonic Intelligence System's ability
    to identify and tag structural vs. ornamental tones in a melody.
    
    Returns:
        dict: Score data for PDF/MusicXML export
    """
    from lilypond_parser import parse_lilypond_to_data
    from music_data import data_to_part
    from harmonic_analysis import find_structural_tones, print_structural_analysis
    
    print("\n" + "="*70)
    print("FIFTEENTH STUDY: STRUCTURAL TONE ANALYSIS")
    print("="*70)
    print(f"\nMelody: {'Ornamental' if USE_ORNAMENTAL_MELODY else 'Simple'} melody in C major")
    print("Analyzing structural vs. ornamental tones...")
    print()
    
    # Select melody based on toggle
    melody_lily = ORNAMENTAL_MELODY_LILY if USE_ORNAMENTAL_MELODY else MELODY_LILY
    
    # Parse melody from LilyPond
    melody_data = parse_lilypond_to_data(melody_lily, part_name='Melody')
    
    # Convert to music21 Part for analysis
    melody_part = data_to_part(melody_data['parts']['Melody'], melody_data.get('metadata'))
    
    # HARMONIC INTELLIGENCE: Analyze structural tones
    analyzed_part = find_structural_tones(melody_part)
    
    # Print detailed analysis to console
    print_structural_analysis(analyzed_part, verbose=True)
    
    # Show what we can do with the analysis results
    from harmonic_analysis import get_structural_notes
    structural = get_structural_notes(analyzed_part)
    
    print("Structural tone sequence:")
    print("  " + " - ".join([n.nameWithOctave for n in structural]))
    print()
    print("This structural framework defines the melodic skeleton that")
    print("harmonic progressions can be aligned with (see sixteenth.py).")
    print()
    
    # Return score_data for standard PDF/MusicXML export
    score_data = {
        'metadata': {
            'title': TITLE,
            'composer': COMPOSER,
            'time_signature': '4/4',
            'key_signature': {'tonic': 'c', 'mode': 'major'},
            'tempo': {'beat_duration': 4, 'bpm': 120}
        },
        'parts': {
            'Melody': melody_data['parts']['Melody']
        }
    }
    
    return score_data


# ============================================================================
# STATION 4: EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
