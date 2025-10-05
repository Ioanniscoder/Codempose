"""
Test file for shorthand to programmatic promotion.

This demonstrates the PROMOTE_TO_PROGRAMMATIC toggle workflow.
"""

from lilypond_parser import parse_lilypond_to_data
from composition_shorthand import build_score_from_assignments, validate_voice_assignments

# Toggle for programmatic dominance (set True to generate programmatic code)
PROMOTE_TO_PROGRAMMATIC = True  # Set to True to trigger promotion

# ============================================================================
# MUSICAL SNIPPETS
# ============================================================================

THEME_LILY = r"""
\relative c' {
    c4 d e f |
    g2 e2 |
}
"""

VARIATION_LILY = r"""
\relative c' {
    e4 f g a |
    b2 g2 |
}
"""

BASS_LILY = r"""
\relative c {
    c2 g2 |
    f2 c2 |
}
"""

# ============================================================================
# VOICE ASSIGNMENTS (Shorthand)
# ============================================================================

VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'THEME + transpose(THEME, 7)',
        'Alto': 'VARIATION + retrograde(VARIATION)',
    },
    'Harmony': {
        'Bass': 'BASS * 4',
    }
}

# ============================================================================
# PROGRAMMATIC VOICE GENERATION (auto-generated from VOICE_ASSIGNMENTS)
# ============================================================================
# Toggle: PROMOTE_TO_PROGRAMMATIC = True to use this instead of shorthand

PROGRAMMATIC_VOICE_GENERATION = '''
def build_score_data_programmatic():
    """
    Auto-generated programmatic version of VOICE_ASSIGNMENTS.
    
    This code was generated from the shorthand and can be modified.
    Set PROMOTE_TO_PROGRAMMATIC = True to use this version.
    """
    from lilypond_parser import parse_lilypond_to_data
    from composition_shorthand import transpose_events, invert_events, retrograde_events
    
    # Parse all voice snippets (add your snippet parsing here)
    # Example:
    # theme_data = parse_lilypond_to_data(THEME_LILY, part_name="Theme")
    # voice_lookup = {"THEME": theme_data["parts"]["Theme"]}
    
    voice_lookup = {}  # TODO: Add your snippet parsing
    
    # Melody Staff
    
    # Soprano: THEME + transpose(THEME, 7)
    soprano_events = (
        voice_lookup["THEME"] +
        transpose_events(voice_lookup["THEME"], 7)
    )
    
    # Alto: VARIATION + retrograde(VARIATION)
    alto_events = (
        voice_lookup["VARIATION"] +
        retrograde_events(voice_lookup["VARIATION"])
    )
    
    # Harmony Staff
    
    # Bass: BASS * 4
    bass_events = voice_lookup["BASS"] * 4
    
    # Assemble final score_data
    score_data = {
        "metadata": {
            "title": "Your Title",  # TODO: Set your title
            "composer": "Your Name",  # TODO: Set your composer
        },
        "parts": {
            "Melody": {
                "Soprano": soprano_events,
                "Alto": alto_events,
            },
            "Harmony": {
                "Bass": bass_events,
            },
        }
    }
    
    return score_data
'''


# ============================================================================
# BUILD FUNCTION
# ============================================================================

def build_score_data():
    """Build score from VOICE_ASSIGNMENTS shorthand."""
    
    # Parse snippets
    theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
    variation_data = parse_lilypond_to_data(VARIATION_LILY, part_name='Variation')
    bass_data = parse_lilypond_to_data(BASS_LILY, part_name='Bass')
    
    # Build voice lookup
    voice_lookup = {
        'THEME': theme_data['parts']['Theme'],
        'VARIATION': variation_data['parts']['Variation'],
        'BASS': bass_data['parts']['Bass'],
    }
    
    # Validate
    errors = validate_voice_assignments(VOICE_ASSIGNMENTS, voice_lookup.keys())
    if errors:
        raise ValueError(f"Voice assignment errors: {errors}")
    
    # Build from shorthand
    return build_score_from_assignments(
        voice_assignments=VOICE_ASSIGNMENTS,
        voice_data=voice_lookup,
        metadata={'title': 'Test Promotion'}
    )


if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
