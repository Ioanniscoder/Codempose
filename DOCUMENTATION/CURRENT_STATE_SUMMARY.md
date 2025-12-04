# Current State Summary - Stave Synchronicity Issue

**Date:** October 20, 2025  
**Status:** INVESTIGATION MODE - NO MORE FIXES UNTIL ROOT CAUSE IDENTIFIED

---

## What We Know

### Working Features ✅
1. **Barline-based duration calculation** works correctly
   - Counts bars in LilyPond source
   - Extracts time signature
   - Calculates accurate total QL (12.0 for THEME_A, not 46.0)
   
2. **Explicit mark override** works correctly
   - Detects `\mark` in snippet source
   - Skips auto-injection when found
   - Shows only "B" mark (THEME_B), not "A" (THEME_A has explicit mark)

3. **Bass staff renders correctly**
   - 4 sections with proper barlines
   - Correct durations: 12, 12, 12, 24 QL
   - Proper rest padding in section 3
   - Clean output in .ly file

### Broken Features ❌
1. **Melody staff renders incorrectly**
   - All sections appear concatenated
   - Contains impossible notes (`d'1` in 3/4 time)
   - Wrong total duration (194 QL instead of 60 QL)
   - Unclear section boundaries

2. **Parser produces wrong event durations**
   - THEME_A (4 bars in 3/4 = 12 QL) parsed as 46 QL
   - Each note gets `ql: 1.0` regardless of actual duration
   - Grace notes, articulations counted as separate events

---

## Two Separate Problems

### Problem 1: Parser Inaccuracy (KNOWN)
**Symptom:** Events have wrong `ql` values

**Example:**
```python
# LilyPond source:
d4-.\p( fis8 g) a4~

# Parser output (WRONG):
[
  {'type': 'note', 'pitch': 'd', 'ql': 1.0},      # Should be 1.0 ✓
  {'type': 'note', 'pitch': 'd', 'ql': 1.0},      # Duplicate from articulation! ✗
  {'type': 'note', 'pitch': 'fis', 'ql': 1.0},    # Should be 0.5 ✗
  {'type': 'note', 'pitch': 'g', 'ql': 1.0},      # Should be 0.5 ✗
  ...
]
```

**Impact:** 
- Event summing gives wrong durations
- Rendering produces incorrect note lengths in output

**Current workaround:**
- Barline-based calculation for **section alignment**
- But events still have wrong ql values for **rendering**

### Problem 2: Stave Synchronicity (UNKNOWN - INVESTIGATION NEEDED)
**Symptom:** Melody staff corrupted, Bass staff correct

**Mysteries:**
1. Why does same code path work for Bass but not Melody?
2. Why are sections concatenated only in Melody?
3. Where are the extra events coming from?
4. Why does `\mark "B"` appear in wrong location?

**This is what we need to investigate NOW**

---

## What We Changed (Recent History)

### Session 1: Barline-Based Duration
- Added `calculate_snippet_duration_from_barlines()` in `snippet_utils.py`
- Used for snippet preview .ly file headers ✓

### Session 2: Snippet Name Marks  
- Added `get_snippet_mark_text()` for underscore convention ✓
- Injected `text_mark` events in blueprint assembly ✓
- Only on top staff ✓

### Session 3: Explicit Mark Override
- Added `snippet_contains_explicit_mark()` regex detection ✓
- Added `original_snippets` to metadata ✓
- Skips auto-injection when explicit mark found ✓

### Session 4: Duration Mismatch Fixes (ATTEMPTED)
- Created `_calculate_accurate_duration()` helper
- Integrated barline-based calculation into assembly
- Handles original snippets, transformations, repetitions
- **Result:** Warnings gone, but OUTPUT STILL WRONG ⚠️

---

## Current Code State

### Files Modified
1. `src/score_builder.py`
   - Added helper functions (lines 70-155)
   - Modified duration calculation (lines 667, 744)
   - Integrated barline counting
   
2. `src/snippet_utils.py` (NEW)
   - Barline counting logic
   
3. `src/project_template.py`
   - Text mark rendering
   
4. `studies/ninetyninth.py`
   - Added `original_snippets` to metadata
   - Added explicit mark to THEME_A

5. `generate_study.py`
   - Updated template with mark documentation
   - Added `original_snippets` example

### Potentially Problematic Areas
1. Event accumulation in Path 3 (lines 705-750)
2. Barline insertion (lines 815-820)
3. Multi-voice vs single-voice branching (lines 620-750)
4. Event-to-LilyPond conversion (lily_converter.py)

---

## What NOT to Do

❌ **Don't add more fixes without understanding root cause**
❌ **Don't modify parser without investigation**
❌ **Don't refactor architecture yet**
❌ **Don't bypass parser until we know it's necessary**

---

## What TO Do Next

✅ **Add debug instrumentation** (see DEBUG_INSTRUMENTATION.py)
✅ **Run investigation** (follow EVALUATION_PLAN_STAVE_SYNC.md)
✅ **Document findings** (create new analysis file)
✅ **Design solution** (after root cause identified)
✅ **Test thoroughly** (before committing)

---

## Key Questions to Answer

1. **Execution path:** Which path (1, 2, or 3) do Melody and Bass take?
2. **Event accumulation:** How many events in `parts['Melody']` after each section?
3. **Barline insertion:** Are barlines added correctly to both staves?
4. **Variable scope:** Is `staff_events` cleared between sections?
5. **Parser behavior:** What events does THEME_A actually produce?

---

## Investigation Priority

**HIGH PRIORITY:**
- Trace execution flow with debug output
- Count events at each stage
- Verify barline placement
- Compare Melody vs Bass processing

**MEDIUM PRIORITY:**
- Understand parser behavior
- Document event structure
- Review rendering logic

**LOW PRIORITY (AFTER ROOT CAUSE FOUND):**
- Design parser bypass
- Refactor architecture
- Optimize performance

---

## Success Criteria

Investigation complete when we can answer:
- **Where exactly does Melody staff processing diverge from Bass?**
- **What causes the corruption?**
- **Why are sections concatenated?**
- **What is the minimal fix?**

Only THEN implement solution.

---

## Risk Assessment

**If we fix without investigating:**
- Might fix symptom, not root cause
- Could break other features
- May introduce new bugs
- Won't understand the system

**If we investigate first:**
- Understand the actual problem
- Design targeted fix
- Avoid breaking changes
- Learn system architecture

**Recommendation:** INVESTIGATE, don't guess.
