# Promotion System: Dual-Format Workflow

## Overview

The Codempose promotion system enables **visual correlation** between LilyPond and TinyNotation formats while controlling which format is **dominant** (gets processed by the pipeline).

## Core Principle

**Both formats coexist** in study files for comparison and learning:
- `SOURCE_MELODY_LILY` - LilyPond notation (visual reference)
- `SOURCE_MELODY_TINY` - TinyNotation format (compact representation)

The `PROMOTE_TO_TINYNOTATION` toggle controls which format is **dominant** (processed by the pipeline).

---

## File Management Strategy

### During Normal Processing (No Promotion)

When you run a study file (e.g., `python3 first.py`):

1. **Root directory**: Study file remains unchanged
2. **outputs/ directory**: 
   - Study file copied → `outputs/first.py` (for inspection)
   - Generated files → `outputs/first.ly`, `first.pdf`, `first.midi`

**Result**: You can inspect `outputs/first.py` to see both LILY and TINY formats side-by-side.

---

### During Promotion (Toggle Change)

When `PROMOTE_TO_TINYNOTATION = True` is set:

#### Phase 1: Backup Original
```
Original file → outputs/first.TIMESTAMP.bak
```
The original study file is backed up to `outputs/` **before** any modifications.

#### Phase 2: Modify Root
```
Modified file → first.py (root directory, replaces original)
```
The study file in the root is updated with:
- Toggle state changed (True ↔ False)
- TinyNotation added (if missing)

#### Phase 3: Copy Modified to Outputs
```
Modified file → outputs/first.py (for inspection)
```
The **modified** version is copied to `outputs/` so you can see the current state.

---

## Promotion Scenarios

### Scenario 1: First-Time Promotion (Generate TinyNotation)

**Initial state** - Study file has only LilyPond:
```python
PROMOTE_TO_TINYNOTATION = False

SOURCE_MELODY_LILY = r"""
\relative e' {
    e2 bmol4 c2 r4 |
}
""".strip()

# TinyNotation will be generated when promoted
```

**Set toggle to True**:
```python
PROMOTE_TO_TINYNOTATION = True  # ← Change this
```

**Run the file**:
```bash
python3 first.py
```

**What happens**:
1. ✅ Original saved → `outputs/first.20251004_120000.bak`
2. ✅ LilyPond converted to TinyNotation
3. ✅ Modified file written → `first.py` (root) with both formats
4. ✅ Modified file copied → `outputs/first.py`
5. ⚠️ User prompted to re-run

**After promotion** - Study file now has both formats:
```python
PROMOTE_TO_TINYNOTATION = True  # TinyNotation is now dominant

SOURCE_MELODY_LILY = r"""
\relative e' {
    e2 bmol4 c2 r4 |
}
""".strip()

# TinyNotation equivalent (for visual comparison with LilyPond)
# PROMOTE_TO_TINYNOTATION toggle controls which format is dominant (gets processed)
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 e2 b-4 c'2 r4"
```

**Re-run to process**:
```bash
python3 first.py
```
Now the TinyNotation format will be processed (since toggle is True).

---

### Scenario 2: Toggle Dominance (Switch Formats)

**Current state** - Both formats exist, TinyNotation dominant:
```python
PROMOTE_TO_TINYNOTATION = True  # TinyNotation is dominant

SOURCE_MELODY_LILY = "..."
SOURCE_MELODY_TINY = "..."
```

**Switch to LilyPond dominance**:
```python
PROMOTE_TO_TINYNOTATION = False  # ← Change to False
```

**Run the file**:
```bash
python3 first.py
```

**What happens**:
1. ✅ Original saved → `outputs/first.20251004_120500.bak`
2. ✅ Toggle switched → `PROMOTE_TO_TINYNOTATION = True` (flipped)
3. ✅ Modified file written → `first.py` (root)
4. ✅ Modified file copied → `outputs/first.py`
5. ⚠️ User prompted to re-run

**After toggle**:
```python
PROMOTE_TO_TINYNOTATION = False  # LilyPond is now dominant
```

**Re-run to process**:
```bash
python3 first.py
```
Now the LilyPond format will be processed (since toggle is False).

---

## Priority Order (Pipeline Processing)

The pipeline checks sources in this order:

1. **`build_score_data()` function** ← Highest priority (used by `first.py`)
2. **`SOURCE_MELODY_TINY`** - If `PROMOTE_TO_TINYNOTATION = True`
3. **`SOURCE_MELODY_LILY`** - If `PROMOTE_TO_TINYNOTATION = False`
4. **`build_part()` function** ← Lowest priority

**Note**: When `build_score_data()` exists (like in `first.py`), it takes precedence regardless of toggle state. The toggle only affects priority between `SOURCE_MELODY_TINY` and `SOURCE_MELODY_LILY` when they are the primary input method.

---

## File Locations Summary

| File | Location | Purpose |
|------|----------|---------|
| **Active study file** | `first.py` (root) | Working version, gets modified during promotion |
| **Backup (original)** | `outputs/first.TIMESTAMP.bak` | Snapshot before promotion changes |
| **Output copy** | `outputs/first.py` | Inspection copy (shows current state with both formats) |
| **LilyPond source** | `outputs/first.ly` | Generated engraving source |
| **PDF score** | `outputs/first.pdf` | Musical notation (visual) |
| **MIDI audio** | `outputs/first.midi` | Playback file |

---

## Visual Correlation Benefits

Having both formats in the same file enables:

1. **Learning**: See how LilyPond syntax maps to TinyNotation
2. **Debugging**: Compare formats to identify conversion issues
3. **Experimentation**: Edit one format, promote to regenerate the other
4. **Documentation**: Study files are self-documenting with dual examples

### Example Comparison

**LilyPond** (verbose, explicit):
```lilypond
\relative e' {
    \time 6/4
    \key c \major
    \tempo 4=90
    e2 bmol4 c2 r4 |
}
```

**TinyNotation** (compact, metadata header):
```
time=6/4 key=Cmajor tempo=90 e2 b-4 c'2 r4
```

Both represent the same musical idea - two half notes (E, C) and a quarter note (B♭) with a quarter rest.

---

## Best Practices

### 1. Start with Both Formats

New study files should include both `SOURCE_MELODY_LILY` and `SOURCE_MELODY_TINY` from the beginning:

```python
SOURCE_MELODY_LILY = r"""
\relative c' { c4 d e f }
""".strip()

SOURCE_MELODY_TINY = "c4 d4 e4 f4"
```

### 2. Use Promotion for Conversion

If you only have LilyPond and want to generate TinyNotation:
1. Set `PROMOTE_TO_TINYNOTATION = True`
2. Run the file once (generates TinyNotation, creates backup)
3. Run again to process with new format

### 3. Toggle for Experimentation

To test both formats produce the same output:
1. Run with `PROMOTE_TO_TINYNOTATION = False` → check PDF
2. Toggle to `True`, re-run → compare PDF
3. Should be identical!

### 4. Check outputs/ for History

The `outputs/` directory accumulates:
- Timestamped backups (`.bak` files)
- Current study file copy (`.py`)
- Generated artifacts (`.ly`, `.pdf`, `.midi`)

This provides a complete audit trail of your work.

---

## Integration with build_score_data()

The `first.py` template demonstrates the recommended pattern:

```python
def build_score_data():
    """Use SOURCE_MELODY_LILY as the reference source"""
    melody_data = parse_lilypond_to_data(SOURCE_MELODY_LILY, part_name='Melody')
    # ... transform with music21 ...
    return score_data
```

**Why use LILY in build_score_data()?**
- LilyPond is the authoritative source (more explicit)
- TinyNotation is derived/generated (convenient but less precise)
- Keeps transformations based on the reference format

**When to use TINY directly?**
- Simple melodies without transformations
- Quick prototyping
- When compactness is preferred over verbosity

---

## Troubleshooting

### Q: I set PROMOTE_TO_TINYNOTATION = True but nothing happened

**A**: The promotion happens on the **first run** after setting the toggle. You must run the file twice:
1. First run: Performs promotion, modifies file
2. Second run: Processes the promoted format

### Q: Where did my original file go?

**A**: It's in `outputs/first.TIMESTAMP.bak`. The system always backs up before modifications.

### Q: Can I manually edit SOURCE_MELODY_TINY?

**A**: Yes! Both formats are editable. If you change TINY, you can:
1. Set toggle to `True` to make it dominant
2. Optionally regenerate LILY by converting back (future feature)

### Q: Which format gets processed?

**A**: Check the pipeline output:
```
✅ Successfully loaded via: build_score_data
```
This tells you which input method was used.

If using SOURCE variables directly (no build_score_data):
- `True` → Uses `SOURCE_MELODY_TINY`
- `False` → Uses `SOURCE_MELODY_LILY`

---

## Summary

✅ **Both formats coexist** for visual correlation  
✅ **Toggle controls dominance** (which format is processed)  
✅ **Backups created automatically** before modifications  
✅ **Modified files go to root** (working version)  
✅ **Output copies show current state** (inspection)  
✅ **Complete audit trail** in `outputs/` directory  

This workflow balances **flexibility** (edit any format) with **safety** (automatic backups) and **transparency** (both formats visible for learning).
# Promotion System - Quick Reference Card

## File Locations After Running first.py

```
Root Directory:
├── first.py ← Working version (both LILY + TINY formats)

outputs/ Directory:
├── first.py ← Inspection copy (shows both formats)
├── first.ly ← Generated LilyPond source
├── first.pdf ← Musical score (visual)
├── first.midi ← Audio playback
└── first.TIMESTAMP.bak ← Backup (only if promotion occurred)
```

---

## Toggle Behavior

```python
PROMOTE_TO_TINYNOTATION = False  # LilyPond is dominant
PROMOTE_TO_TINYNOTATION = True   # TinyNotation is dominant
```

**Note**: Only affects Stations 2 & 3 (SOURCE variables). `build_score_data()` has priority.

---

## Format Correlation Example

**LilyPond (verbose)**:
```lilypond
\relative e' {
    \time 6/4
    \key c \major
    \tempo 4=90
    e2 bmol4 c2 r4 |
}
```

**TinyNotation (compact)**:
```
time=6/4 key=Cmajor tempo=90 e2 b-4 c'2 r4
```

---

## Common Commands

### Run pipeline:
```bash
python3 first.py
```

### Check outputs:
```bash
ls -lh outputs/
cat outputs/first.py  # See both formats
```

### View PDF:
```bash
$BROWSER outputs/first.pdf
```

### Play MIDI:
```bash
# Use your preferred MIDI player
```

---

## Promotion Workflow

### 1st Run After Toggle Change:
```
📊 Found build_score_data() function

🔄 PROMOTION: Toggling format dominance
💾 Original copied to: outputs/first.TIMESTAMP.bak
✅ Modified file written to: first.py (root)
📋 Modified file copied to: outputs/first.py

⚠️  File has been promoted. Please re-run.
```

### 2nd Run (Processing):
```
📊 Found build_score_data() function
✅ Successfully loaded via: build_score_data

🎶 Engraving 'First Study - Two-Part Composition'...
📋 Copied first.py to outputs/ (shows both LILY and TINY formats)
✅ Successfully compiled first.pdf and .midi
```

---

## Pipeline Priority Order

1. **`build_score_data()`** ← Highest (used by first.py)
2. **`SOURCE_MELODY_TINY`** (if toggle = True)
3. **`SOURCE_MELODY_LILY`** (if toggle = False)
4. **`build_part()`** ← Lowest

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Toggle changed but no effect | Run file twice (1st: promotion, 2nd: processing) |
| Can't find backup | Check `outputs/*.bak` (not root) |
| Both formats not showing | Check `outputs/first.py` copy |
| Wrong format processed | Check toggle state and pipeline priority |

---

## Documentation Index

1. **PROMOTION_WORKFLOW.md** - Complete guide (read first!)
2. **PROMOTION_UPDATE.md** - Summary of changes
3. **PROMOTION_VERIFICATION.md** - Test results
4. **PROMOTION_QUICK_REFERENCE.md** - This card

---

## One-Page Cheat Sheet

### Files
- **Root**: Working version (`first.py`)
- **outputs/**: Inspection copies + generated files

### Toggle
- `False` = LilyPond dominant
- `True` = TinyNotation dominant

### Workflow
1. Edit formats in `first.py`
2. Set toggle if switching dominant format
3. Run `python3 first.py` (twice if toggle changed)
4. Check `outputs/` for results

### Correlation
- Both formats always visible in study file
- Comment blocks explain which is dominant
- `outputs/first.py` shows current state

---

**Last Updated**: October 4, 2025  
**Version**: 2.0 (Dual-Format Workflow)
