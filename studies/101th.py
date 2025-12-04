"""
101TH STUDY: Auto-Parse Test
=============================

This study uses the Blueprint String Framework - the composer-first approach
to music composition in Codempose.

BLUEPRINT STRINGS: Musical structure using intuitive delimiters
- ; (semicolon)  = Section separator (like double barlines)
- & (ampersand)  = Staff separator (vertical stacking)  
- | (pipe)       = Snippet concatenator (horizontal "then")
- , (comma)      = Voice separator (multi-voice staves)
- 'r'            = Auto-rest placeholder

TRANSFORMATIONS: Musical transformations on-the-fly in Blueprint Strings

**HYBRID SUFFIX MODEL** (Backward compatible + explicit multi-part):

1. SINGLE-PART TRANSFORMATIONS (No suffix needed):
   
   transpose_part(THEME, 'P5')      ← Works! Auto-assigns .id = 'melody'
   invert_part(THEME, 'C4')          ← Backward compatible
   retrograde_part(BASS)             ← No changes needed
   augment_part(THEME, 2.0)          ← Simple and clear
   
   Available: transpose_part, invert_part, retrograde_part, augment_part,
              diminish_part, chordify_part, analyze_structural_tones

2. MULTI-PART TRANSFORMATIONS (Suffix REQUIRED):
   
   harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody     ← Part 1 (melody)
   harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony    ← Part 2 (bass)
   
   • Transformation runs ONCE (on first call)
   • All parts cached with semantic IDs (:melody, :harmony)
   • Second call is instant lookup (no re-execution)
   • Without suffix → ERROR with helpful message
   
   Example in Blueprint:
   
   VOICE_STAVE_DEF = "Melody & Bass"
   
   VOICE_STAVE_DATA = """
       MELODY & r;
       harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody
       &
       harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony
   """

3. REPEAT OPERATOR:
   
   THEME * 3        ← Repeats THEME three times
   MELODY * 2       ← Concatenates MELODY twice
   
   Example:
   VOICE_STAVE_DATA = """
       INTRO & BASS;
       THEME * 3 & BASS * 2
   """

FEATURES DEMONSTRATED:
- Blueprint String Framework (VOICE_STAVE_DEF + VOICE_STAVE_DATA)
- On-the-fly transformations with hybrid suffix model
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
from src.score_builder import build_score_from_blueprint_auto
from src.project_template import run_pipeline_from_file

# Optional imports for alternative approaches (see bottom of file)
# from music_data import data_to_part, part_to_data
# from composition_shorthand import build_score_from_assignments
# from harmonic_engine import harmonize_melody


# ============================================================================
# ADVANCED: User Library Imports (from src/lib/)
# ============================================================================
# 
# The src/lib/ directory contains advanced music transformation libraries
# that you can import and use in your studies. Uncomment the imports you need:
#
# MUSIC21 TRANSFORMATION EXAMPLES:
# from station4_music21_examples import (
#     example_canon_at_interval,      # Create canons (Bach/Pachelbel style)
#     example_augmentation,            # Lengthen/shorten note durations
#     example_sequence_pattern,        # Repeat patterns at different pitches
#     example_motivic_development      # Transform and develop motifs
# )
#
# MUSIC21 API HELPERS:
# from MUSIC21_API_TEMPLATES import (
#     example_scale,                   # Generate scales
#     example_chord_progression,       # Build chord progressions
#     analyze_intervals,               # Analyze melodic intervals
#     get_pitch_class_distribution     # Analyze pitch usage
# )
#
# TONAL HARMONY TEMPLATES:
# from TONAL_HARMONY_TEMPLATES import (
#     PROGRESSION_I_IV_V_I,            # Classic cadence
#     PROGRESSION_ii_V_I,              # Jazz progression
#     harmonize_melody,                # Auto-harmonization
#     add_bass_line                    # Generate walking bass
# )
#
# See Variant 12 below and studies/eleventh_example.py for usage examples!


# ============================================================================
# METADATA
# ============================================================================

TITLE = "101TH Study: Auto-Parse Test"
COMPOSER = "Codempose Framework"
OPUS_NUMBER = "101TH"


# ============================================================================
# STATION 1: MUSICAL IDEAS (LilyPond Snippets)
# ============================================================================
# 
# Define your musical building blocks using LilyPond notation.
# These snippets are the "LEGO blocks" that Blueprint Strings will assemble.
#
# NAMING: Use descriptive uppercase names (INTRO, THEME_A, BASS_FIGURE, etc.)
# No need for _LILY suffix - the framework auto-detects them from VOICE_STAVE_DATA!
#
# BEST PRACTICES:
# - Include \key, \time, \tempo in first snippet
# - Add dynamics, articulations for musical expression
# - Keep snippets focused and reusable
# - Use \clef bass for bass parts

INTRO = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=120
    c4 d4 e4 f4 |
    g2 a2
}
""".strip()

THEME_A = r"""
\relative c'' {
    c4 e4 g4 e4 |
    f4 d4 e4 c4
}
""".strip()

THEME_B = r"""
\relative c'' {
    g4 a4 b4 c4 |
    d2 c2
}
""".strip()

HARMONY = r"""
\relative c' {
    <c e g>2 <d f a>2 |
    <e g b>2 <f a c>2
}
""".strip()

BASS = r"""
\relative c {
    \clef bass
    c2 g2 |
    f2 c2
}
""".strip()

# ----------------------------------------------------------------------------
# CREATIVE EXAMPLES (from second.py study)
# ----------------------------------------------------------------------------
# These are real musical compositions - feel free to use them as starting points!

# Short, rhythmic motif - great for transformations
# SOURCE_THEME = r"""
# \relative c' {
#     \time 4/4
#     \key c \major
#     e4 b4 e'4 b4
# }
# """.strip()

# Expressive melodic phrase with interesting intervals and rhythm
# SOURCE_MELODY = r"""
# \relative e {
#     \time 6/4
#     \key c \major
#     \tempo 4=90
#     e2 bes4 c2 r4 |
#     e2 fis4 e2 r4 |
#     b2. f'2. |
#     e2. c2. |
#     e2 b2 c2
# }
# """.strip()

# Add more snippets as needed for your composition


# ============================================================================
# STATION 2: INTERNAL SNIPPET LIBRARY (Automatic - No Code Needed!)
# ============================================================================
#
# Station 2 is the framework's internal library that holds parsed snippets.
# You DON'T define it - it's populated automatically!
#
# The framework analyzes VOICE_STAVE_DATA (Station 3) to detect which
# snippets you reference (INTRO, THEME_A, etc.), then:
# 1. Finds those variables in Station 1
# 2. Parses the LilyPond code into events
# 3. Stores them in the internal SNIPPETS dictionary
#
# Example of what gets stored automatically:
#   SNIPPETS['INTRO'] = [event1, event2, ...]       # From INTRO snippet
#   SNIPPETS['THEME_A'] = [...]                      # From THEME_A snippet
#   SNIPPETS['transpose_part(THEME_A)'] = [...]     # From transformation
#
# You'll see this in the console output:
#   ✓ INTRO: 12 events
#   ✓ THEME_A: 8 events
#   ✓ BASS: 10 events


# ============================================================================
# STATION 3: BLUEPRINT STRINGS - SCORE STRUCTURE
# ============================================================================
#
# This is where you define HOW your snippets are arranged!
# Use intuitive delimiters to build your score structure.
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


# ----------------------------------------------------------------------------
# VARIANT 8: Transformations (Single-Part - No Suffix Needed) ⭐ NEW!
# ----------------------------------------------------------------------------
# Use for: Musical variations using transformations
#
# VOICE_STAVE_DEF = "Melody & Bass"
#
# VOICE_STAVE_DATA = """
#     THEME_A & BASS;
#     transpose_part(THEME_A, 'P5') & BASS;
#     invert_part(THEME_A, 'C4') & BASS;
#     retrograde_part(THEME_A) & BASS;
#     augment_part(THEME_A, 2.0) & BASS
# """


# ----------------------------------------------------------------------------
# VARIANT 9: Harmonization (Multi-Part - Suffix Required) ⭐ NEW!
# ----------------------------------------------------------------------------
# Use for: Auto-generated bass lines from chord progressions
#
# VOICE_STAVE_DEF = "Melody & Bass"
#
# VOICE_STAVE_DATA = """
#     INTRO & r;
#     harmonize_part(INTRO, 'I-IV-V-I', 'C'):melody
#     &
#     harmonize_part(INTRO, 'I-IV-V-I', 'C'):harmony;
#     
#     THEME_A & r;
#     harmonize_part(THEME_A, 'I-vi-IV-V', 'C'):melody
#     &
#     harmonize_part(THEME_A, 'I-vi-IV-V', 'C'):harmony
# """
#
# Note: harmonize_part() runs ONCE per unique call, caches both :melody
#       and :harmony parts, second reference is instant lookup


# ----------------------------------------------------------------------------
# VARIANT 10: Repeat Operator (Pattern Repetition) ⭐ NEW!
# ----------------------------------------------------------------------------
# Use for: Repeating musical patterns
#
# VOICE_STAVE_DEF = "Melody & Bass"
#
# VOICE_STAVE_DATA = """
#     THEME_A * 3 & BASS;
#     INTRO * 2 & BASS * 2;
#     transpose_part(THEME_A, 'P5') * 2 & BASS
# """


# ----------------------------------------------------------------------------
# VARIANT 11: Creative Composition Example ⭐ REAL MUSIC!
# ----------------------------------------------------------------------------
# Use for: Building expressive compositions with transformations
#
# Uses SOURCE_THEME_LILY and SOURCE_MELODY_LILY from Station 1
#
# VOICE_STAVE_DEF = "Melody & Bass"
#
# VOICE_STAVE_DATA = """
#     SOURCE_MELODY & r;
#     SOURCE_THEME & r;
#     transpose_part(SOURCE_THEME, 'P5') & r;
#     invert_part(SOURCE_THEME, 'G4') & r;
#     harmonize_part(SOURCE_MELODY, 'I-IV-V-I', 'C'):melody
#     &
#     harmonize_part(SOURCE_MELODY, 'I-IV-V-I', 'C'):harmony
# """
#
# This demonstrates:
# • Expressive original melody (6/4 time with interesting intervals)
# • Short rhythmic motif (4/4) perfect for transformations
# • Transposition and inversion creating variations
# • Auto-harmonization generating bass line


# VARIANT 12: Music21 Library Examples ⭐ ADVANCED!
# ----------------------------------------------------------------------------
# Use for: Advanced transformations using pre-built library functions
#
# First, uncomment the library imports at the top of this file:
# from station4_music21_examples import example_canon_at_interval
#
# Then use in build_score_data():
#
# def build_score_data() -> Dict:
#     parsed_snippets = parse_all_snippets()
#     THEME = parsed_snippets['THEME']
#     
#     # Create canon at the fifth (Pachelbel/Bach style)
#     canon_follower = example_canon_at_interval(
#         THEME,
#         interval_semitones=7,  # Perfect 5th
#         delay_quarters=4       # 4 beats delay
#     )
#     
#     return {
#         'parts': {
#             'Melody': [THEME],
#             'Canon': [canon_follower]
#         },
#         'metadata': METADATA
#     }
#
# See studies/eleventh_example.py for complete working examples!
# Available functions: example_canon_at_interval, example_augmentation,
#                      example_sequence_pattern, example_motivic_development


# ============================================================================
# STATION 3: BUILD SCORE DATA (Blueprint String Framework)
# ============================================================================

def build_score_data() -> Dict:
    """
    Build score using Blueprint String Framework with AUTO-PARSING.
    
    This is APPROACH 1 (RECOMMENDED): The clean composer interface.
    
    NEW: No need for snippets_to_parse dictionary!
    The framework automatically detects which snippets are referenced
    in VOICE_STAVE_DATA and parses them from your Station 1 definitions.
    
    Workflow:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. Analyze VOICE_STAVE_DATA → extract snippet names (THEME_A, BASS, etc.)
    2. Look up snippet variables in this file's namespace
    3. Auto-parse LilyPond code → populate Station 2 library
    4. Build score from blueprint → return score_data
    
    Returns:
        dict: Complete score_data {'metadata': {}, 'parts': {}}
    """
    
    print("\n" + "="*70)
    print("101TH STUDY: Blueprint String Framework")
    print("="*70)
    print(f"\nLayout: {VOICE_STAVE_DEF}")
    
    # ========================================================================
    # Define Score Metadata
    # ========================================================================
    
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER,
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        'tempo': {'beat_duration': 4, 'bpm': 120},
        # original_snippets will be auto-populated by the framework
    }
    
    # ========================================================================
    # Call Auto-Parsing Blueprint Builder
    # ========================================================================
    # This automatically:
    # - Extracts snippet names from VOICE_STAVE_DATA
    # - Finds snippet variables (INTRO_LILY, THEME_A_LILY, etc.)
    # - Parses LilyPond → Station 2 library
    # - Assembles score from blueprint
    
    score_data = build_score_from_blueprint_auto(
        VOICE_STAVE_DEF,    # Layout: "Melody & Bass"
        VOICE_STAVE_DATA,   # Structure: sections with snippets
        metadata,           # Score metadata
        globals()           # Pass this file's namespace to find snippets
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
# APPROACH 4: Harmonic Intelligence (Auto-Harmonization) ⭐ RECOMMENDED
# ----------------------------------------------------------------------------
# Use when: You want to auto-generate bass from chord progressions
#
# This demonstrates the HYBRID SUFFIX MODEL for multi-part transformations.
#
# VOICE_STAVE_DEF = "Melody & Bass"
#
# VOICE_STAVE_DATA = """
#     THEME_A & r;
#     harmonize_part(THEME_A, 'I-IV-V-I', 'C'):melody
#     &
#     harmonize_part(THEME_A, 'I-IV-V-I', 'C'):harmony
# """
#
# def build_score_data():
#     # Parse melody
#     melody_data = parse_lilypond_to_data(THEME_A_LILY, part_name='THEME_A')
#     
#     SNIPPETS = {
#         'THEME_A': melody_data['parts']['THEME_A']
#     }
#     
#     metadata = {
#         'title': TITLE,
#         'composer': COMPOSER,
#         'time_signature': '4/4',
#         'key_signature': {'tonic': 'c', 'mode': 'major'},
#         'tempo': {'beat_duration': 4, 'bpm': 120}
#     }
#     
#     # Blueprint framework handles harmonize_part() automatically!
#     # The transformation runs ONCE, caches :melody and :harmony parts
#     score_data = build_score_from_blueprint(
#         VOICE_STAVE_DEF,
#         VOICE_STAVE_DATA,
#         SNIPPETS,
#         metadata
#     )
#     
#     return score_data


# ----------------------------------------------------------------------------
# APPROACH 5: Transformations in Blueprint (Feature Variations) ⭐ RECOMMENDED
# ----------------------------------------------------------------------------
# Use when: You want musical variations using transformations
#
# VOICE_STAVE_DEF = "Melody & Bass"
#
# VOICE_STAVE_DATA = """
#     THEME & BASS;
#     transpose_part(THEME, 'P5') & BASS;
#     invert_part(THEME, 'C4') & BASS;
#     retrograde_part(THEME) & BASS;
#     augment_part(THEME, 2.0) & BASS;
#     THEME * 3 & BASS * 2
# """
#
# def build_score_data():
#     # Parse snippets
#     theme_data = parse_lilypond_to_data(THEME_A_LILY, part_name='THEME')
#     bass_data = parse_lilypond_to_data(BASS_LILY, part_name='BASS')
#     
#     SNIPPETS = {
#         'THEME': theme_data['parts']['THEME'],
#         'BASS': bass_data['parts']['BASS']
#     }
#     
#     metadata = {
#         'title': TITLE,
#         'composer': COMPOSER,
#         'time_signature': '4/4',
#         'key_signature': {'tonic': 'c', 'mode': 'major'},
#         'tempo': {'beat_duration': 4, 'bpm': 120}
#     }
#     
#     # Blueprint framework applies transformations on-the-fly!
#     # Single-part transformations work WITHOUT suffix (backward compatible)
#     # Each transformation runs once and caches results
#     score_data = build_score_from_blueprint(
#         VOICE_STAVE_DEF,
#         VOICE_STAVE_DATA,
#         SNIPPETS,
#         metadata
#     )
#     
#     return score_data


# ----------------------------------------------------------------------------
# APPROACH 6: Programmatic Harmonic Intelligence (Station 4 Mode)
# ----------------------------------------------------------------------------
# Use when: You need complex custom harmonic analysis
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
#     # Auto-harmonize (programmatic mode)
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
# APPROACH 7: Programmatic Transformations (Maximum Control)
# ----------------------------------------------------------------------------
# Use when: You need complex custom transformations beyond Blueprint
#
# from transformations import transpose_part, invert_part, retrograde_part
# from music_data import data_to_part, part_to_data
#
# def build_score_data():
#     # Parse melody
#     melody_data = parse_lilypond_to_data(THEME_A_LILY)
#     melody_part = data_to_part(melody_data['parts']['Part 1'])
#     
#     # Apply transformations programmatically
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
