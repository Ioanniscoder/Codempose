"""
TWO-STAVE TEST: Theme A with Chord Harmony
===========================================

This test file demonstrates a two-staff piano-style arrangement:

Upper Staff (Treble Clef): Theme A melody with variations
Lower Staff (Bass Clef): Intermezzo chord harmony

Structure:
- Upper plays Theme A while Lower rests
- Both play Intermezzo together
- Upper plays Theme A variation while Lower rests
- Pattern repeats

This tests:
1. Multi-part voice assignment
2. Chord parsing (once enabled)
3. Two-staff LilyPond/MusicXML export
4. Time alignment between staves
"""

from typing import Dict
from lilypond_parser import parse_lilypond_to_data
from music_data import extract_data_from_part, data_to_part
from transformations import transpose_part, invert_part

# ============================================================================
# MUSICAL MATERIALS
# ============================================================================

# Theme A: Melodic line (upper staff)
THEME_A_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    \tempo 4=120
    c4 d4 e4 f4 |
    e2 d2 |
    c1
}
"""

# Intermezzo: Chord harmony (lower staff)
INTERMEZZO_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    <c e g>2 <d f a>2 |
    <e g b>2 <f a c>2
}
"""

# ============================================================================
# SCORE BUILDING
# ============================================================================

def build_score_data() -> Dict:
    """
    Build two-staff arrangement.
    
    Returns:
        Dictionary with 'metadata' and 'parts' keys
        Parts will contain 'UpperStaff' and 'LowerStaff'
    """
    print("\n" + "="*70)
    print("TWO-STAVE TEST: Theme A + Chord Harmony")
    print("="*70)
    
    # Parse materials
    print("\n[Parsing materials...]")
    
    parsed_a = parse_lilypond_to_data(THEME_A_LILY, part_name='ThemeA')
    theme_a_events = parsed_a.get('parts', {}).get('ThemeA', [])
    theme_a_part = data_to_part(theme_a_events, parsed_a.get('metadata', {}))
    print(f"✓ Theme A: {len(theme_a_events)} events")
    
    parsed_intermezzo = parse_lilypond_to_data(INTERMEZZO_LILY, part_name='Intermezzo')
    intermezzo_events = parsed_intermezzo.get('parts', {}).get('Intermezzo', [])
    intermezzo_part = data_to_part(intermezzo_events, parsed_intermezzo.get('metadata', {}))
    print(f"✓ Intermezzo: {len(intermezzo_events)} events (chords)")
    
    if len(intermezzo_events) == 0:
        print("   ⚠️  WARNING: Chord parsing not yet enabled!")
        print("   ℹ️  See ISSUE_INVESTIGATION_REPORT.md for details")
    
    # Generate variations
    print("\n[Generating variations...]")
    theme_a_transposed = extract_data_from_part(transpose_part(theme_a_part, 'P5'))
    theme_a_inverted = extract_data_from_part(invert_part(theme_a_part, 'C4'))
    print(f"✓ Theme A variations: Transposed (+P5), Inverted (C4)")
    
    # Build upper staff (melody)
    print("\n[Assembling upper staff...]")
    upper_staff = []
    
    # Section 1: Theme A original
    upper_staff.extend(theme_a_events)
    upper_staff.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Section 2: Rest during intermezzo
    upper_staff.append({'type': 'rest', 'ql': 8.0})  # 2 bars of 4/4
    upper_staff.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Section 3: Theme A transposed
    upper_staff.extend(theme_a_transposed)
    upper_staff.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Section 4: Rest during intermezzo
    upper_staff.append({'type': 'rest', 'ql': 8.0})
    upper_staff.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Section 5: Theme A inverted
    upper_staff.extend(theme_a_inverted)
    
    print(f"✓ Upper staff: {len(upper_staff)} events")
    
    # Build lower staff (harmony)
    print("\n[Assembling lower staff...]")
    lower_staff = []
    
    # Section 1: Rest during theme
    lower_staff.append({'type': 'rest', 'ql': 12.0})  # 3 bars of 4/4
    lower_staff.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Section 2: Intermezzo chords (or full rest bars if chords not parsed)
    if len(intermezzo_events) > 0:
        lower_staff.extend(intermezzo_events)
    else:
        # Show full bars of rest when chords not available
        lower_staff.append({'type': 'rest', 'ql': 8.0})  # 2 bars of 4/4
    lower_staff.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Section 3: Rest during theme
    lower_staff.append({'type': 'rest', 'ql': 12.0})
    lower_staff.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Section 4: Intermezzo chords (repeat, or full rest bars)
    if len(intermezzo_events) > 0:
        lower_staff.extend(intermezzo_events)
    else:
        # Show full bars of rest when chords not available
        lower_staff.append({'type': 'rest', 'ql': 8.0})  # 2 bars of 4/4
    lower_staff.append({'type': 'barline', 'style': '||', 'ql': 0.0})
    
    # Section 5: Rest during theme
    lower_staff.append({'type': 'rest', 'ql': 12.0})
    
    print(f"✓ Lower staff: {len(lower_staff)} events")
    
    # Voice tracking metadata
    voice_tracking = {
        'UpperStaff': {
            '01_ThemeA_Original': {
                'source': 'THEME_A_LILY',
                'measures': '1-3',
                'description': 'Original theme in C major',
                'events': len(theme_a_events),
            },
            '02_Rest': {
                'source': 'REST',
                'measures': '4-5',
                'description': 'Silent during intermezzo',
                'events': 1,
            },
            '03_ThemeA_Transposed': {
                'source': 'THEME_A_LILY',
                'measures': '6-8',
                'description': 'Theme transposed up P5 to G major',
                'events': len(theme_a_transposed),
            },
            '04_Rest': {
                'source': 'REST',
                'measures': '9-10',
                'description': 'Silent during intermezzo',
                'events': 1,
            },
            '05_ThemeA_Inverted': {
                'source': 'THEME_A_LILY',
                'measures': '11-13',
                'description': 'Theme inverted around C4',
                'events': len(theme_a_inverted),
            },
        },
        'LowerStaff': {
            '01_Rest': {
                'source': 'REST',
                'measures': '1-3',
                'description': 'Silent during theme',
                'events': 1,
            },
            '02_Intermezzo': {
                'source': 'INTERMEZZO_LILY',
                'measures': '4-5',
                'description': 'Chord harmony support',
                'events': len(intermezzo_events),
            },
            '03_Rest': {
                'source': 'REST',
                'measures': '6-8',
                'description': 'Silent during theme',
                'events': 1,
            },
            '04_Intermezzo': {
                'source': 'INTERMEZZO_LILY',
                'measures': '9-10',
                'description': 'Chord harmony support (repeat)',
                'events': len(intermezzo_events),
            },
            '05_Rest': {
                'source': 'REST',
                'measures': '11-13',
                'description': 'Silent during theme',
                'events': 1,
            },
        },
    }
    
    return {
        'metadata': {
            'title': 'Two-Stave Test: Theme A + Harmony',
            'composer': 'Codempose Framework',
            'time_signature': '4/4',
            'tempo': '120',
            'key_signature': 'C major',
            'original_snippets': {
                'THEME_A': THEME_A_LILY,
                'INTERMEZZO': INTERMEZZO_LILY,
            },
            'voice_tracking': voice_tracking,
            'staff_info': {
                'UpperStaff': {
                    'clef': 'treble',
                    'role': 'melody',
                },
                'LowerStaff': {
                    'clef': 'bass',
                    'role': 'harmony',
                },
            },
        },
        'parts': {
            'UpperStaff': upper_staff,
            'LowerStaff': lower_staff,
        }
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    
    print("\n" + "="*70)
    print("TWO-STAVE TEST")
    print("="*70)
    print("\n📋 Testing:")
    print("   1. Two-part voice structure (UpperStaff + LowerStaff)")
    print("   2. Chord parsing (INTERMEZZO)")
    print("   3. Staff-specific clef assignment")
    print("   4. Time alignment between staves")
    print("\n⚠️  Note: Chord parsing currently disabled")
    print("   See ISSUE_INVESTIGATION_REPORT.md for details")
    print("   Intermezzo will show 0 events until chords are enabled")
    print("\n" + "="*70 + "\n")
    
    # Run the standard pipeline
    # NOTE: Current pipeline may not support multiple parts yet
    # This will be updated after chord parsing is fixed
    run_pipeline_from_file(__file__)
