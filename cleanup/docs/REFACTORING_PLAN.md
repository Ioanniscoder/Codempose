# CODEMPOSE REFACTORING PLAN
Date: October 14, 2025

## CRITICAL ISSUES IDENTIFIED

### 1. CHORD PARSING - WRONG IMPLEMENTATION
**Status:** ❌ NEEDS IMMEDIATE FIX
**Problem:** Agent implemented Option A (string pass-through) instead of Option B (Parse Root Only)
**Impact:** Cannot transform chords, blocks tonal harmony roadmap
**Solution:** Revert to blueprint implementation with proper pitch resolution

### 2. MEASURE STRUCTURE - MISSING CONTEXT
**Status:** ⚠️ ARCHITECTURAL ISSUE
**Problem:** No measure-level abstraction; barlines calculated post-hoc by music21
**Impact:** Single duration error breaks all subsequent barlines
**Solution:** Introduce measure-aware shorthand and processing

### 3. CODE DUPLICATION - TRANSFORMATIONS
**Status:** ⚠️ MAINTENANCE ISSUE
**Problem:** transformation functions duplicated in every study file
**Impact:** Bug fixes must be manually copied to all files
**Solution:** Create centralized transformations.py library

## IMPLEMENTATION SEQUENCE

### PHASE 1: Fix Chord Parsing (PRIORITY 1)
- [ ] Verify current implementation is string pass-through
- [ ] Implement "Parse First Note" strategy as per blueprint
- [ ] Test with INTERMEZZO chords
- [ ] Verify transpose_part() works on chords
- [ ] Document pitch resolution logic

### PHASE 2: Create Transformations Library (PRIORITY 2)
- [ ] Create lib/transformations.py
- [ ] Move all transformation functions from study files
- [ ] Add proper docstrings and type hints
- [ ] Update all study files to import from library
- [ ] Remove duplicate code from study files

### PHASE 3: Measure-Aware Architecture (PRIORITY 3)
- [ ] Design measure-based shorthand format
- [ ] Implement measure-aware parser
- [ ] Add error isolation per measure
- [ ] Update build_score_from_assignments()
- [ ] Migrate existing studies to new format

## VERIFICATION CRITERIA

### Chord Parsing
- Chords parse to pitch dictionaries with step/octave/alter
- transpose_part(<chord>) produces correct transposed chord
- invert_part(<chord>) produces correct inverted chord
- LilyPond export reconstructs chord notation correctly

### Transformations Library
- No transformation code in any study file
- All studies import from lib/transformations.py
- Single source of truth for all transformations
- Easy to add new transformations

### Measure Architecture
- Voice assignments use measure list format
- Parsing errors isolated to single measure
- Barlines deterministic, not calculated post-hoc
- Support for time signature changes

## CURRENT STATE ASSESSMENT

Files needing transformation migration:
- thirteenth.py (current work)
- twelfth.py
- eleventh.py
- tenth.py
- (possibly others)

Chord parsing status:
- Tokenizer: ✅ Correct (recursive parse of first note)
- Relative Octave: ✅ Correct (processes base note)
- Parser: ❌ WRONG (passes string, doesn't build pitch list)
- Converter: ❌ WRONG (assumes string input)

## NEXT STEPS

1. Confirm current chord implementation is wrong
2. Get approval for refactoring scope
3. Execute Phase 1 (chord fix) first
4. Execute Phase 2 (transformations) second
5. Design Phase 3 (measures) for future implementation
