"""
NEWFUGUE STUDY: Newfugue Study
===============================

Codempose Four-Station Workflow demonstration.
Uses Blueprint Strings (Station 3) by default.
Set PROMOTE_TO_PROGRAMMATIC = True to use Station 4 instead.

# ============================================================================
# TEMPLATE ARCHITECTURE MAP
# ============================================================================
# This template follows the Codempose Four-Station Workflow:
#
# STATION 1 (DEFINE): LilyPond snippets → parsed to event dicts
#   ↓ Framework automatically populates SNIPPETS library
# STATION 2 (LIBRARY): SNIPPETS dictionary holds all parsed/transformed events
#   ↓ Used by Station 3 Blueprint or Station 4 Programmatic
# STATION 3 (ASSEMBLE): Blueprint strings define score structure
#   ↓ OR (if PROMOTE_TO_PROGRAMMATIC=True) ↓
# STATION 4 (PROGRAMMATIC): Python functions build score with logic
#   ↓ Both stations output: {'parts': {'VoiceName': [events, ...]}}
# RENDERING: Framework converts events → LilyPond/MusicXML/MIDI/PDF
#
# DATA LIFECYCLE:
#   LilyPond string → parse → event dict list → music21 objects → output formats
#
# EVENT DICT STRUCTURE (What you work with internally):
#   [{'type': 'note', 'step': 'd', 'octave': 5, 'alter': 0, 'ql': 1.0, ...},
#    {'type': 'rest', 'ql': 2.0, 'step': 'r', ...},
#    {'type': 'barline', 'ql': 0.0, ...}]
# ============================================================================
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
from src.lib.station4_music21_examples import example_fugue_exposition
# from src.lib.TONAL_HARMONY_TEMPLATES import PROGRESSION_I_IV_V_I

# ============================================================================
# RELATED DOCUMENTATION
# ============================================================================
# Quick Recipes:        outputs/TEMPLATES/ADVANCED_MUSIC21_GUIDE.md
# Tonal Harmony:        src/lib/TONAL_HARMONY_TEMPLATES.py
# Music21 Patterns:     src/lib/MUSIC21_API_TEMPLATES.py
# Station 4 Examples:   src/lib/station4_music21_examples.py
# Working Studies:      studies/100th.py, studies/fugue.py
# ============================================================================


# ============================================================================
# !! STATION 4 PROMOTION TOGGLE !!
# ============================================================================
# Set this to True to bypass Station 3 (Blueprint) and use Station 4
# (Programmatic Composition) defined further below.
PROMOTE_TO_PROGRAMMATIC = False
# ============================================================================


# ============================================================================
# METADATA
# ============================================================================
# Based on proven patterns from thirteenth.py and fourteenth.py

TITLE = "NEWFUGUE Study: Newfugue Study"
COMPOSER = "Codempose Framework"
OPUS_NUMBER = "NEWFUGUE"
INSTRUMENTATION = "Piano"  # or "SATB Choir", "String Quartet", etc.


# ============================================================================
# QUICK START GUIDE
# ============================================================================
# NEW USERS:
# 1. Edit THEME_A_LILY in Station 1 below (use LilyPond notation)
# 2. Edit VOICE_STAVE_DATA in Station 3 (use snippet names like THEME_A)
# 3. Run: python this_file.py
# 4. Check outputs/ folder for PDF, MIDI, MusicXML
#
# ADVANCED USERS:
# - Set PROMOTE_TO_PROGRAMMATIC = True
# - Implement build_score_data_programmatic() in Station 4
# - Use music21 API for algorithmic composition
#
# TROUBLESHOOTING:
# - Import errors? Run: python setup_paths.py
# - No output? Check Station 1 LilyPond syntax (must be valid)
# - See outputs/TEMPLATES/ADVANCED_MUSIC21_GUIDE.md for recipes
# ============================================================================


############################################################################
## STATION 1: DEFINE MUSICAL IDEAS (LilyPond Snippets)                     ##
############################################################################
# Define your musical building blocks using LilyPond notation.
# These snippets will be parsed into Station 2's internal library.
#
# LILYPOND → EVENT DICT FORMAT:
# Your LilyPond strings become event dictionaries like:
#   d4      → {'type': 'note', 'step': 'd', 'octave': 4, 'ql': 1.0, ...}
#   d4.     → {'type': 'note', 'step': 'd', 'octave': 4, 'ql': 1.5, ...}  # Dotted
#   r4      → {'type': 'rest', 'ql': 1.0, 'step': 'r', ...}
#   <c e g>4 → {'type': 'chord', 'pitches': [...], 'ql': 1.0, ...}
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
#   Example: \mark \markup {{ \bold \box "Custom" }} prevents auto-mark

# ============================================================================
# FUGUE SUBJECT - Main melodic idea (this is your creative input!)
# ============================================================================
# A good fugue subject should be:
# - Distinctive and memorable
# - Works in different keys (for the Answer)
# - Has clear rhythmic character
# - Not too long (2-4 measures typically)

FUGUE_SUBJECT_LILY = r"""
\relative c' {
    \key c \major
    \time 4/4
    \tempo "Moderato" 4=100
    c4 e g8 f e d |          % Rising then falling contour
    c4 d e2 |                 % Stepwise motion
    f4 e d c |                % Descending line
    b2 c2                     % Cadence on tonic
}
""".strip()

# COUNTERSUBJECT - Melody that accompanies later entries
# This should complement the subject rhythmically and melodically
COUNTERSUBJECT_LILY = r"""
\relative c' {
    \key c \major
    \time 4/4
    r4 c8 d e4 d8 c |         % Counter-rhythm to subject
    b4 c d2 |                  % Contrary motion
    e4 d c b |                 % Descending against subject
    a2 g2                      % Cadence
}
""".strip()

# ----------------------------------------------------------------------------
# ORIGINAL TEMPLATE THEMES (Commented out - keep for reference)
# ----------------------------------------------------------------------------
# Richer default example (G major, 3/4 time with musical expression)
# THEME_A_LILY = r"""
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

# Contrasting phrase
# THEME_B_LILY = r"""
# \relative c' {
#     \key g \major
#     \time 3/4
#     g4( fis e) |
#     d2.~ |
#     d4 e fis |
#     g2.
# }
# """.strip()

# Bass figure
# BASS_FIGURE_LILY = r"""
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

# Harmonic support (chords)
# HARMONY_CHORDS_LILY = r"""
# \relative c' {
#     \key g \major
#     \time 3/4
#     <g b d>2. |
#     <a c e>2. |
#     <g b d>2.
# }
# """.strip()

# Add more snippets here as your composition grows...

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
# WHAT GETS STORED (for reference):
#   SNIPPETS['THEME_A'] = [event1, event2, ...]  # From parsing THEME_A_LILY
#   SNIPPETS['THEME_A_TRANSPOSED'] = [...]       # From transformation
#
# TRANSFORMATION CACHING (How multi-part transformations work):
#
# Example: harmonize_part(MELODY, 'I-IV-V'):melody
# Step 1: Framework calls harmonize_part(MELODY, 'I-IV-V')
# Step 2: Function returns Score with parts['melody'] and parts['harmony']
# Step 3: Framework caches BOTH parts in SNIPPETS:
#         SNIPPETS['harmonize_part(MELODY,I-IV-V):melody'] = [events...]
#         SNIPPETS['harmonize_part(MELODY,I-IV-V):harmony'] = [events...]
# Step 4: :melody suffix extracts first part
# Step 5: Subsequent calls with same args are FREE (cached lookup)
#
# IMPORTANT: Always use suffix when function returns multiple parts!
#
# TinyNotation equivalents (optional reference - generated automatically):
#   THEME_A_TINY = "tinynotation: 3/4 G:maj d4-. fis8( g) a4~ a g-> fis e4.( d8~ d4) b'4 c d"


############################################################################
## STATION 3: ASSEMBLE SCORE STRUCTURE (Blueprint Strings)               ##
############################################################################
# Define the overall structure using Blueprint strings.
# This section is used IF `PROMOTE_TO_PROGRAMMATIC` is False (default).
#
# BLUEPRINT SYNTAX VISUAL GUIDE:
#
# Vertical stacking (&):
#   MELODY & BASS    →    [MELODY staff]
#                         [BASS staff]
#
# Horizontal concat (|):
#   A | B | A        →    [A-B-A in sequence on same staff]
#
# Sections (;):
#   A & B ; C & D    →    Section 1: A/B staves, Section 2: C/D staves
#
# Multi-voice (,):
#   A, B             →    Voice 1: A  } same staff
#                         Voice 2: B  }
#
# Repeats (*):
#   THEME * 3        →    THEME | THEME | THEME
#
# TRANSFORMATION EXAMPLES:
#   Single-part (no suffix):    transpose_part(THEME, 'P5')
#   Multi-part (suffix needed): harmonize_part(MELODY):melody, :harmony
#
# For more examples, see:
# - ADVANCED_MUSIC21_GUIDE.md § "Multi-Part Transformations"
# - TONAL_HARMONY_TEMPLATES.py: harmonize_with_roman_numerals()

# ============================================================================
# STATION 3 OPTION: BLUEPRINT-BASED FUGUE
# ============================================================================
# For a simple fugue using Blueprint strings (no programming required):

VOICE_STAVE_DEF = "Soprano & Alto & Tenor & Bass"

VOICE_STAVE_DATA = """
    # EXPOSITION: Each voice enters with Subject or Answer
    
    # Measure 1-4: Soprano enters with Subject
    FUGUE_SUBJECT & r & r & r;
    
    # Measure 5-8: Alto enters with Answer (at 5th), Soprano plays Countersubject
    COUNTERSUBJECT & transpose_part(FUGUE_SUBJECT, 'P5') & r & r;
    
    # Measure 9-12: Tenor enters with Subject, Alto plays Countersubject
    r & COUNTERSUBJECT & FUGUE_SUBJECT & r;
    
    # Measure 13-16: Bass enters with Answer, Tenor plays Countersubject
    r & r & COUNTERSUBJECT & transpose_part(FUGUE_SUBJECT, 'P5')
"""

# ============================================================================
# ORIGINAL TEMPLATE BLUEPRINTS (Commented out - keep for reference)
# ============================================================================
# --- Active Blueprint Example: Piano Style (Two Staves) ---
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
# Blueprint Assembly Function (Processes Station 3)
# --------------------------------------------------------------------------
def build_score_data() -> Dict:
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
    print("NEWFUGUE STUDY: Blueprint String Framework")
    print("="*70)
    
    # --- STATION 1 → STATION 2: Parse LilyPond Snippets ---
    print("\n[Station 1 Parsing] Populating Internal Snippet Library (Station 2)...")
    
    # Define which snippets to parse (matches your Station 1 definitions)
    snippets_to_parse = {
        'FUGUE_SUBJECT': FUGUE_SUBJECT_LILY,
        'COUNTERSUBJECT': COUNTERSUBJECT_LILY,
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
    
    print(f"\n  → Station 2 Library: {len(SNIPPETS)} snippets ready")
    
    # --- Define Score Metadata ---
    # Based on patterns from thirteenth.py, fourteenth.py
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER,
        'instrumentation': INSTRUMENTATION,
        'key_signature': {'tonic': 'c', 'mode': 'major'},  # From fugue subject
        'time_signature': '4/4',                              # From fugue subject
        'tempo': 'Moderato, quarter note = 100',             # From \tempo directive
        'original_snippets': snippets_to_parse,              # For explicit \mark detection
        'source_file': __file__,                             # For Station 2 library naming
    }
    
    # --- STATION 3: Assemble Score using Blueprint Strings ---
    print("\n[Station 3 Processing] Building score from Blueprint strings...")
    print(f"  • Layout: {VOICE_STAVE_DEF}")
    print(f"  • Structure: {len(VOICE_STAVE_DATA.strip().split(';'))} sections")
    
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
# STATION 4 DATA CONVERSION WORKFLOW:
#
# Step 1: Parse LilyPond to events
#   snippet_events = parse_lilypond_to_data(THEME)['parts']['theme']
#   Type: list of dicts
#
# Step 2: Convert to music21 (if using music21 API)
#   part = data_to_part(snippet_events)
#   Type: music21.stream.Part
#
# Step 3: Apply transformations (music21 functions)
#   part.transpose(interval.Interval('P5'), inPlace=True)
#   Type: still music21.stream.Part (modified)
#
# Step 4: Convert back to events
#   result_events = part_to_data(part)
#   Type: list of dicts (compatible with framework)
#
# Step 5: Return structure
#   return {'parts': {'VoiceName': result_events}}
#   Type: dict with 'parts' key (required by framework)
#
# For harmonization examples, see:
# - ADVANCED_MUSIC21_GUIDE.md § "Tonal Harmony Implementation"
# - TONAL_HARMONY_TEMPLATES.py: harmonize_with_roman_numerals()
#
# Based on patterns from first.py, seventh.py, tenth.py

def build_score_data_programmatic() -> Dict:
    """
    Builds a complete fugue programmatically using music21 functions.
    
    This demonstrates STATION 4 power - algorithmic fugue composition
    using the example_fugue_exposition() function from the template library.
    
    Workflow:
    1. Parse fugue subject from LilyPond
    2. Generate Answer, Countersubject, variations automatically
    3. Assemble 4-voice fugue exposition with proper voice entries
    4. Return complete score structure
    """
    
    print("\n" + "="*70)
    print("NEWFUGUE STUDY: Programmatic Fugue Composition (Station 4)")
    print("="*70)

    # Import necessary functions (uncomment the imports at top first!)
    from src.lib.station4_music21_examples import example_fugue_exposition
    from src.voice_documentation import register_and_document_voice
    
    # --- Parse the fugue subject ---
    print("\n[Station 1] Parsing fugue subject...")
    subject_data = parse_lilypond_to_data(FUGUE_SUBJECT_LILY, part_name='Subject')
    subject_events = subject_data['parts']['Subject']
    print(f"  ✓ FUGUE_SUBJECT: {len(subject_events)} events")
    
    # Optional: Parse countersubject if you want to use your custom one
    counter_data = parse_lilypond_to_data(COUNTERSUBJECT_LILY, part_name='Countersubject')
    custom_counter_events = counter_data['parts']['Countersubject']
    print(f"  ✓ COUNTERSUBJECT: {len(custom_counter_events)} events")
    
    # --- Generate fugue parts using music21 ---
    print("\n[Station 4] Generating fugue exposition...")
    
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER,
        'instrumentation': 'Four-Voice Fugue',
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        'time_signature': '4/4',
        'tempo': 'Moderato, quarter note = 100',
        'source_file': __file__,
    }
    
    voice_lookup = {}
    
    # Generate all fugue components automatically
    fugue_parts = example_fugue_exposition(subject_events, voice_lookup, metadata)
    
    print(f"  ✓ Generated Subject, Answer, Countersubject, Augmented Subject")
    
    # --- Build the fugue exposition structure ---
    # Classic fugue: S-A-S-A pattern with counterpoint
    print("\n[Assembly] Creating 4-voice fugue exposition...")
    
    # Helper: create rest events
    def make_rest(ql):
        return [{'type': 'rest', 'ql': ql, 'step': None, 'octave': None, 'alter': 0}]
    
    # Calculate lengths for proper timing
    subject_length = sum(e['ql'] for e in fugue_parts['subject'])
    
    # SOPRANO: Subject (m.1) → Countersubject with Alto's Answer (m.5) → free material
    soprano_part = (
        fugue_parts['subject'] +                    # m.1-4: Subject entry
        custom_counter_events                        # m.5-8: Countersubject against Alto
    )
    
    # ALTO: Rest → Answer (m.5) → Countersubject with Tenor (m.9)
    alto_part = (
        make_rest(subject_length) +                  # m.1-4: Rest (Soprano solo)
        fugue_parts['answer'] +                      # m.5-8: Answer entry (at 5th)
        custom_counter_events                        # m.9-12: Countersubject against Tenor
    )
    
    # TENOR: Rest → Rest → Subject (m.9) → Countersubject with Bass
    tenor_part = (
        make_rest(subject_length * 2) +              # m.1-8: Rest (Soprano, Alto)
        fugue_parts['subject'] +                     # m.9-12: Subject entry
        custom_counter_events                        # m.13-16: Countersubject against Bass
    )
    
    # BASS: Rest → Rest → Rest → Answer (m.13)
    bass_part = (
        make_rest(subject_length * 3) +              # m.1-12: Rest (waiting for entry)
        fugue_parts['answer']                        # m.13-16: Answer entry (at 5th)
    )
    
    print(f"  • Soprano: {len(soprano_part)} events")
    print(f"  • Alto: {len(alto_part)} events")
    print(f"  • Tenor: {len(tenor_part)} events")
    print(f"  • Bass: {len(bass_part)} events")
    
    # --- Return complete score structure ---
    print("\n" + "="*70)
    print("✅ Programmatic Fugue Complete!")
    print("="*70)
    
    return {
        'metadata': metadata,
        'parts': {
            'Soprano': soprano_part,
            'Alto': alto_part,
            'Tenor': tenor_part,
            'Bass': bass_part
        }
    }
    # melody_events = theme_a_events + transposed_events + theme_a_events
    
    print(f"  → Assembled melody: {{len(melody_events)}} total events")
    print(f"  → Assembled bass: {{len(bass_events_full)}} total events")
    
    # --- Define Metadata ---
    metadata = {
        'title': TITLE + " (Programmatic)",
        'composer': COMPOSER,
        'opus_number': OPUS_NUMBER + "-Prog",
        'instrumentation': INSTRUMENTATION,
        'key_signature': {'tonic': 'g', 'mode': 'major'},
        'time_signature': '3/4',
        'tempo': 'Andante, quarter note = 90',
    }

    print("\n" + "="*70)
    print("✅ Station 4 Programmatic Assembly Complete")
    print("="*70)

    # --- Return Final Score Data ---
    return {
        'metadata': metadata,
        'parts': {
            'Melody': melody_events,
            'Bass': bass_events_full,
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
