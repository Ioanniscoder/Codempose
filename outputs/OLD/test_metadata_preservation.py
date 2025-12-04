"""Test: Metadata Preservation Through Transformations

This test verifies that articulations, dynamics, and tracking labels
are preserved when transformations are applied via Blueprint Strings.
"""

import _study_path

from typing import Dict
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file


# ============================================================================
# METADATA
# ============================================================================

TITLE = "Metadata Preservation Test"
COMPOSER = "Testing Framework"


# ============================================================================
# STATION 1: SNIPPET WITH METADATA
# ============================================================================

# Theme with articulations, dynamics, and tracking labels
THEME_WITH_METADATA_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    c4(., themeStart) d4(-, p) e4(>, mf) f4(themeEnd) |
    g2(f) a2(ff) |
    b4(.) a4 g4(themeStart) f4 |
    e1(p)
}
""".strip()


# ============================================================================
# STATION 2: BLUEPRINT STRINGS WITH TRANSFORMATIONS
# ============================================================================

VOICE_STAVE_DEF = "Melody"

VOICE_STAVE_DATA = """
    THEME;
    transpose_part(THEME, 'P5');
    invert_part(THEME, 'C4')
"""


# ============================================================================
# STATION 3: BUILD AND VERIFY
# ============================================================================

def build_score_data() -> Dict:
    """Build score and check metadata preservation."""
    
    print("\n" + "="*70)
    print("METADATA PRESERVATION TEST")
    print("="*70)
    
    # Parse snippet with metadata
    print("\n[Parsing snippet with metadata...]")
    theme_parsed = parse_lilypond_to_data(THEME_WITH_METADATA_LILY, 'Melody')
    theme_events = theme_parsed['parts']['Melody']
    
    # Count metadata in original
    original_articulations = sum(1 for e in theme_events if 'articulations' in e)
    original_dynamics = sum(1 for e in theme_events if 'dynamics' in e)
    original_trackers = sum(1 for e in theme_events if 'tracker' in e)
    
    print(f"\n✓ Original THEME parsed: {len(theme_events)} events")
    print(f"  • Articulations: {original_articulations} events")
    print(f"  • Dynamics: {original_dynamics} events")
    print(f"  • Tracking labels: {original_trackers} events")
    
    # Show first few events with metadata
    print("\n[Sample events from original THEME:]")
    for i, event in enumerate(theme_events[:4]):
        metadata_tags = []
        if 'articulations' in event:
            metadata_tags.append(f"articulations={event['articulations']}")
        if 'dynamics' in event:
            metadata_tags.append(f"dynamics={event['dynamics']}")
        if 'tracker' in event:
            metadata_tags.append(f"tracker={event['tracker']}")
        
        if metadata_tags:
            print(f"  Event {i}: {event.get('type')} {event.get('step', 'r')}{event.get('octave', '')} - {', '.join(metadata_tags)}")
    
    # Build snippets
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
    
    # Build with transformations
    print("\n[Building with transformations...]")
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
    
    # Check if transformed snippets preserved metadata
    print("\n" + "="*70)
    print("METADATA VERIFICATION")
    print("="*70)
    
    transformed_keys = [k for k in SNIPPETS.keys() if k.startswith(('transpose', 'invert'))]
    
    for key in transformed_keys:
        transformed_events = SNIPPETS[key]
        trans_articulations = sum(1 for e in transformed_events if 'articulations' in e)
        trans_dynamics = sum(1 for e in transformed_events if 'dynamics' in e)
        trans_trackers = sum(1 for e in transformed_events if 'tracker' in e)
        
        print(f"\n{key}:")
        print(f"  Events: {len(transformed_events)}")
        print(f"  • Articulations: {trans_articulations} events")
        print(f"  • Dynamics: {trans_dynamics} events")
        print(f"  • Tracking labels: {trans_trackers} events")
        
        # Show warning if metadata lost
        if trans_articulations == 0 and original_articulations > 0:
            print(f"  ⚠️  WARNING: Articulations LOST in transformation!")
        if trans_dynamics == 0 and original_dynamics > 0:
            print(f"  ⚠️  WARNING: Dynamics LOST in transformation!")
        if trans_trackers == 0 and original_trackers > 0:
            print(f"  ⚠️  WARNING: Tracking labels LOST in transformation!")
    
    print("\n" + "="*70)
    
    # Calculate preservation rate
    all_preserved = True
    for key in transformed_keys:
        transformed_events = SNIPPETS[key]
        if original_articulations > 0 and sum(1 for e in transformed_events if 'articulations' in e) == 0:
            all_preserved = False
        if original_dynamics > 0 and sum(1 for e in transformed_events if 'dynamics' in e) == 0:
            all_preserved = False
        if original_trackers > 0 and sum(1 for e in transformed_events if 'tracker' in e) == 0:
            all_preserved = False
    
    if all_preserved:
        print("✅ METADATA PRESERVED: All transformations retained metadata!")
    else:
        print("❌ METADATA LOST: Transformations lost some metadata!")
        print("   This needs to be fixed in music_data.py")
    
    print("="*70 + "\n")
    
    return score_data


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    run_pipeline_from_file(__file__)
