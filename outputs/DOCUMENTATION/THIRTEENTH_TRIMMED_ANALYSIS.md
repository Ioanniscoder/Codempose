# Thirteenth Study: Trimmed Analysis

## Date: 2025-10-13
## Purpose: Focused inspection of Theme A and Intermezzo only

---

## Changes Made

1. **Created backup**: `thirteenth.py.bak` (original with all 3 themes)
2. **Commented out**: All THEME_B and THEME_C code throughout `thirteenth.py`
3. **Trimmed to**: Theme A + Intermezzo only (86 events vs original 220 events)

---

## Three Issues Under Investigation

### ❌ Issue 1: Tuplets Appear Dotted When They Shouldn't Be

**Expected Behavior**: 
- Input: `[d e f]8` - 3 notes as eighth-note tuplets
- Should output: Three eighth notes without dots

**Actual Behavior**:
- Output: `d''16. e''16. f''16.` - three DOTTED sixteenth notes
- Duration: 16. = dotted 16th = 0.375 quarter length
- Problem: Adding dots when input has no dots

**Evidence from .ly file** (line 120):
```
c''4 d''16. e''16. f''16. e''2 ...
```

**Evidence from console warnings**:
```
[warning] approximate duration: requested ql=1/3 approximated as 0.375 (LilyPond: 16.); diff=0.041666666666666685
```

**Analysis**:
- Tuplet duration: 1/3 quarter length (0.333...)
- music21 approximation: 0.375 quarter length (dotted 16th)
- Difference: ~0.042 QL
- Root cause: music21 cannot represent exact triplet eighth notes as single LilyPond duration
- **ACTUAL PROBLEM**: Should use `\tuplet 3/2 { d8 e8 f8 }` notation, NOT dotted notes

---

### ❌ Issue 2: Tuplets Missing Standard Arc with "3" Notation

**Expected Behavior**:
- LilyPond syntax: `\tuplet 3/2 { d8 e8 f8 }`
- Visual output: Arc/bracket over notes with "3" number
- Standard notation: Shows rhythmic grouping clearly

**Actual Behavior**:
- Output: Individual dotted notes (no tuplet markup)
- Missing: `\tuplet` command entirely
- Result: Looks like regular dotted notes, not triplets

**Root Cause**:
- Bracket notation `[d e f]8` is being parsed correctly
- Duration calculation is happening (1/3 QL per note)
- BUT: LilyPond export is NOT using `\tuplet` command
- Instead: Approximating as dotted durations

**Fix Needed**:
- `lily_converter.py` must detect tuplet events
- Output proper `\tuplet N/M { ... }` syntax
- NOT approximated dotted durations

---

### ❌ Issue 3: Harmony Sections (INTERMEZZO) Not Appearing

**Expected Behavior**:
- Input: `<c e g>2 <d f a>2 | <e g b>2 <f a c>2`
- Should appear: 4 chord events between theme sections
- Voice tracking: Shows "Intermezzo_1", "Intermezzo_2", "Intermezzo_3", etc.

**Actual Behavior**:
- Console output: `✓ Intermezzo: 0 events (harmony)`
- Voice tracking: `'events': 0` for all Intermezzo sections
- Result: Intermezzo sections are MISSING from output

**Evidence from console**:
```
✓ Theme A: 20 events (tuplets, ties, grace notes)
✓ Intermezzo: 0 events (harmony)
```

**Evidence from voice tracking** (line 93-96 of .ly):
```
% 02_Intermezzo_1:
%   Transformation: identity
%   Description: Harmonic interlude (chords)
%   Events: 0
```

**Root Cause Investigation Needed**:
1. Is INTERMEZZO_LILY being parsed correctly?
2. Are chord events `<c e g>2` being extracted?
3. Is `lily_to_tiny()` handling chord syntax?
4. Check `extract_data_from_part()` for chord support

---

## LilyPond Output Analysis

### Current Output (line 120):
```lilypond
c''4 d''16. e''16. f''16. e''2 g''64 a''2\p b''16. c'''16. d'''16. c'''2 e'''16. f'''16. g'''16. f'''4 e'''2 d'''4 c'''64 e'''2. r2 \bar "||" \bar "||"
```

### Issues Visible:
1. **d''16. e''16. f''16.** - Should be `\tuplet 3/2 { d''8 e''8 f''8 }`
2. **g''64** - Grace note approximated as 64th note (should be `\grace { g''16 }`)
3. **\bar "||" \bar "||"** - Double bar lines (because Intermezzo sections are empty)
4. **No chords** - Completely missing INTERMEZZO chord progressions

---

## Next Steps

### 1. Fix Tuplet Export
- Modify `lily_converter.py` to detect `event.get('type') == 'tuplet'`
- Generate `\tuplet N/M { ... }` syntax instead of approximating
- Preserve exact tuplet ratios (3:2, 5:4, etc.)

### 2. Fix Grace Note Export
- Use `\grace { ... }` or `\acciaccatura` syntax
- Not approximated 64th notes

### 3. Investigate Intermezzo Parsing
- Debug why `extract_data_from_part(parse_part(INTERMEZZO_LILY))` returns 0 events
- Test chord parsing: `<c e g>2` → should create chord events
- Check if `lily_to_tiny()` handles chord syntax correctly
- Verify `parse_part()` and `extract_data_from_part()` for chord support

---

## Test Environment

- **File**: `thirteenth.py` (trimmed version)
- **Backup**: `thirteenth.py.bak` (original)
- **Output**: `outputs/thirteenth.*` (ly, pdf, midi, musicxml)
- **Events**: 86 total (Theme A variations + empty Intermezzo slots)
- **Structure**: 
  - Theme A Original (20 events)
  - Intermezzo 1 (0 events) ❌
  - Theme A Transposed (20 events)
  - Intermezzo 2 (0 events) ❌
  - Theme A Inverted (20 events)
  - Intermezzo 3 (0 events) ❌
  - Theme A Harmonized (20 events)

---

## Files Modified

1. `thirteenth.py` - Commented out all Theme B and C code
2. `thirteenth.py.bak` - Backup of original
3. `outputs/thirteenth.ly` - Generated with issues visible
4. `outputs/thirteenth.pdf` - Compiled (shows dotted notes, missing chords)
5. `outputs/thirteenth.musicxml` - Exported (same issues)

---

## Success Criteria

✅ **COMPLETED**: Trimmed study to minimal test case  
❌ **PENDING**: Fix tuplet export to use `\tuplet` syntax  
❌ **PENDING**: Fix grace note export to use `\grace` syntax  
❌ **PENDING**: Debug and fix Intermezzo chord parsing (0 events → 4 events)

---

## Console Output Summary

```
✓ Theme A: 20 events (tuplets, ties, grace notes)
✓ Intermezzo: 0 events (harmony)  ← PROBLEM

✓ Theme A: Transposed (+P5), Inverted (C4), Harmonized

✅ Built complete score: 86 total events

✓ Theme A features:
   - Tuplets: 0  ← SHOULD BE > 0
   - Grace notes: 2
   - Tied notes: 5

[warning] approximate duration: requested ql=1/3 approximated as 0.375  ← TUPLET PROBLEM
```

---

## music21 Warnings

**Pattern**: 36 warnings about approximate durations
- Tuplets: `ql=1/3` → approximated as `0.375` (dotted 16th)
- Grace notes: `ql=0.0` → approximated as `0.0625` (64th note)

**Implication**: music21 is approximating instead of using proper notation syntax

---

## Recommendations

1. **Immediate**: Fix tuplet export in `lily_converter.py`
2. **High Priority**: Debug Intermezzo chord parsing
3. **Medium Priority**: Fix grace note export
4. **Future**: Consider bypassing music21 for LilyPond export (direct token → LilyPond)

