# CODEMPOSE TEMPLATES - QUICK START GUIDE

This directory contains templates for creating compositions with Codempose. **Start here** to understand how to actually use the framework.

---

## The 4-Station Workflow (Simple Version)

### Station 1: Write Musical Snippets
Write small musical ideas in LilyPond syntax:

```python
THEME = r"\relative c' { c4 d e f | g2 f4 e | d1 }"
```

### Station 2: Internal Parsing
**You don't touch this!** The framework automatically parses your LilyPond snippets into internal event dictionaries. This happens behind the scenes.

### Station 3: Arrange with Shorthand (Simple Compositions)
Use shorthand syntax to build your score:

```python
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'THEME + THEME',           # Play theme twice
        'Alto': 'transpose(THEME, 5)'         # Transpose up 5 semitones
    }
}
```

### Station 4: Program with Python (Complex Compositions)
Write Python code to generate and transform musical material:

```python
def build_score_data():
    theme_events = parse_lilypond_to_data(THEME)['parts']['theme']
    answer = transpose_events(theme_events, 7)  # Perfect 5th up
    inverted = invert_events(theme_events, 'c4')  # Mirror around C4
    
    return {
        'parts': {
            'Voice1': theme_events,
            'Voice2': answer,
            'Voice3': inverted
        }
    }
```

---

## FILES IN THIS DIRECTORY

### 📝 `study_template.py` - Basic Template
Copy this to start a new composition. Contains:
- Metadata setup (title, composer, opus)
- Station 1 snippet definitions
- Station 3 shorthand examples
- Complete working example

**Start here if:** You're new to Codempose or want simple transformations.

### 🎼 `station4_music21_examples.py` - Advanced Transformations
**Reference library** of music21-powered transformations. Contains example functions for:
- Pitch transformations (transpose, invert, retrograde)
- Rhythm transformations (augmentation, diminution)
- Contrapuntal techniques (canon, fugue)
- Harmonic analysis

**Use this when:** You need complex transformations like fugues, canons, or algorithmic composition.

**IMPORTANT**: These are example functions to copy/adapt, not a persistent library of your snippets.

### 🎵 `MUSIC21_API_TEMPLATES.py` & `TONAL_HARMONY_TEMPLATES.py`
Reference files showing music21 API usage and harmonic analysis patterns.

---

## HOW STATION 2 ACTUALLY WORKS

**Station 2 is a SNIPPET LIBRARY** that stores both original and transformed snippets in LilyPond format for copy-paste reuse.

### What Station 2 Really Is

**Station 2 = Automatic Library Builder**

When you use **Station 3 (Blueprint/Shorthand)**, the framework automatically:

1. **Parses** your Station 1 snippets into internal events
2. **Executes** transformations (transpose, invert, retrograde)
3. **Converts back** to LilyPond absolute notation
4. **Stores** ALL snippets (original + transformed) in Station 2 library
5. **Outputs** the library in TWO places:
   - In your `.py` file (for direct reuse in Python)
   - In your `.ly` file header (for reference)

### Where to Find Station 2 Snippets

**After running a Station 3 study** (one that uses `VOICE_ASSIGNMENTS`):

**Location 1: In the generated `.py` file** (in `outputs/` directory)
```python
# ============================================================================
# STATION 2: SNIPPET LIBRARY (Editable LilyPond - Absolute Notation)
# ============================================================================

THEME_A = r"""
\time 3/4 \key g \major
d'4 fis'8 g'8 a'4 | a'4 g'4 fis'4 | ...
"""

THEME_A_transpose_5 = r"""
\time 3/4 \key g \major
g'4 b'8 c''8 d''4 | d''4 c''4 b'4 | ...
"""

# Total snippets in Station 2 library: 8
# ✨ These include both original AND transformed snippets!
```

**Location 2: In the `.ly` file header** (for reference)
```lilypond
% ========================================
% ORIGINAL SNIPPETS (Station 1 & 2)
% ========================================
%
% THEME_A (12.0 QL, 4 bars, 3/4):
%   \relative c'' {
%       d4-. fis8 g a4~ | ...
%   }
```

### Station 3 vs Station 4 Difference

| Feature | Station 3 (Blueprint) | Station 4 (Programmatic) |
|---------|---------------------|------------------------|
| **Syntax** | `'transpose(THEME, 5)'` | `transpose_events(theme, 5)` |
| **Station 2 Library** | ✅ Auto-generated | ❌ Not generated |
| **Snippet Reuse** | Copy from `.py` file | Copy from `.ly` header or regenerate |
| **Use Case** | Simple arrangements | Complex logic, loops, conditions |

### Example: How Station 2 Builds

**Your Station 1 input:**
```python
THEME = r"\relative c' { c4 d e f }"

VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'THEME + transpose(THEME, 5)'
    }
}
```

**Station 2 library created automatically:**
```python
THEME = r"""
\time 4/4 \key c \major
c'4 d'4 e'4 f'4
"""

THEME_transpose_5 = r"""
\time 4/4 \key c \major
f'4 g'4 a'4 bes'4
"""
```

**You can then copy `THEME_transpose_5` into another study!**

### Why Doesn't fugue.py Have Station 2 Library?

`fugue.py` uses **Station 4** (programmatic), which doesn't auto-generate the Station 2 library because:
- You're writing Python directly (`transpose_events()`, `invert_events()`)
- The transformations are computed on-the-fly
- No intermediate snippet names to store

**To get Station 2 snippets from Station 4 code:**
1. Copy the LilyPond output from `fugue.ly` header
2. Paste into Station 1 of a new study
3. OR: Convert your Station 4 code to Station 3 shorthand

### Practical Usage

**Scenario 1: Reusing a Transformed Snippet**

After running `100th.py` (Station 3):
1. Open `outputs/100th.py`
2. Find Station 2 library section
3. Copy `THEME_A_transpose_5` variable
4. Paste into new study's Station 1
5. Use it: `'Soprano': 'THEME_A_transpose_5'`

**Scenario 2: Building a Library**

Create a "library study" just for generating snippets:
```python
# library_builder.py
THEME_A = r"..."
THEME_B = r"..."

VOICE_ASSIGNMENTS = {
    'Test': {
        'V1': 'transpose(THEME_A, 5)',
        'V2': 'invert(THEME_A)',
        'V3': 'retrograde(THEME_A)',
        'V4': 'transpose(THEME_B, 7)'
    }
}
```

Run it once → Copy all Station 2 snippets → Use in real compositions!

---

## COMPLETE PRACTICAL EXAMPLE

### Example 1: Simple 2-Part Canon (Station 3)

```python
"""Simple canon using Station 3 shorthand"""

# Station 1: Write your theme
THEME = r"""
\relative c' {
    \time 3/4
    c4 d e | f e d | e2 c4 | d2.
}
"""

# Station 3: Arrange with shorthand
VOICE_ASSIGNMENTS = {
    'Canon': {
        'Leader': 'THEME',
        'Follower': 'transpose(THEME, 7)'  # Perfect 5th up
    }
}

# Metadata
TITLE = "Canon at the Fifth"
COMPOSER = "Your Name"

# That's it! Run the file.
```

### Example 2: Fugue (Station 4)

```python
"""Fugue exposition using Station 4 programmatic approach"""

from src.lilypond_parser import parse_lilypond_to_data
from src.composition_shorthand import transpose_events, invert_events

# Station 1: Fugue subject
SUBJECT = r"\relative c' { c8 d e f | g4 f8 e | d2 }"

# Station 4: Build score programmatically
def build_score_data():
    # Parse subject
    data = parse_lilypond_to_data(SUBJECT, 'subject')
    subject = data['parts']['subject']
    
    # Generate transformations
    answer = transpose_events(subject, 7)      # +P5
    inversion = invert_events(subject, 'c4')   # Mirror
    
    # Assemble fugue with staggered entries
    return {
        'parts': {
            'Soprano': subject + make_rests(16),
            'Alto': make_rests(8) + answer + make_rests(8),
            'Tenor': make_rests(16) + inversion
        }
    }

def make_rests(ql):
    """Helper to create rest events"""
    return [{'type': 'rest', 'ql': float(ql), 'step': 'r', 
             'octave': 0, 'alter': 0}]

TITLE = "Fugue in C"
PROMOTE_TO_PROGRAMMATIC = True  # Use Station 4
```

---

## TRANSFORMATION QUICK REFERENCE

### Available in Station 3 Shorthand

```python
'Soprano': 'THEME'                    # Original
'Soprano': 'THEME + THEME'            # Concatenate (then)
'Soprano': 'THEME * 3'                # Repeat 3 times
'Soprano': 'transpose(THEME, 5)'      # Transpose +5 semitones
'Soprano': 'invert(THEME)'            # Invert around C4
'Soprano': 'retrograde(THEME)'        # Reverse (crab motion)
```

### Available in Station 4 Python

```python
from src.composition_shorthand import (
    transpose_events,  # (events, semitones)
    invert_events,     # (events, axis_pitch)
    retrograde_events, # (events)
    filter_events      # (events, exclude_types=['barline'])
)

# Example usage:
transposed = transpose_events(theme, 7)         # +P5
inverted = invert_events(theme, 'c4')           # Mirror C4
backwards = retrograde_events(theme)            # Reverse
clean = filter_events(theme, exclude_types=['barline'])
```

---

## COMMON WORKFLOWS

### Workflow 1: Simple Arrangement (Station 3)
1. Copy `study_template.py` → `mypiece.py`
2. Write snippets in Station 1
3. Use shorthand in `VOICE_ASSIGNMENTS`
4. Run: `python mypiece.py`
5. Check: `outputs/mypiece.pdf`

### Workflow 2: Complex Transformations (Station 4)
1. Copy `study_template.py` → `myfugue.py`
2. Set `PROMOTE_TO_PROGRAMMATIC = True`
3. Write `build_score_data()` function
4. Use transformation functions from `composition_shorthand`
5. Run: `python myfugue.py`

### Workflow 3: Study Advanced Examples
1. Read `station4_music21_examples.py` for ideas
2. Copy example functions into your study
3. Adapt to your needs
4. Test incrementally

---

## TIPS FOR SUCCESS

### ✅ DO

- Start with Station 3 shorthand for simple pieces
- Use Station 4 when you need loops, conditions, or complex logic
- Copy working examples and modify them
- Test small sections before building full pieces
- Check the `.ly` output to see what was generated

### ❌ DON'T

- Don't expect Station 2 to be a persistent snippet database
- Don't try to modify framework source files (use them as-is)
- Don't mix Station 3 and Station 4 in the same file (pick one)
- Don't write huge snippets (break into smaller sections)

---

## TROUBLESHOOTING

**Q: Where are my transformed snippets stored?**  
A: Transformed snippets are auto-populated as LilyPond variables in **Station 2** of your study file. Define placeholder variables (e.g., `THEME_P5_LILY = None`) and the framework fills them after running transformations.

**Q: Can I save transformation results for reuse?**  
A: Yes! Station 2 variables are automatically populated with LilyPond strings. After running your study once, the variables contain the transformed snippets ready to copy/paste for reuse in new compositions.

**Q: What's the difference between Station 3 and 4?**  
A: Station 3 uses string-based shorthand (`'THEME + transpose(THEME, 5)'`). Station 4 uses Python functions for complex logic.

**Q: Do I need to understand music21?**  
A: Not for basic use. The framework wraps music21 functionality in simple functions like `transpose_events()`.

---

## NEXT STEPS

1. **Beginner**: Copy `study_template.py`, modify snippets, use Station 3 shorthand
2. **Intermediate**: Try Station 4 with simple transformations (transpose, invert)
3. **Advanced**: Study `station4_music21_examples.py` for fugues and canons
4. **Expert**: Combine transformations and create algorithmic compositions

**Start with small experiments!** The framework handles all the complexity of LilyPond/PDF/MIDI/MusicXML generation automatically.
