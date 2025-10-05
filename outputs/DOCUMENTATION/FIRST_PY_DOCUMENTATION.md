# first.py - Two-Stave Composition Template

## Overview

`first.py` is a restructured study file demonstrating Codempose's dual-format system with two-stave musical output.

## Key Features

### 1. **Dual-Format Support**
Both LilyPond and TinyNotation formats coexist in the same file:

```python
# LilyPond format (always preserved for reference)
SOURCE_MELODY_LILY = r"""
\relative e {
    \time 6/4
    \key c \major
    \tempo 4=90
    e2 bmol4 c2 r4 |
    e2 f#4 e2 r4 |
    b2. f'2. |
    e2. c2. |
    e2 b2 c2
}
""".strip()

# TinyNotation format (auto-generated after promotion)
# Will appear here when PROMOTE_TO_TINYNOTATION = True
```

### 2. **Two-Stave Output**
Generates musical scores with separate melody and harmony parts:

- **Treble clef (top)**: Melody part
- **Bass clef (bottom)**: Harmony part (transposed down octave)

### 3. **Organized Snippet Collections**

#### Melody Snippets
```python
MELODY_SNIPPETS = {
    'simple': r"\relative c' { c4 d e f | g a b c }",
    'ascending': r"\relative g' { e4 fs g a | b c d e }",
    'descending': r"\relative c'' { c4 b a g | f e d c }",
}
```

#### Harmony Snippets
```python
HARMONY_SNIPPETS = {
    'simple_chords': r"\relative c { <e g b>2 <f a c'>2 <g b d'>2 }",
    'bass_line': r"\relative c { e2 b2 c2 f2 g2 c2 }",
    'arpeggios': r"\relative c { e8 g b g e g b g }",
    'sustained': r"\relative c { e1 b1 c1 }",
}
```

### 4. **Music21 Transformations**

The `build_score_data()` function demonstrates various transformations:

```python
def build_score_data():
    # Parse LilyPond snippets
    melody_data = parse_lilypond_to_data(SOURCE_MELODY_LILY)
    harmony_data = parse_lilypond_to_data(DEFAULT_HARMONY)
    
    # Convert to music21 Parts
    melody_part = data_to_part(melody_events)
    harmony_part = data_to_part(harmony_events)
    
    # Transform 1: Identity/Copy
    melody_final = melody_part.flatten().notesAndRests.stream()
    
    # Transform 2: Transpose harmony down octave
    harmony_final = harmony_part.transpose(-12)
    
    # Return combined score
    return {
        'metadata': {...},
        'parts': {
            'Melody': melody_final_events,
            'Harmony': harmony_final_events,
        }
    }
```

## File Structure

```
first.py
├── PROMOTION TOGGLE
│   └── PROMOTE_TO_TINYNOTATION = False
│
├── MELODY SNIPPETS
│   ├── SOURCE_MELODY_LILY (LilyPond format)
│   ├── SOURCE_MELODY_TINY (TinyNotation - after promotion)
│   └── MELODY_SNIPPETS (alternatives)
│
├── HARMONY SNIPPETS
│   ├── HARMONY_SNIPPETS (collection)
│   └── DEFAULT_HARMONY (selected harmony)
│
├── COMPOSITION FUNCTIONS
│   └── build_score_data() (builds two-part score)
│
└── EXECUTION
    └── run_pipeline_from_file(__file__)
```

## Usage

### Basic Execution

```bash
python3 first.py
```

Output:
```
============================================================
🎵 CODEMPOSE PIPELINE
============================================================
Study file: first.py
Output: outputs/first.*
============================================================

📊 Found build_score_data() function
✅ Successfully loaded via: build_score_data
   Metadata: {'title': 'First Study - Two-Part Composition', ...}
   Parts: ['Melody', 'Harmony']

🎶 Engraving 'First Study - Two-Part Composition'...
📋 Copied first.py to outputs/
Wrote LilyPond file: outputs/first.ly
✅ Successfully compiled first.pdf and .midi

============================================================
✅ PIPELINE COMPLETE
============================================================
Generated files:
  • outputs/first.ly   (LilyPond source)
  • outputs/first.pdf  (Musical score)
  • outputs/first.midi (Audio playback)
============================================================
```

### Generated Files

1. **outputs/first.ly** - LilyPond source with two staves
2. **outputs/first.pdf** - Compiled musical score
3. **outputs/first.midi** - Audio playback
4. **outputs/first.py** - Copy of source file for inspection

## LilyPond Output

The generated `outputs/first.ly` contains:

```lilypond
\version "2.24.1"
\header { title = "First Study - Two-Part Composition" }
\score {
  <<
    \new Staff {
      \clef bass
      \time 6/4 \key c \major \tempo 4 = 90
      e,,2 b,,2 c,2 f,2 g,2 c2
    }
    \new Staff {
      \clef treble
      \time 6/4 \key c \major \tempo 4 = 90
      e,2 bes,4 c2 r4 e2 fis4 e2 r4 b2. f'2. e'2. c'2. e'2 b'2 c''2
    }
  >>
  \layout { }
  \midi { }
}
```

Note the `<<` ... `>>` syntax indicating simultaneous staves.

## Promotion Workflow

### Step 1: Enable Promotion

Edit `first.py`:
```python
PROMOTE_TO_TINYNOTATION = True  # Change from False to True
```

### Step 2: Run to Generate TinyNotation

```bash
python3 first.py
```

Output:
```
============================================================
🔄 PROMOTION: Adding TinyNotation (preserving LilyPond)
============================================================
📝 Converting: \relative e { \time 6/4 \key c \major ...
✅ TinyNotation: time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4...
💾 Backup created: first.20251004_123456.bak
✅ File updated: first.py
   - PROMOTE_TO_TINYNOTATION disabled
   - SOURCE_MELODY_LILY preserved (for reference)
   - SOURCE_MELODY_TINY added (takes priority in pipeline)
```

### Step 3: Verify Dual Format

After promotion, `first.py` contains:

```python
PROMOTE_TO_TINYNOTATION = False  # Auto-disabled

SOURCE_MELODY_LILY = r"""
\relative e {
    \time 6/4
    \key c \major
    \tempo 4=90
    e2 bmol4 c2 r4 | ...
}
""".strip()

# TinyNotation equivalent (auto-generated from SOURCE_MELODY_LILY)
# Toggle PROMOTE_TO_TINYNOTATION to switch which format gets processed
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4 e2 f#4 e2 r4 ..."
```

### Step 4: Pipeline Uses TinyNotation

Next execution automatically uses `SOURCE_MELODY_TINY`:

```bash
python3 first.py
```

Output:
```
🎹 Found SOURCE_MELODY_TINY variable (promoted TinyNotation)
   TinyNotation input: time=6/4 key=Cmajor tempo=90 E2 B-4...
   Detected metadata header: time=6/4 key=Cmajor tempo=90
✅ Successfully loaded via: SOURCE_MELODY_TINY
```

## Pipeline Priority

The pipeline checks for these entry points in order:

| Priority | Entry Point | Description |
|----------|-------------|-------------|
| 1 | `build_score_data()` | Function returning score_data dict |
| 2 | `SOURCE_MELODY_TINY` | TinyNotation string (promoted) |
| 3 | `SOURCE_MELODY_LILY` | LilyPond string |
| 4 | `build_part()` | Function returning music21.Part |

**Current state**: `first.py` uses **Priority 1** (`build_score_data()` function).

## Music21 Transformation Examples

The file includes commented-out examples for experimentation:

### Chordify (Vertical Harmony)
```python
# Combine melody and harmony into chords
combined = music21.stream.Score([melody_part, harmony_part])
chordified = combined.chordify()
```

### Melodic Inversion
```python
# Mirror melodic contours around C4
inverted_melody = melody_part.transpose(0)  # Copy first
for note in inverted_melody.flatten().notes:
    interval = music21.interval.Interval(note, music21.pitch.Pitch('C4'))
    note.transpose(-2 * interval.semitones, inPlace=True)
```

### Transposition
```python
# Transpose melody up a fifth
transposed = melody_part.transpose(7)  # 7 semitones = perfect fifth
```

### Retrograde
```python
# Reverse the melody
retrograde = melody_part.augmentOrDiminish(1)
retrograde = retrograde.reverse()
```

## Customization

### Change Harmony Pattern

Edit the `DEFAULT_HARMONY` variable:

```python
# Option 1: Use a predefined pattern
DEFAULT_HARMONY = HARMONY_SNIPPETS['simple_chords']

# Option 2: Define custom harmony
DEFAULT_HARMONY = r"\relative c { <c e g>1 <f a c'>1 }"
```

### Add New Transformations

Modify `build_score_data()`:

```python
def build_score_data():
    # ... existing code ...
    
    # Add augmentation (double note durations)
    augmented = melody_part.augmentOrDiminish(2)
    
    # Add custom transformation
    for note in melody_part.flatten().notes:
        note.quarterLength *= 1.5  # Add swing feel
    
    # Return modified score
    return score_data
```

### Switch Between Snippet Collections

Use different melody variants:

```python
# In build_score_data(), replace:
melody_data = parse_lilypond_to_data(SOURCE_MELODY_LILY, ...)

# With:
melody_data = parse_lilypond_to_data(MELODY_SNIPPETS['ascending'], ...)
```

## Troubleshooting

### Issue: "No build_score_data found"

**Solution**: The function is present but may have a syntax error. Check Python indentation.

### Issue: "Parser did not return events"

**Solution**: Verify LilyPond syntax in `SOURCE_MELODY_LILY`. Must use `\relative` block.

### Issue: "Both staves appear identical"

**Solution**: Check that `DEFAULT_HARMONY` is different from `SOURCE_MELODY_LILY`.

### Issue: "Harmony not transposed to bass range"

**Solution**: Verify this line in `build_score_data()`:
```python
harmony_final = harmony_part.transpose(-12)
```

## Next Steps

### Experiment with Variations

1. Try different harmony patterns from `HARMONY_SNIPPETS`
2. Uncomment chordify transformation
3. Add your own melody snippets to `MELODY_SNIPPETS`

### Extend to Three or More Staves

```python
def build_score_data():
    # ... existing code ...
    
    # Add bass line
    bass_data = parse_lilypond_to_data(BASS_SNIPPET, part_name='Bass')
    bass_part = data_to_part(bass_data['parts']['Bass'])
    bass_final = bass_part.transpose(-24)  # Two octaves down
    
    return {
        'metadata': {...},
        'parts': {
            'Melody': melody_events,
            'Harmony': harmony_events,
            'Bass': extract_data_from_part(bass_final),
        }
    }
```

### Create Variations

Save `first.py` as `second.py`, `third.py`, etc. and experiment with different:
- Melody patterns
- Harmony styles
- Transformations (inversion, retrograde, augmentation)
- Time signatures and keys

## Summary

✅ **Two-stave output** - Treble melody + bass harmony  
✅ **Dual-format snippets** - LilyPond and TinyNotation coexist  
✅ **Organized collections** - Melody and harmony snippet libraries  
✅ **Music21 transformations** - Identity, transpose, chordify examples  
✅ **Full metadata** - Time signature, key, tempo preserved  
✅ **Promotion system** - One-toggle conversion to TinyNotation  
✅ **Visual inspection** - Source file copied to outputs/  

The file serves as a template for creating more complex multi-part compositions with programmatic transformations.
