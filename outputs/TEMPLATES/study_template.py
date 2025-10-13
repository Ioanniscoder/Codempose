"""
STUDY TEMPLATE: [Name] Study
=============================

This is a template for creating new study files in the Codempose framework.

Four-Station Workflow:
1. Station 1 (LilyPond): Original musical snippets in LilyPond notation
2. Station 2 (TinyNotation): Equivalent representations in TinyNotation
3. Station 3 (Shorthand): Combine voices using programmatic shorthand
4. Station 4 (Programmatic): Generate new voices via transformations

PROMOTION TOGGLES:
- PROMOTE_TO_TINYNOTATION: When True, TinyNotation becomes the dominant format
- PROMOTE_TO_PROGRAMMATIC: When True, programmatic code dominates over shorthand
"""

# ============================================================================
# PROMOTION TOGGLES
# ============================================================================

# Set to True to promote TinyNotation as the dominant format
PROMOTE_TO_TINYNOTATION = False

# Set to True to use programmatic generation instead of shorthand
PROMOTE_TO_PROGRAMMATIC = False


# ============================================================================
# IMPORTS
# ============================================================================

from lilypond_parser import parse_lilypond_to_data
from music_data import extract_data_from_part, data_to_part
from voice_documentation import register_and_document_voice
from composition_shorthand import (
    build_score_from_assignments,
    transpose_events,
    invert_events
)


# ============================================================================
# STATION 1: ORIGINAL LILYPOND SNIPPETS
# ============================================================================

# Add your LilyPond snippets here
MELODY_LILY = r"\relative c' { \time 4/4 \key c \major c4 d e f | g2 g2 | }"

HARMONY_LILY = r"\relative c { \time 4/4 \key c \major c2 g2 | c1 | }"


# ============================================================================
# STATION 2: TINYNOTATION EQUIVALENTS
# ============================================================================

# TinyNotation equivalents (can be auto-generated via promotion)
MELODY_TINY = "tinynotation: 4/4 c4 d e f g2 g2"
HARMONY_TINY = "tinynotation: 4/4 c2 G2 c1"


# ============================================================================
# STATION 3: SHORTHAND STRUCTURE
# ============================================================================

# Define how voices are arranged using shorthand
VOICE_ASSIGNMENTS = {
    'Treble': {
        'Melody': 'MELODY',
    },
    'Bass': {
        'Harmony': 'HARMONY',
    }
}


# ============================================================================
# STATION 4: PROGRAMMATIC GENERATION WITH DOCUMENTATION
# ============================================================================

def build_score_data():
    """
    MASTER CONTROLLER: Build the complete score.
    
    This function orchestrates the entire composition process:
    1. Parse original snippets
    2. Generate new voices programmatically (optional)
    3. Use shorthand to arrange voices
    4. Return complete score data with documentation
    """
    metadata = {
        'title': 'My Study Title',
        'composer': 'Your Name',
        'subtitle': 'Description',
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        
        # Station 1: Original snippets (LilyPond)
        'original_snippets': {
            'MELODY_LILY': MELODY_LILY,
            'HARMONY_LILY': HARMONY_LILY,
        },
        
        # Station 2: TinyNotation equivalents
        'tinynotation_snippets': {
            'MELODY_TINY': MELODY_TINY,
            'HARMONY_TINY': HARMONY_TINY,
        },
        
        # Station 3: Shorthand assignments
        'voice_assignments': VOICE_ASSIGNMENTS,
    }
    
    # Parse original snippets
    melody_data = parse_lilypond_to_data(MELODY_LILY, 'Melody')
    harmony_data = parse_lilypond_to_data(HARMONY_LILY, 'Harmony')
    
    melody = melody_data['parts']['Melody']
    harmony = harmony_data['parts']['Harmony']
    
    voice_lookup = {
        'MELODY': melody,
        'HARMONY': harmony,
    }
    
    # Optional: Generate programmatic voices
    # Example:
    # melody_transposed = transpose_events(melody, 7)
    # register_and_document_voice('MELODY_UP', melody_transposed, voice_lookup, metadata)
    
    # Build score using shorthand
    final_score = build_score_from_assignments(
        voice_assignments=VOICE_ASSIGNMENTS,
        voice_data=voice_lookup,
        metadata=metadata
    )
    
    return final_score


# ============================================================================
# ALTERNATIVE: FULLY PROGRAMMATIC (NO SHORTHAND)
# ============================================================================

def build_score_data_programmatic():
    """
    Alternative: Build entire score programmatically without shorthand.
    
    Set PROMOTE_TO_PROGRAMMATIC = True to use this version.
    """
    # Parse snippets
    melody_data = parse_lilypond_to_data(MELODY_LILY, 'Melody')
    harmony_data = parse_lilypond_to_data(HARMONY_LILY, 'Harmony')
    
    melody = melody_data['parts']['Melody']
    harmony = harmony_data['parts']['Harmony']
    
    # Manual assembly
    return {
        'metadata': {
            'title': 'My Study Title (Programmatic)',
            'composer': 'Your Name',
        },
        'parts': {
            'Treble': melody,
            'Bass': harmony,
        }
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    
    # Override if programmatic mode enabled
    if PROMOTE_TO_PROGRAMMATIC:
        build_score_data = build_score_data_programmatic
    
    # Run the standard pipeline (handles all output formats)
    run_pipeline_from_file(__file__)
