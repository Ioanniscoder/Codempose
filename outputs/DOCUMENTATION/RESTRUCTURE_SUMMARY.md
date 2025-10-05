# Summary: Restructured first.py with Dual-Format System

## What You Asked For

✅ **Understanding SOURCE_MELODY_TINY location**: 
- `SOURCE_MELODY_TINY` doesn't exist in `first.py` yet
- It will be auto-generated when you set `PROMOTE_TO_TINYNOTATION = True`
- It appears right after `SOURCE_MELODY_LILY` definition (line 28-40)

✅ **Formatted snippet collections**:
- Melody snippets: Lines 43-48 (organized dictionary)
- Harmony snippets: Lines 54-60 (organized dictionary)

✅ **Two-stave output with music21 functions**:
- Function: `build_score_data()` (lines 66-141)
- Transformations: Identity/copy, transpose
- Output: Treble melody + bass harmony staves

## File Structure

```
first.py (174 lines)
═══════════════════════════════════════════════════════

Lines 1-11:   Module docstring
Lines 15-18:  PROMOTION TOGGLE
              └─ PROMOTE_TO_TINYNOTATION = False

Lines 23-40:  MELODY SNIPPETS  
              ├─ SOURCE_MELODY_LILY (LilyPond format)
              └─ SOURCE_MELODY_TINY (will appear after promotion)

Lines 43-48:  MELODY_SNIPPETS (alternatives)
              ├─ 'simple'
              ├─ 'ascending'
              └─ 'descending'

Lines 54-60:  HARMONY SNIPPETS
              ├─ 'simple_chords'
              ├─ 'bass_line'
              ├─ 'arpeggios'
              └─ 'sustained'

Lines 62-63:  DEFAULT_HARMONY selection

Lines 66-141: build_score_data() function
              ├─ Parse melody and harmony
              ├─ Convert to music21 Parts
              ├─ Apply transformations
              │  ├─ Identity/copy (melody)
              │  ├─ Transpose -12 semitones (harmony → bass)
              │  └─ (Commented: chordify, inversion)
              └─ Return score_data dict

Lines 148-151: Execution
               └─ run_pipeline_from_file(__file__)
```

## Current State vs. After Promotion

### BEFORE Promotion (Current)

```python
# Line 18
PROMOTE_TO_TINYNOTATION = False

# Lines 28-40
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

# TinyNotation format will appear here after promotion
# (auto-generated when PROMOTE_TO_TINYNOTATION = True)
```

### AFTER Promotion (Will become)

```python
# Line 18
PROMOTE_TO_TINYNOTATION = False  # Promotion completed - both formats available

# Lines 28-40
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

# TinyNotation equivalent (auto-generated from SOURCE_MELODY_LILY)
# Toggle PROMOTE_TO_TINYNOTATION to switch which format gets processed
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4 e2 f#4 e2 r4 b2. f'2. e'2. c'2. e'2 b'2 c''2"
```

## How Snippets Are Used

### Melody Processing Chain

```
SOURCE_MELODY_LILY (line 28)
         ↓
parse_lilypond_to_data() (line 91)
         ↓
melody_data dict {'parts': {'Melody': [events]}, 'metadata': {...}}
         ↓
data_to_part() (line 96)
         ↓
melody_part (music21.stream.Part object)
         ↓
melody_part.flatten().notesAndRests.stream() (line 108)
         ↓
melody_final (transformed Part)
         ↓
extract_data_from_part() (line 127)
         ↓
melody_final_events (list of event dicts)
         ↓
score_data['parts']['Melody'] (line 137)
```

### Harmony Processing Chain

```
DEFAULT_HARMONY = HARMONY_SNIPPETS['bass_line'] (line 63)
         ↓
parse_lilypond_to_data() (line 94)
         ↓
harmony_data dict
         ↓
data_to_part() (line 97)
         ↓
harmony_part (music21.stream.Part)
         ↓
harmony_part.transpose(-12) (line 111)
         ↓
harmony_final (transposed down one octave)
         ↓
extract_data_from_part() (line 128)
         ↓
harmony_final_events
         ↓
score_data['parts']['Harmony'] (line 138)
```

## Two-Stave Output Flow

```
build_score_data() returns:
{
    'metadata': {
        'title': 'First Study - Two-Part Composition',
        'time_signature': '6/4',
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        'tempo': {'beat_duration': 4, 'bpm': 90},
        'composer': 'Codempose'
    },
    'parts': {
        'Harmony': [e,,2, b,,2, c,2, ...],  # Bass clef
        'Melody': [e,2, bes,4, c2, ...]     # Treble clef
    }
}
         ↓
engrave_with_abjad() in project_template.py
         ↓
outputs/first.ly:
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
         ↓
LilyPond compiler
         ↓
outputs/first.pdf (two-stave score)
outputs/first.midi (audio)
```

## Music21 Transformation Examples in Code

### Current: Identity + Transpose

```python
# Line 108: Identity/Copy - preserve original melody
melody_final = melody_part.flatten().notesAndRests.stream()

# Line 111: Transpose harmony down octave
harmony_final = harmony_part.transpose(-12)
```

### Available (Commented): Chordify

```python
# Lines 113-115
# combined = music21.stream.Score([melody_part, harmony_part])
# chordified = combined.chordify()
```

### Available (Commented): Inversion

```python
# Lines 117-121
# inverted_melody = melody_part.transpose(0)  # Copy first
# for note in inverted_melody.flatten().notes:
#     interval = music21.interval.Interval(note, music21.pitch.Pitch('C4'))
#     note.transpose(-2 * interval.semitones, inPlace=True)
```

## Visual Comparison: Before and After

### Before Restructuring (Original first.py)

- ❌ Single LilyPond snippet only
- ❌ No snippet organization
- ❌ build_part() returns single Part
- ❌ No promotion system
- ❌ Manual harmony construction
- ❌ No transformation examples

### After Restructuring (New first.py)

- ✅ Dual-format support (LilyPond + TinyNotation)
- ✅ Organized snippet collections (MELODY_SNIPPETS, HARMONY_SNIPPETS)
- ✅ build_score_data() returns full score with metadata
- ✅ Promotion toggle system
- ✅ Automatic two-stave generation
- ✅ Music21 transformation examples (identity, transpose, chordify, inversion)

## Key Differences: Promotion Toggle Behavior

### Old System (test_promotion_full.py style)

```python
# BEFORE: Comments out SOURCE_MELODY_LILY
# SOURCE_MELODY_LILY = r"\relative e { ... }"  # Promoted to TinyNotation

# AFTER: Only TinyNotation visible
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 ..."
```

### New System (first.py style)

```python
# BEFORE: Both formats visible
SOURCE_MELODY_LILY = r"\relative e { ... }"

# AFTER: Both formats still visible
SOURCE_MELODY_LILY = r"\relative e { ... }"
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 ..."
```

**Key difference**: New system preserves both for visual inspection!

## Testing the Promotion

### Step 1: Enable Promotion
```python
# Edit line 18 in first.py
PROMOTE_TO_TINYNOTATION = True
```

### Step 2: Run
```bash
python3 first.py
```

### Step 3: Check Result
```bash
# View the updated file
grep -A 3 "SOURCE_MELODY_TINY" first.py

# Expected output:
# SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4 e2 f#4 e2 r4 b2. f'2. e'2. c'2. e'2 b'2 c''2"
```

### Step 4: Verify Backup
```bash
ls -la first.*.bak
# Should show: first.20251004_HHMMSS.bak
```

## Answer to Your Question

> "I would like to understand where in the updated first.py the tinynotation is found. I thought it would be named SOURCE_MELODY_TINY but cannot find it."

**Answer**: 
- `SOURCE_MELODY_TINY` doesn't exist in `first.py` **yet**
- It will be **auto-generated** when you set `PROMOTE_TO_TINYNOTATION = True` and run the file
- After promotion, it appears at **line ~42** (right after `SOURCE_MELODY_LILY`)
- **Both formats will coexist** for visual inspection
- The promotion toggle determines which one the pipeline processes

## Documentation Created

1. **PROMOTION_SYSTEM.md** - Complete guide to dual-format promotion system
2. **FIRST_PY_DOCUMENTATION.md** - Detailed documentation of first.py structure
3. **This summary** - Quick reference showing file structure and workflow

## Files Generated

Running `python3 first.py` creates:
- `outputs/first.ly` - Two-stave LilyPond source
- `outputs/first.pdf` - Musical score with treble + bass staves
- `outputs/first.midi` - Audio playback
- `outputs/first.py` - Copy of source file for inspection

## Next Steps

1. **Try promotion**: Set `PROMOTE_TO_TINYNOTATION = True` in first.py
2. **Experiment with snippets**: Change `DEFAULT_HARMONY` to different patterns
3. **Enable transformations**: Uncomment chordify or inversion examples
4. **Create variations**: Save as second.py, third.py with different melodies

The restructured `first.py` is now a complete template for two-stave composition with visual snippet comparison!
