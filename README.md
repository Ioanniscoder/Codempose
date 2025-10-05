# Codempose

A powerful framework for algorithmic music composition using Python, music21, and LilyPond.

## Overview

Codempose provides a **hybrid model** for musical composition that combines the simplicity of declarative shorthand with the power of programmatic transformations. This approach allows composers to work at the right level of abstraction for each task.

## Key Features

- **Composition Shorthand**: Simple, declarative functions for common musical operations
- **Advanced Transformations**: Complex, music-theory-aware transformations using the full power of music21
- **Event-Based Architecture**: Clean separation between musical content and engraving
- **LilyPond Integration**: Professional-quality music engraving via Abjad
- **Extensible Design**: Easy to add new transformations and compositional techniques

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from composition_shorthand import from_scale_degrees, from_roman_numerals
from advanced_transformations import create_melodic_sequence

# Create a simple melody using scale degrees
melody = from_scale_degrees(
    degree_str="1-3-5-4-3-2-1",
    key_str="C",
    rhythm_str="q-q-q-q-q-q-h"
)

# Create a harmonic progression
harmony = from_roman_numerals(
    progression_str="I-IV-V-I",
    key_str="C",
    rhythm_str="w-w-w-w"
)

# Create a complex melodic sequence
sequence = create_melodic_sequence(
    events=melody,
    interval_pattern=[-2, -2, 2],
    key='C major'
)
```

## Modules

### `composition_shorthand.py`

Simple functions for declarative music creation:

- **`from_roman_numerals()`** - Generate chord progressions from Roman numeral notation
- **`from_scale_degrees()`** - Create melodies from scale degree numbers
- **`stretch_events()`** - Rhythmic augmentation/diminution
- **`transpose_events()`** - Transpose notes and chords
- **`augment()` / `diminish()`** - Convenience functions for rhythmic transformation

**Use when**: Arguments are simple, operations are straightforward, you want readable code.

### `advanced_transformations.py`

Complex, programmatic transformations:

- **`create_melodic_sequence()`** - Melodic sequencing with interval patterns
- **`realize_figured_bass()`** - Generate upper voices from figured bass notation
- **`apply_modal_mixture()`** - Modal interchange/borrowing techniques

**Use when**: You need complex arguments, music theory awareness, or full music21 API access.

## Documentation

- **[Advanced Transformations Guide](ADVANCED_TRANSFORMATIONS_GUIDE.md)** - Comprehensive guide to both modules
- **[Development Guide](DEVELOPMENT.md)** - How to run and develop the project

## Examples

### Running the Test Suite

```bash
python3 test_transformations.py
```

### Running the Example Composition

```bash
python3 example_composition.py
```

### Creating a Complete Composition

```python
from composition_shorthand import from_scale_degrees, from_roman_numerals, augment
from advanced_transformations import create_melodic_sequence, realize_figured_bass


def build_score_data():
    """Build a complete musical score using the hybrid model."""

    # Simple operations with shorthand
    theme = from_scale_degrees("1-3-5-3-1", "C", "q-q-q-q-h")
    harmony = from_roman_numerals("I-IV-V-I", "C", "w-w-w-w")

    # Complex operations programmatically
    soprano_sequence = create_melodic_sequence(
        events=theme,
        interval_pattern=[-2, -2, 2],
        key='C major'
    )

    bass_line = from_scale_degrees("1-4-5-1", "C", "w-w-w-w")
    satb_voices = realize_figured_bass(
        bass_events=bass_line,
        figures="5/3 6 5/3 5/3"
    )

    # Combine into final score
    return {
        'metadata': {
            'title': 'My Composition',
            'composer': 'Codempose User'
        },
        'parts': {
            'Melody': {'Soprano': soprano_sequence},
            'Harmony': {
                'Alto': satb_voices['Alto'],
                'Tenor': satb_voices['Tenor'],
                'Bass': satb_voices['Bass']
            }
        }
    }
```

## Architecture

Codempose uses a **two-tiered architecture**:

```
┌─────────────────────────────────────────┐
│ COMPOSITION SHORTHAND                   │
│ Simple, declarative operations          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ ADVANCED TRANSFORMATIONS                │
│ Complex, programmatic operations        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ EVENT DICTIONARIES                      │
│ Canonical representation                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ ENGRAVING (Abjad/LilyPond)             │
│ Professional music notation output      │
└─────────────────────────────────────────┘
```

This separation ensures:
- ✅ Clean, readable code for 80% of operations
- ✅ Unlimited power for complex 20%
- ✅ Easy maintenance and extension
- ✅ Type safety and IDE support

## Event Dictionary Format

All functions use a canonical event dictionary format:

**Note**:
```python
{
    'type': 'note',
    'step': 'C',      # Note name (C, D, E, F, G, A, B)
    'octave': 4,      # Octave number
    'alter': 0,       # Accidental (-1=flat, 0=natural, 1=sharp)
    'ql': 1.0         # Quarter length (duration)
}
```

**Rest**:
```python
{
    'type': 'rest',
    'ql': 1.0
}
```

**Chord**:
```python
{
    'type': 'chord',
    'ql': 1.0,
    'pitches': [
        {'step': 'C', 'octave': 4, 'alter': 0},
        {'step': 'E', 'octave': 4, 'alter': 0},
        {'step': 'G', 'octave': 4, 'alter': 0}
    ]
}
```

## Contributing

Contributions are welcome! When adding new transformations:

1. **For simple operations**: Add to `composition_shorthand.py`
   - Keep arguments simple (strings, numbers)
   - Return event dictionaries
   - Add documentation and examples

2. **For complex operations**: Add to `advanced_transformations.py`
   - Accept complex arguments as needed
   - Leverage music21 API extensively
   - Add comprehensive documentation

3. **Always**:
   - Add tests to `test_transformations.py`
   - Update `ADVANCED_TRANSFORMATIONS_GUIDE.md`
   - Follow existing code style

## Technologies

- **[music21](https://web.mit.edu/music21/)** - Music analysis and generation
- **[Abjad](https://abjad.github.io/)** - LilyPond score construction
- **[LilyPond](http://lilypond.org/)** - Music engraving
- **Python 3.12+** - Programming language

## License

See repository for license information.

## Acknowledgments

This framework is inspired by principles from tonal harmony theory and designed to support both traditional compositional techniques and modern algorithmic approaches.
