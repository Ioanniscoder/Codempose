# Hybrid Suffix Model for Transformations

**Status:** ✅ IMPLEMENTED  
**Date:** October 19, 2025  
**Files Modified:** `src/score_builder.py`, `src/transformations.py`

---

## Overview

The **Hybrid Suffix Model** provides a clean, backward-compatible way to handle both single-part and multi-part transformations in Blueprint Strings.

### Design Goals

1. ✅ **Backward Compatible**: Existing studies using single-part transformations continue to work without changes
2. ✅ **Explicit Multi-Part**: Multi-part transformations (like `harmonize_part`) require clear suffix syntax
3. ✅ **Efficient Caching**: Transformations run once, all parts cached, lookups are instant
4. ✅ **Clear Error Messages**: Helpful guidance when suffix is missing or wrong
5. ✅ **Auto-ID Assignment**: Single-part returns get `.id = 'melody'` automatically

---

## How It Works

### Case 1: Single-Part Transformations (No Suffix)

**Before (Still Works):**
```python
VOICE_STAVE_DATA = """
    transpose_part(THEME, 'P5') & BASS;
    invert_part(THEME, 'C4') & BASS
"""
```

**Behavior:**
- Transformation runs
- Returns `music21.stream.Part`
- If `.id` not set → auto-assigned `.id = 'melody'`
- Events cached and returned
- ✅ **Backward compatible with all existing studies**

### Case 2: Multi-Part Transformations (Suffix Required)

**New Syntax:**
```python
VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody
    &
    harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony
"""
```

**Behavior:**
- First call runs transformation ONCE
- Returns `music21.stream.Score` with 2 parts
- Both parts cached with suffixes:
  - `harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody`
  - `harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony`
- Second call is instant lookup (no re-execution)
- Each staff gets the correct part's events

### Case 3: Error Handling

**Missing Suffix on Multi-Part:**
```python
# ❌ This will ERROR
harmonize_part(MELODY, 'I-IV-V-I', 'C')  # No suffix!
```

**Error Message:**
```
❌ Transformation 'harmonize_part(MELODY, 'I-IV-V-I', 'C')' returns multiple parts.
   You MUST specify which part you want using a suffix.
   Example: harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody
        or  harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony
```

---

## Implementation Details

### 1. Score Builder Changes (`src/score_builder.py`)

**Global Cache:**
```python
_TRANSFORMATION_CACHE_STATUS = {}  # Cleared at start of each build
```

**Cache Clearing:**
```python
def build_score_from_blueprint(...):
    # Clear cache to prevent pollution between builds
    global _TRANSFORMATION_CACHE_STATUS
    _TRANSFORMATION_CACHE_STATUS.clear()
    ...
```

**Suffix Detection:**
```python
# Regex matches: "function_call():part_id"
suffix_match = re.match(r'^(.*\)):(\w+)$', snippet_name)

if suffix_match:
    base_instruction = suffix_match.group(1)  # "harmonize_part(MELODY, 'I-V-I')"
    requested_part_id = suffix_match.group(2)  # "harmony"
    ...
```

**Auto-ID Assignment:**
```python
if isinstance(transformed_result, music21.stream.Part):
    if not transformed_result.id:
        transformed_result.id = 'melody'
        print(f"      ℹ️  Auto-assigned .id = 'melody' to single-part result")
    ...
```

**Multi-Part Caching:**
```python
elif isinstance(transformed_result, music21.stream.Score):
    if requested_part_id is None:
        raise ValueError("Multi-part transformation requires suffix")
    
    # Cache all parts with their IDs
    for part in transformed_result.parts:
        full_key = f"{base_instruction}:{part.id}"
        snippets[full_key] = part_to_data(part)
        print(f"         ... Cached as '{full_key}'")
    ...
```

### 2. Transformation Changes (`src/transformations.py`)

**Setting Part IDs:**
```python
def harmonize_part(melody_part, progression_string, key='C'):
    ...
    harmonized_score = harmonize_melody(melody_part, progression_string, key)
    
    # SET PART IDs (CRITICAL for hybrid suffix model)
    harmonized_score.parts[0].id = 'melody'
    harmonized_score.parts[1].id = 'harmony'
    
    return harmonized_score
```

**Single-Part Transformations:**
```python
# These DON'T need to set .id - auto-assigned by framework
def transpose_part(part, interval_str):
    return part.transpose(interval_str)  # .id will be auto-set

def invert_part(part, center_pitch):
    ...
    return inverted_part  # .id will be auto-set
```

---

## Usage Examples

### Example 1: Simple Transformation (No Suffix)

```python
VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    THEME & BASS;
    transpose_part(THEME, 'P5') & BASS;
    invert_part(THEME, 'C4') & BASS
"""
```

**Result:**
- ✅ All transformations work without suffix
- ✅ Backward compatible
- ✅ Auto-assigned `.id = 'melody'`

### Example 2: Harmonization (Suffix Required)

```python
VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    MELODY & r;
    harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody
    &
    harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony
"""
```

**Result:**
- ✅ Transformation runs once
- ✅ Both parts cached
- ✅ Melody gets melody part, Bass gets harmony part
- ✅ Second call is instant lookup

### Example 3: Complex Multi-Section

```python
VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    # Section 1: Original
    THEME_A & BASS;
    
    # Section 2: Harmonized Theme A
    harmonize_part(THEME_A, 'I-V-I'):melody & harmonize_part(THEME_A, 'I-V-I'):harmony;
    
    # Section 3: Harmonized Theme B (different progression)
    harmonize_part(THEME_B, 'I-IV-V'):melody & harmonize_part(THEME_B, 'I-IV-V'):harmony;
    
    # Section 4: Mixed
    transpose_part(THEME_A, 'P5') & harmonize_part(THEME_B, 'I-IV-V'):harmony
"""
```

**Result:**
- ✅ Each unique transformation runs once
- ✅ All parts cached for reuse
- ✅ Mix single-part and multi-part freely

---

## Available Part IDs

### Current Implementation

| Transformation | Return Type | Part IDs |
|---------------|-------------|----------|
| `transpose_part` | Part | `:melody` (auto) |
| `invert_part` | Part | `:melody` (auto) |
| `retrograde_part` | Part | `:melody` (auto) |
| `augment_part` | Part | `:melody` (auto) |
| `diminish_part` | Part | `:melody` (auto) |
| `chordify_part` | Part | `:melody` (auto) |
| `harmonize_part` | Score | `:melody`, `:harmony` |
| `analyze_structural_tones` | Part | `:melody` (auto) |

### Future Extensions

To add new multi-part transformations:

1. **Set `.id` on all parts:**
   ```python
   def my_multi_part_transform(part):
       result_score = music21.stream.Score()
       
       melody = music21.stream.Part()
       melody.id = 'melody'  # REQUIRED
       
       harmony = music21.stream.Part()
       harmony.id = 'harmony'  # REQUIRED
       
       result_score.insert(0, melody)
       result_score.insert(0, harmony)
       
       return result_score
   ```

2. **Use in Blueprint:**
   ```python
   my_multi_part_transform(THEME):melody & my_multi_part_transform(THEME):harmony
   ```

---

## Benefits

### 1. Backward Compatibility
- **All existing studies work unchanged**
- No breaking changes to single-part transformations
- Smooth migration path

### 2. Clarity
- Multi-part transformations are explicit (`:melody`, `:harmony`)
- No ambiguity about which part goes where
- Self-documenting Blueprint Strings

### 3. Efficiency
- Transformation runs once, regardless of how many parts used
- Caching prevents redundant computation
- Fast lookups for subsequent calls

### 4. Error Prevention
- Clear error if suffix missing on multi-part
- Helpful suggestions in error messages
- Type safety (can't mix up parts)

### 5. Flexibility
- Mix single-part and multi-part freely
- Optional suffix on single-part (for consistency)
- Easy to add new multi-part transformations

---

## Testing

### Test Files

1. **`studies/test_transformations_blueprint.py`**
   - Tests backward compatibility
   - All single-part transformations without suffix
   - ✅ PASSES

2. **`studies/test_harmonic_intelligence.py`**
   - Tests new hybrid suffix model
   - Multi-part `harmonize_part` with `:melody` and `:harmony`
   - ✅ PASSES

### Verification

```bash
# Test backward compatibility
python studies/test_transformations_blueprint.py

# Test hybrid suffix model
python studies/test_harmonic_intelligence.py
```

**Expected Output:**
```
✓ Single Part returned, cached as 'transpose_part(THEME, 'P5')'
✓ Single Part returned, cached as 'invert_part(THEME, 'C4')'
...

🔄 Applying transformation: harmonize_part(MELODY, 'I-IV-V-I', 'C')
→ Detected Score with 2 parts. Caching all:
   ... Cached as 'harmonize_part(MELODY, 'I-IV-V-I', 'C'):melody'
   ... Cached as 'harmonize_part(MELODY, 'I-IV-V-I', 'C'):harmony'
```

---

## Migration Guide

### For Existing Studies

**No changes needed!** All existing single-part transformation calls continue to work.

### For New Multi-Part Transformations

**Old approach (no longer works):**
```python
# ❌ This will ERROR now
harmonize_part(MELODY, 'I-V-I')  # No way to specify which part
```

**New approach (required):**
```python
# ✅ Explicit and clear
harmonize_part(MELODY, 'I-V-I'):melody & harmonize_part(MELODY, 'I-V-I'):harmony
```

---

## Future Enhancements

### Possible Extensions

1. **More Part IDs:**
   - `:soprano`, `:alto`, `:tenor`, `:bass` for four-part harmony
   - `:counterpoint` for contrapuntal transformations
   - `:accompaniment` for piano-style accompaniment

2. **Pattern Shortcuts:**
   - `**harmonize_part(...)` → expands to all staves automatically?
   - Experimental - needs analysis

3. **Part Mapping:**
   - Allow custom ID mapping in layout?
   - `Melody=:soprano & Bass=:bass`

---

## Summary

The **Hybrid Suffix Model** successfully balances:
- ✅ Backward compatibility (existing code works)
- ✅ Clarity (explicit multi-part handling)
- ✅ Efficiency (run once, cache all)
- ✅ Developer experience (helpful errors, auto-ID)
- ✅ Extensibility (easy to add new transformations)

**Result:** Clean, powerful, future-proof transformation system for Blueprint Strings.
