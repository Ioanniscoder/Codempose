# Codempose - Compositional Music Framework

**A Python-based music composition framework with LilyPond engraving, MIDI export, and MusicXML generation.**

---

## 🎵 Quick Start

### 1. Generate a New Study
```bash
python generate_study.py 2 "My Composition"
```

This creates `studies/second.py` with a complete Blueprint Strings template.

### 2. Edit Your Composition
Open `studies/second.py` and edit the musical snippets:
```python
SNIPPETS = {
    'INTRO': r"\relative c' { c4 d e f }",
    'THEME': r"\relative c' { g4 a b c }",
}
```

### 3. Run the Pipeline
```bash
python studies/second.py
```

This generates in `outputs/`:
- `second.ly` - LilyPond source
- `second.pdf` - Engraved score
- `second.midi` - Audio playback
- `second.musicxml` - MuseScore import

---

## 📂 Project Structure

```
Codempose/
├── generate_study.py              # Generate new study files
├── CODEMPOSE_STUDY_TEMPLATES.py   # Template library
│
├── src/                           # Core modules
│   ├── project_template.py        # Main pipeline
│   ├── score_builder.py           # Blueprint Strings engine
│   ├── lilypond_parser.py         # Parser
│   └── ...                        # Other modules
│
├── studies/                       # Your compositions
│   ├── _study_path.py             # Auto-import helper
│   └── OLD/                       # Archived studies
│
├── outputs/                       # Generated files (browser root)
│   ├── TEMPLATES/                 # Reference examples
│   └── DOCUMENTATION/             # Generated docs
│
├── tests/                         # Test suite (11 tests, 100% passing)
└── DOCUMENTATION/                 # Project documentation
```

---

## 🎼 Blueprint Strings Framework (Recommended)

The **composer-first** approach using musical delimiters:

### Delimiters
- `;` (semicolon) - Section separator
- `&` (ampersand) - Staff separator (vertical stacking)
- `|` (pipe) - Concatenation (horizontal "then")
- `,` (comma) - Voice separator (polyphonic staves)
- `'r'` - Auto-rest placeholder

### 🆕 On-The-Fly Transformations (New!)
Apply musical transformations directly in blueprint strings:

```python
# Single-part transformations (no suffix needed)
VOICE_STAVE_DATA = """
    THEME & BASS;
    transpose_part(THEME, 'P5') & BASS;
    invert_part(THEME, 'C4') & BASS;
    retrograde_part(THEME) & BASS
"""

# Multi-part transformations (suffix required)
VOICE_STAVE_DATA = """
    harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody
    &
    harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony
"""
```

**Available transformations:**
- **Single-part**: `transpose_part`, `invert_part`, `retrograde_part`, `augment_part`, `diminish_part`, `chordify_part`
- **Multi-part**: `harmonize_part` (returns `:melody` and `:harmony`)

**Hybrid Suffix Model**: Single-part transformations work without suffix (backward compatible), multi-part transformations require explicit suffix like `:melody` or `:harmony`.

📖 **See:** `DOCUMENTATION/HYBRID_SUFFIX_MODEL.md` | `DOCUMENTATION/TRANSFORMATION_QUICK_REFERENCE.md`

### Example
```python
VOICE_STAVE_DEF = "Melody & Bass"
VOICE_STAVE_DATA = "INTRO ; THEME_A | transpose_part(THEME_A, 'P5') & BASS"
```

**Result**: 2 staves, 2 sections
- Section 1: Melody plays INTRO, Bass rests
- Section 2: Melody plays THEME_A + HARMONY (polyphonic), Bass plays BASS

See generated study files for all 7 layout variants!

---

## 🔧 Running from Different Locations

Studies work from anywhere thanks to absolute paths:
```bash
# From root
python studies/second.py

# From studies/
cd studies && python second.py

# From anywhere
python /path/to/studies/second.py
```

All outputs always go to `/workspaces/Codempose/outputs/`

---

## 📚 Documentation

- `DOCUMENTATION/` - Migration reports, analysis docs
- `outputs/TEMPLATES/` - Music21 API examples, tonal harmony templates
- `outputs/DOCUMENTATION/` - Generated documentation
- Generated studies - Inline comments with all examples

---

## ✅ Test Suite

```bash
python -m pytest tests/ -v
```

**Status**: 11 tests, 100% passing  
**Coverage**: 
- Chord parsing, pipeline, MIDI generation
- Hybrid enharmonic handling (LILY + TINY formats)
- Blueprint transformations (single-part + multi-part)
- Harmonic intelligence (harmonize_part with suffix model)
- Station 2 dual-format population

---

## 🎯 Features

- **Blueprint Strings** - Intuitive composition with musical delimiters
- **Hybrid Suffix Model** - Single-part transformations auto-handled, multi-part explicit
- **Harmonic Intelligence** - Auto-harmonization with chord progressions
- **Musical Transformations** - Transpose, invert, retrograde, augment, diminish, chordify
- **LilyPond Engraving** - Professional score layout via Abjad
- **Multi-format Export** - PDF, MIDI, MusicXML, LilyPond
- **Hybrid Verification** - Intelligent pitch spelling validation with LILY + TINY formats
- **Station Architecture** - 4-station model (Input → Validation → Blueprint → Programmatic)
- **Composition Shortcuts** - Repeat operator (`*3` syntax) for pattern repetition
- **Absolute Paths** - Works from any directory, browser integration ready
- **Creative Examples** - Real musical snippets included in template generator

---

## 📖 Example Workflow

```bash
# 1. Generate new study
python generate_study.py 5 "SATB Chorale"

# 2. Edit studies/fifth.py - add your music

# 3. Run pipeline
python studies/fifth.py

# 4. View outputs/fifth.pdf in browser
# (outputs/ directory is the browser root)

# 5. Import outputs/fifth.musicxml to MuseScore for further editing
```

---

## 🛠️ Requirements

- Python 3.11+
- Abjad (LilyPond wrapper)
- music21
- LilyPond (for PDF generation)

See `requirements.txt` or `.devcontainer/` for full setup.

---

**Version**: October 2025  
**Structure**: Clean migration - src/ organized, 100% tests passing, Blueprint Strings as default  
**Latest**: Hybrid suffix model + harmonic intelligence + creative examples (Oct 19, 2025)
