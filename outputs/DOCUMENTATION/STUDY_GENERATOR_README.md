# Codempose Study File Generator

Generate new study files with comprehensive templates including all Codempose features.

## Quick Start

```bash
# Generate a new study file
python generate_study.py 18

# Generate with custom title
python generate_study.py 19 "Advanced Harmonic Analysis"

# Generate any number
python generate_study.py 100 "Centennial Study"
```

## What Gets Generated

Each generated study file includes:

### ✅ Complete Station Structure
- **Station 1**: LilyPond Snippets (musical ideas)
- **Station 2**: Programmatic Voice Generation
- **Station 3**: Composition Shorthand
- **Station 4**: Harmonic Intelligence
- **Station 5**: Score Assembly

### ✅ All Feature Examples
- **Parser Features**: Tuplets, ties, grace notes, articulations, dynamics, chords
- **Transformations**: Transpose, invert, retrograde
- **Composition Patterns**: LilyPond snippets, programmatic, shorthand
- **Harmonic Intelligence**: Structural analysis, auto-harmonization
- **Multi-Voice**: SATB arrangement template

### ✅ Multiple Approaches
The template includes 4 different approaches (commented out, uncomment to use):

1. **Simple Single Melody** (default, active)
2. **Multi-Part Score** (melody + harmony + bass)
3. **Composition Shorthand** (declarative combinations)
4. **Harmonic Intelligence** (auto-harmonization)

## Generated File Structure

```python
"""
EIGHTEENTH STUDY: Feature Demonstration
========================================

Comprehensive template with all features...
"""

import _study_path  # Auto-path setup

# Imports for all features
from lilypond_parser import parse_lilypond_to_data
from composition_shorthand import build_score_from_assignments
from harmonic_engine import harmonize_melody
# ... etc

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================

MELODY_LILY = r"""
\relative c'' {
    \time 4/4
    c4-. d4-> e4-- f4-^  |    # Articulations
    \acciaccatura { d8 } c4   # Grace notes
    \tuplet 3/2 { c8 d e }    # Tuplets
    a4~ a4                     # Ties
    <c e g>2                   # Chords
}
"""

# ... More snippets

# ============================================================================
# STATION 5: BUILD SCORE DATA
# ============================================================================

def build_score_data():
    # Parse and return score
    melody_data = parse_lilypond_to_data(MELODY_LILY)
    melody_events = melody_data['parts']['Part 1']
    
    return {
        'metadata': {'title': TITLE, 'composer': COMPOSER},
        'parts': {'Melody': melody_events}
    }

if __name__ == '__main__':
    run_pipeline_from_file(__file__)
```

## Usage Examples

### Example 1: Generate Basic Study
```bash
python generate_study.py 20
```

Output: `studies/twentieth.py`

### Example 2: Generate with Custom Title
```bash
python generate_study.py 25 "Modal Composition Study"
```

Output: `studies/twentyfifth.py` with title "TWENTYFIFTH Study: Modal Composition Study"

### Example 3: Run Generated Study
```bash
# Generate
python generate_study.py 21

# Run from root
python studies/twentyfirst.py

# Or run from studies directory
cd studies
python twentyfirst.py
```

## Customizing Generated Files

After generation, edit the file to:

1. **Modify LilyPond Snippets** (Station 1)
   - Change the melody, harmony, bass patterns
   - Add more musical features

2. **Choose Approach** (Station 5)
   - Uncomment one of the 4 approaches
   - Comment out the default simple approach

3. **Add Transformations**
   - Use composition_shorthand for declarative combinations
   - Use harmonic_engine for auto-harmonization
   - Use transformations for transpose/invert/retrograde

## Features in Template

### Parser Features Demonstrated
```lilypond
% Articulations
c4-. d4-> e4-- f4-^

% Dynamics
c4\f d4\p e2

% Grace notes
\acciaccatura { d8 } c4

% Tuplets
\tuplet 3/2 { c8 d e }

% Ties
a4~ a4

% Chords
<c e g>2
```

### Composition Shorthand Examples
```python
SHORTHAND_ASSIGNMENTS = {
    'Soprano': {
        'Main': 'MELODY',  # Direct reference
    },
    'Alto': {
        'Main': 'transpose(MELODY, -5)',  # Transpose
    },
    'Bass': {
        'Main': 'BASS',
    }
}
```

### Harmonic Intelligence Example
```python
# In build_score_data():
melody_part = data_to_part(melody_events)

# Analyze
structural_analysis = find_structural_tones(melody_part)

# Harmonize
harmonized_score = harmonize_melody(melody_part, "I - IV - V - I", "C")
```

## Number to Ordinal Conversion

The generator automatically converts numbers to ordinal words:

| Number | Ordinal | Filename |
|--------|---------|----------|
| 18 | eighteenth | eighteenth.py |
| 19 | nineteenth | nineteenth.py |
| 20 | twentieth | twentieth.py |
| 25 | twentyfifth | twentyfifth.py |
| 100 | 100th | 100th.py |

## File Locations

- **Generator**: `generate_study.py` (root directory)
- **Output**: `studies/<ordinal>.py`
- **Execution**: Works from root or studies/ directory (thanks to `_study_path.py`)

## Integration with Codempose

Generated files:
- ✅ Include `import _study_path` for automatic path resolution
- ✅ Work from both root and studies/ directory
- ✅ Use standard Codempose pipeline via `run_pipeline_from_file()`
- ✅ Generate PDF, MIDI, and MusicXML outputs

## Summary

The study generator provides a comprehensive starting point for new compositions with:
- All Codempose features demonstrated
- Multiple composition approaches
- Complete documentation
- Ready to run and customize

**Generate your first study:**
```bash
python generate_study.py 18 "My First Generated Study"
cd studies
python eighteenth.py
```

Your PDF, MIDI, and MusicXML files will be in `outputs/`!
