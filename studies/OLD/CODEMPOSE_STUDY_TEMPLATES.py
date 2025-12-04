"""
Codempose Study File Templates

This file provides templates for creating new study files in Codempose.
Use these as starting points for your own compositions.

TEMPLATES INCLUDED:
0. Blueprint Strings Framework (RECOMMENDED - Composer-First Approach)
1. Basic Single-Voice Study
2. Multi-Voice Study (SATB)
3. Harmonized Study (with Harmonic Intelligence)
4. Advanced Features Study
5. Custom build_score_data() Patterns

RECOMMENDED: Start with TEMPLATE_BLUEPRINT for the most intuitive,
non-Python-like composition workflow!
"""

# ============================================================================
# TEMPLATE 0: BLUEPRINT STRINGS FRAMEWORK (RECOMMENDED)
# ============================================================================

"""
THE COMPOSER-FIRST APPROACH - Blueprint String Framework

This is the RECOMMENDED method for composing in Codempose. It uses an
intuitive, non-Python-like syntax with musical delimiters.

DELIMITER REFERENCE:
  ; (semicolon)  = Section separator (like double barlines)
  & (ampersand)  = Staff separator (vertical stacking)
  | (pipe)       = Snippet concatenator (horizontal "then")
  , (comma)      = Voice separator (multi-voice staves)
  'r'            = Auto-rest placeholder (matches section duration)

Examples: thirteenth.py, fourteenth.py

ALL VOICE_STAVE_DEF VARIANTS ARE SHOWN BELOW - Pick the one you need!
"""

TEMPLATE_BLUEPRINT = '''
"""Study file: Blueprint Strings Framework Demonstration"""

import _study_path  # Auto-path setup for study files

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Dict
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file


# ============================================================================
# METADATA
# ============================================================================

TITLE = "Blueprint Strings Study"
COMPOSER = "Codempose Framework"


# ============================================================================
# STATION 1: LILYPOND SNIPPETS (Musical Building Blocks)
# ============================================================================

# Define your musical ideas as LilyPond snippets
# These become the "LEGO blocks" for assembly

INTRO_LILY = r"""
\\relative c\'\' {{
    \\time 4/4
    \\key c \\major
    c4 d4 e4 f4 |
    g2 a2
}}
""".strip()

THEME_A_LILY = r"""
\\relative c\'\' {{
    c4 e4 g4 e4 |
    f4 d4 e4 c4
}}
""".strip()

THEME_B_LILY = r"""
\\relative c\'\' {{
    g4 a4 b4 c4 |
    d2 c2
}}
""".strip()

HARMONY_LILY = r"""
\\relative c\' {{
    <c e g>2 <d f a>2 |
    <e g b>2 <f a c>2
}}
""".strip()

BASS_LILY = r"""
\\relative c {{
    \\clef bass
    c2 g2 |
    f2 c2
}}
""".strip()

# For multi-voice examples (SATB)
SOPRANO_LILY = r"""
\\relative c\'\' {{
    c4 d4 e4 f4 |
    g1
}}
""".strip()

ALTO_LILY = r"""
\\relative c\' {{
    e4 f4 g4 a4 |
    b1
}}
""".strip()

TENOR_LILY = r"""
\\relative c\' {{
    g4 a4 c4 d4 |
    d1
}}
""".strip()

BASS_SATB_LILY = r"""
\\relative c {{
    \\clef bass
    c4 d4 e4 f4 |
    g1
}}
""".strip()


# ============================================================================
# STATION 2: BLUEPRINT STRINGS - STRUCTURE DEFINITION
# ============================================================================
#
# This is where the magic happens! Define your score structure using
# simple, musical delimiters instead of complex Python code.
#
# READ THE STRUCTURE LIKE A TABLE:
#   - Each section ends with ;
#   - Staves are separated by &
#   - Within a section, read left-to-right for what each staff plays


# ----------------------------------------------------------------------------
# VARIANT 1: Single Staff, Single Voice (Simplest)
# ----------------------------------------------------------------------------
# Use this for: Solo pieces, single melodic lines
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
# VARIANT 2: Two Staves, Single Voice Each (Piano-style)
# ----------------------------------------------------------------------------
# Use this for: Piano pieces, melody + bass, treble + bass
#
# VOICE_STAVE_DEF = "UpperStaff & LowerStaff"
#
# VOICE_STAVE_DATA = """
#     INTRO & r;
#     THEME_A & BASS;
#     r & HARMONY;
#     THEME_B & BASS
# """


# ----------------------------------------------------------------------------
# VARIANT 3: Multiple Staves, Single Voice Each
# ----------------------------------------------------------------------------
# Use this for: Three or more independent parts
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
# Use this for: Two voices on one staff (like Bach inventions)
#
# VOICE_STAVE_DEF = "(Voice1, Voice2)"
#
# VOICE_STAVE_DATA = """
#     THEME_A, r;
#     THEME_A, THEME_B;
#     r, THEME_A
# """


# ----------------------------------------------------------------------------
# VARIANT 5: Two Staves, Multi-Voice (SATB Hymn Style)
# ----------------------------------------------------------------------------
# Use this for: SATB hymns, choral music with piano reduction
#
# VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
#
# VOICE_STAVE_DATA = """
#     SOPRANO, ALTO & TENOR, BASS_SATB;
#     SOPRANO, r & r, BASS_SATB;
#     SOPRANO, ALTO & TENOR, BASS_SATB
# """


# ----------------------------------------------------------------------------
# VARIANT 6: Mixed Layout (Some Multi-Voice, Some Single)
# ----------------------------------------------------------------------------
# Use this for: Complex arrangements, string quartets with piano
#
# VOICE_STAVE_DEF = "(Violin1, Violin2) & Viola & Cello"
#
# VOICE_STAVE_DATA = """
#     THEME_A, THEME_B & HARMONY & BASS;
#     THEME_A, r & HARMONY & BASS;
#     r, THEME_B & r & BASS
# """


# ----------------------------------------------------------------------------
# VARIANT 7: Snippet Concatenation with | (Pipe)
# ----------------------------------------------------------------------------
# Use this for: Building longer phrases from smaller snippets
#
# VOICE_STAVE_DEF = "Melody & Bass"
#
# VOICE_STAVE_DATA = """
#     INTRO | THEME_A & BASS;
#     THEME_B | THEME_A & BASS | HARMONY;
#     INTRO & r
# """


# ============================================================================
# 🆕 ON-THE-FLY TRANSFORMATIONS (New Feature!)
# ============================================================================
#
# You can now apply musical transformations DIRECTLY in VOICE_STAVE_DATA!
# No need to pre-compute variations in build_score_data().
#
# The system automatically:
#   1. Detects transformation syntax
#   2. Applies the transformation
#   3. Saves the result to the SNIPPETS dictionary for inspection
#
# SYNTAX: function_name(base_snippet, 'arg1', arg2, ...)
#
# ----------------------------------------------------------------------------
# AVAILABLE TRANSFORMATION FUNCTIONS (from src/transformations.py):
# ----------------------------------------------------------------------------
#
# identity(snippet)
#     Returns the snippet unchanged (useful for testing)
#
# transpose_part(snippet, 'interval')
#     Transpose by musical interval
#     Examples:
#       transpose_part(THEME_A, 'P5')      # Up perfect 5th
#       transpose_part(THEME_A, '-m3')     # Down minor 3rd
#       transpose_part(THEME_A, 'M2')      # Up major 2nd
#
# invert_part(snippet, 'center_pitch')
#     Melodic inversion around a center pitch
#     Examples:
#       invert_part(THEME_A, 'C4')         # Invert around middle C
#       invert_part(MELODY, 'G4')          # Invert around G4
#
# retrograde_part(snippet)
#     Play the snippet backwards (reverse order)
#     Examples:
#       retrograde_part(THEME_A)
#       retrograde_part(INTRO)
#
# augment_part(snippet, factor)
#     Stretch note durations by factor (rhythmic augmentation)
#     Examples:
#       augment_part(THEME_A, 2.0)         # Double all note lengths
#       augment_part(THEME_A, 1.5)         # 1.5x slower
#
# diminish_part(snippet, factor)
#     Shrink note durations by factor (rhythmic diminution)
#     Examples:
#       diminish_part(THEME_A, 2.0)        # Half all note lengths
#       diminish_part(THEME_A, 4.0)        # Quarter note lengths
#
# chordify_part(snippet, 'chord_type')
#     Harmonize melody with chords
#     Examples:
#       chordify_part(MELODY, 'major')     # Major triads
#       chordify_part(MELODY, 'minor')     # Minor triads
#
# retrograde_inversion(snippet, 'center_pitch')
#     Combination: invert AND reverse
#     Examples:
#       retrograde_inversion(THEME_A, 'C4')
#
# transpose_and_augment(snippet, 'interval', factor)
#     Combination: transpose AND stretch rhythm
#     Examples:
#       transpose_and_augment(THEME_A, 'P5', 2.0)  # Up P5 + 2x slower
#
# ----------------------------------------------------------------------------
# TRANSFORMATION EXAMPLES IN BLUEPRINT STRINGS:
# ----------------------------------------------------------------------------
#
# Example 1: Simple Transformations
#   VOICE_STAVE_DATA = """
#       THEME_A & BASS;
#       transpose_part(THEME_A, 'P5') & BASS;
#       invert_part(THEME_A, 'C4') & BASS;
#       retrograde_part(THEME_A) & BASS
#   """
#
# Example 2: Combining with Concatenation (|)
#   VOICE_STAVE_DATA = """
#       THEME_A | transpose_part(THEME_A, 'P5') | invert_part(THEME_A, 'C4') & BASS
#   """
#
# Example 3: Multi-Voice with Transformations
#   VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
#   VOICE_STAVE_DATA = """
#       THEME_A, transpose_part(THEME_A, '-P5') & HARMONY, BASS;
#       invert_part(THEME_A, 'C4'), retrograde_part(THEME_A) & r, BASS
#   """
#
# Example 4: Complex Transformations
#   VOICE_STAVE_DATA = """
#       INTRO & BASS;
#       transpose_and_augment(THEME_A, 'P5', 2.0) & chordify_part(BASS, 'major');
#       retrograde_inversion(THEME_A, 'C4') & r
#   """
#
# 💡 TIP: All transformation results are saved to the SNIPPETS dictionary
#         with their full syntax as the key. You can inspect them after
#         build_score_data() runs!
#
# ============================================================================


# ----------------------------------------------------------------------------
# ACTIVE EXAMPLE: Choose one variant above and uncomment it,
# or define your own custom layout here:
# ----------------------------------------------------------------------------

# Simple two-staff example (Variant 2)
VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    INTRO & r;
    THEME_A & BASS;
    THEME_B & HARMONY;
    THEME_A | INTRO & BASS
"""


# ============================================================================
# STATION 3: BUILD SCORE DATA
# ============================================================================

def build_score_data() -> Dict:
    """
    Build score using Blueprint String Framework.
    
    This function:
    1. Parses all LilyPond snippets
    2. Creates snippets library
    3. Calls build_score_from_blueprint() with your structure
    4. Returns canonical score_data
    
    Returns:
        dict: Score data with metadata and parts
    """
    
    print("\\n" + "="*70)
    print("BLUEPRINT STRINGS FRAMEWORK")
    print("="*70)
    print(f"\\nTitle: {{TITLE}}")
    print(f"Layout: {{VOICE_STAVE_DEF}}")
    print()
    
    # ========================================================================
    # STEP 1: Parse all LilyPond snippets
    # ========================================================================
    
    print("[Step 1: Parsing LilyPond snippets...]")
    
    snippets_to_parse = {{
        'INTRO': INTRO_LILY,
        'THEME_A': THEME_A_LILY,
        'THEME_B': THEME_B_LILY,
        'HARMONY': HARMONY_LILY,
        'BASS': BASS_LILY,
        # Add more as needed
        # 'SOPRANO': SOPRANO_LILY,
        # 'ALTO': ALTO_LILY,
        # 'TENOR': TENOR_LILY,
        # 'BASS_SATB': BASS_SATB_LILY,
    }}
    
    SNIPPETS = {{}}
    for name, lily_code in snippets_to_parse.items():
        parsed = parse_lilypond_to_data(lily_code, part_name=name)
        SNIPPETS[name] = parsed['parts'][name]
        print(f"  ✓ {{name}}: {{len(SNIPPETS[name])}} events")
    
    # ========================================================================
    # STEP 2: Build score using Blueprint Strings
    # ========================================================================
    
    print("\\n[Step 2: Building score from blueprint...]")
    
    metadata = {{
        'title': TITLE,
        'composer': COMPOSER,
        'time_signature': '4/4',
        'key_signature': {{'tonic': 'c', 'mode': 'major'}},
    }}
    
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,    # Structure layout
        VOICE_STAVE_DATA,   # Content definition
        SNIPPETS,           # Musical building blocks
        metadata            # Score metadata
    )
    
    print("\\n" + "="*70)
    print("✅ SCORE ASSEMBLY COMPLETE")
    print("="*70)
    print("\\nGenerated staves:")
    for staff_name in score_data['parts'].keys():
        print(f"  • {{staff_name}}")
    print()
    
    return score_data


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
#   Meaning: Three sections, each is a musical phrase/segment
#   Visual: Like double barlines in a score
#
# & (AMPERSAND) - Staff separator
#   Example: "MELODY & BASS"
#   Meaning: Two staves playing simultaneously (vertically stacked)
#   Visual: Like the grand staff in piano music
#
# | (PIPE) - Snippet concatenator
#   Example: "INTRO | THEME_A"
#   Meaning: Play INTRO, then immediately play THEME_A (horizontal)
#   Visual: Like measures flowing left to right
#
# , (COMMA) - Voice separator within a staff
#   Example: "(Soprano, Alto)"
#   Meaning: Two voices sharing one staff (polyphonic)
#   Visual: Like stem-up and stem-down notes on same staff
#
# 'r' - Auto-rest placeholder
#   Example: "THEME_A & r"
#   Meaning: Upper staff plays THEME_A, lower staff rests
#   Visual: Automatically generates rests matching the duration
#
# ============================================================================
# TIPS FOR BLUEPRINT STRINGS
# ============================================================================
#
# 1. START SIMPLE: Begin with single-staff, add complexity as needed
#
# 2. READ LIKE A TABLE: Each line is a section, columns are staves
#    Section 1:  INTRO     & r         & r
#    Section 2:  THEME_A   & HARMONY   & BASS
#    Section 3:  THEME_B   & HARMONY   & BASS
#
# 3. USE WHITESPACE: Align & symbols vertically for readability
#    GOOD:  "INTRO    & BASS"
#           "THEME_A  & HARMONY"
#    BAD:   "INTRO&BASS"
#           "THEME_A&HARMONY"
#
# 4. COMBINE SNIPPETS: Use | to build longer phrases
#    "INTRO | THEME_A | CODA" = Three snippets in sequence
#
# 5. MULTI-VOICE: Use parentheses for voices on same staff
#    "(Soprano, Alto)" = Two voices, one staff
#    "Soprano & Alto" = Two voices, two staves
#
# 6. REST WISELY: Use 'r' when one staff rests while others play
#    "SOLO & r" = Solo melody with silent bass
#
# 7. TEST INCREMENTALLY: Start with one section, add more gradually
#
# ============================================================================
'''


# ============================================================================
# TEMPLATE 1: BASIC SINGLE-VOICE STUDY
# ============================================================================

"""
Use this template for simple single-voice compositions.
Examples: first.py, second.py, third.py
"""

TEMPLATE_BASIC = '''
"""Study file: [DESCRIPTION]"""

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

MELODY_LILY = r"""
\\relative c\'\' {
    \\time 4/4
    \\key c \\major
    \\tempo 4=120
    c4 d4 e4 f4 |
    g2 a2 |
    b4 a4 g4 f4 |
    e2 d2 |
    c1
}
""".strip()

TITLE = "My Study Title"
COMPOSER = "Composer Name"


# ============================================================================
# STATION 2: REAL-TIME VALIDATION
# ============================================================================
# (Automatic via LilyPond parser)


# ============================================================================
# STATION 3: BUILD SCORE DATA
# ============================================================================

def build_score_data():
    """
    Build score data from LilyPond snippets.
    
    Returns:
        dict: Score data with metadata and parts
    """
    from lilypond_parser import parse_lilypond_to_data
    
    # Parse melody
    melody_data = parse_lilypond_to_data(MELODY_LILY, part_name=\'Melody\')
    
    # Build score data
    score_data = {
        \'metadata\': {
            \'title\': TITLE,
            \'composer\': COMPOSER,
            \'time_signature\': \'4/4\',
            \'key_signature\': {\'tonic\': \'c\', \'mode\': \'major\'},
            \'tempo\': {\'beat_duration\': 4, \'bpm\': 120}
        },
        \'parts\': {
            \'Melody\': melody_data[\'parts\'][\'Melody\']
        }
    }
    
    return score_data


# ============================================================================
# STATION 4: EXECUTION
# ============================================================================

if __name__ == \'__main__\':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
'''


# ============================================================================
# TEMPLATE 2: MULTI-VOICE STUDY (SATB)
# ============================================================================

"""
Use this template for four-voice compositions.
Example: tenth.py
"""

TEMPLATE_MULTI_VOICE = '''
"""Multi-voice study file: [DESCRIPTION]"""

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

SOPRANO_LILY = r"""
\\relative c\'\' {
    \\time 4/4
    \\key c \\major
    c2 d2 |
    e2 f2 |
    g1
}
""".strip()

ALTO_LILY = r"""
\\relative c\' {
    \\time 4/4
    \\key c \\major
    e2 f2 |
    g2 a2 |
    b1
}
""".strip()

TENOR_LILY = r"""
\\relative c\' {
    \\time 4/4
    \\key c \\major
    \\clef "treble_8"
    g2 a2 |
    c2 d2 |
    d1
}
""".strip()

BASS_LILY = r"""
\\relative c {
    \\time 4/4
    \\key c \\major
    \\clef bass
    c2 d2 |
    e2 f2 |
    g1
}
""".strip()

TITLE = "Four-Voice Composition"
COMPOSER = "Composer Name"


# ============================================================================
# STATION 3: BUILD SCORE DATA
# ============================================================================

def build_score_data():
    """Build four-voice score data."""
    from lilypond_parser import parse_lilypond_to_data
    
    # Parse all voices
    soprano_data = parse_lilypond_to_data(SOPRANO_LILY, part_name=\'Soprano\')
    alto_data = parse_lilypond_to_data(ALTO_LILY, part_name=\'Alto\')
    tenor_data = parse_lilypond_to_data(TENOR_LILY, part_name=\'Tenor\')
    bass_data = parse_lilypond_to_data(BASS_LILY, part_name=\'Bass\')
    
    # Build score data
    score_data = {
        \'metadata\': {
            \'title\': TITLE,
            \'composer\': COMPOSER,
            \'time_signature\': \'4/4\',
            \'key_signature\': {\'tonic\': \'c\', \'mode\': \'major\'},
            \'tempo\': {\'beat_duration\': 4, \'bpm\': 100}
        },
        \'parts\': {
            \'Soprano\': soprano_data[\'parts\'][\'Soprano\'],
            \'Alto\': alto_data[\'parts\'][\'Alto\'],
            \'Tenor\': tenor_data[\'parts\'][\'Tenor\'],
            \'Bass\': bass_data[\'parts\'][\'Bass\']
        }
    }
    
    return score_data


# ============================================================================
# STATION 4: EXECUTION
# ============================================================================

if __name__ == \'__main__\':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
'''


# ============================================================================
# TEMPLATE 3: HARMONIZED STUDY (WITH HARMONIC INTELLIGENCE)
# ============================================================================

"""
Use this template to automatically harmonize melodies.
Examples: sixteenth.py, seventeenth.py
"""

TEMPLATE_HARMONIZED = '''
"""Harmonized study with automatic bass generation."""

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

MELODY_LILY = r"""
\\relative c\'\' {
    \\time 4/4
    \\key c \\major
    \\tempo 4=120
    c4 d4 e4 f4 |
    g2 e2 |
    f4 e4 d4 c4 |
    c1
}
""".strip()

# Define chord progression
PROGRESSION_STRING = "I - IV - V - I"
KEY = "C"

TITLE = "Harmonized Melody"
COMPOSER = "Harmonic Engine"


# ============================================================================
# STATION 3: BUILD SCORE DATA
# ============================================================================

def build_score_data():
    """
    Build harmonized score with auto-generated bass.
    
    Returns:
        dict: Score data with melody and bass parts
    """
    from lilypond_parser import parse_lilypond_to_data
    from music_data import data_to_part, part_to_data
    from harmonic_engine import harmonize_melody
    
    print("\\n" + "="*70)
    print(f"HARMONIZING: {TITLE}")
    print("="*70)
    print(f"Key: {KEY}")
    print(f"Progression: {PROGRESSION_STRING}\\n")
    
    # Parse melody
    melody_data = parse_lilypond_to_data(MELODY_LILY, part_name=\'Melody\')
    melody_part = data_to_part(melody_data[\'parts\'][\'Melody\'], melody_data.get(\'metadata\'))
    
    # Harmonize melody with progression
    harmonized_score = harmonize_melody(
        melody_part=melody_part,
        progression_string=PROGRESSION_STRING,
        key=KEY,
        harmonic_rhythm="auto"  # or "one_per_measure"
    )
    
    # Convert back to canonical format
    melody_events = part_to_data(harmonized_score.parts[0])
    bass_events = part_to_data(harmonized_score.parts[1])
    
    score_data = {
        \'metadata\': {
            \'title\': TITLE,
            \'composer\': COMPOSER,
            \'time_signature\': \'4/4\',
            \'key_signature\': {\'tonic\': \'c\', \'mode\': \'major\'},
            \'tempo\': {\'beat_duration\': 4, \'bpm\': 120}
        },
        \'parts\': {
            \'Melody\': melody_events,
            \'Bass\': bass_events  # Auto-generated!
        }
    }
    
    print("="*70)
    print("HARMONIZATION COMPLETE")
    print("="*70 + "\\n")
    
    return score_data


# ============================================================================
# STATION 4: EXECUTION
# ============================================================================

if __name__ == \'__main__\':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
'''


# ============================================================================
# TEMPLATE 4: ADVANCED FEATURES STUDY
# ============================================================================

"""
Use this template to demonstrate advanced notation features.
Examples: eighth.py (grace notes), seventh.py (ties), sixth.py (tuplets)
"""

TEMPLATE_ADVANCED = '''
"""Advanced features study: [FEATURE]"""

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

# Example with grace notes
MELODY_LILY = r"""
\\relative c\'\' {
    \\time 4/4
    \\key c \\major
    
    % Grace notes (acciaccatura)
    \\acciaccatura { d8 } c4
    
    % Appoggiatura
    \\appoggiatura { e8 } d4
    
    % Tuplets
    \\tuplet 3/2 { e8 f g }
    
    % Ties
    c4~ c4
    
    % Articulations
    d4-. e4-> f4-!
    
    % Dynamics
    g4\\f a4\\p
}
""".strip()

TITLE = "Advanced Features"
COMPOSER = "Composer Name"


# ============================================================================
# STATION 3: BUILD SCORE DATA
# ============================================================================

def build_score_data():
    """Build score with advanced features."""
    from lilypond_parser import parse_lilypond_to_data
    
    # Parse melody
    melody_data = parse_lilypond_to_data(MELODY_LILY, part_name=\'Melody\')
    
    # Optional: Print analysis
    print("\\nFeatures demonstrated:")
    print("  - Grace notes (acciaccatura, appoggiatura)")
    print("  - Tuplets")
    print("  - Ties")
    print("  - Articulations (staccato, accent, marcato)")
    print("  - Dynamics (forte, piano)")
    
    score_data = {
        \'metadata\': {
            \'title\': TITLE,
            \'composer\': COMPOSER,
            \'time_signature\': \'4/4\',
            \'key_signature\': {\'tonic\': \'c\', \'mode\': \'major\'},
        },
        \'parts\': {
            \'Melody\': melody_data[\'parts\'][\'Melody\']
        }
    }
    
    return score_data


# ============================================================================
# STATION 4: EXECUTION
# ============================================================================

if __name__ == \'__main__\':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
'''


# ============================================================================
# TEMPLATE 5: CUSTOM TRANSFORMATIONS
# ============================================================================

"""
Use this template when you need custom transformations
of musical data before export.
"""

TEMPLATE_CUSTOM = '''
"""Study with custom transformations."""

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

MELODY_LILY = r"""
\\relative c\'\' {
    c4 d4 e4 f4 |
    g2 a2
}
""".strip()

TITLE = "Custom Transformations"
COMPOSER = "Composer Name"


# ============================================================================
# STATION 3: BUILD SCORE DATA
# ============================================================================

def build_score_data():
    """Build score with custom transformations."""
    from lilypond_parser import parse_lilypond_to_data
    from music_data import data_to_part, part_to_data
    
    # Parse melody
    melody_data = parse_lilypond_to_data(MELODY_LILY, part_name=\'Melody\')
    
    # Convert to music21 for transformations
    melody_part = data_to_part(melody_data[\'parts\'][\'Melody\'])
    
    # CUSTOM TRANSFORMATIONS HERE
    # Example: Transpose up a major third
    from music21 import interval
    transposed_part = melody_part.transpose(\'M3\')
    
    # Example: Add articulations
    from music21 import articulations
    for n in transposed_part.flatten().notes:
        if n.pitch.midi % 2 == 0:  # Even MIDI numbers
            n.articulations.append(articulations.Staccato())
    
    # Example: Double tempo
    for n in transposed_part.flatten().notesAndRests:
        n.quarterLength = n.quarterLength / 2
    
    # Convert back to canonical format
    transformed_events = part_to_data(transposed_part)
    
    score_data = {
        \'metadata\': {
            \'title\': TITLE,
            \'composer\': COMPOSER,
            \'time_signature\': \'4/4\',
            \'key_signature\': {\'tonic\': \'e\', \'mode\': \'major\'},  # Transposed key
            \'tempo\': {\'beat_duration\': 4, \'bpm\': 240}  # Doubled tempo
        },
        \'parts\': {
            \'Melody\': transformed_events
        }
    }
    
    return score_data


# ============================================================================
# STATION 4: EXECUTION
# ============================================================================

if __name__ == \'__main__\':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
'''


# ============================================================================
# COMMON LILYPOND PATTERNS
# ============================================================================

LILYPOND_PATTERNS = """
# ============================================================================
# COMMON LILYPOND NOTATION PATTERNS
# ============================================================================

# BASIC NOTE ENTRY
# ----------------
c4 d4 e4 f4              # Quarter notes
c2 d2                    # Half notes
c1                       # Whole note
c8 d8 e8 f8              # Eighth notes
c16 d16 e16 f16          # Sixteenth notes

# RESTS
# -----
r4                       # Quarter rest
r2                       # Half rest
r1                       # Whole rest

# OCTAVES (relative mode)
# -----------------------
c' d' e'                 # One octave up
c'' d'' e''              # Two octaves up
c d e                    # Same octave
c, d, e,                 # One octave down

# ACCIDENTALS
# -----------
cis4                     # C sharp
des4                     # D flat
c!4                      # C natural (force)

# DURATIONS
# ---------
c4.                      # Dotted quarter (1.5 beats)
c2.                      # Dotted half (3 beats)
c4..                     # Double-dotted quarter

# TIES
# ----
c4~ c4                   # Tied quarter notes
c2~ c4~ c4               # Extended tie

# TUPLETS
# -------
\\tuplet 3/2 { c8 d e }  # Triplet (3 eighth notes in 2)
\\tuplet 5/4 { c16 d e f g }  # Quintuplet

# SLURS
# -----
c4( d e f)               # Slur from c to f

# ARTICULATIONS
# -------------
c4-.                     # Staccato
c4->                     # Accent
c4-!                     # Marcato
c4-_                     # Tenuto
c4-+                     # Stopped (horn)
c4-|                     # Staccatissimo

# DYNAMICS
# --------
c4\\pp                    # Pianissimo
c4\\p                     # Piano
c4\\mp                    # Mezzo-piano
c4\\mf                    # Mezzo-forte
c4\\f                     # Forte
c4\\ff                    # Fortissimo
c4\\< d e f\\!            # Crescendo to f

# GRACE NOTES
# -----------
\\acciaccatura { d8 } c4  # Slashed grace note
\\appoggiatura { e8 } d4  # Unslashed grace note

# ORNAMENTS
# ---------
c4\\trill                 # Trill
c4\\turn                  # Turn
c4\\mordent               # Mordent
c4\\prall                 # Inverted mordent

# TIME SIGNATURES
# ---------------
\\time 4/4               # Common time
\\time 3/4               # Waltz time
\\time 6/8               # Compound meter
\\time 5/4               # Irregular meter

# KEY SIGNATURES
# --------------
\\key c \\major          # C major
\\key g \\major          # G major (1 sharp)
\\key a \\minor          # A minor
\\key d \\minor          # D minor (1 flat)

# CLEFS
# -----
\\clef treble            # Treble clef
\\clef bass              # Bass clef
\\clef alto              # Alto clef
\\clef tenor             # Tenor clef

# TEMPO
# -----
\\tempo 4=120            # Quarter = 120 BPM
\\tempo "Allegro" 4=132  # With text

# BARLINES
# --------
\\bar "|"                # Normal barline
\\bar "||"               # Double barline
\\bar "|."               # Final barline

# REPEATS
# -------
\\repeat volta 2 { c4 d e f }  # Repeat 2 times

# COMMENTS
# --------
% Single line comment
%{ Multi-line
   comment }%
"""


# ============================================================================
# CANONICAL FORMAT PATTERNS
# ============================================================================

CANONICAL_PATTERNS = """
# ============================================================================
# CANONICAL EVENT FORMAT PATTERNS
# ============================================================================

# BASIC NOTE EVENT
# ----------------
{
    'type': 'note',
    'step': 'C',           # A-G
    'octave': 4,           # 0-8
    'alter': 0,            # -2 (double flat) to 2 (double sharp)
    'ql': 1.0              # Quarter length (1.0 = quarter note)
}

# REST EVENT
# ----------
{
    'type': 'rest',
    'ql': 1.0
}

# NOTE WITH ARTICULATIONS
# -----------------------
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'alter': 0,
    'ql': 1.0,
    'articulations': ['staccato', 'accent']
}

# NOTE WITH DYNAMICS
# ------------------
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'alter': 0,
    'ql': 1.0,
    'dynamics': 'f'        # pp, p, mp, mf, f, ff, fff
}

# TUPLET NOTES
# ------------
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'alter': 0,
    'ql': 0.6667,          # 2/3 for triplet
    'tuplet': {
        'actual': 3,
        'normal': 2
    }
}

# TIED NOTE
# ---------
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'alter': 0,
    'ql': 1.0,
    'tie': 'start'         # 'start', 'continue', 'stop'
}

# GRACE NOTE
# ----------
{
    'type': 'grace',
    'step': 'D',
    'octave': 4,
    'alter': 0,
    'grace_type': 'acciaccatura'  # or 'appoggiatura'
}

# CHORD EVENT
# -----------
{
    'type': 'chord',
    'pitches': [
        {'step': 'C', 'octave': 4, 'alter': 0},
        {'step': 'E', 'octave': 4, 'alter': 0},
        {'step': 'G', 'octave': 4, 'alter': 0}
    ],
    'ql': 1.0
}

# METADATA
# --------
{
    'title': 'Composition Title',
    'composer': 'Composer Name',
    'time_signature': '4/4',
    'key_signature': {'tonic': 'c', 'mode': 'major'},
    'tempo': {'beat_duration': 4, 'bpm': 120}
}
"""


# ============================================================================
# QUICK REFERENCE GUIDE
# ============================================================================

QUICK_REFERENCE = """
# ============================================================================
# CODEMPOSE STUDY FILE QUICK REFERENCE
# ============================================================================

## FILE STRUCTURE

Every study file has 4 stations:

1. LILYPOND SNIPPETS
   - Define your musical content in LilyPond notation
   - Use variables: MELODY_LILY, SOPRANO_LILY, etc.
   - Set TITLE and COMPOSER

2. REAL-TIME VALIDATION
   - Automatic - no code needed
   - Parser validates LilyPond syntax

3. BUILD SCORE DATA
   - Define build_score_data() function
   - Parse LilyPond with parse_lilypond_to_data()
   - Return score_data dictionary

4. EXECUTION
   - Always the same: run_pipeline_from_file(__file__)
   - Handles all export formats automatically


## BASIC WORKFLOW

1. Write melody in LilyPond (MELODY_LILY variable)
2. Parse it: parse_lilypond_to_data(MELODY_LILY)
3. Build score_data dictionary with metadata and parts
4. Run file - exports to PDF, MusicXML, MIDI automatically


## HARMONIC INTELLIGENCE WORKFLOW

1. Write melody in LilyPond
2. Define PROGRESSION_STRING = "I - IV - V - I"
3. Convert to music21: data_to_part()
4. Harmonize: harmonize_melody(melody_part, PROGRESSION_STRING, KEY)
5. Convert back: part_to_data()
6. Build score_data with melody and bass parts


## KEY FUNCTIONS

### Parsing
- parse_lilypond_to_data(lily_string, part_name='Melody')
  Returns: dict with 'parts' and 'metadata'

### Conversion
- data_to_part(events, metadata=None)
  Canonical events → music21.stream.Part

- part_to_data(part)
  music21.stream.Part → Canonical events

### Harmonization
- harmonize_melody(melody_part, progression_string, key, harmonic_rhythm="auto")
  Returns: music21.stream.Score with melody and bass

### Analysis
- find_structural_tones(melody_part)
  Tags notes as structural or ornamental

- print_structural_analysis(melody_part, verbose=True)
  Prints analysis to console


## EXPORT FORMATS

All study files automatically export to:
- PDF (via LilyPond)
- MusicXML (for MuseScore, Finale, etc.)
- MIDI (for playback)
- LilyPond source (.ly file)

Files saved to: outputs/[filename].*


## COMMON PATTERNS

### Single voice:
score_data = {
    'metadata': {...},
    'parts': {
        'Melody': melody_events
    }
}

### Multi-voice (SATB):
score_data = {
    'metadata': {...},
    'parts': {
        'Soprano': soprano_events,
        'Alto': alto_events,
        'Tenor': tenor_events,
        'Bass': bass_events
    }
}

### Harmonized (melody + bass):
score_data = {
    'metadata': {...},
    'parts': {
        'Melody': melody_events,
        'Bass': bass_events  # Auto-generated
    }
}
"""


# ============================================================================
# EXAMPLE: CREATE A NEW STUDY FILE
# ============================================================================

def create_study_file(filename, template_type='blueprint'):
    """
    Helper function to create a new study file from a template.
    
    Args:
        filename (str): Name of the new file (e.g., 'eighteenth.py')
        template_type (str): 'blueprint' (RECOMMENDED), 'basic', 'multi_voice', 
                            'harmonized', 'advanced', or 'custom'
    """
    templates = {
        'blueprint': TEMPLATE_BLUEPRINT,  # RECOMMENDED - Composer-first approach
        'basic': TEMPLATE_BASIC,
        'multi_voice': TEMPLATE_MULTI_VOICE,
        'harmonized': TEMPLATE_HARMONIZED,
        'advanced': TEMPLATE_ADVANCED,
        'custom': TEMPLATE_CUSTOM
    }
    
    template = templates.get(template_type, TEMPLATE_BLUEPRINT)  # Default to Blueprint
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"Created {filename} from {template_type} template")
    print(f"Edit the file to customize your composition!")


if __name__ == '__main__':
    # Print quick reference
    print(QUICK_REFERENCE)
    
    # Example usage:
    # create_study_file('twentyfirst.py', 'blueprint')  # RECOMMENDED
    # create_study_file('eighteenth.py', 'harmonized')
