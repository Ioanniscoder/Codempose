# Codempose Study Files

This directory contains 17 study files demonstrating all features of the Codempose framework.

## 🎵 Running Study Files

Study files can be run from **anywhere**:

```bash
# From the studies/ directory:
cd studies
python first.py
python seventeenth.py

# From the root directory:
python studies/sixth.py
python studies/sixteenth.py

# From any location:
python /path/to/Codempose/studies/tenth.py
```

The automatic path detection in each study file ensures core modules are always found.

## 📚 Study Files Overview

### Basic Studies (1-7)
- **first.py** - Template study with melody variants
- **second.py** - Simple melody demonstration
- **third.py** - Rhythm and duration examples
- **fourth.py** - Key signatures and tempo
- **fifth.py** - Articulations showcase
- **sixth.py** - Multi-voice polyphony (2 voices, 1 staff)
- **seventh.py** - Dynamics and expressions

### Advanced Studies (8-14)
- **eighth.py** - Grace notes (acciaccatura, appoggiatura)
- **ninth.py** - Tuplets (triplets, quintuplets)
- **tenth.py** - Multi-voice SATB (4 voices, 2 staves)
- **eleventh.py** - Transformations (transpose, invert, retrograde)
- **twelfth.py** - Chord notation and harmony
- **thirteenth.py** - **Complete feature showcase** (all parser features + transformations)
- **fourteenth.py** - Blueprint string framework

### Harmonic Intelligence (15-17)
- **fifteenth.py** - Structural tone analysis
- **sixteenth.py** - Basic harmonization (I-IV-V-I)
- **seventeenth.py** - Advanced harmonization (I-vi-IV-V-I)

## 🎼 Study File Structure

Each study file follows the "Composer-First" workflow with 4 stations:

```python
"""Docstring - describes the study"""

import _study_path  # Auto-path setup (DO NOT REMOVE)

# ============================================================================
# STATION 1: LILYPOND SNIPPETS
# ============================================================================
MELODY_LILY = r"""
\relative c'' {
    c4 d e f | g2 a2
}
""".strip()

# ============================================================================
# STATION 2: VALIDATION (automatic)
# ============================================================================
# (Optional - parser validates automatically)

# ============================================================================
# STATION 3: BUILD SCORE DATA
# ============================================================================
def build_score_data():
    # Programmatic composition logic
    return score_data

# ============================================================================
# STATION 4: EXECUTION
# ============================================================================
if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
```

## 🔧 Technical Details

### Automatic Path Detection

Each study file imports `_study_path` which:
- Detects the root directory automatically
- Adds it to `sys.path` for module imports
- Works from any execution location

This is implemented in `_study_path.py`:

```python
import sys
from pathlib import Path

study_dir = Path(__file__).parent.resolve()
root_dir = study_dir.parent

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
```

### Core Module Imports

Study files can import core Codempose modules:

```python
from project_template import run_pipeline_from_file
from lilypond_parser import parse_lilypond_to_data
from music_data import data_to_part, part_to_data
from harmonic_analysis import find_structural_tones
from harmonic_engine import harmonize_melody
from score_builder import build_score_from_blueprint
from transformations import transpose_melody, invert_melody
```

## 📤 Output

All study files generate output in the `outputs/` directory:

```
outputs/
├── first.ly          # LilyPond source
├── first.pdf         # Engraved score
├── first.midi        # MIDI playback
├── first.musicxml    # MusicXML export
├── ...
└── seventeenth.*     # (same for each study)
```

## 🎯 Creating New Studies

1. Copy an existing study file as a template
2. Modify the LilyPond snippets in STATION 1
3. Optionally add programmatic logic in STATION 3
4. Keep the `import _study_path` line at the top
5. Run your new study: `python my_new_study.py`

Example:

```bash
cp seventeenth.py eighteenth.py
# Edit eighteenth.py
python eighteenth.py
```

## ⚠️ Important Notes

- **DO NOT REMOVE** the `import _study_path` line - it's required for path setup
- Study files are **self-contained** and **executable**
- All imports happen at runtime (inside functions or `if __name__ == '__main__'`)
- Backup files (`.bak`) are kept for safety - you can delete them if everything works

## 🚀 Quick Examples

### Run a Simple Study
```bash
python studies/first.py
# Generates: outputs/first.pdf, outputs/first.midi, outputs/first.musicxml
```

### Run Harmonization
```bash
python studies/sixteenth.py
# Generates two-stave score with melody + bass line
```

### Run Complete Showcase
```bash
python studies/thirteenth.py
# Demonstrates ALL parser features and transformations
```

## 📖 For More Information

- See `CODEMPOSE_STUDY_TEMPLATES.py` for template code
- See `outputs/DOCUMENTATION/` for comprehensive guides
- See `project_template.py` for pipeline documentation
