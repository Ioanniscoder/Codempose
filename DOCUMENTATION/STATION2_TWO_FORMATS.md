# Station 2: Two Formats Explained

**Date:** October 19, 2025  
**Status:** ✅ IMPLEMENTED AND TESTED

## The Question

"In station 2 also tinynotation snippets are shown for pitch resolution. Is this still working? or are the transformed snippets already showing pitch resolution (don't think so, I see \relative)"

## The Answer: YES - Both Formats Available! ✅

Station 2 now provides **TWO FORMATS** for every snippet (original + transformed):

### 1. TinyNotation Format (Pitch Verification)
**Purpose:** Absolute pitch resolution for verification  
**Example:** `tinynotation: 4/4 C64 D64 E64 F64 G62 F62`

Shows:
- Absolute pitch names (C6, D6, E6 instead of `c''`, `d''`, `e''`)
- Octave numbers (4 = middle C octave, 6 = two octaves above, etc.)
- Duration suffixes (4 = quarter, 2 = half, 1 = whole)

### 2. LilyPond Format (Reusable Snippets)
**Purpose:** Ready-to-use snippets for further composition  
**Example:** `\relative c'' { c'''4 d'''4 e'''4 f'''4 g'''2 f'''2 }`

Shows:
- LilyPond notation with `\relative` (compositional format)
- Can be copied for manual editing
- Can be used as input for more transformations

---

## Why Both Formats?

### TinyNotation = Verification Tool
When you apply a transformation like `transpose_part(THEME, 'P5')`, you want to **verify** that the octaves resolved correctly.

**Without TinyNotation:**
```python
# Original
THEME_LILY = r"\relative c'' { c4 d4 e4 f4 | g2 f2 }"

# Transposed (hard to verify octaves!)
THEME_P5_LILY = r"\relative c'' { g'''4 a'''4 b'''4 c''''4 d''''2 c''''2 }"
# Are those the right octaves? Hard to tell! 🤔
```

**With TinyNotation:**
```python
# Original (absolute pitches)
THEME_TINY = "tinynotation: 4/4 C64 D64 E64 F64 G62 F62"
# C6, D6, E6, F6, G6, F6 - clear!

# Transposed (absolute pitches)
THEME_P5_TINY = "tinynotation: 4/4 G64 A64 B64 C74 D72 C72"
# G6, A6, B6, C7, D7, C7 - perfect fifth up! ✅
```

You can **instantly verify** that:
- C6 → G6 (up a fifth) ✅
- D6 → A6 (up a fifth) ✅
- E6 → B6 (up a fifth) ✅
- F6 → C7 (up a fifth) ✅

### LilyPond = Composition Tool
After verifying correctness with TinyNotation, you use the LilyPond format to **reuse** the snippet:

```python
# Copy this snippet for further composition
THEME_P5_LILY = r"\relative c'' { g'''4 a'''4 b'''4 c''''4 d''''2 c''''2 }"

# Use it in a new blueprint
VOICE_STAVE_DATA_2 = """
    THEME_P5;
    invert_part(THEME_P5, 'C4')  # ← Cascade transformations!
"""
```

---

## Test Output

### Example from `test_station2_reuse.py`:

```
======================================================================
STATION 2: GENERATING REUSABLE SNIPPETS
======================================================================

Converting transformed snippets to LilyPond format...
These will be available for inspection and reuse!

✓ THEME_TINY (pitch verification):
  tinynotation: 4/4 C64 D64 E64 F64 G62 F62

✓ THEME_P5_LILY (reusable snippet):
  \relative c'' { \time 4/4 \key c \major g'''4 a'''4 b'''4 c''''4 d''''2 c''''2 }
✓ THEME_P5_TINY (pitch verification):
  tinynotation: 4/4 G64 A64 B64 C74 D72 C72

✓ THEME_INVERTED_LILY (reusable snippet):
  \relative c' { \time 4/4 \key c \major c'4 bes'4 aes'4 g'4 f'2 g'2 }
✓ THEME_INVERTED_TINY (pitch verification):
  tinynotation: 4/4 C44 Bb44 Ab44 G44 F42 G42

✓ THEME_P5_INVERTED_LILY (cascaded - reusable snippet):
  \relative c' { \time 4/4 \key c \major f'4 ees'4 des'4 c'4 bes'2 c'2 }
✓ THEME_P5_INVERTED_TINY (cascaded - pitch verification):
  tinynotation: 4/4 F44 Eb44 Db44 C44 Bb42 C42
```

---

## Implementation Details

### New Function: `events_to_tinynotation()`

Added to `src/lily_converter.py`:

```python
def events_to_tinynotation(events, metadata=None):
    """
    Convert canonical event dictionaries to TinyNotation format.
    
    Example output: "tinynotation: 4/4 C64 D64 E64 F64 G62 F62"
    
    Shows absolute pitches (C6, D6, etc.) instead of relative notation,
    making it easy to verify octave resolution.
    """
    # ... implementation ...
```

### Station 2 Population Pattern

```python
def build_score_data():
    # ... parse and build score ...
    
    # Import both converters
    from lily_converter import events_to_lily, events_to_tinynotation
    
    # Declare global variables for both formats
    global THEME_TINY, THEME_P5_LILY, THEME_P5_TINY
    
    # Convert original theme
    THEME_TINY = events_to_tinynotation(theme_events, metadata)
    
    # Convert transformed snippets to BOTH formats
    if "transpose_part(THEME, 'P5')" in SNIPPETS:
        THEME_P5_LILY = events_to_lily(
            SNIPPETS["transpose_part(THEME, 'P5')"], 
            metadata
        )
        THEME_P5_TINY = events_to_tinynotation(
            SNIPPETS["transpose_part(THEME, 'P5')"],
            metadata
        )
    
    return score_data
```

---

## Comparison Table

| Aspect | TinyNotation | LilyPond |
|--------|-------------|----------|
| **Pitch Format** | Absolute (C6, D6) | Relative (c'', d'') |
| **Purpose** | Verification | Reuse |
| **Readability** | High (octaves clear) | Medium (relative jumps) |
| **Editability** | Low (not valid LilyPond) | High (valid LilyPond) |
| **Use Case** | "Did transformation work?" | "Use this snippet!" |
| **Display** | Console output | Console + Station 2 var |

---

## TinyNotation Syntax Reference

### Pitch Format
- **Note name + Octave number**: `C6`, `D#5`, `Bb3`
- **Octave 4** = Middle C octave (C4 = middle C)
- **Octave 5** = One octave above middle C
- **Octave 6** = Two octaves above middle C

### Duration Suffixes
- `1` = whole note (4.0 QL)
- `2` = half note (2.0 QL)
- `4` = quarter note (1.0 QL)
- `8` = eighth note (0.5 QL)
- `16` = sixteenth note (0.25 QL)
- `2.` = dotted half (3.0 QL)
- `4.` = dotted quarter (1.5 QL)

### Special Elements
- **Rest**: `r4`, `r2`, `r1`
- **Chord**: `<C4 E4 G4>2`
- **Tuplet**: `[C64 D64 E64]` (simplified)
- **Grace note**: `C616grace` (C6, sixteenth, grace)

### Example
```
tinynotation: 4/4 C64 D64 E64 F64 G62 F62
```
Means:
- Time signature: 4/4
- C in octave 6, quarter note
- D in octave 6, quarter note
- E in octave 6, quarter note
- F in octave 6, quarter note
- G in octave 6, half note
- F in octave 6, half note

---

## Best Practices

### 1. Always Generate Both Formats

```python
# ❌ Bad - only LilyPond
THEME_P5_LILY = events_to_lily(transformed_events, metadata)

# ✅ Good - both formats
THEME_P5_LILY = events_to_lily(transformed_events, metadata)
THEME_P5_TINY = events_to_tinynotation(transformed_events, metadata)
```

### 2. Print Both in Console Output

```python
print(f"✓ THEME_P5_LILY (reusable snippet):")
print(f"  {THEME_P5_LILY}")
print(f"✓ THEME_P5_TINY (pitch verification):")
print(f"  {THEME_P5_TINY}")
```

### 3. Use Descriptive Variable Names

```python
# Good - indicates format
THEME_P5_LILY = "..."  # LilyPond format
THEME_P5_TINY = "..."  # TinyNotation format

# Less clear
THEME_P5 = "..."  # Which format?
```

### 4. Verify Before Reusing

**Workflow:**
1. Apply transformation
2. Check TinyNotation (verify pitches correct)
3. Use LilyPond snippet (reuse in composition)

```python
# Step 1: Apply transformation
VOICE_STAVE_DATA = "transpose_part(THEME, 'P5')"

# Step 2: Check TinyNotation output
# THEME_P5_TINY = "tinynotation: 4/4 G64 A64 B64 C74 D72 C72"
# ✅ Verified: G6, A6, B6, C7 (correct P5 transposition)

# Step 3: Reuse LilyPond snippet
VOICE_STAVE_DATA_2 = """
    THEME_P5;
    invert_part(THEME_P5, 'C4')
"""
```

---

## Files Modified

1. **`src/lily_converter.py`**:
   - Added `events_to_tinynotation()` function
   - Added helper functions: `_pitch_to_tinynotation()`, `_ql_to_tinynotation_duration()`

2. **`studies/test_station2_reuse.py`**:
   - Added TinyNotation variables at Station 2
   - Updated `build_score_data()` to generate both formats
   - Demonstrated both formats in console output

3. **`studies/test_transformations_blueprint.py`**:
   - Added TinyNotation variables at Station 2
   - Updated `build_score_data()` to generate both formats
   - Demonstrated both formats for all 6 transformations

---

## Summary

✅ **TinyNotation is still working!**  
✅ **Both formats are now generated at Station 2**  
✅ **TinyNotation shows absolute pitch resolution**  
✅ **LilyPond shows reusable snippets with `\relative`**  
✅ **Both formats tested and documented**  

The two-format approach gives composers the best of both worlds:
- **Verification** (TinyNotation - "Is this right?")
- **Reuse** (LilyPond - "Use this!")

Just like in `thirteenth.py`, Station 2 now contains complete reference material for all snippets, making it easy to verify transformations and reuse the results! 🎵
