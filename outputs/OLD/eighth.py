"""Study file: Advanced Composition Shorthand with Transformations

This module demonstrates the ENHANCED shorthand approach:
- Declarative VOICE_ASSIGNMENTS structure
- Musical transformations (transpose, invert, retrograde)
- Pre-validation of voice assignments
- Uses formalized composition_shorthand.py module

ENHANCED SYNTAX:
    'THEME'                     -> Single snippet
    'THEME * 3'                 -> Repeat 3 times
    'THEME + VARIATION'         -> Chain snippets
    'transpose(THEME, 5)'       -> Transpose up 5 semitones (P4)
    'transpose(THEME, 7)'       -> Transpose up 7 semitones (P5)
    'invert(THEME)'             -> Melodic inversion
    'retrograde(THEME)'         -> Reverse (play backwards)
    'THEME + transpose(THEME, 7) + invert(THEME)'  -> Complex combinations

This demonstrates algorithmic composition through declarative transformation!
"""

# ============================================================================
# VOICE SNIPPETS (Station 1)
# ============================================================================

# Main theme - simple ascending pattern
THEME_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=120
    c4 d4 e4 f4 |
    g2 e2 |
}
""".strip()

THEME_TINY = "c'4 d'4 e'4 f'4 g'2 e'2"

# Variation - descending pattern
VARIATION_LILY = r"""
\relative c'' {
    g4 f4 e4 d4 |
    c2 e2 |
}
""".strip()

VARIATION_TINY = "g'4 f'4 e'4 d'4 c'2 e'2"

# Bass pattern
BASS_LILY = r"""
\relative c {
    c2 g2 |
    f2 g2 |
}
""".strip()

BASS_TINY = "c2 G2 F2 G2"

# Toggle for format dominance
PROMOTE_TO_TINYNOTATION = False  # LilyPond is dominant by default


# ============================================================================
# COMPOSITION STRUCTURE (Station 2 - Musical Blueprint with Transformations)
# ============================================================================

# This demonstrates the POWER of the shorthand with transformations!
# The musical structure is clear, concise, and uses algorithmic techniques.

VOICE_ASSIGNMENTS = {
    'Melody': {
        # Original theme, transposed up P5, inverted, then back to original
        'Soprano': 'THEME + transpose(THEME, 7) + invert(THEME) + THEME',
        
        # Retrograde (backwards) then forward variation
        'Alto': 'retrograde(VARIATION) + VARIATION',
    },
    'Harmony': {
        # Transposed bass (up P4) then original
        'Tenor': 'transpose(BASS, 5) + BASS',
        
        # Bass ostinato (repeated 4 times)
        'Bass': 'BASS * 4',
    }
}


# ============================================================================
# COMPOSITION FUNCTION (Station 3 - Uses Formalized Module)
# ============================================================================

def build_score_data():
    """
    Build score from VOICE_ASSIGNMENTS using formalized composition_shorthand module.
    
    This demonstrates:
    1. Pre-validation of voice assignments
    2. Use of transformation functions
    3. Automatic score generation from declarative structure
    
    Returns:
        dict: Complete score_data ready for engraving
    """
    from lilypond_parser import parse_lilypond_to_data
    from composition_shorthand import (
        build_score_from_assignments,
        validate_voice_assignments,
    )
    
    # Parse all voice snippets independently
    theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
    variation_data = parse_lilypond_to_data(VARIATION_LILY, part_name='Variation')
    bass_data = parse_lilypond_to_data(BASS_LILY, part_name='Bass')
    
    # Build voice lookup table
    voice_lookup = {
        'THEME': theme_data['parts']['Theme'],
        'VARIATION': variation_data['parts']['Variation'],
        'BASS': bass_data['parts']['Bass'],
    }
    
    # PRE-VALIDATION: Check VOICE_ASSIGNMENTS before processing
    print("\n🔍 Validating VOICE_ASSIGNMENTS...")
    errors = validate_voice_assignments(VOICE_ASSIGNMENTS, list(voice_lookup.keys()))
    
    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  • {error}")
        raise ValueError("Invalid VOICE_ASSIGNMENTS - fix errors above")
    else:
        print("✅ Validation passed - all voice references are valid")
    
    # Get metadata from first voice
    metadata = theme_data['metadata']
    
    # Build original snippets documentation for .ly file comments
    original_snippets = f"""COMPOSITION STRUCTURE (Enhanced Shorthand with Transformations):

Melody Staff:
  Soprano: {VOICE_ASSIGNMENTS['Melody']['Soprano']}
  Alto: {VOICE_ASSIGNMENTS['Melody']['Alto']}

Harmony Staff:
  Tenor: {VOICE_ASSIGNMENTS['Harmony']['Tenor']}
  Bass: {VOICE_ASSIGNMENTS['Harmony']['Bass']}

TRANSFORMATIONS USED:
  - transpose(V, N) = Transpose voice V up N semitones
  - invert(V) = Melodic inversion of voice V around C4
  - retrograde(V) = Reverse voice V (play backwards)

VOICE SNIPPETS:

THEME:
LILYPOND FORMAT:
{THEME_LILY}
TINYNOTATION FORMAT:
{THEME_TINY}

VARIATION:
LILYPOND FORMAT:
{VARIATION_LILY}
TINYNOTATION FORMAT:
{VARIATION_TINY}

BASS:
LILYPOND FORMAT:
{BASS_LILY}
TINYNOTATION FORMAT:
{BASS_TINY}"""
    
    # Auto-generate score_data using formalized module
    score_data = build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
    
    # Add metadata
    score_data['metadata'] = {
        'title': 'Eighth Study - Algorithmic Composition (Transformations)',
        'time_signature': metadata.get('time_signature', '4/4'),
        'key_signature': metadata.get('key_signature', {'tonic': 'c', 'mode': 'major'}),
        'tempo': metadata.get('tempo', {'beat_duration': 4, 'bpm': 120}),
        'composer': 'Codempose',
        'original_input': original_snippets,
    }
    
    return score_data


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
