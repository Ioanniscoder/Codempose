# Advanced Transformations Guide

This guide explains the two-tiered system for musical transformations in Codempose:

1. **Composition Shorthand** (`composition_shorthand.py`) - Simple, declarative functions
2. **Advanced Transformations** (`advanced_transformations.py`) - Complex, programmatic functions

## Architecture Overview

The framework uses a **hybrid model** that separates simple operations from complex ones:

```
┌─────────────────────────────────────────────────────────────┐
│ COMPOSITION SHORTHAND (composition_shorthand.py)            │
│ ─────────────────────────────────────────────────────────── │
│ Purpose: Simple functions with clear arguments              │
│                                                              │
│ ✅ Use for:                                                 │
│   • Harmonic progressions: from_roman_numerals()            │
│   • Scale degree melodies: from_scale_degrees()             │
│   • Rhythmic changes: stretch_events(), augment()           │
│   • Simple transposition: transpose_events()                │
│                                                              │
│ ❌ Don't use for:                                           │
│   • Complex argument parsing (lists, nested structures)     │
│   • Context-dependent operations                            │
│   • Multi-step algorithms                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADVANCED TRANSFORMATIONS (advanced_transformations.py)      │
│ ─────────────────────────────────────────────────────────── │
│ Purpose: Complex, music-theory-aware transformations        │
│                                                              │
│ ✅ Use for:                                                 │
│   • Melodic sequencing: create_melodic_sequence()           │
│   • Figured bass realization: realize_figured_bass()        │
│   • Modal mixture: apply_modal_mixture()                    │
│   • Advanced voice leading                                  │
│   • Automated harmonization                                 │
│                                                              │
│ Implementation:                                              │
│   • Import and call from build_score_data()                 │
│   • Use full music21 API                                    │
│   • Handle complex arguments with Python native types       │
└─────────────────────────────────────────────────────────────┘
```

---

## Composition Shorthand Functions

### 1. Harmonic Progressions from Roman Numerals

**Function**: `from_roman_numerals(progression_str, key_str, rhythm_str)`

Generate chord sequences from Roman numeral notation.

**Example Usage**:
```python
from composition_shorthand import from_roman_numerals

# Create a I-V-vi-IV progression in C major
progression_events = from_roman_numerals(
    progression_str="I-V-vi-IV",
    key_str="C",
    rhythm_str="w-w-w-w"
)

# Create a progression with inversions
complex_progression = from_roman_numerals(
    progression_str="I-V65-I6-IV",
    key_str="D",
    rhythm_str="h-h-h-h"
)
```

**Parameters**:
- `progression_str`: Roman numerals separated by `-` (e.g., `"I-V65-i"`)
- `key_str`: Key name (`"C"` = C major, `"c"` = c minor, `"F#"` = F# major)
- `rhythm_str`: Duration codes separated by `-` (see Rhythm Notation below)

**Rhythm Notation**:
- `w` or `1` = whole note (4.0 quarter lengths)
- `h` or `2` = half note (2.0 quarter lengths)
- `q` or `4` = quarter note (1.0 quarter length)
- `e` or `8` = eighth note (0.5 quarter length)
- `16` = sixteenth note (0.25 quarter length)

---

### 2. Melody from Scale Degrees

**Function**: `from_scale_degrees(degree_str, key_str, rhythm_str)`

Create melodic lines from scale degree numbers.

**Example Usage**:
```python
from composition_shorthand import from_scale_degrees

# Create a simple ascending scale
scale_melody = from_scale_degrees(
    degree_str="1-2-3-4-5-6-7-1",
    key_str="A",
    rhythm_str="q-q-q-q-q-q-q-h"
)

# Create a melody with rests
theme = from_scale_degrees(
    degree_str="1-7-1-5-r-6-4-5",
    key_str="C",
    rhythm_str="q-e-e-q-q-q-q-h"
)
```

**Parameters**:
- `degree_str`: Scale degrees separated by `-` (1-7), use `r` for rest
- `key_str`: Key name (same as `from_roman_numerals`)
- `rhythm_str`: Duration codes separated by `-`

---

### 3. Rhythmic Augmentation/Diminution

**Function**: `stretch_events(events, multiplier)`  
**Aliases**: `augment(events, multiplier=2.0)`, `diminish(events, multiplier=0.5)`

Multiply the duration of all events.

**Example Usage**:
```python
from composition_shorthand import stretch_events, augment, diminish

# Double all durations (augmentation)
theme_augmented = augment(theme_events)  # Default multiplier = 2.0
theme_double = stretch_events(theme_events, 2.0)  # Explicit

# Half all durations (diminution)
theme_diminished = diminish(theme_events)  # Default multiplier = 0.5
theme_half = stretch_events(theme_events, 0.5)  # Explicit

# Custom scaling
theme_stretched = stretch_events(theme_events, 1.5)  # 150% duration
```

**Parameters**:
- `events`: List of event dictionaries
- `multiplier`: Factor to multiply durations by

---

### 4. Simple Transposition

**Function**: `transpose_events(events, semitones)`

Transpose all notes and chords by semitones.

**Example Usage**:
```python
from composition_shorthand import transpose_events

# Transpose up a perfect fifth (7 semitones)
transposed_up = transpose_events(melody_events, 7)

# Transpose down a major third (4 semitones)
transposed_down = transpose_events(melody_events, -4)
```

**Parameters**:
- `events`: List of event dictionaries
- `semitones`: Number of semitones (positive = up, negative = down)

---

## Advanced Transformation Functions

### 1. Melodic Sequencing

**Function**: `create_melodic_sequence(events, interval_pattern, key, preserve_rhythm)`

Repeat a melodic fragment at different pitch levels.

**Example Usage**:
```python
from advanced_transformations import create_melodic_sequence

# In your build_score_data() function:
def build_score_data():
    # Define a theme
    theme_events = from_scale_degrees("1-2-3", "C", "q-q-q")
    
    # Create a descending sequence
    soprano_events = create_melodic_sequence(
        events=theme_events,
        interval_pattern=[-2, -2, -2],  # Down a step each time
        key='C major',
        preserve_rhythm=True
    )
    
    return {
        'parts': {
            'Melody': {'Soprano': soprano_events}
        }
    }
```

**Parameters**:
- `events`: The melodic fragment to sequence
- `interval_pattern`: List of semitone intervals for each repetition
- `key`: Key context (default: `'C major'`)
- `preserve_rhythm`: Keep original rhythms if True (default: `True`)

**Common Interval Patterns**:
- `[-2, -2, 2]` = Down step, down step, up step
- `[2, 2, 2]` = Rising sequence by steps
- `[-1, -1, -1]` = Chromatic descent
- `[5, 5, -10]` = Up fourth, up fourth, down octave

---

### 2. Figured Bass Realization

**Function**: `realize_figured_bass(bass_events, figures, num_voices)`

Generate upper voices from a bass line and figured bass notation.

**Example Usage**:
```python
from advanced_transformations import realize_figured_bass
from composition_shorthand import from_scale_degrees

# In your build_score_data() function:
def build_score_data():
    # Create a bass line
    bass_line = from_scale_degrees("1-5-1-4-5-1", "C", "w-w-w-w-w-w")
    
    # Realize the figured bass
    harmony = realize_figured_bass(
        bass_events=bass_line,
        figures="5/3 5/3 6 6 5/3 5/3",
        num_voices=4
    )
    
    # harmony is now a dict with 'Soprano', 'Alto', 'Tenor', 'Bass'
    return {
        'parts': {
            'SATB': harmony
        }
    }
```

**Parameters**:
- `bass_events`: List of bass note events
- `figures`: Figured bass notation (e.g., `"6 6 5 6/4 3"`)
- `num_voices`: Number of voices (default: 4 for SATB)

**Returns**: Dictionary with voice names as keys and event lists as values

**Common Figures**:
- `5/3` or `3` = Root position triad
- `6` or `6/3` = First inversion (sixth chord)
- `6/4` = Second inversion (six-four chord)
- `7` = Seventh chord
- `6/5` = First inversion seventh

---

### 3. Modal Mixture (Modal Interchange)

**Function**: `apply_modal_mixture(events, key, borrow_from)`

Borrow notes from a parallel mode.

**Example Usage**:
```python
from advanced_transformations import apply_modal_mixture

# In your build_score_data() function:
def build_score_data():
    # Start with a melody in C major
    melody = from_scale_degrees("1-3-5-6-1", "C", "q-q-q-q-h")
    
    # Borrow from parallel minor (Eb and Ab instead of E and A)
    modal_mixture = apply_modal_mixture(
        events=melody,
        key='C major',
        borrow_from='parallel_minor'
    )
    
    return {
        'parts': {
            'Melody': {'Theme': modal_mixture}
        }
    }
```

**Parameters**:
- `events`: List of note/chord events
- `key`: Original key (e.g., `'C major'`)
- `borrow_from`: `'parallel_minor'` or `'parallel_major'`

---

## Event Dictionary Format

All functions use the canonical event dictionary format:

**Note Event**:
```python
{
    'type': 'note',
    'step': 'C',        # Note name (C, D, E, F, G, A, B)
    'octave': 4,        # Octave number
    'alter': 0,         # Accidental (-2=bb, -1=b, 0=natural, 1=#, 2=##)
    'ql': 1.0           # Quarter length (duration)
}
```

**Rest Event**:
```python
{
    'type': 'rest',
    'ql': 1.0           # Quarter length (duration)
}
```

**Chord Event**:
```python
{
    'type': 'chord',
    'ql': 1.0,
    'pitches': [        # List of pitch dictionaries
        {'step': 'C', 'octave': 4, 'alter': 0},
        {'step': 'E', 'octave': 4, 'alter': 0},
        {'step': 'G', 'octave': 4, 'alter': 0}
    ]
}
```

---

## Complete Example: Hybrid Composition

Here's a complete example showing both shorthand and programmatic approaches:

```python
from composition_shorthand import from_roman_numerals, from_scale_degrees, augment
from advanced_transformations import create_melodic_sequence, realize_figured_bass


def build_score_data():
    """Build a complete musical score using the hybrid model."""
    
    # ═══════════════════════════════════════════════════════
    # SHORTHAND: Simple operations
    # ═══════════════════════════════════════════════════════
    
    # Create a simple theme using scale degrees
    theme = from_scale_degrees(
        degree_str="1-3-5-3-1",
        key_str="C",
        rhythm_str="q-q-q-q-h"
    )
    
    # Create a harmonic progression
    harmony = from_roman_numerals(
        progression_str="I-IV-V-I",
        key_str="C",
        rhythm_str="w-w-w-w"
    )
    
    # Simple augmentation
    theme_augmented = augment(theme, multiplier=2.0)
    
    # ═══════════════════════════════════════════════════════
    # PROGRAMMATIC: Complex operations
    # ═══════════════════════════════════════════════════════
    
    # Create a melodic sequence (more complex)
    soprano_sequence = create_melodic_sequence(
        events=theme,
        interval_pattern=[-2, -2, 2, -3],
        key='C major',
        preserve_rhythm=True
    )
    
    # Create a bass line and realize it
    bass_line = from_scale_degrees("1-5-1-4-5-1", "C", "w-w-w-w-w-w")
    satb_voices = realize_figured_bass(
        bass_events=bass_line,
        figures="5/3 5/3 6 6/4 5/3 5/3"
    )
    
    # ═══════════════════════════════════════════════════════
    # COMBINE: Build the final score
    # ═══════════════════════════════════════════════════════
    
    score_data = {
        'metadata': {
            'title': 'Hybrid Composition Example',
            'composer': 'Codempose Framework'
        },
        'parts': {
            'Melody': {
                'Soprano': soprano_sequence,
                'Alto': satb_voices['Alto']
            },
            'Harmony': {
                'Tenor': satb_voices['Tenor'],
                'Bass': satb_voices['Bass']
            }
        }
    }
    
    return score_data


if __name__ == '__main__':
    # This would be called by your engraving system
    score = build_score_data()
    # Then pass to engrave_with_abjad() or similar
```

---

## Best Practices

### When to Use Shorthand vs. Programmatic

**Use Composition Shorthand when**:
- ✅ Arguments are simple (strings, numbers)
- ✅ Operation is conceptually simple
- ✅ You want readable, declarative code
- ✅ The transformation is context-independent

**Use Advanced Transformations when**:
- ✅ Arguments are complex (lists, dicts, multiple parameters)
- ✅ Operation requires music theory knowledge
- ✅ You need access to full music21 API
- ✅ The transformation is context-dependent

### Code Organization

1. **Import both modules** at the top of your study files
2. **Use shorthand functions** for simple building blocks
3. **Use programmatic functions** in `build_score_data()` for complex logic
4. **Combine results** into the final score structure

### Extension Guidelines

**To add a new shorthand function**:
1. Add to `composition_shorthand.py`
2. Keep arguments simple (strings, numbers, lists)
3. Return event dictionaries
4. Add documentation with examples

**To add a new advanced function**:
1. Add to `advanced_transformations.py`
2. Accept complex arguments as needed
3. Leverage music21 API extensively
4. Return event dictionaries or voice dictionaries
5. Add comprehensive documentation

---

## References

- **Music Theory Concepts**: Based on principles from tonal harmony textbooks
- **music21 Documentation**: https://web.mit.edu/music21/doc/
- **Abjad Documentation**: https://abjad.github.io/

---

## Summary

The Codempose framework provides a **two-tiered architecture**:

1. **Simple operations** → Use `composition_shorthand.py` functions
2. **Complex operations** → Use `advanced_transformations.py` functions

This separation keeps the framework clean, maintainable, and scalable while providing both ease of use and unlimited power.

**The shorthand is not a limitation—it's a feature.** For the 80% of common operations, it provides elegance and clarity. For the 20% of complex operations, you have the full power of Python and music21 at your disposal.
