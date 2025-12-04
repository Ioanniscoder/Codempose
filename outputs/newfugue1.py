"""
NEWFUGUE1 STUDY: Newfugue1 Study
=================================

Codempose Four-Station Workflow demonstration.
Uses Blueprint Strings (Station 3) by default.
Set PROMOTE_TO_PROGRAMMATIC = True to use Station 4 instead.
"""

import _study_path  # Auto-path setup

# ============================================================================
# IMPORTS
# ============================================================================

from typing import Dict
# Essential for Station 3 (Blueprint)
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file

# Optional imports for Station 4 / advanced use (uncomment as needed)
from src.music_data import data_to_part, part_to_data
from src.transformations import transpose_part, invert_part, retrograde_part
# from src.harmonic_engine import harmonize_melody
# from src.lib.station4_music21_examples import example_canon_at_interval
# from src.lib.TONAL_HARMONY_TEMPLATES import PROGRESSION_I_IV_V_I


# ============================================================================
# !! STATION 4 PROMOTION TOGGLE !!
# ============================================================================
# Set this to True to bypass Station 3 (Blueprint) and use Station 4
# (Programmatic Composition) defined further below.
PROMOTE_TO_PROGRAMMATIC = True  # ← FUGUE REQUIRES STATION 4 (staggered voice entries)
# ============================================================================


# ============================================================================
# METADATA
# ============================================================================
# Based on proven patterns from thirteenth.py and fourteenth.py

TITLE = "Four-Voice Fugue Exposition"
COMPOSER = "Codempose Framework"
OPUS_NUMBER = "NEWFUGUE1"
INSTRUMENTATION = "Four-Voice Fugue (SATB)"


############################################################################
## STATION 1: DEFINE MUSICAL IDEAS (LilyPond Snippets)                     ##
############################################################################
# Define your musical building blocks using LilyPond notation.
# These snippets will be parsed into Station 2's internal library.
#
# BEST PRACTICES (from old studies):
# - Use descriptive variable names ending with _LILY
# - Include \key, \time, \tempo in first snippet
# - Add dynamics, articulations, ornaments to showcase features
# - Keep snippets focused and reusable
#
# AUTOMATIC REHEARSAL MARKS:
# - Snippets named "PREFIX_SUFFIX" auto-generate \mark "SUFFIX" in PDF
#   Example: "THEME_A" → displays mark "A", "INTRO_Main" → displays "Main"
# - Transformations (transpose, invert) and repeats (*) don't generate marks
# - Explicit \mark in snippet OVERRIDES automatic injection
#   Example: \mark \markup { \bold \box "Custom" } prevents auto-mark

# ============================================================================
# FUGUE SUBJECT - Main melodic idea (4 measures, C major)
# ============================================================================
# Subject uses middle-range pitches (C4-G4) so it works in all voices
# when transposed to their respective ranges.

FUGUE_SUBJECT_LILY = r"""
{
    \key c \major
    \time 4/4
    \tempo "Moderato" 4=100
    c'4 e' g'8 f' e' d' |          % Rising then falling contour
    c'4 d' e'2 |                    % Stepwise motion
    f'4 e' d' c' |                  % Descending line
    b2 c'2                          % Cadence on tonic
}
""".strip()

# ============================================================================
# COUNTERSUBJECT - Complementary melody (algorithmically derived)
# ============================================================================
# This is the INVERTED subject with rhythmic variation for independence.
# When subject ascends, countersubject descends (contrary motion).
# Active rhythm (eighths) complements subject's sustained notes.

COUNTERSUBJECT_LILY = r"""
{
    \key c \major
    \time 4/4
    c'8 b a g f4 g8 a |            % Inverted opening, eighth-note motion
    b4 a g2 |                       % Contrary to subject's ascent
    d'8 c' b a g4 a |               % Active rhythm vs subject's quarters
    f2 e2                           % Cadence (third below subject)
}
""".strip()

# ----------------------------------------------------------------------------
# TEMPLATE EXAMPLES (commented out - preserved for educational reference)
# ----------------------------------------------------------------------------
# These show Station 3 Blueprint patterns. For fugues, use Station 4 instead.

# # Richer default example (G major, 3/4 time with musical expression)
# TEMPLATE_THEME_A_LILY = r"""
# \relative c'' {
#     \key g \major
#     \time 3/4
#     \tempo "Andante" 4=90
#     d4-.\p( fis8 g) a4~ |      % Staccato, piano, slur, tie
#     a4 g4->( fis) |             % Accent, phrase
#     e4.( d8~ d4) |              % Dotted rhythm
#     b'4\f c4 d4                % Forte, climax
# }
# """.strip()

# # Contrasting phrase
# TEMPLATE_THEME_B_LILY = r"""
# \relative c' {
#     \key g \major
#     \time 3/4
#     g4( fis e) |
#     d2.~ |
#     d4 e fis |
#     g2.
# }
# """.strip()

# # Bass figure
# TEMPLATE_BASS_FIGURE_LILY = r"""
# \relative c {
#     \clef bass
#     \key g \major
#     \time 3/4
#     g4 d' b |
#     c2 b4 |
#     a4 g fis |
#     g2.
# }
# """.strip()

# ----------------------------------------------------------------------------
# CREATIVE EXAMPLES (from second.py study)
# ----------------------------------------------------------------------------
# Real musical compositions - uncomment to use as starting points!

# Short, rhythmic motif - great for transformations
# SOURCE_THEME_LILY = r"""
# \relative c' {
#     \time 4/4
#     \key c \major
#     e4 b4 e'4 b4
# }
# """.strip()

# Expressive melodic phrase with interesting intervals and rhythm
# SOURCE_MELODY_LILY = r"""
# \relative e {
#     \time 6/4
#     \key c \major
#     \tempo 4=90
#     e2 bes4 c2 r4 |
#     e2 fis4 e2 r4 |
#     b2. f'2. |
#     e2. c2. |
#     e2 b2 c2
# }
# """.strip()


############################################################################
## STATION 2: INTERNAL SNIPPET LIBRARY (Conceptual)                      ##
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
# TEMPLATE STATION 3 - COMMENTED OUT (Using Station 4 for this fugue)
#
# NOTE: Blueprint syntax CANNOT handle staggered voice entries (fugues).
# Station 3 is designed for parallel structures (melody + bass, SATB hymns).
# For fugues with successive voice entrances, Station 4 is REQUIRED.
#
# BLUEPRINT SYNTAX QUICK REFERENCE (for non-fugue compositions):
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

# --- TEMPLATE: Blueprint Example (commented - preserved for reference) ---
# VOICE_STAVE_DEF = "Melody & Bass"

# VOICE_STAVE_DATA = """
#     # Section 1: Exposition
#     THEME_A & BASS_FIGURE;
#
#     # Section 2: Development with transposition
#     transpose_part(THEME_A, 'P4') & BASS_FIGURE;
#
#     # Section 3: Contrasting material
#     THEME_B & r;
#
#     # Section 4: Recapitulation with repetition
#     THEME_A * 2 & BASS_FIGURE * 2
# """

# --- Variant 1: Single Staff (Solo) ---
# VOICE_STAVE_DEF = "Solo Melody"
# VOICE_STAVE_DATA = """
#     THEME_A;
#     THEME_B;
#     transpose_part(THEME_A, 'P5')
# """

# --- Variant 2: SATB Hymn (Multi-Voice, Two Staves) ---
# VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
# VOICE_STAVE_DATA = """
#     SOPRANO_A, ALTO_A & TENOR_A, BASS_A;
#     SOPRANO_B, ALTO_B & TENOR_B, BASS_B
# """
# Note: Requires defining SOPRANO_A, ALTO_A, TENOR_A, BASS_A, etc. in Station 1

# --- Variant 3: Harmonization (Multi-Part Transformation) ---
# VOICE_STAVE_DEF = "Melody & Harmony"
# VOICE_STAVE_DATA = """
#     THEME_A & r;
#     harmonize_part(THEME_A, 'I-IV-V-I', 'G'):melody
#     &
#     harmonize_part(THEME_A, 'I-IV-V-I', 'G'):harmony
# """

# --- Variant 4: Complex Form (ABA with Coda) ---
# VOICE_STAVE_DEF = "Treble & Bass"
# VOICE_STAVE_DATA = """
#     THEME_A & BASS_FIGURE;                          # A section
#     THEME_B & r;                                    # B section
#     transpose_part(THEME_A, 'P8') & BASS_FIGURE;   # A' section (octave higher)
#     THEME_A * 2 & BASS_FIGURE * 2                  # Coda (repeated)
# """


# --------------------------------------------------------------------------
# TEMPLATE: Blueprint Assembly Function (Processes Station 3)
# --------------------------------------------------------------------------
# COMMENTED OUT - Using Station 4 instead for fugue composition
# Preserved for educational reference showing how Station 3 works

def build_score_data_TEMPLATE_STATION3() -> Dict:
    """
    Builds score using Station 3 Blueprint definition.
    
    This is APPROACH 1 (RECOMMENDED): The composer-first method.
    
    Four-Station Workflow:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    1. Parse Station 1 snippets → populate SNIPPETS (Station 2)
    2. Process Blueprint strings (VOICE_STAVE_DEF + VOICE_STAVE_DATA)
    3. Apply transformations → add results to SNIPPETS (Station 2 grows)
    4. Assemble final score_data from SNIPPETS library
    
    Returns:
        dict: Canonical score_data {'metadata': {}, 'parts': {}}
    """
    
    print("\n" + "="*70)
    print("NEWFUGUE1 STUDY: Blueprint String Framework")
    print("="*70)
    
    # --- STATION 1 → STATION 2: Parse LilyPond Snippets ---
    print("\n[Station 1 Parsing] Populating Internal Snippet Library (Station 2)...")
    
    # Define which snippets to parse (matches your Station 1 definitions)
    snippets_to_parse = {
        'THEME_A': THEME_A_LILY,
        'THEME_B': THEME_B_LILY,
        'BASS_FIGURE': BASS_FIGURE_LILY,
        'HARMONY_CHORDS': HARMONY_CHORDS_LILY,
    }
    
    # Initialize Station 2 library
    SNIPPETS: Dict[str, list] = {}
    
    # Parse each snippet and populate SNIPPETS
    for name, lily_code in snippets_to_parse.items():
        try:
            # Parse LilyPond → canonical data structure
            parsed = parse_lilypond_to_data(lily_code, part_name=name)
            
            # Extract events from parsed data
            if parsed and 'parts' in parsed and name in parsed['parts']:
                SNIPPETS[name] = parsed['parts'][name]
                event_count = len(SNIPPETS[name])
                print(f"  ✓ {name}: {event_count} events")
            else:
                print(f"  ⚠️  {name}: Parse failed or no events found")
                SNIPPETS[name] = []  # Empty list prevents KeyError later
                
        except Exception as e:
            print(f"  ❌ {name}: Error: {e}")
            SNIPPETS[name] = []
    
    print(f"\n  → Station 2 Library: {{len(SNIPPETS)}} snippets ready")
    
    # --- Define Score Metadata ---
    # Based on patterns from thirteenth.py, fourteenth.py
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER,
        'instrumentation': INSTRUMENTATION,
        'key_signature': {'tonic': 'g', 'mode': 'major'},  # Inferred from snippets
        'time_signature': '3/4',                              # Inferred from snippets
        'tempo': 'Andante, quarter note = 90',               # From \tempo directive
        'original_snippets': snippets_to_parse,              # For explicit \mark detection
    }
    
    # --- STATION 3: Assemble Score using Blueprint Strings ---
    print("\n[Station 3 Processing] Building score from Blueprint strings...")
    print(f"  • Layout: {{VOICE_STAVE_DEF}}")
    print(f"  • Structure: {{len(VOICE_STAVE_DATA.strip().split(';'))}} sections")
    
    # Call the Blueprint processor
    # This will:
    #   - Parse VOICE_STAVE_DATA
    #   - Execute any transformations (adding results to SNIPPETS)
    #   - Assemble final score from SNIPPETS
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
    
    print("\n" + "="*70)
    print("✅ Station 3 Blueprint Assembly Complete")
    print("="*70)
    
    return score_data


############################################################################
## STATION 4: PROGRAMMATIC COMPOSITION (Alternative to Station 3)        ##
############################################################################
# Define score structure entirely using Python code.
# This section is used IF `PROMOTE_TO_PROGRAMMATIC` is True.
#
# Based on patterns from first.py, seventh.py, tenth.py

def build_score_data() -> Dict:
    """
    STATION 4: Four-Voice Fugue Exposition
    
    Demonstrates programmatic fugue composition with staggered voice entries.
    
    Structure:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Soprano: Subject (C5)     → Countersubject → Free material
    Alto:    Rest → Answer (G4, P5 up)  → Countersubject → Free
    Tenor:   Rest → Rest → Subject (C4) → Countersubject
    Bass:    Rest → Rest → Rest → Answer (G3, P5 up)
    
    Voice Ranges (proper SATB spacing):
    - Soprano: C5-G5 (subject starting at middle C')
    - Alto: G4-D5 (answer a fifth up from subject)
    - Tenor: C4-G4 (subject an octave below soprano)
    - Bass: G3-D4 (answer an octave below alto)
    
    Returns:
        dict: Canonical score_data {'metadata': {}, 'parts': {}}
    """
    
    print("\n" + "="*70)
    print("FOUR-VOICE FUGUE EXPOSITION (Station 4)")
    print("="*70)

    # --- Parse Subject and Countersubject ---
    print("\n[Station 1] Parsing fugue materials...")
    
    subject_data = parse_lilypond_to_data(FUGUE_SUBJECT_LILY, part_name='Subject')
    counter_data = parse_lilypond_to_data(COUNTERSUBJECT_LILY, part_name='Countersubject')
    
    subject_events = subject_data['parts']['Subject']
    counter_events = counter_data['parts']['Countersubject']
    
    print(f"  ✓ Subject: {len(subject_events)} events")
    print(f"  ✓ Countersubject: {len(counter_events)} events")
    
    # --- Calculate durations for rest generation ---
    subject_duration = sum(e.get('ql', 0) for e in subject_events if e.get('type') != 'barline')
    
    def make_rest(duration_ql):
        """
        Generate properly structured rest events for any duration.
        
        Splits long durations into standard LilyPond rest values to avoid
        'approximate duration' warnings and ensure correct measure alignment.
        
        Args:
            duration_ql: Total rest duration in quarter-note lengths
        
        Returns:
            List of rest event dictionaries using standard durations
        """
        rests = []
        remaining = duration_ql
        
        # Split into standard durations (descending order for efficiency)
        # Whole note rest = 4.0 QL (most common for 4/4 time)
        while remaining >= 4.0:
            rests.append({'type': 'rest', 'ql': 4.0, 'step': None, 'octave': None, 'alter': 0})
            remaining -= 4.0
        
        # Half note rest = 2.0 QL
        while remaining >= 2.0:
            rests.append({'type': 'rest', 'ql': 2.0, 'step': None, 'octave': None, 'alter': 0})
            remaining -= 2.0
        
        # Quarter note rest = 1.0 QL
        while remaining >= 1.0:
            rests.append({'type': 'rest', 'ql': 1.0, 'step': None, 'octave': None, 'alter': 0})
            remaining -= 1.0
        
        # Eighth note rest = 0.5 QL
        while remaining >= 0.5:
            rests.append({'type': 'rest', 'ql': 0.5, 'step': None, 'octave': None, 'alter': 0})
            remaining -= 0.5
        
        # Sixteenth note rest = 0.25 QL
        while remaining >= 0.25:
            rests.append({'type': 'rest', 'ql': 0.25, 'step': None, 'octave': None, 'alter': 0})
            remaining -= 0.25
        
        # Handle any tiny remainder (should be rare with proper durations)
        if remaining > 0.01:  # Tolerance for floating-point errors
            rests.append({'type': 'rest', 'ql': remaining, 'step': None, 'octave': None, 'alter': 0})
        
        return rests
    
    # --- Generate Answer (subject transposed up P5) ---
    print("\n[Station 4] Generating transformations...")
    
    subject_part = data_to_part(subject_events, {})
    answer_part = transpose_part(subject_part, 'P5')  # Up a perfect fifth
    answer_events = part_to_data(answer_part)
    
    print(f"  ✓ Answer (P5 up): {len(answer_events)} events")
    
    # --- Transpose materials to proper voice ranges ---
    # Subject is at C5 (c'), which is correct for Soprano
    # For Tenor, transpose DOWN an octave (P-8)
    subject_part_tenor = data_to_part(subject_events, {})
    subject_tenor = transpose_part(subject_part_tenor, 'P-8')  # Octave down
    subject_tenor_events = part_to_data(subject_tenor)
    
    # Answer is at G5 (g'), correct for Alto
    # For Bass, transpose DOWN an octave (P-8)
    answer_part_bass = data_to_part(answer_events, {})
    answer_bass = transpose_part(answer_part_bass, 'P-8')  # Octave down
    answer_bass_events = part_to_data(answer_bass)
    
    # Countersubject ranges (adjust for each voice)
    counter_part_soprano = data_to_part(counter_events, {})
    counter_soprano = transpose_part(counter_part_soprano, 'P8')  # Octave up for soprano range
    counter_soprano_events = part_to_data(counter_soprano)
    
    counter_part_alto = data_to_part(counter_events, {})
    counter_alto = transpose_part(counter_part_alto, 'P5')  # Up P5 for alto range
    counter_alto_events = part_to_data(counter_alto)
    
    counter_tenor_events = counter_events  # Original range works for tenor
    
    print(f"  ✓ Subject (Tenor octave): {len(subject_tenor_events)} events")
    print(f"  ✓ Answer (Bass octave): {len(answer_bass_events)} events")
    print(f"  ✓ Countersubjects transposed for each voice")
    
    # --- Assemble Fugue Voices ---
    print("\n[Station 4] Assembling 4-voice fugue exposition...")
    
    # SOPRANO: Subject (m.1-4) → Countersubject (m.5-8)
    soprano_part = subject_events + counter_soprano_events
    
    # ALTO: Rest (m.1-4) → Answer (m.5-8) → Countersubject (m.9-12)
    alto_part = make_rest(subject_duration) + answer_events + counter_alto_events
    
    # TENOR: Rest (m.1-8) → Subject (m.9-12) → Countersubject (m.13-16)
    tenor_part = make_rest(subject_duration * 2) + subject_tenor_events + counter_tenor_events
    
    # BASS: Rest (m.1-12) → Answer (m.13-16)
    bass_part = make_rest(subject_duration * 3) + answer_bass_events
    
    print(f"  • Soprano: {len(soprano_part)} events")
    print(f"  • Alto: {len(alto_part)} events")
    print(f"  • Tenor: {len(tenor_part)} events")
    print(f"  • Bass: {len(bass_part)} events")
    
    # --- Define Metadata ---
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER,
        'instrumentation': INSTRUMENTATION,
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        'time_signature': '4/4',
        'tempo': 'Moderato, quarter note = 100',
        'source_file': __file__,
    }

    print("\n" + "="*70)
    print("✅ Fugue Exposition Complete!")
    print("="*70)

    # --- Return Final Score Data ---
    return {
        'metadata': metadata,
        'parts': {
            'Soprano': soprano_part,
            'Alto': alto_part,
            'Tenor': tenor_part,
            'Bass': bass_part,
        }
    }


# --- Additional Station 4 Functions (Optional) ---

def build_score_data_with_library() -> Dict:
    """
    Station 4 example using src/lib/ transformation libraries.
    
    Demonstrates integration with advanced music21-based tools.
    Requires uncommenting library imports at top of file.
    """
    print("\n[Station 4 + Library] Advanced programmatic composition...")
    
    # Example workflow:
    # 1. Parse base snippet
    # 2. Apply library transformation (e.g., canon_at_interval)
    # 3. Combine with original
    # 4. Return score_data
    
    # Implementation left as exercise - see eleventh_example.py for reference
    
    return {
        'metadata': {'title': TITLE},
        'parts': {'Main': []}
    }


# ============================================================================
# MAIN EXECUTION CONTROL
# ============================================================================

if __name__ == '__main__':
    # The framework automatically calls build_score_data() by default.
    # To use Station 4 instead, set PROMOTE_TO_PROGRAMMATIC = True above,
    # then manually rename build_score_data_programmatic to build_score_data.
    run_pipeline_from_file(__file__)
