"""
TWENTYTH STUDY: First real melody
==================================

This study demonstrates comprehensive Codempose features including:
- Multiple composition patterns (LilyPond snippets, programmatic, shorthand)
- All parser features (tuplets, ties, grace notes, articulations, dynamics)
- Transformations (transpose, invert, retrograde)
- Harmonic intelligence (structural analysis, auto-harmonization)
- Multi-voice arrangements
- Blueprint-based composition

STRUCTURE:
- Station 1: LilyPond Snippets (musical ideas)
- Station 2: Programmatic Voices (music21-based generation)
- Station 3: Composition Shorthand (declarative combinations)
- Station 4: Harmonic Intelligence (auto-harmonization)
- Station 5: Multi-Voice Score Assembly
"""

import _study_path  # Auto-path setup for study files

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Dict, List, Optional
from lilypond_parser import parse_lilypond_to_data
from music_data import data_to_part, part_to_data
from lily_converter import events_to_lily
from voice_documentation import register_and_document_voice
from project_template import run_pipeline_from_file

# Composition tools (import as needed)
from composition_shorthand import (
    build_score_from_assignments,
    transpose_events,
    invert_events,
    retrograde_events
)

from score_builder import build_score_from_blueprint
from transformations import transpose_part, invert_part, retrograde_part

# Harmonic intelligence (optional)
from harmonic_analysis import find_structural_tones, print_structural_analysis
from harmonic_engine import harmonize_melody


# ============================================================================
# METADATA
# ============================================================================

TITLE = "TWENTYTH Study: First real melody"
COMPOSER = "Codempose Framework"


# ============================================================================
# STATION 1: LILYPOND SNIPPETS (Primary Musical Ideas)
# ============================================================================

# Main melody with comprehensive features
MELODY_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    \tempo 4=120
    
    % Measure 1: Basic notes with articulations
    c4-. d4-> e4-- f4-^ |
    
    % Measure 2: Dynamics and grace notes
    \acciaccatura { d8 } c4\f d4\p e2 |
    
    % Measure 3: Tuplet
    \tuplet 3/2 { c8 d e } f4 g2 |
    
    % Measure 4: Ties
    a4~ a4 g4 f4 |
    
    % Measure 5: Chords
    <c e g>2 <d f a>2 |
    
    % Final cadence
    <e g b>1 |
}
""".strip()

# Harmony part (simple accompaniment)
HARMONY_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    c4 c4 c4 c4 |
    c4 c4 c2 |
    c4 c4 c2 |
    c4 c4 c4 c4 |
    <c e>2 <d f>2 |
    <e g>1 |
}
""".strip()

# Bass line
BASS_LILY = r"""
\relative c {
    \time 4/4
    \key c \major
    c2 g2 |
    f2 c2 |
    c2 g2 |
    f2 c2 |
    c1 |
    c1 |
}
""".strip()


# ============================================================================
# STATION 2: PROGRAMMATIC VOICE GENERATION (Optional)
# ============================================================================

def generate_counterpoint(melody_events):
    """
    Generate a counterpoint voice from the melody.
    
    Example of programmatic composition using music21.
    """
    from music21 import note, stream
    
    # Convert to music21
    melody_part = data_to_part(melody_events)
    
    # Create counterpoint (simple inversion for demonstration)
    inverted = invert_part(melody_part, 'C4')
    
    # Convert back to canonical format
    counterpoint_events = part_to_data(inverted)
    
    return counterpoint_events


# ============================================================================
# STATION 3: COMPOSITION SHORTHAND (Optional)
# ============================================================================

# Example shorthand assignments (declarative composition)
SHORTHAND_ASSIGNMENTS = {
    'Soprano': {
        'Main': 'MELODY',  # Uses MELODY_LILY
    },
    'Alto': {
        'Main': 'transpose(MELODY, -5)',  # Transpose down perfect 4th
    },
    'Tenor': {
        'Main': 'HARMONY',  # Uses HARMONY_LILY
    },
    'Bass': {
        'Main': 'BASS',  # Uses BASS_LILY
    }
}


# ============================================================================
# STATION 4: HARMONIC INTELLIGENCE (Optional)
# ============================================================================

# Uncomment to use auto-harmonization:
# PROGRESSION = "I - IV - V - I"  # Chord progression
# KEY = "C"  # Key for harmonization


# ============================================================================
# STATION 5: BUILD SCORE DATA
# ============================================================================

def build_score_data():
    """
    Build the final score data structure.
    
    Choose one approach:
    1. Simple: Single melody from LilyPond
    2. Multi-part: Multiple LilyPond snippets
    3. Shorthand: Use composition_shorthand
    4. Blueprint: Use score_builder
    5. Harmonic: Use harmonic_engine
    """
    
    # -------------------------------------------------------------------------
    # APPROACH 1: Simple Single Melody
    # -------------------------------------------------------------------------
    
    # Parse the main melody
    melody_data = parse_lilypond_to_data(MELODY_LILY)
    melody_events = melody_data['parts']['Part 1']  # Parser uses 'Part 1' by default
    
    return {
        'metadata': {
            'title': TITLE,
            'composer': COMPOSER,
        },
        'parts': {
            'Melody': melody_events,
        }
    }
    
    # -------------------------------------------------------------------------
    # APPROACH 2: Multi-Part Score (Uncomment to use)
    # -------------------------------------------------------------------------
    
    # melody_data = parse_lilypond_to_data(MELODY_LILY)
    # harmony_data = parse_lilypond_to_data(HARMONY_LILY)
    # bass_data = parse_lilypond_to_data(BASS_LILY)
    
    # return {
    #     'metadata': {
    #         'title': TITLE,
    #         'composer': COMPOSER,
    #     },
    #     'parts': {
    #         'Melody': melody_data['parts']['Part 1'],
    #         'Harmony': harmony_data['parts']['Part 1'],
    #         'Bass': bass_data['parts']['Part 1'],
    #     }
    # }
    
    # -------------------------------------------------------------------------
    # APPROACH 3: Composition Shorthand (Uncomment to use)
    # -------------------------------------------------------------------------
    
    # # Parse base voices
    # voice_data = {}
    # for name, snippet in [('MELODY', MELODY_LILY), 
    #                       ('HARMONY', HARMONY_LILY), 
    #                       ('BASS', BASS_LILY)]:
    #     parsed = parse_lilypond_to_data(snippet)
    #     voice_data[name] = parsed['parts']['Part 1']  # Parser uses 'Part 1'
    
    # # Build score using shorthand
    # from composition_shorthand import build_score_from_assignments
    # score_data = build_score_from_assignments(SHORTHAND_ASSIGNMENTS, voice_data)
    # score_data['metadata'] = {'title': TITLE, 'composer': COMPOSER}
    
    # return score_data
    
    # -------------------------------------------------------------------------
    # APPROACH 4: Harmonic Intelligence (Uncomment to use)
    # -------------------------------------------------------------------------
    
    # melody_data = parse_lilypond_to_data(MELODY_LILY)
    # melody_events = melody_data['parts']['Part 1']  # Parser uses 'Part 1'
    # melody_part = data_to_part(melody_events)
    
    # # Analyze structural tones
    # structural_analysis = find_structural_tones(melody_part)
    # print_structural_analysis(structural_analysis)
    
    # # Generate harmonization
    # harmonized_score = harmonize_melody(melody_part, "I - IV - V - I", "C")
    
    # # Extract parts
    # melody_final = part_to_data(harmonized_score.parts[0])
    # bass_final = part_to_data(harmonized_score.parts[1])
    
    # return {
    #     'metadata': {'title': TITLE, 'composer': COMPOSER},
    #     'parts': {
    #         'Melody': melody_final,
    #         'Bass': bass_final,
    #     }
    # }


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == '__main__':
    run_pipeline_from_file(__file__)
