"""
TENTH STUDY: Complete Four-Station Documentation Feedback Loop
================================================================

This study demonstrates the COMPLETE circular workflow where programmatic
voices are generated, documented, and then REUSED in shorthand expressions.

Four-Station Workflow:
1. Station 1 (LilyPond): Original musical snippets in LilyPond notation
2. Station 2 (TinyNotation): Equivalent representations in TinyNotation
3. Station 3 (Shorthand): Combine voices using programmatic shorthand
4. Station 4 (Programmatic): Generate new voices via transformations

PROMOTION TOGGLES:
- PROMOTE_TO_TINYNOTATION: When True, TinyNotation becomes the dominant format
- PROMOTE_TO_PROGRAMMATIC: When True, programmatic code dominates over shorthand

The generated documentation shows:
- Original snippets (both LilyPond AND TinyNotation)
- Shorthand expressions combining original + generated voices
- Programmatic voices as reusable snippets
- Complete feedback loop: Generated → Documented → Reusable
"""

# ============================================================================
# PROMOTION TOGGLES
# ============================================================================

# Set to True to promote TinyNotation as the dominant format
PROMOTE_TO_TINYNOTATION = False  # Will be toggled after first run

# Set to True to use programmatic generation instead of shorthand
PROMOTE_TO_PROGRAMMATIC = False  # Will be toggled after reviewing generated code


# ============================================================================
# IMPORTS
# ============================================================================

from lilypond_parser import parse_lilypond_to_data
from lily_to_tiny import lilypond_to_tinynotation
from music_data import extract_data_from_part, data_to_part
from second import transpose_events, invert_events
from voice_documentation import register_and_document_voice
from composition_shorthand import build_score_from_assignments


# ============================================================================
# STATION 1: ORIGINAL LILYPOND SNIPPETS
# ============================================================================

SOPRANO_THEME_LILY = r"\relative c'' { \time 4/4 \key c \major e4 d8 c8 b4 a4 | g2 a2 | }"

ALTO_THEME_LILY = r"\relative c' { \time 4/4 \key c \major c4 b8 a8 g4 f4 | e2 f2 | }"

BASS_PATTERN_LILY = r"\relative c { \time 4/4 \key c \major c2 g2 | f2 c2 | }"


# ============================================================================
# STATION 2: TINYNOTATION EQUIVALENTS
# ============================================================================

# Generated from LilyPond snippets - will be populated by promotion system
SOPRANO_THEME_TINY = "tinynotation: 4/4 e'4 d'8 c'8 b4 a4 g2 a2"
ALTO_THEME_TINY = "tinynotation: 4/4 c'4 b8 a8 g4 f4 e2 f2"
BASS_PATTERN_TINY = "tinynotation: 4/4 c2 G2 F2 C2"


# ============================================================================
# STATION 3: SHORTHAND STRUCTURE
# ============================================================================

# This demonstrates the COMPLETE LOOP:
# 1. Original snippets (Station 1)
# 2. Programmatic generation creates new voices (Station 4)
# 3. Shorthand REUSES both original AND generated voices (Station 3)

VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'SOPRANO_THEME + ALTO_GENERATED',       # Mix Station 1 + Station 4
        'Alto': 'ALTO_GENERATED * 2',                      # Repeat generated voice
    },
    'Harmony': {
        'Tenor': 'TENOR_GENERATED + transpose(BASS_PATTERN, 12)',  # Generated + transformed original
        'Bass': 'BASS_PATTERN + BASS_GENERATED',           # Original + generated
    }
}


# ============================================================================
# STATION 4: PROGRAMMATIC GENERATION WITH DOCUMENTATION
# ============================================================================

def build_score_data():
    """
    MASTER CONTROLLER: Hybrid composition demonstrating the complete workflow.
    
    Flow:
    1. Station 1: Parse original LilyPond snippets
    2. Station 4: Generate new voices programmatically + DOCUMENT them
    3. Station 3: Use SHORTHAND to arrange BOTH original AND generated voices
    4. Output: Complete documentation showing all stations + formats
    """
    metadata = {
        'title': 'Tenth Study: Complete Four-Station Workflow',
        'composer': 'Codempose Framework',
        'subtitle': 'Stations 1→4→3 with Shorthand Reuse',
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        
        # Station 1: Original snippets (LilyPond)
        'original_snippets': {
            'SOPRANO_THEME_LILY': SOPRANO_THEME_LILY,
            'ALTO_THEME_LILY': ALTO_THEME_LILY,
            'BASS_PATTERN_LILY': BASS_PATTERN_LILY,
        },
        
        # Station 2: TinyNotation equivalents
        'tinynotation_snippets': {
            'SOPRANO_THEME_TINY': SOPRANO_THEME_TINY,
            'ALTO_THEME_TINY': ALTO_THEME_TINY,
            'BASS_PATTERN_TINY': BASS_PATTERN_TINY,
        },
        
        # Station 3: Shorthand assignments (showing REUSE of programmatic voices)
        'voice_assignments': VOICE_ASSIGNMENTS,
    }
    
    print("\n" + "="*70)
    print("TENTH STUDY: Complete Four-Station Workflow")
    print("="*70)
    
    # === STATION 1: Parse original snippets ===
    print("\n[Station 1] Parsing original LilyPond snippets...")
    soprano_data = parse_lilypond_to_data(SOPRANO_THEME_LILY, 'Soprano')
    alto_theme_data = parse_lilypond_to_data(ALTO_THEME_LILY, 'AltoTheme')
    bass_pattern_data = parse_lilypond_to_data(BASS_PATTERN_LILY, 'BassPattern')
    
    soprano_theme = soprano_data['parts']['Soprano']
    alto_theme = alto_theme_data['parts']['AltoTheme']
    bass_pattern = bass_pattern_data['parts']['BassPattern']
    
    voice_lookup = {
        'SOPRANO_THEME': soprano_theme,
        'ALTO_THEME': alto_theme,
        'BASS_PATTERN': bass_pattern,
    }
    print(f"  ✓ Parsed {len(voice_lookup)} original snippets")
    
    # === STATION 4: Generate programmatically + DOCUMENT ===
    print("\n[Station 4] Generating programmatic voices...")
    
    # Alto: transpose soprano down a fifth
    alto_generated = transpose_events(soprano_theme, -7)
    register_and_document_voice('ALTO_GENERATED', alto_generated, voice_lookup, metadata)
    print(f"  ✓ Generated ALTO_GENERATED (transpose -7)")
    
    # Tenor: invert the alto theme
    tenor_generated = invert_events(alto_theme, 'c4')
    register_and_document_voice('TENOR_GENERATED', tenor_generated, voice_lookup, metadata)
    print(f"  ✓ Generated TENOR_GENERATED (invert around c4)")
    
    # Bass: transpose tenor down an octave
    bass_generated = transpose_events(tenor_generated, -12)
    register_and_document_voice('BASS_GENERATED', bass_generated, voice_lookup, metadata)
    print(f"  ✓ Generated BASS_GENERATED (transpose -12)")
    
    # === STATION 3: Use SHORTHAND to arrange ALL voices ===
    print("\n[Station 3] Building final structure with SHORTHAND...")
    print("  Using VOICE_ASSIGNMENTS to combine:")
    print("    - Original snippets (Station 1)")
    print("    - Programmatic voices (Station 4)")
    
    # Build complete score using shorthand - this REUSES the programmatic voices!
    final_score = build_score_from_assignments(
        voice_assignments=VOICE_ASSIGNMENTS,
        voice_data=voice_lookup,
        metadata=metadata
    )
    
    print(f"  ✓ Built score with shorthand expressions:")
    for part_name, voices in final_score['parts'].items():
        if isinstance(voices, dict):
            for voice_name, events in voices.items():
                print(f"    {part_name}.{voice_name}: {len(events)} events")
    
    print("\n" + "="*70)
    print("✅ Complete workflow demonstrated:")
    print("   Station 1: Parsed LilyPond snippets")
    print("   Station 2: TinyNotation equivalents available")
    print("   Station 4: Generated & documented new voices")
    print("   Station 3: Arranged BOTH with shorthand")
    print("   Check outputs/tenth.ly for complete documentation!")
    print("="*70)
    
    return final_score


# ============================================================================
# ALTERNATIVE: FULLY PROGRAMMATIC (NO SHORTHAND)
# ============================================================================

def build_score_data_programmatic():
    """
    Alternative implementation: Build entire score programmatically.
    
    This bypasses the shorthand system entirely, giving you complete
    control over every detail. Uncomment in main to use this version.
    
    Set PROMOTE_TO_PROGRAMMATIC = True to enable this version.
    """
    print("\n🔧 PROGRAMMATIC MODE: Building without shorthand")
    
    # Parse original snippets
    soprano_data = parse_lilypond_to_data(SOPRANO_THEME_LILY, 'Soprano')
    alto_theme_data = parse_lilypond_to_data(ALTO_THEME_LILY, 'AltoTheme')
    bass_pattern_data = parse_lilypond_to_data(BASS_PATTERN_LILY, 'BassPattern')
    
    soprano_theme = soprano_data['parts']['Soprano']
    alto_theme = alto_theme_data['parts']['AltoTheme']
    bass_pattern = bass_pattern_data['parts']['BassPattern']
    
    # Generate voices
    alto_generated = transpose_events(soprano_theme, -7)
    tenor_generated = invert_events(alto_theme, 'c4')
    bass_generated = transpose_events(tenor_generated, -12)
    
    # Manual assembly (equivalent to shorthand expressions)
    soprano_voice = soprano_theme + alto_generated
    alto_voice = alto_generated * 2
    tenor_voice = tenor_generated + transpose_events(bass_pattern, 12)
    bass_voice = bass_pattern + bass_generated
    
    return {
        'metadata': {
            'title': 'Tenth Study: Programmatic Mode',
            'composer': 'Codempose Framework',
        },
        'parts': {
            'Melody': {
                'Soprano': soprano_voice,
                'Alto': alto_voice,
            },
            'Harmony': {
                'Tenor': tenor_voice,
                'Bass': bass_voice,
            }
        }
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    
    # Override build_score_data if programmatic mode is enabled
    if PROMOTE_TO_PROGRAMMATIC:
        print("\n🔄 PROMOTION: Using programmatic mode")
        build_score_data = build_score_data_programmatic
    
    print("\n💡 Key Features:")
    print("  1. Four-station workflow: LilyPond → TinyNotation → Shorthand → Programmatic")
    print("  2. Programmatic voices are DOCUMENTED and REUSABLE")
    print("  3. Shorthand expressions combine original + generated voices")
    print("  4. Complete feedback loop closes the creative cycle")
    print("  5. MusicXML export for MuseScore compatibility")
    print("\n🎼 Documentation shows both LilyPond AND TinyNotation formats!\n")
    
    # Run the standard pipeline (handles LilyPond, MusicXML, promotion)
    run_pipeline_from_file(__file__)
