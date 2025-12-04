"""
NINETYEIGHTH STUDY: Feature Demonstration
==========================================

Codempose Four-Station Workflow demonstration.
Uses Blueprint Strings (Station 3) by default.
Set PROMOTE_TO_PROGRAMMATIC = True to use Station 4 instead.
"""

import _study_path  # Auto-path setup

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Dict
# Essential for Station 3 (Blueprint)
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file

# Optional imports for Station 4 / advanced use (uncomment as needed)
# from src.music_data import data_to_part, part_to_data
# from src.transformations import transpose_part, invert_part, retrograde_part
# from src.harmonic_engine import harmonize_melody
# from src.lib.station4_music21_examples import example_canon_at_interval
# from src.lib.TONAL_HARMONY_TEMPLATES import PROGRESSION_I_IV_V_I


# ============================================================================
# !! STATION 4 PROMOTION TOGGLE !!
# ============================================================================
# Set this to True to bypass Station 3 (Blueprint) and use Station 4
# (Programmatic Composition) defined further below.
PROMOTE_TO_PROGRAMMATIC = False
# ============================================================================


# ============================================================================
# METADATA
# ============================================================================
# Based on proven patterns from thirteenth.py and fourteenth.py

TITLE = "NINETYEIGHTH Study: Feature Demonstration"
COMPOSER = "Codempose Framework"
OPUS_NUMBER = "NINETYEIGHTH"
INSTRUMENTATION = "Piano"  # or "SATB Choir", "String Quartet", etc.


############################################################################
## STATION 1: DEFINE MUSICAL IDEAS (LilyPond Snippets)                     ##
############################################################################
# Define your musical building blocks using LilyPond notation.
# These snippets will be parsed into Station 2's internal library.
#
# BEST PRACTICES (from old studies):
# - Use descriptive variable names ending with _LILY
# - Include \key, \time, \tempo in first snippet
# - Add dynamics, articulations, ornaments to showcase features
# - Keep snippets focused and reusable
#
# AUTOMATIC REHEARSAL MARKS:
# - Snippets named "PREFIX_SUFFIX" auto-generate \mark "SUFFIX" in PDF
#   Example: "THEME_A" → displays mark "A", "INTRO_Main" → displays "Main"
# - Transformations (transpose, invert) and repeats (*) don't generate marks
# - Explicit \mark in snippet OVERRIDES automatic injection
#   Example: \mark \markup { \bold \box "Custom" } prevents auto-mark

# Richer default example (G major, 3/4 time with musical expression)
THEME_A_LILY = r"""
\relative c'' {
    \key g \major
    \time 3/4
    \tempo "Andante" 4=90
    d4-.\p( fis8 g) a4~ |      % Staccato, piano, slur, tie
    a4 g4->( fis) |             % Accent, phrase
    e4.( d8~ d4) |              % Dotted rhythm
    b'4\f c4 d4                % Forte, climax
}
""".strip()

# Contrasting phrase
THEME_B_LILY = r"""
\relative c' {
    \key g \major
    \time 3/4
    g4( fis e) |
    d2.~ |
    d4 e fis |
    g2.
}
""".strip()

# Bass figure
BASS_FIGURE_LILY = r"""
\relative c {
    \clef bass
    \key g \major
    \time 3/4
    g4 d' b |
    c2 b4 |
    a4 g fis |
    g2.
}
""".strip()

# Harmonic support (chords)
HARMONY_CHORDS_LILY = r"""
\relative c' {
    \key g \major
    \time 3/4
    <g b d>2. |
    <a c e>2. |
    <g b d>2.
}
""".strip()

# Add more snippets here as your composition grows...

# ----------------------------------------------------------------------------
# CREATIVE EXAMPLES (from second.py study)
# ----------------------------------------------------------------------------
# Real musical compositions - uncomment to use as starting points!

# Short, rhythmic motif - great for transformations
# SOURCE_THEME_LILY = r"""
# \relative c' {
#     \time 4/4
#     \key c \major
#     e4 b4 e'4 b4
# }
# """.strip()

# Expressive melodic phrase with interesting intervals and rhythm
# SOURCE_MELODY_LILY = r"""
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


############################################################################
## STATION 2: INTERNAL SNIPPET LIBRARY (Conceptual)                      ##
############################################################################
# Station 2 is the **internal SNIPPETS dictionary** that holds:
#   1. Parsed events from Station 1 (your LilyPond snippets)
#   2. Generated events from transformations (transpose, invert, etc.)
#   3. TinyNotation equivalents (for validation and alternative input)
#
# This station is built automatically during build_score_data() execution.
# You don't define it explicitly - it's populated by the framework.
#
# Example of what gets stored in SNIPPETS (for reference):
#   SNIPPETS['THEME_A'] = [event1, event2, ...]  # From parsing
#   SNIPPETS['THEME_A_TRANSPOSED'] = [...]       # From transformation
#
# TinyNotation equivalents (optional reference - generated automatically):
#   THEME_A_TINY = "tinynotation: 3/4 G:maj d4-. fis8( g) a4~ a g-> fis e4.( d8~ d4) b'4 c d"


############################################################################
## STATION 3: ASSEMBLE SCORE STRUCTURE (Blueprint Strings)               ##
############################################################################
# Define the overall structure using Blueprint strings.
# This section is used IF `PROMOTE_TO_PROGRAMMATIC` is False (default).
#
# BLUEPRINT SYNTAX QUICK REFERENCE:
#   ; = Section separator (like double barlines)
#   & = Staff separator (vertical stacking)
#   | = Snippet concatenator (horizontal "then")
#   , = Voice separator (multi-voice in same staff)
#   r = Auto-rest placeholder
#   * N = Repeat snippet N times
#
# TRANSFORMATION EXAMPLES:
#   Single-part (no suffix):    transpose_part(THEME, 'P5')
#   Multi-part (suffix needed): harmonize_part(MELODY):melody, :harmony

# --- Active Blueprint Example: Piano Style (Two Staves) ---
VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    # Section 1: Exposition
    THEME_A & BASS_FIGURE;

    # Section 2: Development with transposition
    transpose_part(THEME_A, 'P4') & BASS_FIGURE;

    # Section 3: Contrasting material
    THEME_B & r;

    # Section 4: Recapitulation with repetition
    THEME_A * 2 & BASS_FIGURE * 2
"""

# --- Variant 1: Single Staff (Solo) ---
# VOICE_STAVE_DEF = "Solo Melody"
# VOICE_STAVE_DATA = """
#     THEME_A;
#     THEME_B;
#     transpose_part(THEME_A, 'P5')
# """

# --- Variant 2: SATB Hymn (Multi-Voice, Two Staves) ---
# VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
# VOICE_STAVE_DATA = """
#     SOPRANO_A, ALTO_A & TENOR_A, BASS_A;
#     SOPRANO_B, ALTO_B & TENOR_B, BASS_B
# """
# Note: Requires defining SOPRANO_A, ALTO_A, TENOR_A, BASS_A, etc. in Station 1

# --- Variant 3: Harmonization (Multi-Part Transformation) ---
# VOICE_STAVE_DEF = "Melody & Harmony"
# VOICE_STAVE_DATA = """
#     THEME_A & r;
#     harmonize_part(THEME_A, 'I-IV-V-I', 'G'):melody
#     &
#     harmonize_part(THEME_A, 'I-IV-V-I', 'G'):harmony
# """

# --- Variant 4: Complex Form (ABA with Coda) ---
# VOICE_STAVE_DEF = "Treble & Bass"
# VOICE_STAVE_DATA = """
#     THEME_A & BASS_FIGURE;                          # A section
#     THEME_B & r;                                    # B section
#     transpose_part(THEME_A, 'P8') & BASS_FIGURE;   # A' section (octave higher)
#     THEME_A * 2 & BASS_FIGURE * 2                  # Coda (repeated)
# """


# --------------------------------------------------------------------------
# Blueprint Assembly Function (Processes Station 3)
# --------------------------------------------------------------------------
def build_score_data() -> Dict:
    """
    Builds score using Station 3 Blueprint definition.
    
    This is APPROACH 1 (RECOMMENDED): The composer-first method.
    
    Four-Station Workflow:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. Parse Station 1 snippets → populate SNIPPETS (Station 2)
    2. Process Blueprint strings (VOICE_STAVE_DEF + VOICE_STAVE_DATA)
    3. Apply transformations → add results to SNIPPETS (Station 2 grows)
    4. Assemble final score_data from SNIPPETS library
    
    Returns:
        dict: Canonical score_data {'metadata': {}, 'parts': {}}
    """
    
    print("\n" + "="*70)
    print("NINETYEIGHTH STUDY: Blueprint String Framework")
    print("="*70)
    
    # --- STATION 1 → STATION 2: Parse LilyPond Snippets ---
    print("\n[Station 1 Parsing] Populating Internal Snippet Library (Station 2)...")
    
    # Define which snippets to parse (matches your Station 1 definitions)
    snippets_to_parse = {
        'THEME_A': THEME_A_LILY,
        'THEME_B': THEME_B_LILY,
        'BASS_FIGURE': BASS_FIGURE_LILY,
        'HARMONY_CHORDS': HARMONY_CHORDS_LILY,
    }
    
    # Initialize Station 2 library
    SNIPPETS: Dict[str, list] = {}
    
    # Parse each snippet and populate SNIPPETS
    for name, lily_code in snippets_to_parse.items():
        try:
            # Parse LilyPond → canonical data structure
            parsed = parse_lilypond_to_data(lily_code, part_name=name)
            
            # Extract events from parsed data
            if parsed and 'parts' in parsed and name in parsed['parts']:
                SNIPPETS[name] = parsed['parts'][name]
                event_count = len(SNIPPETS[name])
                print(f"  ✓ {name}: {event_count} events")
            else:
                print(f"  ⚠️  {name}: Parse failed or no events found")
                SNIPPETS[name] = []  # Empty list prevents KeyError later
                
        except Exception as e:
            print(f"  ❌ {name}: Error: {e}")
            SNIPPETS[name] = []
    
    print(f"\n  → Station 2 Library: {{len(SNIPPETS)}} snippets ready")
    
    # --- Define Score Metadata ---
    # Based on patterns from thirteenth.py, fourteenth.py
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER,
        'instrumentation': INSTRUMENTATION,
        'key_signature': {'tonic': 'g', 'mode': 'major'},  # Inferred from snippets
        'time_signature': '3/4',                              # Inferred from snippets
        'tempo': 'Andante, quarter note = 90',               # From \tempo directive
        'original_snippets': snippets_to_parse,              # For explicit \mark detection
    }
    
    # --- STATION 3: Assemble Score using Blueprint Strings ---
    print("\n[Station 3 Processing] Building score from Blueprint strings...")
    print(f"  • Layout: {{VOICE_STAVE_DEF}}")
    print(f"  • Structure: {{len(VOICE_STAVE_DATA.strip().split(';'))}} sections")
    
    # Call the Blueprint processor
    # This will:
    #   - Parse VOICE_STAVE_DATA
    #   - Execute any transformations (adding results to SNIPPETS)
    #   - Assemble final score from SNIPPETS
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
    
    print("\n" + "="*70)
    print("✅ Station 3 Blueprint Assembly Complete")
    print("="*70)
    
    return score_data


############################################################################
## STATION 4: PROGRAMMATIC COMPOSITION (Alternative to Station 3)        ##
############################################################################
# Define score structure entirely using Python code.
# This section is used IF `PROMOTE_TO_PROGRAMMATIC` is True.
#
# Based on patterns from first.py, seventh.py, tenth.py

def build_score_data_programmatic() -> Dict:
    """
    Builds score programmatically, bypassing Station 3 Blueprint.
    
    This is APPROACH 2 (ADVANCED): For algorithmic composition,
    complex transformations, or when you need full Python control.
    
    Workflow:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. Parse Station 1 snippets
    2. Apply transformations manually using Python
    3. Combine events programmatically (lists, loops, logic)
    4. Assemble final score_data structure
    
    Returns:
        dict: Canonical score_data {'metadata': {}, 'parts': {}}
    """
    
    print("\n" + "="*70)
    print("NINETYEIGHTH STUDY: Programmatic Assembly (Station 4)")
    print("="*70)

    # --- STATION 1 → Parse Snippets ---
    print("\n[Station 1 Parsing] Loading base materials...")
    
    theme_a_data = parse_lilypond_to_data(THEME_A_LILY, part_name='THEME_A')
    theme_b_data = parse_lilypond_to_data(THEME_B_LILY, part_name='THEME_B')
    bass_data = parse_lilypond_to_data(BASS_FIGURE_LILY, part_name='BASS')
    
    # Extract event lists
    theme_a_events = theme_a_data['parts']['THEME_A'] if theme_a_data and 'parts' in theme_a_data else []
    theme_b_events = theme_b_data['parts']['THEME_B'] if theme_b_data and 'parts' in theme_b_data else []
    bass_events = bass_data['parts']['BASS'] if bass_data and 'parts' in bass_data else []
    
    print(f"  ✓ THEME_A: {{len(theme_a_events)}} events")
    print(f"  ✓ THEME_B: {{len(theme_b_events)}} events")
    print(f"  ✓ BASS: {{len(bass_events)}} events")
    
    # --- STATION 4: Programmatic Logic ---
    print("\n[Station 4 Logic] Defining structure programmatically...")
    
    # Example: ABA form with repeated bass
    # (Uncomment transformation imports to use transpose_part, etc.)
    
    # For now, simple concatenation:
    melody_events = theme_a_events + theme_b_events + theme_a_events  # ABA
    bass_events_full = bass_events * 3  # Repeat bass 3 times
    
    # If transformations imported:
    # from src.transformations import transpose_part
    # from src.music_data import data_to_part, part_to_data
    # theme_a_part = data_to_part(theme_a_events, {})
    # transposed_part = transpose_part(theme_a_part, 'P4')
    # transposed_events = part_to_data(transposed_part)
    # melody_events = theme_a_events + transposed_events + theme_a_events
    
    print(f"  → Assembled melody: {{len(melody_events)}} total events")
    print(f"  → Assembled bass: {{len(bass_events_full)}} total events")
    
    # --- Define Metadata ---
    metadata = {
        'title': TITLE + " (Programmatic)",
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER + "-Prog",
        'instrumentation': INSTRUMENTATION,
        'key_signature': {'tonic': 'g', 'mode': 'major'},
        'time_signature': '3/4',
        'tempo': 'Andante, quarter note = 90',
    }

    print("\n" + "="*70)
    print("✅ Station 4 Programmatic Assembly Complete")
    print("="*70)

    # --- Return Final Score Data ---
    return {
        'metadata': metadata,
        'parts': {
            'Melody': melody_events,
            'Bass': bass_events_full,
        }
    }


# --- Additional Station 4 Functions (Optional) ---

def build_score_data_with_library() -> Dict:
    """
    Station 4 example using src/lib/ transformation libraries.
    
    Demonstrates integration with advanced music21-based tools.
    Requires uncommenting library imports at top of file.
    """
    print("\n[Station 4 + Library] Advanced programmatic composition...")
    
    # Example workflow:
    # 1. Parse base snippet
    # 2. Apply library transformation (e.g., canon_at_interval)
    # 3. Combine with original
    # 4. Return score_data
    
    # Implementation left as exercise - see eleventh_example.py for reference
    
    return {
        'metadata': {'title': TITLE},
        'parts': {'Main': []}
    }


# ============================================================================
# MAIN EXECUTION CONTROL
# ============================================================================

if __name__ == '__main__':
    # The framework automatically calls build_score_data() by default.
    # To use Station 4 instead, set PROMOTE_TO_PROGRAMMATIC = True above,
    # then manually rename build_score_data_programmatic to build_score_data.
    run_pipeline_from_file(__file__)
