"""Study file: Composition Shorthand Demonstration

This module demonstrates the SHORTHAND approach to composition:
- Declarative VOICE_ASSIGNMENTS structure (readable musical blueprint)
- Automatic conversion to programmatic chains
- All logic contained in one file - no external dependencies

SHORTHAND SYNTAX:
    'V1'        -> Single snippet
    'V1 + V2'   -> Chain two snippets sequentially
    'V1 * 3'    -> Repeat snippet 3 times
    'V1 + V2 * 2' -> Mixed: V1 followed by V2 repeated twice

Compare to sixth.py which uses manual programmatic chaining.
"""

# ============================================================================
# VOICE SNIPPETS (Station 1)
# ============================================================================

# Intro phrase
INTRO_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=120
    c2 e2 |
    d2 f2 |
}
""".strip()

INTRO_TINY = "c'2 e'2 d'2 f'2"

# Main theme
THEME_LILY = r"""
\relative c'' {
    g4 e4 c4 d4 |
    e2 d2 |
}
""".strip()

THEME_TINY = "g'4 e'4 c'4 d'4 e'2 d'2"

# Variation
VARIATION_LILY = r"""
\relative c'' {
    g4 f4 e4 d4 |
    c2 b2 |
}
""".strip()

VARIATION_TINY = "g'4 f'4 e'4 d'4 c'2 b2"

# Coda
CODA_LILY = r"""
\relative c'' {
    c4 b4 c4 d4 |
    c1 |
}
""".strip()

CODA_TINY = "c'4 b4 c'4 d'4 c'1"

# Bass line
BASS_LILY = r"""
\relative c {
    c2 g2 |
    f2 g2 |
}
""".strip()

BASS_TINY = "c2 G2 F2 G2"

# Harmony
HARMONY_LILY = r"""
\relative c' {
    e2 g2 |
    a2 b2 |
}
""".strip()

HARMONY_TINY = "e2 g2 a2 b2"

# Toggle for format dominance
PROMOTE_TO_TINYNOTATION = False  # LilyPond is dominant by default


# ============================================================================
# COMPOSITION STRUCTURE (Station 2 - Musical Blueprint)
# ============================================================================

# This is the SHORTHAND: declare the musical structure declaratively
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'INTRO + THEME + VARIATION + THEME + CODA',  # ABA form with intro/coda
        'Alto': 'THEME * 3 + CODA',                             # Theme repeated 3 times
    },
    'Harmony': {
        'Tenor': 'HARMONY * 2 + HARMONY',                       # Harmony repeated
        'Bass': 'BASS * 5',                                      # Bass ostinato (5 times)
    }
}


# ============================================================================
# SHORTHAND PARSER (Station 3 - Embedded Helper)
# ============================================================================

def parse_voice_assignment(expression: str, voice_lookup: dict) -> list:
    """
    Convert shorthand expression to event list.
    
    Supports: 'V1', 'V1 + V2', 'V1 * 3', 'V1 + V2 * 2'
    """
    parts = [p.strip() for p in expression.split('+')]
    result = []
    
    for part in parts:
        if '*' in part:
            voice_name, count = [x.strip() for x in part.split('*')]
            count = int(count)
            if voice_name not in voice_lookup:
                raise ValueError(f"Voice '{voice_name}' not found. Available: {list(voice_lookup.keys())}")
            result.extend(voice_lookup[voice_name] * count)
        else:
            if part not in voice_lookup:
                raise ValueError(f"Voice '{part}' not found. Available: {list(voice_lookup.keys())}")
            result.extend(voice_lookup[part])
    
    return result


# ============================================================================
# COMPOSITION FUNCTION (Station 3 - Auto-generated from Shorthand)
# ============================================================================

def build_score_data():
    """
    Build score from VOICE_ASSIGNMENTS shorthand.
    
    This function demonstrates the SHORTHAND workflow:
    1. Parse all voice snippets independently
    2. Build lookup table mapping names to event lists
    3. Use parse_voice_assignment() to interpret shorthand expressions
    4. Auto-generate score_data structure
    
    Returns:
        dict: Complete score_data ready for engraving
    """
    from lilypond_parser import parse_lilypond_to_data
    
    # Parse all voice snippets independently
    intro_data = parse_lilypond_to_data(INTRO_LILY, part_name='Intro')
    theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
    variation_data = parse_lilypond_to_data(VARIATION_LILY, part_name='Variation')
    coda_data = parse_lilypond_to_data(CODA_LILY, part_name='Coda')
    bass_data = parse_lilypond_to_data(BASS_LILY, part_name='Bass')
    harmony_data = parse_lilypond_to_data(HARMONY_LILY, part_name='Harmony')
    
    # Build voice lookup table
    voice_lookup = {
        'INTRO': intro_data['parts']['Intro'],
        'THEME': theme_data['parts']['Theme'],
        'VARIATION': variation_data['parts']['Variation'],
        'CODA': coda_data['parts']['Coda'],
        'BASS': bass_data['parts']['Bass'],
        'HARMONY': harmony_data['parts']['Harmony'],
    }
    
    # Get metadata from first voice
    metadata = intro_data['metadata']
    
    # Build original snippets documentation for .ly file comments
    original_snippets = f"""COMPOSITION STRUCTURE (from VOICE_ASSIGNMENTS):

Melody Staff:
  Soprano: {VOICE_ASSIGNMENTS['Melody']['Soprano']}
  Alto: {VOICE_ASSIGNMENTS['Melody']['Alto']}

Harmony Staff:
  Tenor: {VOICE_ASSIGNMENTS['Harmony']['Tenor']}
  Bass: {VOICE_ASSIGNMENTS['Harmony']['Bass']}

VOICE SNIPPETS:

INTRO:
LILYPOND FORMAT:
{INTRO_LILY}
TINYNOTATION FORMAT:
{INTRO_TINY}

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

CODA:
LILYPOND FORMAT:
{CODA_LILY}
TINYNOTATION FORMAT:
{CODA_TINY}

BASS:
LILYPOND FORMAT:
{BASS_LILY}
TINYNOTATION FORMAT:
{BASS_TINY}

HARMONY:
LILYPOND FORMAT:
{HARMONY_LILY}
TINYNOTATION FORMAT:
{HARMONY_TINY}"""
    
    # Auto-generate parts from VOICE_ASSIGNMENTS shorthand
    parts = {}
    for staff_name, voices in VOICE_ASSIGNMENTS.items():
        parts[staff_name] = {}
        for voice_name, expression in voices.items():
            # Parse shorthand expression into event list
            parts[staff_name][voice_name] = parse_voice_assignment(expression, voice_lookup)
    
    # Construct complete score_data
    score_data = {
        'metadata': {
            'title': 'Seventh Study - Shorthand Composition (ABA Form)',
            'time_signature': metadata.get('time_signature', '4/4'),
            'key_signature': metadata.get('key_signature', {'tonic': 'c', 'mode': 'major'}),
            'tempo': metadata.get('tempo', {'beat_duration': 4, 'bpm': 120}),
            'composer': 'Codempose',
            'original_input': original_snippets,
        },
        'parts': parts
    }
    
    return score_data


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
