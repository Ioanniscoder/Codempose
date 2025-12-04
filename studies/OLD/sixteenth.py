"""Sixteenth study file - Automated Harmonization Showcase.

This study demonstrates the Harmonic Fitting Engine's ability to apply
a user-defined chord progression to a melody and automatically generate
a harmonically correct bass line.

The result is a two-stave score (melody + bass) that can be exported to
PDF, MusicXML, and MIDI for review and further editing.
"""

import _study_path  # Auto-path setup for study files

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

# Simple folk-like melody in C major
MELODY_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=108
    c4 d4 e4 f4 |
    g2 e2 |
    f4 e4 d4 c4 |
    c1
}
""".strip()

# User-defined harmonic progression
# This progression will be aligned with the melody's structural tones
PROGRESSION_STRING = "I - IV - V - I"
KEY = "C"

# Alternative progressions to try:
# PROGRESSION_STRING = "I - vi - IV - V - I"  # 50s progression
# PROGRESSION_STRING = "I - IV - I - V - I"    # Simple folk
# PROGRESSION_STRING = "vi - IV - I - V"       # Modern pop

TITLE = "Automated Harmonization Demo"
COMPOSER = "Harmonic Engine"


# ============================================================================
# STATION 2: REAL-TIME VALIDATION
# ============================================================================
# (Automatic via LilyPond parser)


# ============================================================================
# STATION 3: HARMONIZATION
# ============================================================================

def build_score_data():
    """
    Build score data with automated harmonization.
    
    This function demonstrates the complete Harmonic Intelligence System:
    1. Parse melody from LilyPond
    2. Analyze structural tones
    3. Apply chord progression
    4. Generate bass line
    5. Export two-part score
    
    Returns:
        dict: Score data with melody and generated bass parts
    """
    from lilypond_parser import parse_lilypond_to_data
    from music_data import data_to_part, part_to_data
    from harmonic_engine import harmonize_melody
    
    print("\n" + "="*70)
    print("SIXTEENTH STUDY: AUTOMATED HARMONIZATION")
    print("="*70)
    print(f"\nMelody: Simple folk-like melody in {KEY} major")
    print(f"Progression: {PROGRESSION_STRING}")
    print(f"Goal: Generate harmonically correct bass line\n")
    
    # Parse melody from LilyPond
    melody_data = parse_lilypond_to_data(MELODY_LILY, part_name='Melody')
    melody_part = data_to_part(melody_data['parts']['Melody'], melody_data.get('metadata'))
    
    # HARMONIC INTELLIGENCE: Harmonize melody with progression
    harmonized_score = harmonize_melody(
        melody_part=melody_part,
        progression_string=PROGRESSION_STRING,
        key=KEY,
        harmonic_rhythm="auto"  # Automatically distribute chords
    )
    
    # Show what we created
    print("Result:")
    print(f"  • Melody (original): {len(melody_part.flatten().notes)} notes")
    print(f"  • Bass (generated): {len(harmonized_score.parts[1].flatten().notes)} notes")
    print(f"  • Two-stave score ready for export\n")
    
    # Convert back to score_data format for export
    melody_events = part_to_data(harmonized_score.parts[0])
    bass_events = part_to_data(harmonized_score.parts[1])
    
    score_data = {
        'metadata': {
            'title': TITLE,
            'composer': COMPOSER,
            'time_signature': '4/4',
            'key_signature': {'tonic': 'c', 'mode': 'major'},
            'tempo': {'beat_duration': 4, 'bpm': 108}
        },
        'parts': {
            'Melody': melody_events,
            'Bass': bass_events  # Programmatically generated!
        }
    }
    
    print("="*70)
    print("HARMONIZATION COMPLETE")
    print("="*70)
    print("\nExporting two-stave score (melody + bass)...")
    print("Listen to the MIDI file to hear the harmonization!\n")
    
    return score_data


# ============================================================================
# STATION 4: EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
