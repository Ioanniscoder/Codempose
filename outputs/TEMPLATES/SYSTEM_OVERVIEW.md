# Codempose System Overview

**Purpose**: Quick orientation to the Codempose architecture and workflow.

**Read this first** if you're new to Codempose or want to understand how everything fits together.

**For function reference**, see: `ADVANCED_MUSIC21_GUIDE.md`

---

## The Complete Codempose System

```
YOUR STUDY FILE (studies/mystudy.py)
    ↓
STATION 1: Define snippets in LilyPond
    ↓
STATION 2: Framework auto-parses to event dicts (internal)
    ↓
STATION 3: Blueprint Strings (simple) OR Station 4: Python Code (advanced)
    ↓
RENDERING ENGINE (src/project_template.py)
    ↓
OUTPUTS: PDF, MIDI, MusicXML in outputs/ folder
```

---

## File Structure & Responsibilities

| File Path | What It Does | When You Use It |
|-----------|--------------|-----------------|
| **`studies/your_file.py`** | Your composition file | Always (this is what you create) |
| **`src/lilypond_parser.py`** | Converts LilyPond → event dicts | Automatically (Station 1→2) |
| **`src/score_builder.py`** | Processes Blueprint strings | Automatically (Station 3) |
| **`src/transformations.py`** | **ALL transformation functions** | Station 3 & 4 |
| **`src/composition_shorthand.py`** | Event-level transformations | Station 4 only |
| **`src/music_data.py`** | Converts event dicts ↔ music21 objects | Station 4 only |
| **`src/lib/TONAL_HARMONY_TEMPLATES.py`** | Analysis & validation tools | Station 4 only |
| **`src/lib/MUSIC21_API_TEMPLATES.py`** | music21 cheat sheet | Station 4 reference |
| **`src/project_template.py`** | Rendering engine | Automatically |

---

## Documentation Files

| Document | Purpose | Read This When... |
|----------|---------|-------------------|
| **`SYSTEM_OVERVIEW.md`** (this file) | Architecture overview | You're new or want the big picture |
| **`ADVANCED_MUSIC21_GUIDE.md`** | Complete function reference (Station 3 & 4) | You need to look up functions or code structure |
| **`outputs/TEMPLATES/README.md`** | Basic workflow intro | You want a quick start |
| **`studies/100th.py`** | Working Station 3 example | You want to see Blueprint in action |
| **`studies/fugue.py`** | Working Station 4 example | You want to see programmatic code |

---

## The Four Stations Explained

### STATION 1: Define Musical Ideas (LilyPond)

**What You Do**: Write LilyPond notation strings  
**What Happens**: Framework parses them into event dictionaries  
**Output**: Internal SNIPPETS library  

```python
# In your study file (Station 1):
THEME_LILY = r"""
\relative c' {
    \key c \major \time 4/4
    c4 d e f | g2 e2
}
"""

# Framework converts to (you never see this):
# [
#   {'type': 'note', 'step': 'c', 'octave': 4, 'ql': 1.0, ...},
#   {'type': 'note', 'step': 'd', 'octave': 4, 'ql': 1.0, ...},
#   ...
# ]
```

**Why LilyPond?**
- More readable than raw Python dicts
- Standard music notation format
- Supports complex rhythms, articulations, dynamics
- The framework handles parsing automatically

**You never need to see the event dictionaries unless you're in Station 4.**

---

### STATION 2: Snippet Library (Auto-Generated LilyPond)

**What You Do**: Define placeholder variables for transformed snippets  
**What Happens**: Framework auto-populates them with LilyPond strings after transformations run  
**Output**: Reusable LilyPond snippet variables in your study file  

```python
# In your study file:

# STATION 1: Original snippets
THEME_LILY = r"\relative c' { c4 d e f | g2 e2 }"

# STATION 2: Transformed snippet library (auto-populated)
THEME_P5_LILY = None      # Auto-filled: r"\relative c' { g4 a b c' | d'2 b2 }"
THEME_INVERTED_LILY = None # Auto-filled after running

# STATION 3: Use transformations
VOICE_STAVE_DATA = """
    THEME;
    transpose_part(THEME, 'P5');  # Creates THEME_P5_LILY
    invert_part(THEME, 'c4')      # Creates THEME_INVERTED_LILY
"""
```

**Key Point**: Station 2 is a **library of LilyPond snippet variables**:
- Auto-populated when you run your study
- Available for reuse in new compositions
- No need to copy from .ly files - the variables are already in your .py study file!

---

### STATION 3: Blueprint Strings (Simple Approach)

**What You Do**: Write simple text formulas  
**What Happens**: Framework interprets and builds score  
**Best For**: Simple transformations, declarative structure, visual readability  

```python
# Simple layout definition:
VOICE_STAVE_DEF = "Melody & Bass"

# Simple content definition:
VOICE_STAVE_DATA = """
    THEME & BASS;                              # Section 1
    transpose_part(THEME, 'P5') & BASS         # Section 2: Theme up 5th
"""
```

**Blueprint Operators**:
- `|` = Sequential (one after another on same staff)
- `&` = Parallel (simultaneous on different staves)
- `;` = Section separator (like a double barline)
- `,` = Multi-voice (multiple voices on same staff)

**When to Use Station 3**:
- ✅ Simple transformations (transpose, invert, retrograde)
- ✅ Clear, readable structure
- ✅ No loops or conditionals needed
- ✅ Non-programmers will edit the file

---

### STATION 4: Programmatic Python (Advanced Approach)

**What You Do**: Write full Python code with logic  
**What Happens**: You control everything  
**Best For**: Algorithmic composition, complex logic, validation, performance optimization  

```python
PROMOTE_TO_PROGRAMMATIC = True  # Toggle to Station 4

def build_score_data():
    """Your custom composition logic."""
    from src.composition_shorthand import transpose_events
    
    # Get parsed snippet
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    # Build with logic
    sequence = []
    for semitones in [0, 2, 4, 5, 7]:  # C, D, E, F, G
        sequence += transpose_events(theme, semitones)
    
    return {'parts': {'Melody': sequence}}
```

**When to Use Station 4**:
- ✅ Need loops, conditionals, random generation
- ✅ Algorithmic/generative composition
- ✅ Voice leading validation required
- ✅ Complex multi-section forms
- ✅ Performance optimization (many transformations)

---

## Quick Decision Guide

| Need | Station 3 | Station 4 |
|------|-----------|-----------|
| Simple transformations | ✅ Best choice | ✅ Works |
| Loops/conditionals | ❌ Not possible | ✅ Required |
| Random/algorithmic | ❌ Not possible | ✅ Required |
| Visual readability | ✅ Very clear | ⚠️ More verbose |
| Voice leading validation | ❌ Not available | ✅ Required |
| Non-programmer editing | ✅ Easy | ⚠️ Needs coding knowledge |

---

## Next Steps

1. **New to Codempose?** → Read `outputs/TEMPLATES/README.md` for a quick start
2. **Want to see examples?** → Open `studies/100th.py` (Station 3) or `studies/fugue.py` (Station 4)
3. **Ready to code?** → See `ADVANCED_MUSIC21_GUIDE.md` for complete function reference
4. **Need help?** → Check the troubleshooting section in `ADVANCED_MUSIC21_GUIDE.md`

---

## File Path Quick Reference

```
/workspaces/Codempose/
├── generate_study.py              ← Template (copy to studies/)
├── studies/
│   ├── your_study.py              ← Your composition files go here
│   ├── 100th.py                   ← Station 3 example
│   └── fugue.py                   ← Station 4 example
├── src/
│   ├── transformations.py         ← Station 3 functions (transpose_part, etc.)
│   ├── composition_shorthand.py   ← Station 4 event functions
│   ├── music_data.py              ← Converters (events ↔ music21)
│   └── lib/
│       └── TONAL_HARMONY_TEMPLATES.py  ← Analysis tools
└── outputs/
    └── TEMPLATES/
        ├── SYSTEM_OVERVIEW.md              ← THIS FILE
        ├── ADVANCED_MUSIC21_GUIDE.md       ← Function reference
        └── README.md                        ← Quick start
```
