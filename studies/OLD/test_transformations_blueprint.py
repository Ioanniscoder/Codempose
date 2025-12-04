"""Test Study: Blueprint Strings with On-The-Fly Transformations

This study demonstrates the NEW transformation syntax in Blueprint Strings!

Features tested:
- transpose_part()
- invert_part()
- retrograde_part()
- augment_part()
- diminish_part()
- Combination with | concatenation
- Multi-staff layouts
"""

import _study_path  # Auto-path setup for study files

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Dict
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.lily_converter import events_to_lily
from src.project_template import run_pipeline_from_file


# ============================================================================
# METADATA
# ============================================================================

TITLE = "Transformation Test Study"
COMPOSER = "Blueprint Strings Framework v2.0"


# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

# Simple theme for transformation testing
THEME_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=120
    c4 d4 e4 f4 |
    g2 a2 |
    b4 a4 g4 f4 |
    e1
}
""".strip()

# Bass pattern
BASS_LILY = r"""
\relative c {
    \clef bass
    c2 g2 |
    f2 c2 |
    g2 d2 |
    c1
}
""".strip()


# ============================================================================
# STATION 2: VALIDATION & TRANSFORMED SNIPPETS
# ============================================================================
#
# TWO FORMATS AVAILABLE:
#
# 1. TINYNOTATION (for pitch verification):
#    Shows absolute pitch resolution to verify transformations are correct.
#
# 2. LILYPOND (for reuse):
#    Ready-to-use snippets for inspection and further composition.

# TinyNotation Validation Strings (Absolute Pitches)
THEME_TINY = None                 # Original theme
THEME_TRANSPOSED_TINY = None      # transpose_part(THEME, 'P5')
THEME_INVERTED_TINY = None        # invert_part(THEME, 'C4')
THEME_RETROGRADE_TINY = None      # retrograde_part(THEME)
THEME_AUGMENTED_TINY = None       # augment_part(THEME, 2.0)
THEME_DIMINISHED_TINY = None      # diminish_part(THEME, 2.0)
THEME_TRANSPOSED_M2_TINY = None   # transpose_part(THEME, 'M2')

# LilyPond Reusable Snippets
THEME_TRANSPOSED_LILY = None      # transpose_part(THEME, 'P5')
THEME_INVERTED_LILY = None        # invert_part(THEME, 'C4')
THEME_RETROGRADE_LILY = None      # retrograde_part(THEME)
THEME_AUGMENTED_LILY = None       # augment_part(THEME, 2.0)
THEME_DIMINISHED_LILY = None      # diminish_part(THEME, 2.0)
THEME_TRANSPOSED_M2_LILY = None   # transpose_part(THEME, 'M2')

# Two-staff layout: Upper melody staff, lower bass staff
VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    THEME & BASS;
    transpose_part(THEME, 'P5') & BASS;
    invert_part(THEME, 'C4') & BASS;
    retrograde_part(THEME) & BASS;
    augment_part(THEME, 2.0) & BASS;
    diminish_part(THEME, 2.0) & BASS;
    THEME | transpose_part(THEME, 'M2') & BASS
"""


# ============================================================================
# STATION 3: BUILD SCORE DATA
# ============================================================================

def build_score_data() -> Dict:
    """
    Build score using Blueprint String Framework with transformations.
    
    The framework will automatically:
    1. Parse LilyPond snippets
    2. Detect transformation syntax in VOICE_STAVE_DATA
    3. Apply transformations on-the-fly
    4. Save results to SNIPPETS dictionary for inspection
    """
    
    print("\n" + "="*70)
    print("TRANSFORMATION TEST STUDY")
    print("="*70)
    print("\n[Parsing LilyPond snippets...]")
    
    # Parse snippets
    theme_parsed = parse_lilypond_to_data(THEME_LILY, 'Melody')
    theme_events = theme_parsed['parts']['Melody']
    
    bass_parsed = parse_lilypond_to_data(BASS_LILY, 'Bass')
    bass_events = bass_parsed['parts']['Bass']
    
    print(f"✓ THEME: {len(theme_events)} events")
    print(f"✓ BASS: {len(bass_events)} events")
    
    # Build snippets library (only base snippets needed!)
    SNIPPETS = {
        'THEME': theme_events,
        'BASS': bass_events,
    }
    
    # Metadata
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'}
    }
    
    print("\n[Calling Blueprint Framework with transformation syntax...]")
    print("Expected transformations:")
    print("  • transpose_part(THEME, 'P5')")
    print("  • invert_part(THEME, 'C4')")
    print("  • retrograde_part(THEME)")
    print("  • augment_part(THEME, 2.0)")
    print("  • diminish_part(THEME, 2.0)")
    print()
    
    # Call Blueprint Framework - transformations happen here!
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
    
    # ========================================================================
    # STEP 4: CONVERT TRANSFORMED SNIPPETS TO BOTH FORMATS (Station 2!)
    # ========================================================================
    
    print("\n" + "="*70)
    print("STATION 2: POPULATING TRANSFORMED SNIPPETS")
    print("="*70)
    print("\n[Converting transformed snippets to LilyPond and TinyNotation...]")
    print("LilyPond = reusable snippets | TinyNotation = pitch verification\n")
    
    # Metadata for snippet conversion
    snippet_metadata = {
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'}
    }
    
    # Import tinynotation converter
    from lily_converter import events_to_tinynotation
    
    # Make variables global
    global THEME_TINY
    global THEME_TRANSPOSED_LILY, THEME_TRANSPOSED_TINY
    global THEME_INVERTED_LILY, THEME_INVERTED_TINY
    global THEME_RETROGRADE_LILY, THEME_RETROGRADE_TINY
    global THEME_AUGMENTED_LILY, THEME_AUGMENTED_TINY
    global THEME_DIMINISHED_LILY, THEME_DIMINISHED_TINY
    global THEME_TRANSPOSED_M2_LILY, THEME_TRANSPOSED_M2_TINY
    
    # Convert original theme
    THEME_TINY = events_to_tinynotation(theme_events, snippet_metadata)
    print(f"✓ THEME_TINY:")
    print(f"  {THEME_TINY}")
    print()
    
    # Find transformed snippets in SNIPPETS dictionary
    transformed_snippets = {}
    for key in SNIPPETS.keys():
        if key.startswith(('transpose', 'invert', 'retrograde', 'augment', 'diminish')):
            transformed_snippets[key] = SNIPPETS[key]
    
    # Convert and populate Station 2 variables
    if "transpose_part(THEME, 'P5')" in transformed_snippets:
        THEME_TRANSPOSED_LILY = events_to_lily(
            transformed_snippets["transpose_part(THEME, 'P5')"], 
            snippet_metadata
        )
        THEME_TRANSPOSED_TINY = events_to_tinynotation(
            transformed_snippets["transpose_part(THEME, 'P5')"],
            snippet_metadata
        )
        print(f"✓ THEME_TRANSPOSED_LILY (P5 up):")
        print(f"  {THEME_TRANSPOSED_LILY[:80]}...")
        print(f"✓ THEME_TRANSPOSED_TINY:")
        print(f"  {THEME_TRANSPOSED_TINY}")
        print()
    
    if "invert_part(THEME, 'C4')" in transformed_snippets:
        THEME_INVERTED_LILY = events_to_lily(
            transformed_snippets["invert_part(THEME, 'C4')"], 
            snippet_metadata
        )
        THEME_INVERTED_TINY = events_to_tinynotation(
            transformed_snippets["invert_part(THEME, 'C4')"],
            snippet_metadata
        )
        print(f"✓ THEME_INVERTED_LILY (inverted around C4):")
        print(f"  {THEME_INVERTED_LILY[:80]}...")
        print(f"✓ THEME_INVERTED_TINY:")
        print(f"  {THEME_INVERTED_TINY}")
        print()
    
    if "retrograde_part(THEME)" in transformed_snippets:
        THEME_RETROGRADE_LILY = events_to_lily(
            transformed_snippets["retrograde_part(THEME)"], 
            snippet_metadata
        )
        THEME_RETROGRADE_TINY = events_to_tinynotation(
            transformed_snippets["retrograde_part(THEME)"],
            snippet_metadata
        )
        print(f"✓ THEME_RETROGRADE_LILY (reversed):")
        print(f"  {THEME_RETROGRADE_LILY[:80]}...")
        print(f"✓ THEME_RETROGRADE_TINY:")
        print(f"  {THEME_RETROGRADE_TINY}")
        print()
    
    if "augment_part(THEME, 2.0)" in transformed_snippets:
        THEME_AUGMENTED_LILY = events_to_lily(
            transformed_snippets["augment_part(THEME, 2.0)"], 
            snippet_metadata
        )
        THEME_AUGMENTED_TINY = events_to_tinynotation(
            transformed_snippets["augment_part(THEME, 2.0)"],
            snippet_metadata
        )
        print(f"✓ THEME_AUGMENTED_LILY (2x slower):")
        print(f"  {THEME_AUGMENTED_LILY[:80]}...")
        print(f"✓ THEME_AUGMENTED_TINY:")
        print(f"  {THEME_AUGMENTED_TINY}")
        print()
    
    if "diminish_part(THEME, 2.0)" in transformed_snippets:
        THEME_DIMINISHED_LILY = events_to_lily(
            transformed_snippets["diminish_part(THEME, 2.0)"], 
            snippet_metadata
        )
        THEME_DIMINISHED_TINY = events_to_tinynotation(
            transformed_snippets["diminish_part(THEME, 2.0)"],
            snippet_metadata
        )
        print(f"✓ THEME_DIMINISHED_LILY (2x faster):")
        print(f"  {THEME_DIMINISHED_LILY[:80]}...")
        print(f"✓ THEME_DIMINISHED_TINY:")
        print(f"  {THEME_DIMINISHED_TINY}")
        print()
    
    if "transpose_part(THEME, 'M2')" in transformed_snippets:
        THEME_TRANSPOSED_M2_LILY = events_to_lily(
            transformed_snippets["transpose_part(THEME, 'M2')"], 
            snippet_metadata
        )
        THEME_TRANSPOSED_M2_TINY = events_to_tinynotation(
            transformed_snippets["transpose_part(THEME, 'M2')"],
            snippet_metadata
        )
        print(f"✓ THEME_TRANSPOSED_M2_LILY (M2 up):")
        print(f"  {THEME_TRANSPOSED_M2_LILY[:80]}...")
        print(f"✓ THEME_TRANSPOSED_M2_TINY:")
        print(f"  {THEME_TRANSPOSED_M2_TINY}")
        print()
    
    print("="*70)
    print("✅ TRANSFORMATION TEST COMPLETE")
    print("="*70)
    print(f"✓ Score assembled with {len(score_data['parts'])} staves")
    print(f"✓ {len(transformed_snippets)} transformations generated")
    print(f"✓ All transformed snippets available as LilyPond strings")
    print(f"✓ Ready for reuse in further composition!")
    print()
    
    return score_data


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    run_pipeline_from_file(__file__)
