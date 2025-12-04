"""Test Study: Harmonic Intelligence with Hybrid Suffix Model

This study demonstrates the NEW HYBRID SUFFIX MODEL for transformations:

═══════════════════════════════════════════════════════════════════════════════
TRANSFORMATION SYNTAX GUIDE
═══════════════════════════════════════════════════════════════════════════════

1. SINGLE-PART TRANSFORMATIONS (No suffix needed - backward compatible):
   
   transpose_part(MELODY, 'P5')      ← Works! Auto-assigns .id = 'melody'
   invert_part(THEME, 'C4')          ← Works! Auto-assigns .id = 'melody'
   retrograde_part(BASS)             ← Works! Auto-assigns .id = 'melody'
   
   These can optionally use suffix if desired:
   transpose_part(MELODY, 'P5'):melody    ← Also works!

2. MULTI-PART TRANSFORMATIONS (Suffix REQUIRED):
   
   harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody     ← Part 1 (melody)
   harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony    ← Part 2 (bass)
   
   Without suffix → ERROR:
   harmonize_part(MELODY, 'I-IV-V-I', 'C')  ← ❌ "Multi-part requires suffix"

3. CACHING & EFFICIENCY:
   
   The transformation runs ONCE (on first call with any suffix).
   All parts are cached with their IDs.
   Subsequent calls with same base are lookups (instant).
   
   Example:
   harmonize_part(THEME, 'I-V-I'):melody     ← Runs transformation, caches both parts
   harmonize_part(THEME, 'I-V-I'):harmony    ← Instant lookup, no re-execution

4. AVAILABLE PART IDS:
   
   Single-part transformations:
   - :melody (auto-assigned)
   
   harmonize_part():
   - :melody (original melody with analysis)
   - :harmony (generated bass line)

═══════════════════════════════════════════════════════════════════════════════

Features demonstrated in this study:
- Harmonic intelligence integration (harmonize_part)
- Auto-generated bass lines from chord progressions
- Hybrid suffix model (backward compatible + explicit multi-part)
- Promotion toggle for programmatic mode (Station 4)
- Station 2 population with both TinyNotation and LilyPond
"""

import _study_path

from typing import Dict
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.music_data import data_to_part, extract_data_from_part
from src.lily_converter import events_to_lily, events_to_tinynotation
from src.project_template import run_pipeline_from_file


# ============================================================================
# METADATA
# ============================================================================

TITLE = "Harmonic Intelligence Demo"
COMPOSER = "Blueprint Transformations v3.0"


# ============================================================================
# PROMOTION TOGGLE
# ============================================================================

PROMOTE_TO_STATION4 = False  # Set True for programmatic mode

# When False: Use Stations 1-3 (declarative composition with Blueprint Strings)
# When True: Station 4 becomes active (full programmatic mode with Station 1 access)


# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

MELODY_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=108
    c4 d4 e4 f4 |
    g2 e2 |
    f4 e4 d4 c4 |
    c1
}
""".strip()


# ============================================================================
# STATION 2: VALIDATION & GENERATED INPUT
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

# Original melody
MELODY_TINY = None

# Harmonized (auto-generated via harmonize_part)
MELODY_HARMONIZED_MELODY_LILY = None
MELODY_HARMONIZED_BASS_LILY = None
MELODY_HARMONIZED_MELODY_TINY = None
MELODY_HARMONIZED_BASS_TINY = None

# Repeated melody
MELODY_REPEATED_LILY = None
MELODY_REPEATED_TINY = None


# ============================================================================
# STATION 3: BLUEPRINT STRINGS
# ============================================================================

# Demo 1: Single-staff showing repeat operator
# Demo 2: Multi-staff manual harmonization (showing the output can be used)

# For auto-harmonization demo, we'll use programmatic mode (Station 4)
# because harmonize_part() returns a Score (2 parts), which needs
# explicit staff mapping in Blueprint Strings.

VOICE_STAVE_DEF = "Melody"

# ============================================================================
# STATION 3: BLUEPRINT STRINGS
# ============================================================================

VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    MELODY & r;
    harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody & harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony
"""


# ============================================================================
# STATION 4: PROGRAMMATIC CONTEXT (Optional - accessed via toggle)
# ============================================================================

def build_score_data_programmatic() -> Dict:
    """
    Programmatic composition mode (activated by PROMOTE_TO_STATION4 = True).
    
    Station 1 snippets (MELODY_LILY) are available here for algorithmic
    manipulation. This demonstrates that promotion gives you access to
    base materials while working in fully programmatic mode.
    """
    print("\n🔧 STATION 4 PROGRAMMATIC MODE")
    print("="*70)
    
    # Station 1 snippets are available!
    print("\n[Parsing Station 1 snippet...]")
    melody_parsed = parse_lilypond_to_data(MELODY_LILY, 'Melody')
    melody_part = data_to_part(melody_parsed['parts']['Melody'])
    print(f"✓ MELODY parsed: {len(melody_parsed['parts']['Melody'])} events")
    
    # Use harmonic intelligence
    print("\n[Applying harmonic intelligence...]")
    
    from transformations import analyze_structural_tones, harmonize_part
    from harmonic_analysis import get_structural_notes
    
    # Analyze structural tones
    analyzed = analyze_structural_tones(melody_part)
    structural = get_structural_notes(analyzed)
    
    print("\n✓ Structural tone analysis:")
    for note in structural:
        print(f"  {note.nameWithOctave} (beat {note.beat}, duration {note.quarterLength})")
    
    # Generate harmonization with extended progression
    print("\n✓ Generating harmonization with progression: I-vi-IV-V-I")
    harmonized = harmonize_part(
        melody_part,
        "I-vi-IV-V-I",  # More complex progression
        "C"
    )
    
    # Extract parts
    melody_events = extract_data_from_part(harmonized.parts[0])
    bass_events = extract_data_from_part(harmonized.parts[1])
    
    print(f"  Melody: {len(melody_events)} events")
    print(f"  Bass: {len(bass_events)} events (auto-generated)")
    
    # Populate Station 2
    global MELODY_TINY
    global MELODY_HARMONIZED_MELODY_LILY, MELODY_HARMONIZED_BASS_LILY
    global MELODY_HARMONIZED_MELODY_TINY, MELODY_HARMONIZED_BASS_TINY
    
    metadata = {
        'time_signature': '4/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'}
    }
    
    MELODY_TINY = events_to_tinynotation(melody_events, metadata)
    
    MELODY_HARMONIZED_MELODY_LILY = events_to_lily(melody_events, metadata)
    MELODY_HARMONIZED_BASS_LILY = events_to_lily(bass_events, metadata)
    
    MELODY_HARMONIZED_MELODY_TINY = events_to_tinynotation(melody_events, metadata)
    MELODY_HARMONIZED_BASS_TINY = events_to_tinynotation(bass_events, metadata)
    
    print("\n[STATION 2 populated with programmatically generated snippets]")
    print(f"✓ MELODY_HARMONIZED_BASS_LILY:")
    print(f"  {MELODY_HARMONIZED_BASS_LILY}")
    print(f"✓ MELODY_HARMONIZED_BASS_TINY (pitch verification):")
    print(f"  {MELODY_HARMONIZED_BASS_TINY}")
    
    return {
        'metadata': {
            'title': TITLE + " (Programmatic Mode)",
            'composer': COMPOSER,
            'time_signature': '4/4',
            'key_signature': {'tonic': 'c', 'mode': 'major'},
            'tempo': {'beat_duration': 4, 'bpm': 108}
        },
        'parts': {
            'Melody': melody_events,
            'Bass': bass_events
        }
    }


# ============================================================================
# PROCESSING ENGINE
# ============================================================================

def build_score_data() -> Dict:
    """
    Build score data using selected mode.
    
    Mode controlled by PROMOTE_TO_STATION4 toggle.
    """
    
    if not PROMOTE_TO_STATION4:
        # DECLARATIVE MODE (Stations 1-3)
        print("\n🎼 DECLARATIVE MODE: Using Blueprint Strings")
        print("="*70)
        
        # Parse snippets
        print("\n[STATION 1: Parsing LilyPond snippets...]")
        melody_parsed = parse_lilypond_to_data(MELODY_LILY, 'Melody')
        melody_events = melody_parsed['parts']['Melody']
        print(f"✓ MELODY: {len(melody_events)} events")
        
        SNIPPETS = {'MELODY': melody_events}
        
        metadata = {
            'title': TITLE,
            'composer': COMPOSER,
            'time_signature': '4/4',
            'key_signature': {'tonic': 'c', 'mode': 'major'},
            'tempo': {'beat_duration': 4, 'bpm': 108}
        }
        
        # Build using Blueprint Strings (includes harmonize_part!)
        print("\n[STATION 3: Executing Blueprint Strings...]")
        score_data = build_score_from_blueprint(
            VOICE_STAVE_DEF,
            VOICE_STAVE_DATA,
            SNIPPETS,
            metadata
        )
        
        # Populate Station 2
        print("\n" + "="*70)
        print("STATION 2: GENERATING REUSABLE SNIPPETS")
        print("="*70)
        
        global MELODY_TINY
        global MELODY_HARMONIZED_MELODY_LILY, MELODY_HARMONIZED_BASS_LILY
        global MELODY_HARMONIZED_MELODY_TINY, MELODY_HARMONIZED_BASS_TINY
        global MELODY_REPEATED_LILY, MELODY_REPEATED_TINY
        
        snippet_metadata = {
            'time_signature': '4/4',
            'key_signature': {'tonic': 'c', 'mode': 'major'}
        }
        
        # Original
        MELODY_TINY = events_to_tinynotation(melody_events, snippet_metadata)
        print("\n✓ MELODY_TINY (pitch verification):")
        print(f"  {MELODY_TINY}")
        
        # Harmonized (if present)
        if "harmonize_part(MELODY, 'I-IV-V-I', 'C')" in SNIPPETS:
            result = SNIPPETS["harmonize_part(MELODY, 'I-IV-V-I', 'C')"]
            
            MELODY_HARMONIZED_MELODY_LILY = events_to_lily(result['Melody'], snippet_metadata)
            MELODY_HARMONIZED_BASS_LILY = events_to_lily(result['Bass'], snippet_metadata)
            
            MELODY_HARMONIZED_MELODY_TINY = events_to_tinynotation(result['Melody'], snippet_metadata)
            MELODY_HARMONIZED_BASS_TINY = events_to_tinynotation(result['Bass'], snippet_metadata)
            
            print("\n✓ MELODY_HARMONIZED_BASS_LILY (auto-generated):")
            print(f"  {MELODY_HARMONIZED_BASS_LILY}")
            print("✓ MELODY_HARMONIZED_BASS_TINY (pitch verification):")
            print(f"  {MELODY_HARMONIZED_BASS_TINY}")
        
        # Repeated (if present)
        if "MELODY * 2" in SNIPPETS:
            repeated_events = SNIPPETS["MELODY * 2"]
            
            MELODY_REPEATED_LILY = events_to_lily(repeated_events, snippet_metadata)
            MELODY_REPEATED_TINY = events_to_tinynotation(repeated_events, snippet_metadata)
            
            print("\n✓ MELODY_REPEATED_LILY (repeat operator):")
            print(f"  {MELODY_REPEATED_LILY[:80]}...")
            print("✓ MELODY_REPEATED_TINY (pitch verification):")
            print(f"  {MELODY_REPEATED_TINY[:80]}...")
        
        print("\n" + "="*70)
        print("✅ BLUEPRINT ASSEMBLY COMPLETE")
        print("="*70)
        print("\nFeatures demonstrated:")
        print("  • harmonize_part() - Auto-generated bass line")
        print("  • Repeat operator (*) - MELODY * 2")
        print("  • Station 2 population - Both LILY and TINY formats")
        print("  • Multi-part handling - Score → Melody & Bass staves")
        
        return score_data
    
    else:
        # PROGRAMMATIC MODE (Station 4)
        return build_score_data_programmatic()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("HARMONIC INTELLIGENCE TEST STUDY")
    print("="*70)
    print(f"\nMode: {'PROGRAMMATIC (Station 4)' if PROMOTE_TO_STATION4 else 'DECLARATIVE (Stations 1-3)'}")
    print(f"Toggle: PROMOTE_TO_STATION4 = {PROMOTE_TO_STATION4}")
    print("\nTo switch modes, set PROMOTE_TO_STATION4 = True at the top of this file.")
    
    run_pipeline_from_file(__file__)
