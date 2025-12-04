"""Study file: Multi-voice polyphony demonstration

This module demonstrates independent voices on the same staff:
- Two melodic lines on one staff (stems up/down)
- Each voice from separate LilyPond snippets
- Polyphonic texture (counterpoint)

MULTI-VOICE STRUCTURE:
- Voice 1: Upper melodic line (stems up)
- Voice 2: Lower melodic line (stems down)
- Both rendered on single treble staff
"""

import _study_path  # Auto-path setup for study files

# ============================================================================
# VOICE SNIPPETS
# ============================================================================

# Voice 1: Upper melody (soprano-like)
VOICE_1_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=120
    c4 d e f |
    g2 e4 c |
    d4 e f d |
    e2. r4
}
""".strip()

VOICE_1_TINY = "c'4 d'4 e'4 f'4 g'2 e'4 c'4 d'4 e'4 f'4 d'4 e'2. r4"

# Voice 2: Lower melody (alto-like)
VOICE_2_LILY = r"""
\relative c' {
    e4 f g a |
    b2 c4 g |
    a4 b c a |
    b2. r4
}
""".strip()

VOICE_2_TINY = "e4 f4 g4 a4 b2 c'4 g4 a4 b4 c'4 a4 b2. r4"

# Voice 3: Upper harmony (tenor-like)
VOICE_3_LILY = r"""
\relative c' {
    g4 a b c |
    d2 c4 e |
    f4 g a f |
    g2. r4
}
""".strip()

VOICE_3_TINY = "g4 a4 b4 c'4 d'2 c'4 e'4 f'4 g'4 a'4 f'4 g'2. r4"

# Voice 4: Lower harmony (bass-like)
VOICE_4_LILY = r"""
\relative c {
    c4 f, g a |
    g2 c4 c |
    d4 g, f f |
    c2. r4
}
""".strip()

VOICE_4_TINY = "c4 F4 G4 A4 G2 c4 c4 d4 G4 F4 F4 c2. r4"

# Toggle for format dominance (set to True to use TinyNotation as primary)
PROMOTE_TO_TINYNOTATION = False  # LilyPond is dominant by default

# Alternative voice patterns for experimentation
VOICE_PATTERNS = {
    'walking_bass': r"\relative c { c4 d e f | g a b c }",
    'sustained': r"\relative c' { c1 | g1 }",
    'syncopated': r"\relative c' { r4 c4 r4 e4 | r4 g4 r4 c4 }",
}


# ============================================================================
# COMPOSITION FUNCTION
# ============================================================================

# ============================================================================
# SHORTHAND ALTERNATIVE (Optional - for simpler syntax)
# ============================================================================
# Instead of manual chaining, you can use declarative shorthand:
#
# VOICE_ASSIGNMENTS = {
#     'Melody': {
#         'Voice 1': 'V1',           # Single snippet (4 bars)
#         'Voice Chained': 'V1 + V2', # Chain two snippets (8 bars)
#     },
#     'Harmony': {
#         'Voice 3': 'V3',
#         'Voice 4': 'V4',
#     }
# }
#
# Then in build_score_data():
#   from composition_shorthand import build_score_from_assignments
#   
#   voice_data = {
#       'V1': parse_lilypond_to_data(VOICE_1_LILY)['parts']['Voice 1'],
#       'V2': parse_lilypond_to_data(VOICE_2_LILY)['parts']['Voice 2'],
#       'V3': parse_lilypond_to_data(VOICE_3_LILY)['parts']['Voice 3'],
#       'V4': parse_lilypond_to_data(VOICE_4_LILY)['parts']['Voice 4'],
#   }
#   
#   score_data = build_score_from_assignments(VOICE_ASSIGNMENTS, voice_data)
#
# See composition_shorthand.py and COMPOSITION_SHORTHAND_PROPOSAL.md for details.
# ============================================================================

def build_score_data():
    """
    Build a two-staff polyphonic score demonstrating PROGRAMMATIC CHAINING.
    
    STATION 3 - COMPOSITION CHAINING:
    - Snippets remain separate (Station 2)
    - Chaining happens HERE in build_score_data()
    - Event lists are concatenated: voice1_events + voice2_events
    
    This demonstrates:
    - Treble staff: Voice 1 (4 bars) vs CHAINED voice (Voice 1 + Voice 2 = 8 bars)
    - Bass staff: 2 voices (tenor + bass)
    - Each snippet parsed independently
    - CHAINING: Combining parsed event lists programmatically
    
    Returns:
        dict: Score data with chained voice demonstrating composition paradigm
    """
    from lilypond_parser import parse_lilypond_to_data
    
    # Parse each voice independently from separate snippets
    voice1_data = parse_lilypond_to_data(VOICE_1_LILY, part_name='Voice 1')
    voice2_data = parse_lilypond_to_data(VOICE_2_LILY, part_name='Voice 2')
    voice3_data = parse_lilypond_to_data(VOICE_3_LILY, part_name='Voice 3')
    voice4_data = parse_lilypond_to_data(VOICE_4_LILY, part_name='Voice 4')
    
    # Extract event lists
    voice1_events = voice1_data['parts']['Voice 1']
    voice2_events = voice2_data['parts']['Voice 2']
    voice3_events = voice3_data['parts']['Voice 3']
    voice4_events = voice4_data['parts']['Voice 4']
    
    # ========================================================================
    # PROGRAMMATIC CHAINING (Station 3 - Composition Logic)
    # ========================================================================
    # Chain Voice 1 + Voice 2 by concatenating their event lists
    # This is the core composition paradigm: building longer phrases from snippets
    voice_chained_events = voice1_events + voice2_events  # 4 bars + 4 bars = 8 bars
    
    # Get metadata from first voice
    metadata = voice1_data['metadata']
    
    # Build original snippets for .ly file comments (dual format)
    original_snippets = f"""TREBLE STAFF (Melody):

Voice 1 (Soprano - 4 bars):
LILYPOND FORMAT:
{VOICE_1_LILY}

TINYNOTATION FORMAT:
{VOICE_1_TINY}

Voice CHAINED (Alto - 8 bars):
PROGRAMMATICALLY CHAINED in build_score_data():
  voice_chained_events = voice1_events + voice2_events

Built from Voice 1 + Voice 2:
LILYPOND FORMAT (Voice 2):
{VOICE_2_LILY}

TINYNOTATION FORMAT (Voice 2):
{VOICE_2_TINY}

BASS STAFF (Harmony):

Voice 3 (Tenor):
LILYPOND FORMAT:
{VOICE_3_LILY}

TINYNOTATION FORMAT:
{VOICE_3_TINY}

Voice 4 (Bass):
LILYPOND FORMAT:
{VOICE_4_LILY}

TINYNOTATION FORMAT:
{VOICE_4_TINY}"""
    
    # Construct score_data with multi-voice structure
    score_data = {
        'metadata': {
            'title': 'Sixth Study - Programmatic Voice Chaining',
            'time_signature': metadata.get('time_signature', '4/4'),
            'key_signature': metadata.get('key_signature', {'tonic': 'c', 'mode': 'major'}),
            'tempo': metadata.get('tempo', {'beat_duration': 4, 'bpm': 120}),
            'composer': 'Codempose',
            'original_input': original_snippets,
        },
        'parts': {
            # Treble staff: Voice 1 (4 bars) vs Chained (8 bars)
            'Melody': {
                'Voice 1': voice1_events,           # 4 measures
                'Voice Chained': voice_chained_events,  # 8 measures (programmatically chained)
            },
            # Bass staff: Two-voice polyphony (tenor + bass)
            'Harmony': {
                'Voice 3': voice3_events,  # Tenor (stems up)
                'Voice 4': voice4_events,  # Bass (stems down)
            }
        }
    }
    
    return score_data


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
