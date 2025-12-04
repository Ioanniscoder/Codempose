# Harmonic Intelligence System - Implementation Plan

**Date:** October 15, 2025  
**Phase:** Priority 3B - Tonal Harmony Programmatic Context  
**Status:** Planning Complete - Ready for Implementation

---

## Executive Summary

This document outlines the implementation of the **Harmonic Intelligence System**, the culmination of all foundational work. The goal is to transform Codempose from a notation tool into a **compositional assistant** that applies tonal harmony principles programmatically.

### Mission Statement

Build a system that can:
1. Analyze melodies to identify structural vs. ornamental notes
2. Apply user-defined harmonic progressions to melodies
3. Generate harmonically correct bass lines automatically
4. Follow principles from "Tonal Harmony" textbook

### Scope for Initial Implementation (Priority 3B)

**Phase 1: Structural Tone Analyzer** 
- Module: `harmonic_analysis.py`
- Demo: `fifteenth.py`

**Phase 2: Harmonic Fitting Engine**
- Module: `harmonic_engine.py`
- Demo: `sixteenth.py`

---

## Architecture Analysis

### Current System Compatibility ✅

Our existing architecture is **perfectly positioned** for this enhancement:

#### Strengths
1. **music21 Integration** - Already using music21 library extensively
   - `music_data.py` handles conversions between canonical events and music21 objects
   - Full support for `music21.stream.Part`, `music21.note.Note`, `music21.chord.Chord`
   - MusicXML and LilyPond export already working

2. **Clean Module Structure** - Easy to add new analysis modules
   - `transformations.py` established pattern for library functions
   - `project_template.py` provides `run_pipeline_from_file()` hook
   - Study files (first.py through fourteenth.py) show clear demo pattern

3. **Multi-Voice Capability** - Just completed Priority 3
   - Can already handle multiple parts (melody + bass line)
   - Voice layer creation working via `music_data.py`
   - PDF/MusicXML export supports multi-stave scores

#### Integration Points

```
Current Architecture:
┌─────────────────────────────────────────────────────┐
│ Study File (fifteenth.py, sixteenth.py)            │
│   ↓                                                 │
│ Station 1: Parse melody from LilyPond              │
│   ↓                                                 │
│ Station 2: (Real-time validation)                  │
│   ↓                                                 │
│ Station 3: NEW → Harmonic Analysis & Generation    │ ← INSERT HERE
│   ├─ harmonic_analysis.find_structural_tones()     │
│   └─ harmonic_engine.harmonize_melody()            │
│   ↓                                                 │
│ Station 4: Export (PDF, MusicXML, MIDI)            │
└─────────────────────────────────────────────────────┘
```

### No Breaking Changes Required ✅

The harmonic intelligence system is **additive only**:
- Existing study files (first.py - fourteenth.py) unchanged
- No modifications to core modules (score_builder.py, music_data.py)
- New modules (`harmonic_analysis.py`, `harmonic_engine.py`) are standalone
- Integration happens at study file level (composer's choice)

---

## Phase 1: Structural Tone Analyzer

### Module: `harmonic_analysis.py`

**Purpose:** Identify which notes in a melody are structurally important vs. ornamental.

**Core Function:**
```python
def find_structural_tones(melody_part: music21.stream.Part) -> music21.stream.Part:
    """
    Analyze a melody and tag each note as structural or ornamental.
    
    Rules (from Tonal Harmony textbook):
    1. Strong beat position (beat 1 or 3 in 4/4)
    2. Long duration (quarter note or longer)
    
    Modifies notes in place by adding: note.is_structural = True/False
    
    Args:
        melody_part: music21.stream.Part containing the melody
        
    Returns:
        The modified Part with tagged notes
    """
```

**Implementation Details:**

1. **Iterate through measures**
   ```python
   for measure in melody_part.getElementsByClass('Measure'):
       for note in measure.notes:
           # Analyze beat position and duration
   ```

2. **Check beat position**
   ```python
   beat_offset = note.beat  # music21 provides this automatically
   time_sig = measure.timeSignature or music21.meter.TimeSignature('4/4')
   
   # In 4/4: beats 1 and 3 are strong
   is_strong_beat = (beat_offset == 1.0 or beat_offset == 3.0)
   ```

3. **Check duration**
   ```python
   # Quarter note or longer is structural
   is_long = note.quarterLength >= 1.0
   ```

4. **Tag the note**
   ```python
   note.is_structural = (is_strong_beat or is_long)
   ```

**Dependencies:**
- `music21` library (already installed)
- No dependencies on other Codempose modules

**File Structure:**
```python
"""
harmonic_analysis.py - Structural Tone Analysis for Tonal Harmony

This module provides tools to analyze melodies and identify structural vs.
ornamental tones based on principles from "Tonal Harmony" textbook.
"""

from music21 import stream, note, meter
from typing import List, Tuple


def find_structural_tones(melody_part: stream.Part) -> stream.Part:
    """Implementation here"""
    
def print_structural_analysis(melody_part: stream.Part) -> None:
    """Helper function to print analysis results to console"""
    
__all__ = ['find_structural_tones', 'print_structural_analysis']
```

### Demo: `fifteenth.py`

**Purpose:** Validate that structural tone identification works correctly.

**Structure (follows existing pattern):**
```python
"""Fifteenth study file - Structural Tone Analysis Demonstration.

This study demonstrates the Harmonic Intelligence System's ability to
identify structural vs. ornamental notes in a melody.
"""

# STATION 1: LILYPOND SNIPPETS
MELODY_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    c4 d8 e8 f4 g4 |
    a2 g4 f4 |
    e4 d4 c2
}
"""

# STATION 2: REAL-TIME VALIDATION
# (Automatic via parser)

# STATION 3: HARMONIC ANALYSIS
def build_score_data():
    from lilypond_parser import parse_lilypond_to_data
    from harmonic_analysis import find_structural_tones, print_structural_analysis
    
    # Parse melody
    melody_data = parse_lilypond_to_data(MELODY_LILY, part_name='Melody')
    
    # Convert to music21 Part
    from music_data import data_to_part
    melody_part = data_to_part(melody_data['parts']['Melody'])
    
    # Analyze structural tones
    analyzed_part = find_structural_tones(melody_part)
    
    # Print analysis to console
    print("\n" + "="*70)
    print("STRUCTURAL TONE ANALYSIS")
    print("="*70)
    print_structural_analysis(analyzed_part)
    
    # Return score_data for normal pipeline
    return melody_data

# STATION 4: EXECUTION
if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
```

**Expected Console Output:**
```
======================================================================
STRUCTURAL TONE ANALYSIS
======================================================================
Measure 1:
  C4 (quarter, beat 1.0) → STRUCTURAL (strong beat)
  D4 (eighth, beat 2.0) → Ornamental
  E4 (eighth, beat 2.5) → Ornamental
  F4 (quarter, beat 3.0) → STRUCTURAL (strong beat)
  G4 (quarter, beat 4.0) → Ornamental

Measure 2:
  A4 (half, beat 1.0) → STRUCTURAL (strong beat + long duration)
  G4 (quarter, beat 3.0) → STRUCTURAL (strong beat)
  F4 (quarter, beat 4.0) → Ornamental

Measure 3:
  E4 (quarter, beat 1.0) → STRUCTURAL (strong beat)
  D4 (quarter, beat 2.0) → Ornamental
  C4 (half, beat 3.0) → STRUCTURAL (long duration)

Summary: 7 structural tones, 5 ornamental tones
```

---

## Phase 2: Harmonic Fitting Engine

### Module: `harmonic_engine.py`

**Purpose:** Apply a user-defined chord progression to a melody and generate a bass line.

**Core Function:**
```python
def harmonize_melody(
    melody_part: stream.Part, 
    progression_string: str, 
    key: str
) -> stream.Score:
    """
    Harmonize a melody with a chord progression.
    
    Process:
    1. Analyze structural tones in melody
    2. Parse progression string (e.g., "I - vi - ii - V - I")
    3. Align chords with structural tones
    4. Generate bass line from chord roots
    5. Return two-part score (melody + bass)
    
    Args:
        melody_part: music21.stream.Part with the melody
        progression_string: Roman numeral progression (e.g., "I - IV - V - I")
        key: Key signature (e.g., "C", "A minor")
        
    Returns:
        music21.stream.Score with melody and generated bass line
    """
```

**Implementation Steps:**

1. **Analyze structural tones**
   ```python
   from harmonic_analysis import find_structural_tones
   analyzed_melody = find_structural_tones(melody_part)
   ```

2. **Parse progression string**
   ```python
   from music21 import roman, key as m21key
   
   # Parse key
   key_obj = m21key.Key(key)
   
   # Parse progression
   chord_symbols = [s.strip() for s in progression_string.split('-')]
   chords = [roman.RomanNumeral(sym, key_obj) for sym in chord_symbols]
   ```

3. **Align chords with structural tones**
   ```python
   # Get list of structural notes
   structural_notes = [n for n in analyzed_melody.flatten().notes if n.is_structural]
   
   # Calculate harmonic rhythm
   chords_per_measure = len(chords) // len(analyzed_melody.getElementsByClass('Measure'))
   
   # Align chords with structural tone positions
   aligned_chords = []
   for i, note in enumerate(structural_notes):
       chord_index = min(i // chords_per_measure, len(chords) - 1)
       aligned_chords.append((note.offset, chords[chord_index]))
   ```

4. **Generate bass line**
   ```python
   bass_part = stream.Part()
   
   for offset, chord_obj in aligned_chords:
       # Use chord root for bass note
       bass_note = note.Note(chord_obj.root())
       bass_note.quarterLength = 4.0  # Whole note per measure (example)
       bass_part.insert(offset, bass_note)
   ```

5. **Create score**
   ```python
   score = stream.Score()
   score.insert(0, analyzed_melody)
   score.insert(0, bass_part)
   return score
   ```

**Advanced Features (Phase 2B - Future):**
- Voice-leading rules (avoid parallel fifths/octaves)
- Inversion selection (bass note != chord root)
- Passing tones in bass line
- Chord seventh resolution checking

**File Structure:**
```python
"""
harmonic_engine.py - Harmonic Fitting Engine for Tonal Harmony

This module provides tools to apply chord progressions to melodies and
generate harmonically correct bass lines.
"""

from music21 import stream, note, roman, key, meter
from typing import List, Tuple
from harmonic_analysis import find_structural_tones


def harmonize_melody(
    melody_part: stream.Part, 
    progression_string: str, 
    key: str
) -> stream.Score:
    """Implementation here"""

def validate_progression(progression_string: str, key: str) -> bool:
    """Helper to check if progression follows common practice rules"""

__all__ = ['harmonize_melody', 'validate_progression']
```

### Demo: `sixteenth.py`

**Purpose:** Showcase automated harmonization with user-defined progression.

**Structure:**
```python
"""Sixteenth study file - Automated Harmonization Showcase.

This study demonstrates the Harmonic Fitting Engine's ability to
apply a chord progression to a melody and generate a bass line.
"""

# STATION 1: LILYPOND SNIPPETS
MELODY_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    c4 d4 e4 f4 |
    g2 e2 |
    f4 e4 d4 c4 |
    c1
}
"""

# User-defined harmonic progression
PROGRESSION_STRING = "I - IV - V - I"
KEY = "C"

TITLE = "Automated Harmonization Demo"
COMPOSER = "Harmonic Engine"

# STATION 3: HARMONIZATION
def build_score_data():
    from lilypond_parser import parse_lilypond_to_data
    from music_data import data_to_part, part_to_data
    from harmonic_engine import harmonize_melody
    
    print("\n" + "="*70)
    print("HARMONIC FITTING ENGINE")
    print("="*70)
    print(f"Melody: 4 measures in {KEY} major")
    print(f"Progression: {PROGRESSION_STRING}")
    print()
    
    # Parse melody
    melody_data = parse_lilypond_to_data(MELODY_LILY, part_name='Melody')
    melody_part = data_to_part(melody_data['parts']['Melody'])
    
    # Harmonize (generates two-part score)
    harmonized_score = harmonize_melody(melody_part, PROGRESSION_STRING, KEY)
    
    print("✓ Structural tones identified")
    print("✓ Chord progression aligned")
    print("✓ Bass line generated")
    print()
    
    # Convert back to score_data format
    melody_events = part_to_data(harmonized_score.parts[0])  # Original melody
    bass_events = part_to_data(harmonized_score.parts[1])    # Generated bass
    
    score_data = {
        'metadata': {
            'title': TITLE,
            'composer': COMPOSER,
            'key_signature': {'tonic': 'c', 'mode': 'major'},
            'time_signature': '4/4'
        },
        'parts': {
            'Melody': melody_events,
            'Bass': bass_events  # NEW: Programmatically generated!
        }
    }
    
    return score_data

# STATION 4: EXECUTION
if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
```

**Expected Output:**
- **PDF:** Two-stave score with original melody (treble) and generated bass line (bass clef)
- **Console:** Shows structural tone identification and chord alignment
- **MusicXML:** Importable to MuseScore for further editing

---

## Implementation Roadmap

### Week 1: Phase 1 - Structural Tone Analyzer

**Day 1-2: Create `harmonic_analysis.py`**
- [ ] Implement `find_structural_tones()` function
- [ ] Add beat position detection logic
- [ ] Add duration-based detection logic
- [ ] Implement `print_structural_analysis()` helper
- [ ] Add comprehensive docstrings
- [ ] Unit tests for structural tone identification

**Day 3: Create `fifteenth.py`**
- [ ] Implement study file structure (4 stations)
- [ ] Add simple melody snippet
- [ ] Integrate structural tone analysis
- [ ] Format console output
- [ ] Test PDF/MusicXML generation

**Day 4: Testing & Validation**
- [ ] Test with various melodies (different time signatures)
- [ ] Verify beat position calculations
- [ ] Check edge cases (pickup measures, syncopation)
- [ ] Document findings

### Week 2: Phase 2 - Harmonic Fitting Engine

**Day 5-7: Create `harmonic_engine.py`**
- [ ] Implement `harmonize_melody()` function
- [ ] Add progression string parser
- [ ] Implement chord-to-structural-tone alignment
- [ ] Add bass line generation logic
- [ ] Implement `validate_progression()` helper (optional)
- [ ] Add comprehensive docstrings
- [ ] Unit tests for harmonization

**Day 8: Create `sixteenth.py`**
- [ ] Implement study file structure
- [ ] Add melody + progression string
- [ ] Integrate harmonic engine
- [ ] Add console output formatting
- [ ] Test two-stave output

**Day 9: Testing & Documentation**
- [ ] Test various progressions (I-IV-V-I, vi-ii-V-I, etc.)
- [ ] Test different keys (major and minor)
- [ ] Verify bass line quality
- [ ] Create user documentation
- [ ] Create API reference

**Day 10: Integration & Polish**
- [ ] Final integration testing
- [ ] Performance optimization
- [ ] Code review and refactoring
- [ ] Update README with new features
- [ ] Create demo video/screenshots

---

## Success Criteria

### Phase 1: Structural Tone Analyzer ✅
- [ ] `harmonic_analysis.py` created with `find_structural_tones()` function
- [ ] `fifteenth.py` runs successfully
- [ ] Console output correctly identifies structural vs. ornamental notes
- [ ] PDF shows melody with structural tones highlighted (visual indicator)
- [ ] All existing study files still work (no regressions)

### Phase 2: Harmonic Fitting Engine ✅
- [ ] `harmonic_engine.py` created with `harmonize_melody()` function
- [ ] `sixteenth.py` runs successfully
- [ ] Generated bass line follows specified chord progression
- [ ] Two-stave PDF generated correctly
- [ ] Bass line is musically valid (no awkward leaps, appropriate register)

### Overall System ✅
- [ ] No breaking changes to existing codebase
- [ ] All tests passing (including new harmonic intelligence tests)
- [ ] Documentation complete and clear
- [ ] Code follows existing patterns and style
- [ ] Ready for future enhancements (voice-leading rules, etc.)

---

## Future Enhancements (Priority 3C+)

Based on the Tonal Harmony roadmap, these features can be added incrementally:

### Part Two: Diatonic Triads (Chapters 5-9)
- **Voice-Leading Rules Engine** - Check for parallel fifths/octaves
- **Harmonic Progression Validator** - Validate progressions against functional harmony rules
- **Four-Part Harmonization** - Generate SATB from melody + progression

### Part Three: Diatonic Seventh Chords (Chapters 13-15)
- **Seventh Chord Resolution Checker** - Verify correct resolution of dissonances
- **V7 → I Generator** - Create proper dominant seventh resolutions

### Part Four: Chromaticism 1 (Chapters 16-19)
- **Secondary Dominant Generator** - Create V/V, V/vi, etc.
- **Common Chord Finder** - Identify pivot chords for modulations

### Part Five: Chromaticism 2 (Chapters 21-25)
- **Neapolitan Chord Constructor** - Generate N6 chords
- **Augmented Sixth Constructors** - Generate It+6, Fr+6, Ger+6 chords

---

## Risk Assessment

### Low Risk ✅
- **Architecture compatibility** - music21 provides all needed functionality
- **Integration** - Adding new modules, not modifying existing ones
- **Testing** - Can validate incrementally with each study file

### Medium Risk ⚠️
- **Algorithm complexity** - Harmonic alignment may need tuning
- **Musical quality** - Generated bass lines must sound good, not just be correct
- **Edge cases** - Unusual time signatures, pickup measures, etc.

### Mitigation Strategies
1. **Start simple** - Basic rules first, refine later
2. **Manual validation** - Listen to generated output, adjust algorithms
3. **Extensive testing** - Create test suite with known good/bad examples
4. **Iterative improvement** - Add features one at a time, validate each

---

## Dependencies

### Existing (Already Installed)
- `music21` - Core music analysis library ✅
- `lilypond_parser.py` - LilyPond parsing ✅
- `music_data.py` - Canonical events ↔ music21 conversion ✅
- `project_template.py` - Pipeline infrastructure ✅

### New (To Be Created)
- `harmonic_analysis.py` - Structural tone analyzer
- `harmonic_engine.py` - Harmonization engine
- `fifteenth.py` - Demo study file for analysis
- `sixteenth.py` - Demo study file for harmonization

### Optional Future
- `voice_leading_rules.py` - Voice-leading checker
- `progression_validator.py` - Harmonic progression rules
- `chromatic_harmony.py` - Secondary dominants, augmented sixths, etc.

---

## Conclusion

The Harmonic Intelligence System represents the **culmination** of the Codempose project. All foundational work (parser, Blueprint Framework, multi-voice support) has prepared the system for this moment.

**Current Status:** Architecture is perfectly positioned for this enhancement
**Risk Level:** Low - additive changes only, no breaking modifications
**Timeline:** 2 weeks for initial implementation (Phases 1 & 2)
**Future Potential:** Rich roadmap for advanced features (voice-leading, chromaticism, etc.)

**Recommendation:** Proceed with implementation immediately. Begin with Phase 1 (Structural Tone Analyzer) as it's the foundation for all subsequent features.

---

## Next Steps

1. **Create `harmonic_analysis.py`** - Implement structural tone identification
2. **Create `fifteenth.py`** - Validate analyzer with demo
3. **Create `harmonic_engine.py`** - Implement harmonization engine
4. **Create `sixteenth.py`** - Showcase automated harmonization
5. **Test, document, and celebrate!** 🎉

Ready to begin? Let's transform Codempose into a true compositional assistant!
