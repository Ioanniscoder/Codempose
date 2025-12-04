"""
Test script to verify articulations and dynamics export to LilyPond and MusicXML.
Creates a simple study with all modifier types for quick verification.
"""

from project_template import engrave_with_abjad, export_to_musicxml
from lilypond_parser import parse_lilypond_to_data

# Simple test theme with all modifiers
THEME = r"""
\relative c' {
    \time 4/4
    \key c \major
    c4(.) d4(-, p) e4(>, mf) f4 |
    g4(., f) a4(-, ff) b4(themeTest) c'4(themeTest, ., p)
}
"""

def build_score_data():
    """Build simple test score with articulations and dynamics."""
    
    # Parse theme
    theme_data = parse_lilypond_to_data(THEME, part_name="TestPart")
    theme_events = theme_data['parts']['TestPart']
    
    print(f"✓ Parsed {len(theme_events)} events")
    
    # Check for modifiers
    artic_count = sum(1 for ev in theme_events if ev.get('articulations'))
    dyn_count = sum(1 for ev in theme_events if ev.get('dynamics'))
    track_count = sum(1 for ev in theme_events if ev.get('tracker'))
    
    print(f"✓ Found {artic_count} events with articulations")
    print(f"✓ Found {dyn_count} events with dynamics")
    print(f"✓ Found {track_count} events with tracking labels")
    
    # Print sample events
    print("\nSample events:")
    for i, ev in enumerate(theme_events[:8]):
        note_name = f"{ev.get('step', '?')}{ev.get('octave', '')}"
        mods = []
        if ev.get('articulations'):
            mods.append(f"artic={ev['articulations']}")
        if ev.get('dynamics'):
            mods.append(f"dyn={ev['dynamics']}")
        if ev.get('tracker'):
            mods.append(f"track={ev['tracker']}")
        
        mod_str = ", ".join(mods) if mods else "none"
        print(f"  [{i}] {note_name}: {mod_str}")
    
    # Build score data with original snippet
    score_data = {
        'metadata': {
            'title': 'Articulation & Dynamics Test',
            'composer': 'Codempose Framework',
            'time_signature': '4/4',
            'key_signature': 'C major',
            'tempo': 120,
            'original_snippets': {
                'THEME': THEME
            }
        },
        'parts': {
            'MainLine': theme_events
        }
    }
    
    return score_data


if __name__ == '__main__':
    print("=" * 60)
    print("ARTICULATION & DYNAMICS EXPORT TEST")
    print("=" * 60)
    print()
    
    # Build score
    score_data = build_score_data()
    
    print()
    print("=" * 60)
    print("GENERATING OUTPUTS")
    print("=" * 60)
    
    # Generate outputs
    engrave_with_abjad(score_data, 'test_export', source_file=__file__)
    export_to_musicxml(score_data, 'test_export')
    
    print()
    print("=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    print()
    print("✓ Check outputs/test_export.ly for LilyPond syntax:")
    print("  - Look for: -. (staccato), -- (tenuto), -> (accent)")
    print("  - Look for: \\p (piano), \\mf (mezzo-forte), \\f (forte)")
    print()
    print("✓ Check outputs/test_export.musicxml for XML elements:")
    print("  - Look for: <staccato />, <tenuto />, <accent />")
    print("  - Look for: <dynamics><p /></dynamics>, etc.")
    print()
    print("✓ Import outputs/test_export.musicxml to MuseScore:")
    print("  - Verify articulations visible on notes")
    print("  - Verify dynamics visible below staff")
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
