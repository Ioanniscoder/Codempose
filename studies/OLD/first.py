"""
FIRST STUDY: First Blueprint Study
===================================

This study uses the Blueprint String Framework - the composer-first approach
to music composition in Codempose.

BLUEPRINT STRINGS: Musical structure using intuitive delimiters
- ; (semicolon)  = Section separator (like double barlines)
- & (ampersand)  = Staff separator (vertical stacking)  
- | (pipe)       = Snippet concatenator (horizontal "then")
- , (comma)      = Voice separator (multi-voice staves)
- 'r'            = Auto-rest placeholder

FEATURES DEMONSTRATED:
- Blueprint String Framework (VOICE_STAVE_DEF + VOICE_STAVE_DATA)
- All stave layout variants (single, multi, polyphonic)
- LilyPond parsing for musical snippets
- Automatic rest generation
- Section-based composition
"""

import _study_path  # Auto-path setup for study files

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Dict
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file

# Optional imports for alternative approaches (see bottom of file)
# from music_data import data_to_part, part_to_data
# from composition_shorthand import build_score_from_assignments
# from harmonic_engine import harmonize_melody


# ============================================================================
# METADATA
# ============================================================================

TITLE = "FIRST Study: First Blueprint Study"
COMPOSER = "Codempose Framework"


# ============================================================================
# STATION 1: LILYPOND SNIPPETS (Musical Building Blocks)
# ============================================================================

# Define your musical ideas as LilyPond snippets
# These are the "LEGO blocks" that Blueprint Strings will assemble

INTRO_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=120
    c4 d4 e4 f4 |
    g2 a2
}
""".strip()

THEME_A_LILY = r"""
\relative c'' {
    c4 e4 g4 e4 |
    f4 d4 e4 c4
}
""".strip()

THEME_B_LILY = r"""
\relative c'' {
    g4 a4 b4 c4 |
    d2 c2
}
""".strip()

HARMONY_LILY = r"""
\relative c' {
    <c e g>2 <d f a>2 |
    <e g b>2 <f a c>2
}
""".strip()

BASS_LILY = r"""
\relative c {
    \clef bass
    c2 g2 |
    f2 c2
}
""".strip()

# Add more snippets as needed for your composition


# ============================================================================
# STATION 2: BLUEPRINT STRINGS - STRUCTURE DEFINITION
# ============================================================================
#
# This is the heart of the Blueprint String Framework!
# Define your score structure using intuitive, musical delimiters.
#
# Choose one of the variants below (or create your own):

# ----------------------------------------------------------------------------
# VARIANT 1: Single Staff, Single Voice (Simplest)
# ----------------------------------------------------------------------------
# Use for: Solo pieces, single melodic lines
#
# VOICE_STAVE_DEF = "Melody"
#
# VOICE_STAVE_DATA = """
#     INTRO;
#     THEME_A;
#     THEME_B;
#     THEME_A
# """


# ----------------------------------------------------------------------------
# VARIANT 2: Two Staves, Single Voice Each (Piano-style) ⭐ ACTIVE EXAMPLE
# ----------------------------------------------------------------------------
# Use for: Piano pieces, melody + bass, treble + bass

VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    INTRO & r;
    THEME_A & BASS;
    THEME_B & HARMONY;
    THEME_A | INTRO & BASS
"""


# ----------------------------------------------------------------------------
# VARIANT 3: Multiple Staves (Three or More Parts)
# ----------------------------------------------------------------------------
# Use for: Three or more independent parts
#
# VOICE_STAVE_DEF = "Melody & Harmony & Bass"
#
# VOICE_STAVE_DATA = """
#     INTRO & r & r;
#     THEME_A & HARMONY & BASS;
#     THEME_B & HARMONY & r;
#     THEME_A & r & BASS
# """


# ----------------------------------------------------------------------------
# VARIANT 4: Single Staff, Multi-Voice (Polyphonic)
# ----------------------------------------------------------------------------
# Use for: Two voices on one staff (Bach inventions style)
#
# VOICE_STAVE_DEF = "(Voice1, Voice2)"
#
# VOICE_STAVE_DATA = """
#     THEME_A, r;
#     THEME_A, THEME_B;
#     r, THEME_A
# """


# ----------------------------------------------------------------------------
# VARIANT 5: Two Staves, Multi-Voice Each (SATB Hymn)
# ----------------------------------------------------------------------------
# Use for: SATB hymns, choral music
#
# You'll need to define SOPRANO_LILY, ALTO_LILY, TENOR_LILY, BASS_SATB_LILY
#
# VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
#
# VOICE_STAVE_DATA = """
#     SOPRANO, ALTO & TENOR, BASS_SATB;
#     SOPRANO, r & r, BASS_SATB;
#     SOPRANO, ALTO & TENOR, BASS_SATB
# """


# ----------------------------------------------------------------------------
# VARIANT 6: Mixed Layout (Some Polyphonic, Some Single)
# ----------------------------------------------------------------------------
# Use for: Complex arrangements
#
# VOICE_STAVE_DEF = "(Violin1, Violin2) & Viola & Cello"
#
# VOICE_STAVE_DATA = """
#     THEME_A, THEME_B & HARMONY & BASS;
#     THEME_A, r & HARMONY & BASS
# """


# ----------------------------------------------------------------------------
# VARIANT 7: Snippet Concatenation (Building Longer Phrases)
# ----------------------------------------------------------------------------
# Use | to chain snippets horizontally
#
# VOICE_STAVE_DEF = "Melody & Bass"
#
# VOICE_STAVE_DATA = """
#     INTRO | THEME_A | THEME_B & BASS;
#     THEME_A | INTRO & BASS | HARMONY
# """


# ============================================================================
# STATION 3: BUILD SCORE DATA (Blueprint String Framework)
# ============================================================================

def build_score_data() -> Dict:
    """
    Build score using Blueprint String Framework.
    
    This is APPROACH 1 (RECOMMENDED): The composer-first method.
    
    Workflow:
    1. Parse all LilyPond snippets
    2. Create snippets library
    3. Call build_score_from_blueprint() with your structure
    4. Return canonical score_data
    
    Returns:
        dict: Score data with metadata and parts
    """
    
    print("\n" + "="*70)
    print("FIRST STUDY: Blueprint String Framework")
    print("="*70)
    print(f"\nLayout: {VOICE_STAVE_DEF}")
    print()
    
    # ========================================================================
    # STEP 1: Parse all LilyPond snippets into event lists
    # ========================================================================
    
    print("[Parsing LilyPond snippets...]")
    
    # Define which snippets to parse (matches your VOICE_STAVE_DATA references)
    snippets_to_parse = {
        'INTRO': INTRO_LILY,
        'THEME_A': THEME_A_LILY,
        'THEME_B': THEME_B_LILY,
        'HARMONY': HARMONY_LILY,
        'BASS': BASS_LILY,
        # Add more snippet mappings as needed
    }
    
    # Parse each snippet and store in SNIPPETS library
    SNIPPETS = {}
    for name, lily_code in snippets_to_parse.items():
        parsed = parse_lilypond_to_data(lily_code, part_name=name)
        SNIPPETS[name] = parsed['parts'][name]
        print(f"  ✓ {name}: {len(SNIPPETS[name])} events")
    
    # ========================================================================
    # STEP 2: Build score using Blueprint Strings
    # ========================================================================
    
    print("\n[Building score from blueprint...]")
    
    # Metadata for the score
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        'tempo': {'beat_duration': 4, 'bpm': 120}
    }
    
    # This is the magic call - Blueprint String Framework assembles everything!
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,    # Layout structure (header)
        VOICE_STAVE_DATA,   # Content definition (data)
        SNIPPETS,           # Musical building blocks
        metadata            # Score metadata
    )
    
    print("\n" + "="*70)
    print("✅ SCORE ASSEMBLY COMPLETE")
    print("="*70)
    print("\nGenerated staves:")
    for staff_name in score_data['parts'].keys():
        print(f"  • {staff_name}")
    print()
    
    return score_data


# ============================================================================
# ALTERNATIVE APPROACHES (Commented Out)
# ============================================================================
#
# The Blueprint String Framework (above) is RECOMMENDED, but here are
# alternative composition methods for different use cases:

# ----------------------------------------------------------------------------
# APPROACH 2: Simple LilyPond Parsing (No Blueprint)
# ----------------------------------------------------------------------------
# Use when: You have a simple single-voice or basic multi-part score
#
# def build_score_data():
#     melody_data = parse_lilypond_to_data(THEME_A_LILY, part_name='Melody')
#     
#     return {
#         'metadata': {
#             'title': TITLE,
#             'composer': COMPOSER,
#         },
#         'parts': {
#             'Melody': melody_data['parts']['Melody']
#         }
#     }


# ----------------------------------------------------------------------------
# APPROACH 3: Dictionary-Based Shorthand
# ----------------------------------------------------------------------------
# Use when: You need inline transformations in expressions
#
# from composition_shorthand import build_score_from_assignments, transpose_events
#
# SHORTHAND_ASSIGNMENTS = {
#     'Melody': {
#         'Soprano': 'THEME_A + transpose(THEME_A, 5)',
#     },
#     'Bass': {
#         'Bass': 'HARMONY * 2'
#     }
# }
#
# def build_score_data():
#     # Parse snippets
#     voice_data = {}
#     for name, lily in [('THEME_A', THEME_A_LILY), ('HARMONY', HARMONY_LILY)]:
#         parsed = parse_lilypond_to_data(lily)
#         voice_data[name] = parsed['parts']['Part 1']
#     
#     # Build with shorthand
#     score_data = build_score_from_assignments(
#         SHORTHAND_ASSIGNMENTS, 
#         voice_data,
#         {'title': TITLE, 'composer': COMPOSER}
#     )
#     return score_data


# ----------------------------------------------------------------------------
# APPROACH 4: Harmonic Intelligence (Auto-Harmonization)
# ----------------------------------------------------------------------------
# Use when: You want to auto-generate bass from chord progressions
#
# from harmonic_engine import harmonize_melody
# from music_data import data_to_part, part_to_data
#
# PROGRESSION = "I - IV - V - I"
# KEY = "C"
#
# def build_score_data():
#     # Parse melody
#     melody_data = parse_lilypond_to_data(THEME_A_LILY, part_name='Melody')
#     melody_part = data_to_part(melody_data['parts']['Melody'])
#     
#     # Auto-harmonize
#     harmonized_score = harmonize_melody(melody_part, PROGRESSION, KEY)
#     
#     # Convert back
#     melody_events = part_to_data(harmonized_score.parts[0])
#     bass_events = part_to_data(harmonized_score.parts[1])
#     
#     return {
#         'metadata': {'title': TITLE, 'composer': COMPOSER},
#         'parts': {
#             'Melody': melody_events,
#             'Bass': bass_events  # Auto-generated!
#         }
#     }


# ----------------------------------------------------------------------------
# APPROACH 5: Programmatic (Maximum Control)
# ----------------------------------------------------------------------------
# Use when: You need complex custom transformations
#
# from transformations import transpose_part, invert_part, retrograde_part
# from music_data import data_to_part, part_to_data
#
# def build_score_data():
#     # Parse melody
#     melody_data = parse_lilypond_to_data(THEME_A_LILY)
#     melody_part = data_to_part(melody_data['parts']['Part 1'])
#     
#     # Apply transformations
#     transposed = transpose_part(melody_part, 'P5')
#     inverted = invert_part(melody_part, 'C4')
#     
#     return {
#         'metadata': {'title': TITLE, 'composer': COMPOSER},
#         'parts': {
#             'Original': part_to_data(melody_part),
#             'Transposed': part_to_data(transposed),
#             'Inverted': part_to_data(inverted)
#         }
#     }


# ============================================================================
# STATION 4: EXECUTION
# ============================================================================

if __name__ == '__main__':
    run_pipeline_from_file(__file__)


# ============================================================================
# QUICK REFERENCE: Blueprint String Delimiters
# ============================================================================
#
# ; (SEMICOLON) - Section separator
#   Example: "INTRO; THEME_A; THEME_B"
#   Like: Double barlines in a score
#
# & (AMPERSAND) - Staff separator  
#   Example: "MELODY & BASS"
#   Like: Grand staff (multiple staves stacked vertically)
#
# | (PIPE) - Snippet concatenator
#   Example: "INTRO | THEME_A"
#   Like: Measures flowing left-to-right
#
# , (COMMA) - Voice separator
#   Example: "(Soprano, Alto)"
#   Like: Stem-up and stem-down on same staff
#
# 'r' - Auto-rest
#   Example: "THEME_A & r"
#   Like: Automatically generated rests
#
