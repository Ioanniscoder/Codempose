"""Fourteenth study file - SATB Hymn Demonstration.

Showcases the Multi-Voice Blueprint String Framework with four-part harmony.
Demonstrates polyphonic (multi-voice) staves: Soprano and Alto share the upper
staff (treble clef), while Tenor and Bass share the lower staff (bass clef).

This file follows the four-station composer-first workflow:
  Station 1: LilyPond Input (SOPRANO_*, ALTO_*, TENOR_*, BASS_*)
  Station 2: TinyNotation Validation (automatic real-time feedback)
  Station 3: Blueprint Strings (multi-voice layout and content)
  Station 4: Custom Tools (none needed - using standard library)
"""

import _study_path  # Auto-path setup for study files
from typing import Dict
from lilypond_parser import parse_lilypond_to_data
from score_builder import build_score_from_blueprint


# ============================================================================
# METADATA
# ============================================================================

TITLE = "SATB Hymn Fragment"
COMPOSER = "Codempose Multi-Voice Demo"


# ============================================================================
# STATION 1: COMPOSING INPUT (LilyPond Snippets)
# ============================================================================
#
# Four-part hymn in G major, 4/4 time.
# Two phrases demonstrating SATB texture.

# Phrase A (4 measures)
SOPRANO_PHRASE_A = r"\relative c'' { \time 4/4 \key g \major g4 g a b | c2 b2 | a4 g a b | g2. r4 }"
ALTO_PHRASE_A = r"\relative c' { \time 4/4 \key g \major d4 d d d | e2 d2 | d4 d d d | d2. r4 }"
TENOR_PHRASE_A = r"\relative c' { \time 4/4 \key g \major b4 b c d | c2 g2 | fis4 g fis g | b2. r4 }"
BASS_PHRASE_A = r"\relative c { \time 4/4 \key g \major g4 g fis g | c,2 g'2 | d4 b d g | g2. r4 }"

# Phrase B (4 measures)
SOPRANO_PHRASE_B = r"\relative c'' { b4 b c d | d2 c2 | b4 a g fis | g1 }"
ALTO_PHRASE_B = r"\relative c' { d4 d e fis | g2 g2 | g4 fis e d | d1 }"
TENOR_PHRASE_B = r"\relative c' { g4 g g a | b2 e2 | d4 d b a | b1 }"
BASS_PHRASE_B = r"\relative c { g4 g c d | g2 c,2 | d4 d d d | g,1 }"


# ============================================================================
# STATION 2: VALIDATING INPUT (TinyNotation + Generated Placeholders)
# ============================================================================
#
# Real-time validation happens during build_score_data() execution.
# The console will show:
#   - LilyPond → TinyNotation conversion for each voice
#   - Event counts
#   - Warnings if any parsing issues occur


# ============================================================================
# STATION 3: STRUCTURING INPUT (Blueprint Strings)
# ============================================================================
#
# Multi-voice blueprint syntax:
#   - Use parentheses to group voices: (Voice1, Voice2)
#   - Comma separates voices within a staff
#   - Ampersand separates staves
#
# Layout: Two staves, each with two voices
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"

# Content: Two phrases (sections)
# Each section has four voice parts (Soprano, Alto on staff 1; Tenor, Bass on staff 2)
VOICE_STAVE_DATA = """
    SOPRANO_A, ALTO_A & TENOR_A, BASS_A;
    SOPRANO_B, ALTO_B & TENOR_B, BASS_B
"""


# ============================================================================
# STATION 4: PROGRAMMATIC CONTEXT (Custom Tools)
# ============================================================================
#
# No custom transformation functions needed for this study.
# We're showcasing the multi-voice capability, not transformations.


# ============================================================================
# PROCESSING ENGINE
# ============================================================================

def build_score_data() -> Dict[str, Dict]:
    """Build SATB score using Multi-Voice Blueprint String Framework.
    
    Workflow:
    1. Parse all 8 voice snippets (4 voices × 2 phrases) with lilypond_parser
    2. Build SNIPPETS library with all voice parts
    3. Call build_score_from_blueprint() with multi-voice layout
    4. Framework creates multi_voice_section events
    5. Return canonical score_data for engraving
    """
    
    print("\n" + "="*70)
    print("FOURTEENTH STUDY: SATB HYMN DEMONSTRATION")
    print("="*70)
    print("\n[Parsing voice parts...]")
    
    # Parse Phrase A (all 4 voices)
    print("  Parsing Phrase A...")
    sop_a_parsed = parse_lilypond_to_data(SOPRANO_PHRASE_A, 'Soprano')
    sop_a = sop_a_parsed['parts']['Soprano']
    
    alt_a_parsed = parse_lilypond_to_data(ALTO_PHRASE_A, 'Alto')
    alt_a = alt_a_parsed['parts']['Alto']
    
    ten_a_parsed = parse_lilypond_to_data(TENOR_PHRASE_A, 'Tenor')
    ten_a = ten_a_parsed['parts']['Tenor']
    
    bas_a_parsed = parse_lilypond_to_data(BASS_PHRASE_A, 'Bass')
    bas_a = bas_a_parsed['parts']['Bass']
    
    # Parse Phrase B (all 4 voices)
    print("  Parsing Phrase B...")
    sop_b_parsed = parse_lilypond_to_data(SOPRANO_PHRASE_B, 'Soprano')
    sop_b = sop_b_parsed['parts']['Soprano']
    
    alt_b_parsed = parse_lilypond_to_data(ALTO_PHRASE_B, 'Alto')
    alt_b = alt_b_parsed['parts']['Alto']
    
    ten_b_parsed = parse_lilypond_to_data(TENOR_PHRASE_B, 'Tenor')
    ten_b = ten_b_parsed['parts']['Tenor']
    
    bas_b_parsed = parse_lilypond_to_data(BASS_PHRASE_B, 'Bass')
    bas_b = bas_b_parsed['parts']['Bass']
    
    print("✓ All voice parts parsed successfully\n")
    
    # Real-time validation output
    print("[Real-time Validation]")
    print("  Soprano A:", sop_a_parsed['metadata'].get('tinynotation_inspector', 'N/A'))
    print("  Alto A:   ", alt_a_parsed['metadata'].get('tinynotation_inspector', 'N/A'))
    print("  Tenor A:  ", ten_a_parsed['metadata'].get('tinynotation_inspector', 'N/A'))
    print("  Bass A:   ", bas_a_parsed['metadata'].get('tinynotation_inspector', 'N/A'))
    print()
    
    # Build snippet library (function-scoped, internal to processing engine)
    SNIPPETS = {
        'SOPRANO_A': sop_a,
        'ALTO_A': alt_a,
        'TENOR_A': ten_a,
        'BASS_A': bas_a,
        'SOPRANO_B': sop_b,
        'ALTO_B': alt_b,
        'TENOR_B': ten_b,
        'BASS_B': bas_b,
    }
    
    # Metadata
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'time_signature': '4/4',
        'key_signature': {'tonic': 'g', 'mode': 'major'}
    }
    
    # Call Blueprint Framework with multi-voice layout
    print("[Calling Blueprint Framework with multi-voice layout...]")
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
    
    print("\n" + "="*70)
    print("SATB SCORE ASSEMBLY COMPLETE")
    print("="*70)
    print(f"✓ {len(score_data['parts'])} staves created")
    print(f"✓ Multi-voice polyphonic structure")
    print(f"✓ Ready for engraving\n")
    
    return score_data


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ['build_score_data', 'TITLE', 'COMPOSER']


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)

