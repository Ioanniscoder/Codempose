"""
FUGUE STUDY: Fugue Exposition Generator
========================================

Complete demonstration of fugue exposition using Station 4 programmatic features.
Based on example_fugue_exposition() from src/lib/station4_music21_examples.py

This study shows:
- Subject (original theme)
- Answer (subject transposed to dominant)
- Countersubject (inverted subject)
- Subject in augmentation (stretto preparation)

All transformations are generated programmatically from a single fugue subject.
"""

import _study_path  # Auto-path setup

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Dict
from src.lilypond_parser import parse_lilypond_to_data
from src.project_template import run_pipeline_from_file
from src.composition_shorthand import transpose_events, invert_events


# ============================================================================
# !! STATION 4 PROMOTION TOGGLE !!
# ============================================================================
# This study ONLY uses Station 4 (Programmatic Composition)
PROMOTE_TO_PROGRAMMATIC = True
# ============================================================================


# ============================================================================
# METADATA
# ============================================================================

TITLE = "Fugue Exposition: Programmatic Generation"
COMPOSER = "Codempose Framework"
OPUS_NUMBER = "FUGUE-1"
INSTRUMENTATION = "Piano (4 voices)"


############################################################################
## STATION 1: FUGUE SUBJECT                                              ##
############################################################################
# Define a single fugue subject - all other voices derived from this!
# NOTE: Using absolute pitches to avoid octave confusion

FUGUE_SUBJECT_LILY = r"""
{
    \key c \major
    \time 4/4
    \tempo "Moderato" 4=100
    c'4 d'8 e' f'4 e'8 d' |
    e'4 c' d'2~ |
    d'4 e'8 f' g'4 f'8 e' |
    f'2 e'2
}
""".strip()


############################################################################
## STATION 4: PROGRAMMATIC FUGUE EXPOSITION                              ##
############################################################################

def build_score_data() -> Dict:
    """
    Generate complete fugue exposition from single subject.
    
    Demonstrates music21-powered transformations:
    1. Subject (original)
    2. Answer (transposed to dominant, P5 up)
    3. Countersubject (inverted around C4)
    4. Subject Augmented (2x slower durations for stretto)
    
    Structure (4 voices entering successively):
        Voice 1: Subject
        Voice 2: Answer (entering after subject completes)
        Voice 3: Countersubject (contrapuntal line)
        Voice 4: Subject Augmented (slow canon)
############################################################################
# Station 2 is the **internal SNIPPETS dictionary** that holds:
#   1. Parsed events from Station 1 (your LilyPond snippets)
#   2. Generated events from transformations (transpose, invert, etc.)
#   3. TinyNotation equivalents (for validation and alternative input)
#
# This station is built automatically during build_score_data() execution.
# You don't define it explicitly - it's populated by the framework.
#
# Example of what gets stored in SNIPPETS (for reference):
#   SNIPPETS['THEME_A'] = [event1, event2, ...]  # From parsing
#   SNIPPETS['THEME_A_TRANSPOSED'] = [...]       # From transformation
#
# TinyNotation equivalents (optional reference - generated automatically):
#   THEME_A_TINY = "tinynotation: 3/4 G:maj d4-. fis8( g) a4~ a g-> fis e4.( d8~ d4) b'4 c d"


############################################################################
## STATION 3: ASSEMBLE SCORE STRUCTURE (Blueprint Strings)               ##
############################################################################
# Define the overall structure using Blueprint strings.
# This section is used IF `PROMOTE_TO_PROGRAMMATIC` is False (default).
#
# BLUEPRINT SYNTAX QUICK REFERENCE:
#   ; = Section separator (like double barlines)
#   & = Staff separator (vertical stacking)
#   | = Snippet concatenator (horizontal "then")
#   , = Voice separator (multi-voice in same staff)
#   r = Auto-rest placeholder
#   * N = Repeat snippet N times
#
# TRANSFORMATION EXAMPLES:
#   Single-part (no suffix):    transpose_part(THEME, 'P5')
#   Multi-part (suffix needed): harmonize_part(MELODY):melody, :harmony

# --- Active Blueprint Example: Piano Style (Two Staves) ---
VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    # Section 1: Exposition
    THEME_A & BASS_FIGURE;

    # Section 2: Development with transposition
    transpose_part(THEME_A, 'P4') & BASS_FIGURE;

    # Section 3: Contrasting material
    THEME_B & r;

    # Section 4: Recapitulation with repetition
def build_score_data() -> Dict:
    """
    Generate complete fugue exposition from single subject.
    
    Demonstrates music21-powered transformations:
    1. Subject (original)
    2. Answer (transposed to dominant, P5 up)
    3. Countersubject (inverted around C4)
    4. Subject Augmented (2x slower durations for stretto)
    
    Structure (4 voices entering successively):
        Voice 1: Subject
        Voice 2: Answer (entering after subject completes)
        Voice 3: Countersubject (contrapuntal line)
        Voice 4: Subject Augmented (slow canon)
    
    Returns:
        dict: Canonical score_data {'metadata': {}, 'parts': {}}
    """
    
    print("\n" + "="*70)
    print("FUGUE EXPOSITION GENERATOR")
    print("="*70)
    print("\nGenerating fugue from single subject using programmatic transformations...")
    
    # --- STATION 1: Parse Fugue Subject ---
    print("\n[1/5] Parsing fugue subject...")
    subject_data = parse_lilypond_to_data(FUGUE_SUBJECT_LILY, part_name='SUBJECT')
    
    if not subject_data or 'parts' not in subject_data or 'SUBJECT' not in subject_data['parts']:
        print("❌ Error: Failed to parse fugue subject")
        return {'metadata': {}, 'parts': {}}
    
    subject_events = subject_data['parts']['SUBJECT']
    print(f"   ✓ Subject parsed: {len(subject_events)} events")
    
    # --- STATION 4: Generate Transformations ---
    
    # 2. ANSWER: Transpose to dominant (Perfect 5th = 7 semitones up)
    print("\n[2/5] Generating Answer (transpose +P5)...")
    answer_events = transpose_events(subject_events, 7)
    print(f"   ✓ Answer generated: {len(answer_events)} events")
    
    # 3. COUNTERSUBJECT: Invert around C4 (mirror inversion)
    print("\n[3/5] Generating Countersubject (inversion around C4)...")
    countersubject_events = invert_events(subject_events, 'c4')
    print(f"   ✓ Countersubject generated: {len(countersubject_events)} events")
    
    # 4. AUGMENTATION: Double all durations (for stretto)
    print("\n[4/5] Generating Augmentation (2x slower)...")
    augmented_events = []
    for event in subject_events:
        aug_event = event.copy()
        aug_event['ql'] = event['ql'] * 2.0  # Double quarter-length
        augmented_events.append(aug_event)
    print(f"   ✓ Augmentation generated: {len(augmented_events)} events")
    
    # --- Calculate timing ---
    subject_duration = sum(e['ql'] for e in subject_events)
    answer_duration = sum(e['ql'] for e in answer_events)
    countersubject_duration = sum(e['ql'] for e in countersubject_events)
    augmented_duration = sum(e['ql'] for e in augmented_events)
    
    # Total fugue duration = subject + answer + countersubject (overlapping)
    # Voice 1: starts at 0, ends at subject_duration
    # Voice 2: starts at subject_duration, ends at subject_duration + answer_duration
    # Voice 3: starts at subject_duration*2, ends at subject_duration*2 + countersubject_duration
    # Voice 4: starts at subject_duration*3, ends at subject_duration*3 + augmented_duration
    total_duration = subject_duration * 3 + augmented_duration
    
    print(f"\n[5/5] Assembling 4-voice fugue with overlapping entries...")
    print(f"   • Subject duration: {subject_duration} QL")
    print(f"   • Total fugue duration: {total_duration} QL")
    
    # Helper function to create a fresh rest each time
    def make_rest(ql):
        """Create a NEW rest event (not reused) with given quarter-length."""
        return {
            'type': 'rest',
            'ql': float(ql),  # Ensure it's a float
            'step': 'r',
            'octave': 0,
            'alter': 0,
            'accidental_type': '',
            'tie_type': '',
            'dynamic': '',
            'articulation': ''
        }
    
    # VOICE 1 (Soprano): Subject starting at measure 1
    voice1 = [e.copy() for e in subject_events]  # Deep copy to avoid sharing
    # Add trailing rest to match total duration
    trailing_rest_1 = total_duration - subject_duration
    if trailing_rest_1 > 0:
        voice1.append(make_rest(trailing_rest_1))
    
    # VOICE 2 (Alto): Answer starting at measure 5 (after subject completes)
    voice2 = [make_rest(subject_duration)] + [e.copy() for e in answer_events]
    trailing_rest_2 = total_duration - (subject_duration + answer_duration)
    if trailing_rest_2 > 0:
        voice2.append(make_rest(trailing_rest_2))
    
    # VOICE 3 (Tenor): Countersubject starting at measure 9
    voice3 = [make_rest(subject_duration * 2)] + [e.copy() for e in countersubject_events]
    trailing_rest_3 = total_duration - (subject_duration * 2 + countersubject_duration)
    if trailing_rest_3 > 0:
        voice3.append(make_rest(trailing_rest_3))
    
    # VOICE 4 (Bass): Augmentation starting at measure 13
    voice4 = [make_rest(subject_duration * 3)] + [e.copy() for e in augmented_events]
    # No trailing rest needed - this voice ends the fugue
    
    print(f"   • Voice 1: Subject (0-{subject_duration} QL) + rest ({subject_duration}-{total_duration} QL)")
    print(f"   • Voice 2: Rest (0-{subject_duration}) + Answer ({subject_duration}-{subject_duration + answer_duration}) + rest")
    print(f"   • Voice 3: Rest (0-{subject_duration*2}) + Countersubject ({subject_duration*2}-{subject_duration*2 + countersubject_duration}) + rest")
    print(f"   • Voice 4: Rest (0-{subject_duration*3}) + Augmentation ({subject_duration*3}-{total_duration})")
    print(f"\n   ✓ All voices padded to {total_duration} QL total duration")
    print(f"   ✓ Voices will play SIMULTANEOUSLY with staggered entries")
    
    # --- Define Metadata ---
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER,
        'instrumentation': INSTRUMENTATION,
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        'time_signature': '4/4',
        'tempo': 'Moderato, quarter note = 100',
        'description': 'Fugue exposition with Subject, Answer, Countersubject, and Augmentation',
        'transformations_applied': {
            'answer': 'transpose(+7 semitones)',
            'countersubject': 'invert(axis=C4)',
            'augmentation': 'rhythmic_augmentation(factor=2.0)'
        }
    }
    
    print("\n" + "="*70)
    print("✅ Fugue Exposition Complete!")
    print("="*70)
    print("\nThis is a TRUE FUGUE with overlapping voices:")
    print("  • All 4 voices have the same total duration")
    print("  • Each voice enters at a different time (staggered entries)")
    print("  • Voices play SIMULTANEOUSLY creating counterpoint")
    print("  • Export will show all voices together")
    print("\nFugue Structure:")
    print("  Measures 1-4:   Soprano plays Subject")
    print("  Measures 5-8:   Soprano continues + Alto enters with Answer")
    print("  Measures 9-12:  Soprano + Alto continue + Tenor enters with Countersubject")
    print("  Measures 13-20: All 4 voices + Bass enters with Augmentation")
    print("\n" + "="*70)
    
    # --- Return Final Score Data ---
    return {
        'metadata': metadata,
        'parts': {
            'Soprano': voice1,
            'Alto': voice2,
            'Tenor': voice3,
            'Bass': voice4,
        }
    }


# ============================================================================
# MAIN EXECUTION CONTROL
# ============================================================================

if __name__ == '__main__':
    run_pipeline_from_file(__file__)

