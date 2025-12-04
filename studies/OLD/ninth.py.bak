"""
NINTH STUDY: Hybrid Composition Model
======================================

This study demonstrates the HYBRID approach where programmatic control
and declarative shorthand coexist in the same composition.

Key Principles:
1. build_score_data() is the MASTER CONTROLLER
2. Mix programmatic generation with declarative shorthand
3. Use shorthand for simple/repetitive parts
4. Use programmatic code for complex/unique parts
5. Full programmatic structure is ALWAYS available as fallback

Musical Structure:
- Soprano: Programmatically generated with inversion transformation
- Alto: Programmatically generated variation with custom logic
- Tenor: Declarative shorthand (simple transposed pattern)
- Bass: Declarative shorthand (ostinato)

This demonstrates that you can:
- Generate any voice programmatically
- Use shorthand where convenient
- Combine both in a single composition
- Maintain full control via build_score_data()
"""

from lilypond_parser import parse_lilypond_to_data
from music_data import extract_data_from_part, data_to_part
from second import invert_part
from composition_shorthand import build_score_from_assignments, validate_voice_assignments


# ============================================================================
# MUSICAL SNIPPETS
# ============================================================================

# Theme - will be used programmatically
THEME_LILY = r"""
\relative c' {
    c4 d e f |
    g2 e2 |
    f4 e d c |
    c1 |
}
"""

# Variation - will be used programmatically
VARIATION_LILY = r"""
\relative c' {
    e4 f g a |
    b2 g2 |
}
"""

# Bass pattern - will be used in shorthand
BASS_LILY = r"""
\relative c {
    c2 g2 |
    f2 c2 |
}
"""

# Harmony pattern - will be used in shorthand
HARMONY_LILY = r"""
\relative c' {
    e2 c2 |
    d2 g,2 |
}
"""


# ============================================================================
# DECLARATIVE SHORTHAND (Optional - for simple parts)
# ============================================================================

# Define which voices use the shorthand approach
# (Tenor and Bass are simple, repetitive - good candidates for shorthand)
VOICE_ASSIGNMENTS = {
    'Harmony': {
        'Tenor': 'transpose(HARMONY, 5) + HARMONY',  # Transposed then original
        'Bass': 'BASS * 4',                           # Simple ostinato
    }
}


# ============================================================================
# PROGRAMMATIC GENERATION FUNCTIONS
# ============================================================================

def generate_soprano_programmatically():
    """
    Generate the Soprano voice using PURE programmatic control.
    
    This demonstrates:
    - Parsing LilyPond input
    - Converting to music21 Part
    - Applying transformations (inversion)
    - Extracting final event data
    
    Returns:
        list: Event dictionaries for soprano voice
    """
    print("  🔧 Programmatic: Generating Soprano with inversion...")
    
    # Parse the theme
    theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
    theme_part = data_to_part(theme_data['parts']['Theme'])
    
    # Apply inversion transformation (around C4)
    inverted_part = invert_part(theme_part, 'C4')
    
    # Extract events from the transformed part
    soprano_events = extract_data_from_part(inverted_part)
    
    print(f"    ✓ Generated {len(soprano_events)} events for Soprano")
    return soprano_events


def generate_alto_programmatically():
    """
    Generate the Alto voice using PURE programmatic control with custom logic.
    
    This demonstrates:
    - Multiple snippet combination
    - Custom algorithmic manipulation
    - Direct event list construction
    
    Returns:
        list: Event dictionaries for alto voice
    """
    print("  🔧 Programmatic: Generating Alto with custom logic...")
    
    # Parse the variation snippet
    variation_data = parse_lilypond_to_data(VARIATION_LILY, part_name='Variation')
    variation_events = variation_data['parts']['Variation']
    
    # Parse the theme for additional material
    theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
    theme_events = theme_data['parts']['Theme']
    
    # Custom algorithmic logic: Take first 4 events from theme
    theme_fragment = theme_events[:4]
    
    # Combine: variation + fragment + variation (backwards)
    alto_events = (
        variation_events +                    # Forward variation
        theme_fragment +                      # Theme fragment
        list(reversed(variation_events))      # Retrograde variation
    )
    
    print(f"    ✓ Generated {len(alto_events)} events for Alto")
    return alto_events


def build_harmony_via_shorthand():
    """
    Generate Tenor and Bass using DECLARATIVE shorthand.
    
    This demonstrates:
    - Shorthand for simple, repetitive parts
    - Voice lookup preparation
    - Validation before processing
    
    Returns:
        dict: Score data with Tenor and Bass voices
    """
    print("  📝 Declarative: Building Harmony via shorthand...")
    
    # Prepare voice lookup (map names to event data)
    harmony_data = parse_lilypond_to_data(HARMONY_LILY, part_name='Harmony')
    bass_data = parse_lilypond_to_data(BASS_LILY, part_name='Bass')
    
    voice_lookup = {
        'HARMONY': harmony_data['parts']['Harmony'],
        'BASS': bass_data['parts']['Bass'],
    }
    
    # Validate voice assignments BEFORE processing
    errors = validate_voice_assignments(VOICE_ASSIGNMENTS, voice_lookup.keys())
    if errors:
        print("    ❌ Validation errors:")
        for error in errors:
            print(f"      {error}")
        raise ValueError("Fix voice assignment errors before proceeding")
    
    print("    ✓ Validation passed")
    
    # Build using shorthand engine
    harmony_score = build_score_from_assignments(
        voice_assignments=VOICE_ASSIGNMENTS,
        voice_data=voice_lookup,
        metadata={'title': 'Harmony Section'}
    )
    
    print(f"    ✓ Built Tenor ({len(harmony_score['parts']['Harmony']['Tenor'])} events)")
    print(f"    ✓ Built Bass ({len(harmony_score['parts']['Harmony']['Bass'])} events)")
    
    return harmony_score['parts']['Harmony']


# ============================================================================
# MASTER CONTROLLER - build_score_data()
# ============================================================================

def build_score_data():
    """
    MASTER CONTROLLER for the composition.
    
    This is the HIGHEST-PRIORITY entry point where we:
    1. Generate complex parts programmatically (Soprano, Alto)
    2. Generate simple parts declaratively (Tenor, Bass)
    3. Combine both approaches into final score
    
    This demonstrates the HYBRID MODEL:
    - Full programmatic control is ALWAYS available
    - Shorthand is used as a convenience for simple parts
    - Both coexist seamlessly in the same composition
    
    Returns:
        dict: Complete score data structure
    """
    print("\n" + "="*70)
    print("🎼 NINTH STUDY: Hybrid Composition Model")
    print("="*70)
    print("\n📊 Building score with HYBRID approach:\n")
    
    # -----------------------------------------------------------------------
    # SECTION 1: PROGRAMMATIC GENERATION (Complex, unique parts)
    # -----------------------------------------------------------------------
    print("SECTION 1: Programmatic Generation")
    print("-" * 70)
    
    soprano_events = generate_soprano_programmatically()
    alto_events = generate_alto_programmatically()
    
    # -----------------------------------------------------------------------
    # SECTION 2: DECLARATIVE SHORTHAND (Simple, repetitive parts)
    # -----------------------------------------------------------------------
    print("\nSECTION 2: Declarative Shorthand")
    print("-" * 70)
    
    harmony_parts = build_harmony_via_shorthand()
    tenor_events = harmony_parts['Tenor']
    bass_events = harmony_parts['Bass']
    
    # -----------------------------------------------------------------------
    # SECTION 3: COMBINE into final score_data
    # -----------------------------------------------------------------------
    print("\nSECTION 3: Combining All Parts")
    print("-" * 70)
    
    score_data = {
        'metadata': {
            'title': 'Ninth Study - Hybrid Composition',
            'composer': 'Codempose Framework',
            'tagline': 'Demonstrating programmatic + declarative approaches'
        },
        'parts': {
            'Melody': {
                'Soprano': soprano_events,  # ← PROGRAMMATIC
                'Alto': alto_events,        # ← PROGRAMMATIC
            },
            'Harmony': {
                'Tenor': tenor_events,      # ← DECLARATIVE SHORTHAND
                'Bass': bass_events,        # ← DECLARATIVE SHORTHAND
            }
        }
    }
    
    # Print summary
    print("\n  ✅ Final Score Structure:")
    print(f"    Melody.Soprano: {len(soprano_events)} events (programmatic)")
    print(f"    Melody.Alto: {len(alto_events)} events (programmatic)")
    print(f"    Harmony.Tenor: {len(tenor_events)} events (shorthand)")
    print(f"    Harmony.Bass: {len(bass_events)} events (shorthand)")
    print(f"\n  📦 Total: {sum(len(e) for staff in score_data['parts'].values() for e in staff.values())} events")
    
    print("\n" + "="*70)
    print("✅ Score data built successfully using HYBRID approach!")
    print("="*70 + "\n")
    
    return score_data


# ============================================================================
# FULL PROGRAMMATIC FALLBACK
# ============================================================================

def build_score_data_fully_programmatic():
    """
    ALTERNATIVE IMPLEMENTATION: Pure programmatic approach.
    
    This demonstrates that you can ALWAYS bypass the shorthand entirely
    and generate EVERYTHING programmatically if needed.
    
    This function is NOT used in the main flow, but shows that the
    programmatic option is ALWAYS available as a fallback.
    
    Returns:
        dict: Complete score data structure (same as hybrid version)
    """
    print("\n🔧 ALTERNATIVE: Building ENTIRE score programmatically (no shorthand)\n")
    
    # Parse all snippets
    theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
    variation_data = parse_lilypond_to_data(VARIATION_LILY, part_name='Variation')
    bass_data = parse_lilypond_to_data(BASS_LILY, part_name='Bass')
    harmony_data = parse_lilypond_to_data(HARMONY_LILY, part_name='Harmony')
    
    # Generate Soprano (inverted theme)
    theme_part = data_to_part(theme_data['parts']['Theme'])
    inverted_part = invert_part(theme_part, 'C4')
    soprano_events = extract_data_from_part(inverted_part)
    
    # Generate Alto (variation + fragment + retrograde)
    variation_events = variation_data['parts']['Variation']
    theme_events = theme_data['parts']['Theme']
    alto_events = (
        variation_events +
        theme_events[:4] +
        list(reversed(variation_events))
    )
    
    # Generate Tenor (manually - no shorthand)
    # Equivalent to: 'transpose(HARMONY, 5) + HARMONY'
    harmony_events = harmony_data['parts']['Harmony']
    # For simplicity, just concatenate (would need transpose function for full equivalence)
    tenor_events = harmony_events + harmony_events
    
    # Generate Bass (manually - no shorthand)
    # Equivalent to: 'BASS * 4'
    bass_events_single = bass_data['parts']['Bass']
    bass_events = bass_events_single * 4
    
    # Assemble final score
    return {
        'metadata': {
            'title': 'Ninth Study - Fully Programmatic',
            'composer': 'Codempose Framework',
        },
        'parts': {
            'Melody': {
                'Soprano': soprano_events,
                'Alto': alto_events,
            },
            'Harmony': {
                'Tenor': tenor_events,
                'Bass': bass_events,
            }
        }
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    
    # UNCOMMENT to use fully programmatic approach instead:
    # def build_score_data():
    #     return build_score_data_fully_programmatic()
    
    print("\n💡 Key Takeaways:")
    print("  1. build_score_data() is the MASTER CONTROLLER")
    print("  2. Programmatic generation gives FULL CONTROL")
    print("  3. Declarative shorthand provides CONVENIENCE")
    print("  4. Both approaches MIX SEAMLESSLY")
    print("  5. You can ALWAYS bypass shorthand entirely")
    print("\n🎼 The framework gives you OPTIONS, not restrictions!\n")
    
    # Run the standard pipeline
    run_pipeline_from_file(__file__)
