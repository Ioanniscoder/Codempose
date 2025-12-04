# Blueprint Strings Transformation Quick Reference

## 🎵 Basic Syntax

```python
function_name(base_snippet, 'arg1', arg2)
```

Place this syntax directly in `VOICE_STAVE_DATA` where you would normally put a snippet name.

---

## 📚 Available Transformations

### Pitch Transformations

| Function | Syntax | Example | Description |
|----------|--------|---------|-------------|
| `transpose_part` | `transpose_part(snippet, 'interval')` | `transpose_part(THEME, 'P5')` | Transpose by interval (P5, -m3, M2) |
| `invert_part` | `invert_part(snippet, 'center')` | `invert_part(THEME, 'C4')` | Melodic inversion around pitch |
| `retrograde_part` | `retrograde_part(snippet)` | `retrograde_part(THEME)` | Play backwards |

### Rhythmic Transformations

| Function | Syntax | Example | Description |
|----------|--------|---------|-------------|
| `augment_part` | `augment_part(snippet, factor)` | `augment_part(THEME, 2.0)` | Stretch durations (2.0 = double) |
| `diminish_part` | `diminish_part(snippet, factor)` | `diminish_part(THEME, 2.0)` | Shrink durations (2.0 = half) |

### Harmonic Transformations

| Function | Syntax | Example | Description |
|----------|--------|---------|-------------|
| `chordify_part` | `chordify_part(snippet, 'type')` | `chordify_part(MELODY, 'major')` | Add harmony (major/minor) |

### Compound Transformations

| Function | Syntax | Example | Description |
|----------|--------|---------|-------------|
| `retrograde_inversion` | `retrograde_inversion(snippet, 'center')` | `retrograde_inversion(THEME, 'C4')` | Invert AND reverse |
| `transpose_and_augment` | `transpose_and_augment(snippet, 'interval', factor)` | `transpose_and_augment(THEME, 'P5', 2.0)` | Transpose AND stretch |

---

## 💡 Usage Examples

### Simple Transformation
```python
VOICE_STAVE_DATA = """
    THEME & BASS;
    transpose_part(THEME, 'P5') & BASS;
    invert_part(THEME, 'C4') & BASS
"""
```

### Concatenation (using `|`)
```python
VOICE_STAVE_DATA = """
    THEME | transpose_part(THEME, 'M2') | invert_part(THEME, 'C4') & BASS
"""
```

### Multi-Voice
```python
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
VOICE_STAVE_DATA = """
    THEME, transpose_part(THEME, '-P5') & HARMONY, BASS
"""
```

### Complex Arrangement
```python
VOICE_STAVE_DATA = """
    INTRO & BASS;
    transpose_part(THEME, 'P5') | retrograde_part(THEME) & chordify_part(BASS, 'major');
    invert_part(THEME, 'C4') & augment_part(BASS, 2.0);
    THEME & BASS
"""
```

---

## 🎯 Common Intervals

| Interval | Semitones | Musical Name |
|----------|-----------|--------------|
| `'P1'` | 0 | Perfect Unison |
| `'m2'` | 1 | Minor 2nd |
| `'M2'` | 2 | Major 2nd |
| `'m3'` | 3 | Minor 3rd |
| `'M3'` | 4 | Major 3rd |
| `'P4'` | 5 | Perfect 4th |
| `'P5'` | 7 | Perfect 5th |
| `'m6'` | 8 | Minor 6th |
| `'M6'` | 9 | Major 6th |
| `'m7'` | 10 | Minor 7th |
| `'M7'` | 11 | Major 7th |
| `'P8'` | 12 | Perfect Octave |

**Prefix with `-` to go down:** `'-P5'`, `'-M3'`, `'-P8'`

---

## 🔍 Inspectability

All transformations are automatically saved to the `SNIPPETS` dictionary:

```python
# After build_score_data() runs:
SNIPPETS = {
    'THEME': [original_events],
    "transpose_part(THEME, 'P5')": [transposed_events],
    "invert_part(THEME, 'C4')": [inverted_events],
    # ... etc
}
```

You can inspect these in the console output or programmatically.

---

## ⚠️ Tips & Gotchas

### String Arguments Must Be Quoted
```python
✅ transpose_part(THEME, 'P5')      # Correct
❌ transpose_part(THEME, P5)        # Wrong - will look for snippet named "P5"
```

### Numeric Arguments Don't Need Quotes
```python
✅ augment_part(THEME, 2.0)         # Correct
✅ augment_part(THEME, 2)           # Also correct
❌ augment_part(THEME, '2.0')       # Wrong - will be treated as string
```

### Base Snippet Must Exist
```python
SNIPPETS = {'THEME': theme_events}

✅ transpose_part(THEME, 'P5')      # Works - THEME exists
❌ transpose_part(MELODY, 'P5')     # Error - MELODY not in SNIPPETS
```

### Transformation Names Match transformations.py
```python
✅ transpose_part(THEME, 'P5')      # Correct function name
❌ transpose(THEME, 'P5')           # Wrong - use full name
❌ transposePart(THEME, 'P5')       # Wrong - use snake_case
```

---

## 🚀 Quick Start Template

```python
# 1. Define snippets
THEME_LILY = r"""
\relative c'' {
    c4 d4 e4 f4 | g1
}
""".strip()

# 2. Define layout
VOICE_STAVE_DEF = "Melody & Bass"

# 3. Use transformations!
VOICE_STAVE_DATA = """
    THEME & BASS;
    transpose_part(THEME, 'P5') & BASS;
    invert_part(THEME, 'C4') & BASS
"""

# 4. Build (transformations happen automatically)
def build_score_data():
    theme_events = parse_lilypond_to_data(THEME_LILY, 'Melody')['parts']['Melody']
    bass_events = parse_lilypond_to_data(BASS_LILY, 'Bass')['parts']['Bass']
    
    SNIPPETS = {
        'THEME': theme_events,
        'BASS': bass_events,
    }
    
    return build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
```

That's it! No explicit transformation code needed in `build_score_data()`.

---

## 📖 See Also

- **Full documentation:** `DOCUMENTATION/BLUEPRINT_TRANSFORMATIONS_COMPLETE.md`
- **Template examples:** `CODEMPOSE_STUDY_TEMPLATES.py` (search for "ON-THE-FLY TRANSFORMATIONS")
- **Test study:** `studies/test_transformations_blueprint.py`
- **Transformation source:** `src/transformations.py` (implementation details)
