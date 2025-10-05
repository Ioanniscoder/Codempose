# Promotion System: Dual-Format Preservation

## Overview

The Codempose promotion system allows you to maintain **both LilyPond and TinyNotation formats** in the same file for visual inspection and comparison. The `PROMOTE_TO_TINYNOTATION` toggle determines which format gets processed by the pipeline.

## How It Works

### 1. Initial State (LilyPond only)

```python
# Set to True to generate TinyNotation format
PROMOTE_TO_TINYNOTATION = False

SOURCE_MELODY_LILY = r"""
\relative e {
    \time 6/4
    \key c \major
    \tempo 4=90
    e2 bmol4 c2 r4 |
    e2 f#4 e2 r4
}
""".strip()

# TinyNotation will appear here after promotion
```

### 2. Enable Promotion

Set the toggle to `True`:

```python
PROMOTE_TO_TINYNOTATION = True
```

Run the file:
```bash
python3 first.py
```

### 3. After Promotion (Both formats preserved)

The file is automatically updated:

```python
PROMOTE_TO_TINYNOTATION = False  # Promotion completed - both formats available

SOURCE_MELODY_LILY = r"""
\relative e {
    \time 6/4
    \key c \major
    \tempo 4=90
    e2 bmol4 c2 r4 |
    e2 f#4 e2 r4
}
""".strip()

# TinyNotation equivalent (auto-generated from SOURCE_MELODY_LILY)
# Toggle PROMOTE_TO_TINYNOTATION to switch which format gets processed
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4 e2 f#4 e2 r4"
```

## Pipeline Priority

The `run_pipeline_from_file()` function uses this priority order:

1. **`build_score_data()` function** (highest priority)
2. **`SOURCE_MELODY_TINY` variable** (promoted TinyNotation)
3. **`SOURCE_MELODY_LILY` variable** (raw LilyPond)
4. **`build_part()` function** (lowest priority)

When both `SOURCE_MELODY_LILY` and `SOURCE_MELODY_TINY` exist, **TINY takes priority**.

## Benefits of Dual-Format Preservation

### Visual Comparison
You can see both representations side-by-side:

```python
# LilyPond: verbose but explicit about octaves and directives
SOURCE_MELODY_LILY = r"\relative e { \time 6/4 \key c \major e2 bmol4 c2 r4 }"

# TinyNotation: compact with embedded metadata header
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor E2 B-4 c2 r4"
```

### Educational Value
- **LilyPond format**: Shows relative octave notation, explicit directives
- **TinyNotation format**: Shows absolute octaves, compact header metadata

### Workflow Flexibility
- Keep LilyPond for detailed editing with external tools
- Use TinyNotation for quick manual tweaks and portability

### Debugging
- Compare parser output between both formats
- Verify metadata preservation across conversions
- Spot octave transposition issues

## Example: first.py

The restructured `first.py` demonstrates this system:

```python
# ============================================================================
# PROMOTION TOGGLE
# ============================================================================

PROMOTE_TO_TINYNOTATION = False  # Set to True to generate TinyNotation


# ============================================================================
# MELODY SNIPPETS
# ============================================================================

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


# ============================================================================
# HARMONY SNIPPETS
# ============================================================================

HARMONY_SNIPPETS = {
    'bass_line': r"\relative c { e2 b2 c2 f2 g2 c2 }",
    'simple_chords': r"\relative c { <e g b>2 <f a c'>2 <g b d'>2 }",
}


# ============================================================================
# COMPOSITION FUNCTIONS
# ============================================================================

def build_score_data():
    """Build two-stave score with melody and harmony"""
    # ... music21 transformations ...
    return score_data
```

## Workflow Steps

### Step 1: Create study file with LilyPond
```python
# first.py
PROMOTE_TO_TINYNOTATION = False
SOURCE_MELODY_LILY = r"\relative c' { c4 d e f }"
```

### Step 2: Enable promotion
```python
PROMOTE_TO_TINYNOTATION = True  # Change to True
```

### Step 3: Run to generate TinyNotation
```bash
python3 first.py
```

Output:
```
🔄 PROMOTION: Adding TinyNotation (preserving LilyPond)
📝 Converting: \relative c' { c4 d e f }...
✅ TinyNotation: c'4 d' e' f'
💾 Backup created: first.20251004_123456.bak
✅ File updated: first.py
   - PROMOTE_TO_TINYNOTATION disabled
   - SOURCE_MELODY_LILY preserved (for reference)
   - SOURCE_MELODY_TINY added (takes priority in pipeline)
```

### Step 4: Both formats now visible
```python
PROMOTE_TO_TINYNOTATION = False  # Auto-disabled

SOURCE_MELODY_LILY = r"\relative c' { c4 d e f }"

# TinyNotation equivalent (auto-generated)
SOURCE_MELODY_TINY = "c'4 d' e' f'"
```

### Step 5: Pipeline uses TinyNotation
```bash
python3 first.py  # Re-run - now processes SOURCE_MELODY_TINY
```

Output:
```
🎹 Found SOURCE_MELODY_TINY variable (promoted TinyNotation)
   TinyNotation input: c'4 d' e' f'...
✅ Successfully loaded via: SOURCE_MELODY_TINY
```

## Advanced: Manual Format Switching

To manually switch which format gets processed:

### Option A: Comment out SOURCE_MELODY_TINY
```python
# SOURCE_MELODY_TINY = "c'4 d' e' f'"  # Temporarily disabled
```
Pipeline falls back to `SOURCE_MELODY_LILY`.

### Option B: Rename variables
```python
SOURCE_MELODY_LILY_BACKUP = r"\relative c' { c4 d e f }"
SOURCE_MELODY_TINY = "c'4 d' e' f'"
```
Only `SOURCE_MELODY_TINY` is recognized.

## Testing

See `test_promotion_full.py` for a complete example:

```bash
# View the promoted file
cat test_promotion_full.py

# Run to process TinyNotation format
python3 test_promotion_full.py

# Check generated output
cat outputs/test_promotion_full.ly
```

## Summary

✅ **Both formats preserved** - LilyPond and TinyNotation coexist
✅ **Visual inspection** - Compare formats side-by-side  
✅ **Automatic conversion** - One toggle enables promotion
✅ **Priority system** - TinyNotation takes precedence when present
✅ **Backup safety** - Original file backed up before modification
✅ **Educational** - Learn differences between notation systems
