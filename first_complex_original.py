"""Study file: Two-stave composition with melody and harmony snippets

This module demonstrates the Codempose workflow with:
- Cleanly organized melody and harmony snippets (LilyPond and TinyNotation)
- Two-stave output (treble melody + bass harmony)
- Music21 transformations: identity, chordify, inversion, etc.

PROMOTION SYSTEM:
- Set PROMOTE_TO_TINYNOTATION = True to auto-generate SOURCE_MELODY_TINY
- Both formats are preserved for visual inspection
- SOURCE_MELODY_TINY takes priority when present
"""

# ============================================================================
# PROMOTION TOGGLE
# ============================================================================

# Set to True to generate TinyNotation format from LilyPond
# Both formats will be preserved in the file for comparison
PROMOTE_TO_TINYNOTATION = False


# ============================================================================
# MELODY SNIPPETS
# ============================================================================

# Primary melody in LilyPond format (reference - visual correlation with TinyNotation)
SOURCE_MELODY_LILY = r"""
\relative e' {
    \time 6/4
    \key c \major
    \tempo 4=90
    e2 bmol4 c2 r4 |
    e2 f#4 e2 r4 |
    b2. f'2. |
    e2. c2. |
    e2 b2 c2
}
""".strip()

# TinyNotation equivalent (for visual comparison with LilyPond)
# PROMOTE_TO_TINYNOTATION toggle controls which format is dominant (gets processed)
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 e2 b-4 c'2 r4 e'2 f#'4 e'2 r4 b'2. f''2. e''2. c''2. e''2 b''2 c'''2"


# Alternative melody snippets for experimentation
MELODY_SNIPPETS = {
    'simple': r"\relative c' { c4 d e f | g a b c }",
    'ascending': r"\relative g' { e4 fs g a | b c d e }",
    'descending': r"\relative c'' { c4 b a g | f e d c }",
}


# ============================================================================
# HARMONY SNIPPETS
# ============================================================================

# Harmony patterns to accompany the melody (LilyPond format)
HARMONY_SNIPPETS = {
    'simple_chords': r"\relative c { <e g b>2 <f a c'>2 <g b d'>2 }",
    'bass_line': r"\relative c { e2 b2 c2 f2 g2 c2 }",
    'arpeggios': r"\relative c { e8 g b g e g b g }",
    'sustained': r"\relative c { e1 b1 c1 }",
}

# Default harmony to use
DEFAULT_HARMONY = HARMONY_SNIPPETS['bass_line']


# ============================================================================
# COMPOSITION FUNCTIONS
# ============================================================================

def build_score_data():
    """
    Build a two-part score with melody and harmony.
    
    This function demonstrates music21 transformations:
    - Identity/copy: Create independent parts from the same source
    - Chordify: Combine melody and harmony into chords
    - Transpose: Shift pitches by interval
    - Inversion: Mirror melodic contours
    
    Returns:
        dict: Score data with metadata and parts
    """
    from lilypond_parser import parse_lilypond_to_data
    from music_data import extract_data_from_part, data_to_part
    import music21
    
    # Parse the primary melody
    melody_data = parse_lilypond_to_data(SOURCE_MELODY_LILY, part_name='Melody')
    melody_events = melody_data['parts']['Melody']
    melody_metadata = melody_data['metadata']
    
    # Parse the harmony
    harmony_data = parse_lilypond_to_data(DEFAULT_HARMONY, part_name='Harmony')
    harmony_events = harmony_data['parts']['Harmony']
    
    # Convert to music21 Parts for transformations
    melody_part = data_to_part(melody_events, metadata=melody_metadata)
    harmony_part = data_to_part(harmony_events, metadata=melody_metadata)
    
    # ========================================================================
    # MUSIC21 TRANSFORMATIONS
    # ========================================================================
    
    # 1. Identity/Copy - preserve original melody on top staff
    melody_final = melody_part.flatten().notesAndRests.stream()
    
    # 2. Transpose harmony down an octave for bass range
    harmony_final = harmony_part.transpose(-12)
    
    # Optional: Demonstrate chordify (commented out by default)
    # combined = music21.stream.Score([melody_part, harmony_part])
    # chordified = combined.chordify()
    
    # Optional: Demonstrate inversion (commented out by default)
    # inverted_melody = melody_part.transpose(0)  # Copy first
    # for note in inverted_melody.flatten().notes:
    #     interval = music21.interval.Interval(note, music21.pitch.Pitch('C4'))
    #     note.transpose(-2 * interval.semitones, inPlace=True)
    
    # ========================================================================
    # BUILD FINAL SCORE DATA
    # ========================================================================
    
    # Extract events from transformed parts
    melody_final_events = extract_data_from_part(melody_final)
    harmony_final_events = extract_data_from_part(harmony_final)
    
    # Construct score_data dict
    original_snippets = f"""LILYPOND FORMAT:
{SOURCE_MELODY_LILY}

TINYNOTATION FORMAT:
{SOURCE_MELODY_TINY}"""
    
    score_data = {
        'metadata': {
            'title': 'First Study - Two-Part Composition',
            'time_signature': melody_metadata.get('time_signature', '6/4'),
            'key_signature': melody_metadata.get('key_signature', {'tonic': 'c', 'mode': 'major'}),
            'tempo': melody_metadata.get('tempo', {'beat_duration': 4, 'bpm': 90}),
            'composer': 'Codempose',
            'original_input': original_snippets,
        },
        'parts': {
            'Melody': melody_final_events,
            'Harmony': harmony_final_events,
        }
    }
    
    return score_data


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)

