"""Test Study: Transformed Snippets at Station 2 - Reuse Demo

This study demonstrates that transformed snippets are:
1. Generated on-the-fly during blueprint assembly
2. Converted back to LilyPond format at Station 2
3. Available for further composition and reuse

This follows the "Composer's Workspace" model where Station 2 contains
ALL snippets (original + transformed) in LilyPond format for inspection
and reuse.
"""

import _study_path

from typing import Dict
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.lily_converter import events_to_lily
from src.project_template import run_pipeline_from_file


# ============================================================================
# METADATA
# ============================================================================

TITLE = "Station 2 Snippet Reuse Demo"
COMPOSER = "Blueprint Transformations v2.0"


# ============================================================================
# STATION 1: ORIGINAL LILYPOND SNIPPETS
# ============================================================================

THEME_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    c4 d4 e4 f4 |
    g2 f2
}
""".strip()


# ============================================================================
# STATION 2: TRANSFORMED SNIPPETS (Auto-Generated)
# ============================================================================
#
# TWO FORMATS FOR DIFFERENT PURPOSES:
#
# 1. TINYNOTATION (for pitch verification):
#    Shows absolute pitch resolution (e.g., "C64" = C in octave 6, quarter note)
#    Use these to verify transformations resolved pitches correctly.
#
# 2. LILYPOND (for reuse):
#    Ready-to-use LilyPond snippets that can be:
#    - Inspected by the composer
#    - Copied for manual editing
#    - Reused in future compositions
#    - Used as input for further transformations

# TinyNotation Validation Strings (Absolute Pitches)
THEME_TINY = None            # Original theme
THEME_P5_TINY = None         # transpose_part(THEME, 'P5')
THEME_INVERTED_TINY = None   # invert_part(THEME, 'C4')
THEME_P5_INVERTED_TINY = None  # invert_part(THEME_P5, 'C4') [cascaded]

# LilyPond Reusable Snippets
THEME_P5_LILY = None         # transpose_part(THEME, 'P5')
THEME_INVERTED_LILY = None   # invert_part(THEME, 'C4')
THEME_P5_INVERTED_LILY = None  # invert_part(THEME_P5, 'C4') [cascaded]


# ============================================================================
# STATION 3: BLUEPRINT STRINGS
# ============================================================================

# First pass: Generate basic transformations
VOICE_STAVE_DEF = "Melody"

VOICE_STAVE_DATA = """
    THEME;
    transpose_part(THEME, 'P5');
    invert_part(THEME, 'C4')
"""


# ============================================================================
# STATION 4: BUILD SCORE WITH SNIPPET GENERATION
# ============================================================================

def build_score_data() -> Dict:
    """
    Build score and populate Station 2 with transformed snippets.
    
    Workflow:
    1. Parse original snippets (Station 1)
    2. Run Blueprint Framework (generates transformations)
    3. Convert transformed snippets to LilyPond (populate Station 2)
    4. Return score data
    """
    
    print("\n" + "="*70)
    print("STATION 2 SNIPPET REUSE DEMO")
    print("="*70)
    
    # Parse original snippet
    print("\n[STATION 1: Parsing original LilyPond snippets...]")
    theme_parsed = parse_lilypond_to_data(THEME_LILY, 'Melody')
    theme_events = theme_parsed['parts']['Melody']
    print(f"✓ THEME: {len(theme_events)} events")
    
    # Build snippets library
    SNIPPETS = {
        'THEME': theme_events,
    }
    
    # Metadata
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'}
    }
    
    # Run Blueprint Framework
    print("\n[STATION 3: Running Blueprint Framework...]")
    print("Transformations will be generated on-the-fly:")
    print("  • transpose_part(THEME, 'P5')")
    print("  • invert_part(THEME, 'C4')")
    print()
    
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
    
    # ========================================================================
    # STATION 2: POPULATE TRANSFORMED SNIPPETS
    # ========================================================================
    
    print("\n" + "="*70)
    print("STATION 2: GENERATING REUSABLE SNIPPETS")
    print("="*70)
    print("\nConverting transformed snippets to LilyPond format...")
    print("These will be available for inspection and reuse!\n")
    
    snippet_metadata = {
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'}
    }
    
    global THEME_TINY, THEME_P5_LILY, THEME_P5_TINY
    global THEME_INVERTED_LILY, THEME_INVERTED_TINY
    global THEME_P5_INVERTED_LILY, THEME_P5_INVERTED_TINY
    
    # Import tinynotation converter
    from lily_converter import events_to_tinynotation
    
    # Convert original theme to tinynotation
    THEME_TINY = events_to_tinynotation(theme_events, snippet_metadata)
    print("✓ THEME_TINY (pitch verification):")
    print(f"  {THEME_TINY}")
    print()
    
    # Convert transformed snippets
    if "transpose_part(THEME, 'P5')" in SNIPPETS:
        THEME_P5_LILY = events_to_lily(
            SNIPPETS["transpose_part(THEME, 'P5')"], 
            snippet_metadata
        )
        THEME_P5_TINY = events_to_tinynotation(
            SNIPPETS["transpose_part(THEME, 'P5')"],
            snippet_metadata
        )
        print("✓ THEME_P5_LILY (reusable snippet):")
        print(f"  {THEME_P5_LILY}")
        print("✓ THEME_P5_TINY (pitch verification):")
        print(f"  {THEME_P5_TINY}")
        print()
    
    if "invert_part(THEME, 'C4')" in SNIPPETS:
        THEME_INVERTED_LILY = events_to_lily(
            SNIPPETS["invert_part(THEME, 'C4')"], 
            snippet_metadata
        )
        THEME_INVERTED_TINY = events_to_tinynotation(
            SNIPPETS["invert_part(THEME, 'C4')"],
            snippet_metadata
        )
        print("✓ THEME_INVERTED_LILY (reusable snippet):")
        print(f"  {THEME_INVERTED_LILY}")
        print("✓ THEME_INVERTED_TINY (pitch verification):")
        print(f"  {THEME_INVERTED_TINY}")
        print()
    
    # ========================================================================
    # DEMONSTRATION: REUSE TRANSFORMED SNIPPET
    # ========================================================================
    
    print("=" * 70)
    print("DEMONSTRATION: REUSING TRANSFORMED SNIPPETS")
    print("=" * 70)
    print("\nNow we can use THEME_P5 as input for another transformation!")
    print("Creating: invert_part(THEME_P5, 'C4') - a CASCADED transformation\n")
    
    # Add the P5 version to SNIPPETS under a simple name
    SNIPPETS['THEME_P5'] = SNIPPETS["transpose_part(THEME, 'P5')"]
    
    # Create a new blueprint that uses the transformed snippet
    VOICE_STAVE_DEF_2 = "Melody"
    VOICE_STAVE_DATA_2 = """
        THEME_P5;
        invert_part(THEME_P5, 'C4')
    """
    
    # Run blueprint again with cascaded transformation
    score_data_2 = build_score_from_blueprint(
        VOICE_STAVE_DEF_2,
        VOICE_STAVE_DATA_2,
        SNIPPETS,
        metadata
    )
    
    # Convert the cascaded result
    if "invert_part(THEME_P5, 'C4')" in SNIPPETS:
        THEME_P5_INVERTED_LILY = events_to_lily(
            SNIPPETS["invert_part(THEME_P5, 'C4')"], 
            snippet_metadata
        )
        THEME_P5_INVERTED_TINY = events_to_tinynotation(
            SNIPPETS["invert_part(THEME_P5, 'C4')"],
            snippet_metadata
        )
        print("\n✓ THEME_P5_INVERTED_LILY (cascaded - reusable snippet):")
        print(f"  {THEME_P5_INVERTED_LILY}")
        print("✓ THEME_P5_INVERTED_TINY (cascaded - pitch verification):")
        print(f"  {THEME_P5_INVERTED_TINY}")
        print()
    
    print("=" * 70)
    print("✅ STATION 2 REUSE DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nSummary:")
    print(f"  • Original snippets: 1 (THEME)")
    print(f"  • Transformed snippets: {len([k for k in SNIPPETS if k.startswith(('transpose', 'invert'))])}")
    print(f"  • Station 2 LilyPond snippets populated: 3")
    print(f"  • Cascaded transformations: 1 (THEME_P5_INVERTED)")
    print("\n💡 KEY INSIGHT:")
    print("   Transformed snippets are now available at Station 2 in LilyPond format,")
    print("   making them a 'source of snippets' for further composition!")
    print("   You can inspect, edit, or use them as input for more transformations.")
    print()
    
    # Return the original score (not the cascaded one)
    return score_data


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    run_pipeline_from_file(__file__)
