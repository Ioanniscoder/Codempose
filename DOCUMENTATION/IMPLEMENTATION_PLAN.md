# Implementation Plan: Promotion Toggle & Harmonic Intelligence Integration

**Date:** October 19, 2025  
**Status:** READY FOR IMPLEMENTATION

---

## Summary of Requirements

Based on user clarifications:

1. **✅ Promotion Model** - Keep it, use **TOGGLE** (not commenting out)
2. **✅ Harmonic Intelligence** - Integrate into Blueprint Strings (essential for composers)
3. **✅ Voice Generation** - Part of harmonic intelligence, readily available
4. **✅ Composition Shorthand** - Merge useful operators (like `*`) into Blueprint Strings
5. **✅ Station 4 Access** - Should have access to Station 1 snippets

---

## Implementation Tasks

### **Task 1: Add Promotion Toggle to Blueprint Strings**

**Current State:**
- Historical precedent in `OLD/twelfth.py` shows `PROMOTE_TO_PROGRAMMATIC` toggle
- Pattern: Toggle switches between declarative (Stations 1-3) and programmatic (Station 4)

**Implementation:**

```python
# At top of study file (after METADATA)
# ============================================================================
# PROMOTION TOGGLE
# ============================================================================

PROMOTE_TO_STATION4 = False  # Set True to work in fully programmatic mode

# When False: Use Stations 1-3 (declarative composition)
# When True: Station 4 becomes active (programmatic composition with full access)
```

**Behavior:**

```python
# In build_score_data()
def build_score_data() -> Dict:
    """
    Build score data.
    
    Mode depends on PROMOTE_TO_STATION4 toggle:
    - False: Use Blueprint Strings (Stations 1-3)
    - True: Use programmatic composition (Station 4)
    """
    
    if not PROMOTE_TO_STATION4:
        # DECLARATIVE MODE (Stations 1-3)
        # Parse snippets
        theme_parsed = parse_lilypond_to_data(THEME_LILY, 'Theme')
        theme_events = theme_parsed['parts']['Theme']
        
        SNIPPETS = {'THEME': theme_events}
        
        # Build using Blueprint Strings
        return build_score_from_blueprint(
            VOICE_STAVE_DEF,
            VOICE_STAVE_DATA,
            SNIPPETS,
            metadata
        )
    
    else:
        # PROGRAMMATIC MODE (Station 4)
        # All Station 1 snippets are available
        return build_score_data_programmatic()


def build_score_data_programmatic() -> Dict:
    """
    Programmatic composition (Station 4).
    
    Station 1 snippets (THEME_LILY, etc.) are available here.
    Full music21 API access for algorithmic composition.
    """
    # Parse Station 1 snippets (still available!)
    theme_parsed = parse_lilypond_to_data(THEME_LILY, 'Theme')
    theme_part = data_to_part(theme_parsed['parts']['Theme'])
    
    # Algorithmic composition
    from harmonic_engine import harmonize_melody
    
    harmonized = harmonize_melody(
        melody_part=theme_part,
        progression_string="I-IV-V-I",
        key="C"
    )
    
    # Return score_data
    return {
        'metadata': {...},
        'parts': {
            'Melody': extract_data_from_part(harmonized.parts[0]),
            'Bass': extract_data_from_part(harmonized.parts[1])
        }
    }
```

**Station 1 Access:**
✅ **YES** - All Station 1 snippets (THEME_LILY, etc.) are available in Station 4
- They're module-level variables, accessible anywhere
- Station 4 can parse them with `parse_lilypond_to_data()`
- This allows progressive development (start with snippets, enhance algorithmically)

---

### **Task 2: Integrate Harmonic Intelligence into Blueprint Strings**

**Goal:** Make `harmonize_part()` available as a transformation function

**Current State:**
- `harmonic_engine.py` has `harmonize_melody()` function
- Takes `melody_part`, `progression_string`, `key`, `harmonic_rhythm`
- Returns music21 Score with melody + generated bass

**Implementation:**

#### **Step 2a: Add `harmonize_part()` to transformations.py**

```python
# In src/transformations.py

def harmonize_part(melody_part, progression_string, key='C'):
    """
    Generate harmonic accompaniment (bass line) for a melody.
    
    Uses harmonic intelligence to analyze structural tones and
    fit a chord progression to the melody.
    
    Args:
        melody_part: music21.stream.Part object
        progression_string: Chord progression (e.g., "I-IV-V-I")
        key: Key signature (e.g., "C", "Dm", "G")
    
    Returns:
        music21.stream.Score with two parts: melody + bass
    
    Example:
        harmonize_part(melody, "I-IV-V-I", "C")
    """
    from harmonic_engine import harmonize_melody
    
    # Generate harmonization
    harmonized_score = harmonize_melody(
        melody_part=melody_part,
        progression_string=progression_string,
        key=key,
        harmonic_rhythm="auto"
    )
    
    return harmonized_score
```

#### **Step 2b: Update Blueprint Framework to Handle Score Returns**

**Challenge:** Transformations currently return `Part`, but `harmonize_part()` returns `Score` (2 parts)

**Solution:**

```python
# In src/score_builder.py

def _get_or_create_snippet_events(snippet_syntax, SNIPPETS, metadata):
    """
    Get or create snippet events, handling transformation syntax.
    
    Now handles:
    - Simple snippets: THEME
    - Transformations: transpose_part(THEME, 'P5')
    - Multi-part results: harmonize_part(THEME, 'I-IV-V-I', 'C')
    """
    
    # ... existing code ...
    
    # Apply transformation
    try:
        result = func(input_part, *args)
        
        # Check if result is Score (multi-part) or Part (single-part)
        if isinstance(result, music21.stream.Score):
            # Multi-part result from harmonize_part()
            # Return dict mapping part names to events
            result_dict = {}
            for idx, part in enumerate(result.parts):
                part_name = part.partName or f"Part{idx+1}"
                events = extract_data_from_part(part)
                result_dict[part_name] = events
            
            # Cache and return
            SNIPPETS[full_syntax] = result_dict
            return result_dict
            
        else:
            # Single-part result (standard transformation)
            events = extract_data_from_part(result)
            SNIPPETS[full_syntax] = events
            return events
    
    except Exception as e:
        # ... error handling ...
```

#### **Step 2c: Usage in Blueprint Strings**

```python
# STATION 3: BLUEPRINT STRINGS

VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    THEME & r;
    harmonize_part(THEME, 'I-IV-V-I', 'C')
"""
```

**What happens:**
1. First section: `THEME & r` - Melody plays, bass rests
2. Second section: `harmonize_part(THEME, 'I-IV-V-I', 'C')` returns:
   - `{'Melody': [...], 'Bass': [...]}`
   - Framework maps Melody → Melody staff, Bass → Bass staff
   - Result: Auto-generated harmonization!

#### **Step 2d: Station 2 Population**

```python
# STATION 2: VALIDATION & GENERATED INPUT

# Original
THEME_TINY = None
THEME_LILY = r"..."

# Harmonized (auto-generated)
THEME_HARMONIZED_MELODY_LILY = None  # Melody part of harmonization
THEME_HARMONIZED_BASS_LILY = None    # Generated bass line
THEME_HARMONIZED_MELODY_TINY = None
THEME_HARMONIZED_BASS_TINY = None

# Populated in build_score_data()
if "harmonize_part(THEME, 'I-IV-V-I', 'C')" in SNIPPETS:
    result = SNIPPETS["harmonize_part(THEME, 'I-IV-V-I', 'C')"]
    
    THEME_HARMONIZED_MELODY_LILY = events_to_lily(result['Melody'], metadata)
    THEME_HARMONIZED_BASS_LILY = events_to_lily(result['Bass'], metadata)
    
    THEME_HARMONIZED_MELODY_TINY = events_to_tinynotation(result['Melody'], metadata)
    THEME_HARMONIZED_BASS_TINY = events_to_tinynotation(result['Bass'], metadata)
```

---

### **Task 3: Add Repeat Operator (`*`) to Blueprint Strings**

**From Composition Shorthand:**
```python
'THEME * 3'  # Repeat THEME 3 times
```

**Implementation:**

```python
# In src/score_builder.py

def _get_or_create_snippet_events(snippet_syntax, SNIPPETS, metadata):
    """
    Get or create snippet events.
    
    Supports:
    - THEME
    - transpose_part(THEME, 'P5')
    - THEME * 3  # ← NEW
    """
    
    # Check for repeat syntax: SNIPPET * N
    repeat_match = re.match(r'^\s*(\w+|\w+\(.*\))\s*\*\s*(\d+)\s*$', snippet_syntax)
    if repeat_match:
        base_snippet = repeat_match.group(1).strip()
        repeat_count = int(repeat_match.group(2))
        
        # Get base events
        base_events = _get_or_create_snippet_events(base_snippet, SNIPPETS, metadata)
        
        # Repeat
        repeated_events = []
        for _ in range(repeat_count):
            repeated_events.extend(copy.deepcopy(base_events))
        
        # Cache and return
        SNIPPETS[snippet_syntax] = repeated_events
        return repeated_events
    
    # ... existing code for other patterns ...
```

**Usage:**

```python
VOICE_STAVE_DATA = """
    THEME * 2;
    transpose_part(THEME, 'P5') * 3;
    THEME | THEME | THEME
"""
```

**Note:** The `|` operator already exists for concatenation, so `THEME * 3` is equivalent to `THEME | THEME | THEME` but more concise.

---

### **Task 4: Add Structural Analysis Functions**

**Goal:** Make structural tone analysis accessible (part of harmonic intelligence)

**Implementation:**

```python
# In src/transformations.py

def analyze_structural_tones(melody_part):
    """
    Identify structural vs. ornamental tones in a melody.
    
    Structural tones:
    - Fall on strong beats (beat 1, beat 3 in 4/4)
    - Have longer durations (quarter note or longer)
    
    Args:
        melody_part: music21.stream.Part object
    
    Returns:
        music21.stream.Part with structural tones annotated
    
    Example:
        analyzed = analyze_structural_tones(melody)
        structural_notes = [n for n in analyzed.flatten().notes 
                           if n.editorial.get('structural')]
    """
    from harmonic_analysis import find_structural_tones
    return find_structural_tones(melody_part)
```

**Usage in Station 4:**

```python
def build_score_data_programmatic():
    """Station 4 programmatic composition."""
    
    # Parse melody
    melody_part = data_to_part(melody_events)
    
    # Analyze structure
    analyzed = analyze_structural_tones(melody_part)
    
    # Get structural notes
    from harmonic_analysis import get_structural_notes
    structural = get_structural_notes(analyzed)
    
    print("Structural tone sequence:")
    for note in structural:
        print(f"  {note.nameWithOctave} (beat {note.beat})")
    
    # Use structural analysis for harmonization
    harmonized = harmonize_part(analyzed, "I-IV-V-I", "C")
    
    # ...
```

---

## File Structure After Implementation

```python
"""Study File: Blueprint Strings with Harmonic Intelligence"""

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
COMPOSER = "Codempose Framework"


# ============================================================================
# PROMOTION TOGGLE
# ============================================================================

PROMOTE_TO_STATION4 = False  # Set True for programmatic mode


# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

MELODY_LILY = r"\relative c'' { c4 d4 e4 f4 | g2 a2 | b4 c4 d2 | c1 }"


# ============================================================================
# STATION 2: VALIDATION & GENERATED INPUT
# ============================================================================

# Original
MELODY_TINY = None

# Harmonized (auto-generated)
MELODY_HARMONIZED_MELODY_LILY = None
MELODY_HARMONIZED_BASS_LILY = None
MELODY_HARMONIZED_MELODY_TINY = None
MELODY_HARMONIZED_BASS_TINY = None


# ============================================================================
# STATION 3: BLUEPRINT STRINGS
# ============================================================================

VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    MELODY & r;
    harmonize_part(MELODY, 'I-IV-V-I', 'C');
    MELODY * 2 & r
"""


# ============================================================================
# STATION 4: PROGRAMMATIC CONTEXT (Optional - accessed via toggle)
# ============================================================================

def build_score_data_programmatic() -> Dict:
    """
    Programmatic composition mode (activated by PROMOTE_TO_STATION4 = True).
    
    Station 1 snippets are available here for algorithmic manipulation.
    """
    from harmonic_engine import harmonize_melody
    from harmonic_analysis import find_structural_tones, get_structural_notes
    
    # Parse Station 1 snippet (still available!)
    melody_parsed = parse_lilypond_to_data(MELODY_LILY, 'Melody')
    melody_part = data_to_part(melody_parsed['parts']['Melody'])
    
    # Analyze structural tones
    analyzed = find_structural_tones(melody_part)
    structural = get_structural_notes(analyzed)
    
    print("\nStructural tone analysis:")
    for note in structural:
        print(f"  {note.nameWithOctave} (beat {note.beat})")
    
    # Generate harmonization
    harmonized = harmonize_melody(
        melody_part=analyzed,
        progression_string="I-vi-IV-V-I",
        key="C",
        harmonic_rhythm="auto"
    )
    
    # Extract parts
    melody_events = extract_data_from_part(harmonized.parts[0])
    bass_events = extract_data_from_part(harmonized.parts[1])
    
    return {
        'metadata': {
            'title': TITLE,
            'composer': COMPOSER,
            'time_signature': '4/4',
            'key_signature': {'tonic': 'c', 'mode': 'major'}
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
        
        # Parse snippets
        melody_parsed = parse_lilypond_to_data(MELODY_LILY, 'Melody')
        melody_events = melody_parsed['parts']['Melody']
        
        SNIPPETS = {'MELODY': melody_events}
        
        metadata = {
            'title': TITLE,
            'composer': COMPOSER,
            'time_signature': '4/4',
            'key_signature': {'tonic': 'c', 'mode': 'major'}
        }
        
        # Build using Blueprint Strings (includes harmonize_part!)
        score_data = build_score_from_blueprint(
            VOICE_STAVE_DEF,
            VOICE_STAVE_DATA,
            SNIPPETS,
            metadata
        )
        
        # Populate Station 2
        global MELODY_TINY
        global MELODY_HARMONIZED_MELODY_LILY, MELODY_HARMONIZED_BASS_LILY
        global MELODY_HARMONIZED_MELODY_TINY, MELODY_HARMONIZED_BASS_TINY
        
        MELODY_TINY = events_to_tinynotation(melody_events, metadata)
        
        if "harmonize_part(MELODY, 'I-IV-V-I', 'C')" in SNIPPETS:
            result = SNIPPETS["harmonize_part(MELODY, 'I-IV-V-I', 'C')"]
            
            MELODY_HARMONIZED_MELODY_LILY = events_to_lily(result['Melody'], metadata)
            MELODY_HARMONIZED_BASS_LILY = events_to_lily(result['Bass'], metadata)
            
            MELODY_HARMONIZED_MELODY_TINY = events_to_tinynotation(result['Melody'], metadata)
            MELODY_HARMONIZED_BASS_TINY = events_to_tinynotation(result['Bass'], metadata)
            
            print("\n✓ MELODY_HARMONIZED_BASS_LILY (auto-generated):")
            print(f"  {MELODY_HARMONIZED_BASS_LILY}")
            print("✓ MELODY_HARMONIZED_BASS_TINY (verification):")
            print(f"  {MELODY_HARMONIZED_BASS_TINY}")
        
        return score_data
    
    else:
        # PROGRAMMATIC MODE (Station 4)
        print("\n🔧 PROGRAMMATIC MODE: Using Station 4")
        return build_score_data_programmatic()


if __name__ == '__main__':
    run_pipeline_from_file(__file__)
```

---

## Summary

### ✅ **Task 1: Promotion Toggle**
- Add `PROMOTE_TO_STATION4 = False` at top of study file
- When False: Use Blueprint Strings (declarative)
- When True: Use Station 4 (programmatic)
- Station 1 snippets always available in Station 4

### ✅ **Task 2: Harmonic Intelligence in Blueprints**
- Add `harmonize_part(MELODY, 'I-IV-V-I', 'C')` transformation
- Returns `{'Melody': [...], 'Bass': [...]}` (multi-part)
- Framework maps to correct staves automatically
- Populates Station 2 with both LilyPond and TinyNotation

### ✅ **Task 3: Repeat Operator**
- Add `THEME * 3` syntax to Blueprint Strings
- Equivalent to `THEME | THEME | THEME` but more concise
- Works with transformations: `transpose_part(THEME, 'P5') * 2`

### ✅ **Task 4: Structural Analysis**
- Add `analyze_structural_tones()` helper for Station 4
- Part of harmonic intelligence system
- Available in programmatic mode for advanced composition

---

## Implementation Order

1. **Add repeat operator (`*`)** - Simple regex addition to `_get_or_create_snippet_events()`
2. **Add `harmonize_part()` to transformations.py** - Wrapper around existing `harmonize_melody()`
3. **Update Blueprint framework for multi-part returns** - Handle Score objects
4. **Add promotion toggle pattern** - Conditional in `build_score_data()`
5. **Update CODEMPOSE_STUDY_TEMPLATES.py** - Add new template with toggle
6. **Create example study** - Demonstrates all features

Ready to implement! 🚀
