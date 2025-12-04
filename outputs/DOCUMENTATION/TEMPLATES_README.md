# Codempose Template Files - Quick Reference

**Included in:** `codempose_complete_with_harmonic_intelligence.tar.gz`

---

## Template Files Overview

The complete Codempose system now includes **comprehensive template files** to help you create new compositions and understand all available music21 functionality.

### 📚 Template Files Included

| File | Lines | Purpose |
|------|-------|---------|
| `MUSIC21_API_TEMPLATES.py` | 1,100+ | Complete music21 API reference with working examples |
| `CODEMPOSE_STUDY_TEMPLATES.py` | 700+ | Study file templates for all composition types |
| `project_template.py` | ~1,400 | Core pipeline framework (already in system) |

---

## MUSIC21_API_TEMPLATES.py

### What's Inside

Complete working examples for **17 categories** of music21 functionality:

1. ✅ **Basic Note and Rest Creation** - All methods for creating notes
2. ✅ **Pitch Manipulation** - Transposition, intervals, alterations
3. ✅ **Duration and Rhythm** - All note values, dotted notes, tuplets
4. ✅ **Articulations** - Staccato, accent, tenuto, marcato, etc.
5. ✅ **Expressions** - Fermata, trill, turn, mordent
6. ✅ **Dynamics** - pp to fff, crescendo, diminuendo
7. ✅ **Ornaments** - Grace notes, trills, turns
8. ✅ **Tuplets** - Triplets, quintuplets, nested tuplets
9. ✅ **Ties and Slurs** - Tied notes, phrasing
10. ✅ **Chords** - Chord creation, analysis, inversions
11. ✅ **Measures and Time Signatures** - 4/4, 3/4, 6/8, irregular meters
12. ✅ **Key Signatures** - Major, minor, relatives, parallels
13. ✅ **Tempo Markings** - BPM, text markings
14. ✅ **Parts and Voices** - Multi-part scores, voice management
15. ✅ **Score Assembly** - Complete score construction
16. ✅ **Roman Numeral Analysis** - Harmonic analysis, chord progressions
17. ✅ **Export and Conversion** - All export formats

### Example Usage

```python
# Import the templates
from MUSIC21_API_TEMPLATES import create_chords, roman_numeral_analysis

# Use the examples
c_major = create_chords()
I, IV, V, vi = roman_numeral_analysis()
```

### Quick Examples from Template

**Create a Note:**
```python
n = note.Note('C4', quarterLength=1.0)
n.articulations.append(articulations.Staccato())
```

**Transpose:**
```python
n_up = n.transpose('M3')  # Up major third
```

**Create Chord:**
```python
c_major = chord.Chord(['C4', 'E4', 'G4'])
```

**Roman Numeral:**
```python
I = roman.RomanNumeral('I', key.Key('C'))
root = I.root()  # Returns C
```

---

## CODEMPOSE_STUDY_TEMPLATES.py

### What's Inside

Ready-to-use templates for **5 types** of study files:

1. ✅ **Basic Single-Voice** - Simple melody studies
2. ✅ **Multi-Voice (SATB)** - Four-part compositions
3. ✅ **Harmonized** - Auto-generated bass lines
4. ✅ **Advanced Features** - Grace notes, tuplets, articulations
5. ✅ **Custom Transformations** - Music21 transformations

### Templates Included

| Template | Use Case | Example Files |
|----------|----------|---------------|
| `TEMPLATE_BASIC` | Single melody | first.py, second.py |
| `TEMPLATE_MULTI_VOICE` | SATB composition | tenth.py |
| `TEMPLATE_HARMONIZED` | Auto-harmonization | sixteenth.py, seventeenth.py |
| `TEMPLATE_ADVANCED` | Special notation | eighth.py (grace notes) |
| `TEMPLATE_CUSTOM` | Transformations | Custom studies |

### Quick Start: Create New Study

```python
# Copy template to new file
from CODEMPOSE_STUDY_TEMPLATES import create_study_file

# Create a basic study
create_study_file('eighteenth.py', 'basic')

# Create a harmonized study
create_study_file('nineteenth.py', 'harmonized')
```

### Template Structure

Every study file has 4 stations:

```python
# STATION 1: LILYPOND SNIPPETS
MELODY_LILY = r"""
\relative c'' {
    c4 d4 e4 f4 |
    g2 a2
}
""".strip()

# STATION 2: VALIDATION (automatic)

# STATION 3: BUILD SCORE DATA
def build_score_data():
    # Parse and build
    return score_data

# STATION 4: EXECUTION
if __name__ == '__main__':
    run_pipeline_from_file(__file__)
```

---

## Common LilyPond Patterns

Included in `CODEMPOSE_STUDY_TEMPLATES.py`:

### Notes and Durations
```lilypond
c4 d4 e4 f4              % Quarter notes
c2 d2                    % Half notes
c1                       % Whole note
c4.                      % Dotted quarter
```

### Articulations
```lilypond
c4-.                     % Staccato
c4->                     % Accent
c4-!                     % Marcato
```

### Dynamics
```lilypond
c4\f                     % Forte
c4\p                     % Piano
c4\< d e f\!             % Crescendo
```

### Grace Notes
```lilypond
\acciaccatura { d8 } c4  % Slashed grace note
\appoggiatura { e8 } d4  % Unslashed grace note
```

### Tuplets
```lilypond
\tuplet 3/2 { c8 d e }   % Triplet
```

---

## Canonical Format Patterns

Included in `CODEMPOSE_STUDY_TEMPLATES.py`:

### Basic Note Event
```python
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'alter': 0,
    'ql': 1.0
}
```

### Note with Articulations
```python
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'alter': 0,
    'ql': 1.0,
    'articulations': ['staccato', 'accent']
}
```

### Tuplet Note
```python
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'alter': 0,
    'ql': 0.6667,
    'tuplet': {'actual': 3, 'normal': 2}
}
```

---

## How to Use These Templates

### 1. Reference While Coding

Keep `MUSIC21_API_TEMPLATES.py` open as a reference when working with music21 objects.

### 2. Copy and Modify

Copy relevant sections from templates into your code:

```python
# From MUSIC21_API_TEMPLATES.py
def add_articulations():
    n = note.Note('C4')
    n.articulations.append(articulations.Staccato())
    n.articulations.append(articulations.Accent())
    return n
```

### 3. Start New Studies

Use `CODEMPOSE_STUDY_TEMPLATES.py` to create new study files:

```bash
python3 -c "from CODEMPOSE_STUDY_TEMPLATES import create_study_file; create_study_file('my_study.py', 'harmonized')"
```

### 4. Learn music21

Work through the examples in `MUSIC21_API_TEMPLATES.py` to understand music21's capabilities.

---

## Quick Reference Cheatsheet

### Create a Basic Study

```python
"""My Study"""

MELODY_LILY = r"""
\relative c'' {
    \time 4/4
    \key c \major
    c4 d4 e4 f4 |
    g2 a2
}
""".strip()

def build_score_data():
    from lilypond_parser import parse_lilypond_to_data
    melody_data = parse_lilypond_to_data(MELODY_LILY)
    return {
        'metadata': {'title': 'My Study'},
        'parts': {'Melody': melody_data['parts']['Melody']}
    }

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
```

### Add Harmonization

```python
from harmonic_engine import harmonize_melody
from music_data import data_to_part, part_to_data

melody_part = data_to_part(melody_events)
score = harmonize_melody(melody_part, "I - IV - V - I", "C")
bass_events = part_to_data(score.parts[1])
```

### Use music21 Transformations

```python
from music21 import interval

melody_part = data_to_part(melody_events)
transposed = melody_part.transpose('M3')  # Up major third
transformed_events = part_to_data(transposed)
```

---

## All Identified music21 Functions

**Complete list in `MUSIC21_API_TEMPLATES.py`:**

### Core Classes
- `note.Note()` - Create notes
- `note.Rest()` - Create rests
- `pitch.Pitch()` - Pitch manipulation
- `chord.Chord()` - Create chords
- `stream.Measure()` - Create measures
- `stream.Part()` - Create parts
- `stream.Voice()` - Create voices
- `stream.Score()` - Create scores

### Articulations
- `articulations.Staccato()`
- `articulations.Accent()`
- `articulations.Tenuto()`
- `articulations.Marcato()`
- `articulations.Staccatissimo()`

### Expressions
- `expressions.Fermata()`
- `expressions.Trill()`
- `expressions.Turn()`
- `expressions.Mordent()`
- `expressions.InvertedMordent()`

### Dynamics
- `dynamics.Dynamic('f')` - pp, p, mp, mf, f, ff, fff
- `dynamics.Crescendo()`
- `dynamics.Diminuendo()`

### Meter & Key
- `meter.TimeSignature('4/4')`
- `key.Key('C')` - Major/minor keys
- `tempo.MetronomeMark(number=120)`

### Harmonic Analysis
- `roman.RomanNumeral('I', key)`
- `harmony.ChordSymbol('Cmaj7')`
- `interval.Interval('M3')`

### And Many More!
See `MUSIC21_API_TEMPLATES.py` for complete reference.

---

## Documentation Links

**Within Archive:**
- `MUSIC21_API_TEMPLATES.py` - music21 function reference
- `CODEMPOSE_STUDY_TEMPLATES.py` - Study file templates
- `HARMONIC_IMPLEMENTATION_COMPLETE.md` - Harmonic intelligence API
- `COMPLETE_SYSTEM_MANIFEST.md` - Full system documentation

**External:**
- music21 Official Documentation: https://web.mit.edu/music21/doc/

---

## Summary

✅ **MUSIC21_API_TEMPLATES.py**: Complete music21 function reference with 17 categories  
✅ **CODEMPOSE_STUDY_TEMPLATES.py**: 5 ready-to-use study file templates  
✅ **LilyPond Patterns**: Common notation patterns and syntax  
✅ **Canonical Format**: Internal data format examples  
✅ **Quick Reference**: Cheatsheet for common tasks  

**All templates are working, tested code that you can copy and modify for your own compositions!**
