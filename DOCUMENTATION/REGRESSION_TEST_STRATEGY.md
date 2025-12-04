# Regression Testing Strategy for Smart Stripping Changes

**Date:** October 20, 2025  
**Changes Under Test:** Smart stripping, measure bar generation, section/measure barline distinction  
**Files Modified:** `src/score_builder.py`, `src/project_template.py`

---

## Overview

We need to verify that our changes don't break existing functionality while testing that new features work correctly.

---

## Test Priority Matrix

### Priority 1: CRITICAL - Core Bypass Functionality
Studies that test basic bypass operations with original snippets:

1. **eighteenth.py** - Comprehensive feature demonstration
   - **Tests**: Modern build_score_data() approach, LilyPond snippets, multi-staff
   - **Risk**: LOW - comprehensive baseline with articulations, dynamics, tuplets
   - **Why this instead of first.py**: Uses modern code path (build_score_data with original_snippets)
   - **What to verify**: 
     - PDF compiles successfully
     - All three staves render (Melody, Harmony, Bass)
     - Tuplets, ties, grace notes render correctly
     - No duplicate metadata
     - Visual layout unchanged from baseline
   - **Note**: first.py uses old parsing approach (manual parse + build_from_blueprint)

2. **seventh.py** - Shorthand syntax with repetitions
   - **Tests**: Repetition operator (`V1 * 3`), concatenation (`V1 + V2`)
   - **Risk**: MEDIUM - uses repetitions which trigger smart stripping
   - **What to verify**:
     - Repetitions don't create duplicate metadata
     - Shorthand chains work correctly
     - PDF layout matches expected structure

### Priority 2: HIGH - Advanced Features
Studies that use transformations and complex layouts:

3. **tenth.py** - Four-station workflow with transformations
   - **Tests**: `transpose_events()`, `invert_events()`, programmatic generation
   - **Risk**: HIGH - transformations still use parser (Phase 2 limitation)
   - **What to verify**:
     - Transformations compile (may have wrong QL)
     - Original snippets render correctly
     - Smart stripping doesn't interfere with generated voices
     - Documentation generation works

### Priority 3: MEDIUM - Layout Variants
Studies that test different staff configurations:

4. **eleventh.py** - Multi-voice polyphonic staves
   - **Tests**: `(Voice1, Voice2)` syntax, polyphonic rendering
   - **Risk**: MEDIUM - multi-voice uses different assembly path
   - **What to verify**:
     - Multi-voice sections render correctly
     - Measure bars don't break polyphonic notation
     - Smart stripping applies to each voice independently

5. **thirteenth.py** - Complex multi-staff with auto-rests
   - **Tests**: `r` placeholder, rest generation with measure bars
   - **Risk**: HIGH - tests our new measure bar generation feature
   - **What to verify**:
     - Auto-generated rests have measure bars
     - Rest measures align with active staves
     - System breaks work correctly with rest sections

### Priority 4: LOW - Edge Cases
Studies that might reveal edge case issues:

6. **fifteenth.py** - Long compositions with many sections
   - **Tests**: Section barline logic, pagination
   - **Risk**: LOW - but useful for stress testing break logic
   - **What to verify**:
     - System breaks only after section barlines
     - No breaks after measure bars
     - PDF pagination looks professional

---

## Testing Approach

### Phase 1: Quick Smoke Tests (Priority 1)
**Goal:** Verify basic functionality isn't broken

```bash
# Run eighteenth.py - comprehensive baseline test
cd /workspaces/Codempose
python studies/OLD/eighteenth.py

# Check for errors:
# ✓ Compiles without errors
# ✓ PDF generated
# ✓ All three staves present (Melody, Harmony, Bass)
# ✓ Visual inspection: tuplets, ties, grace notes correct
```

**Expected Results:**
- No compilation errors
- PDF generated successfully
- All three staves render (Melody, Harmony, Bass)
- Advanced features work: tuplets, ties, grace notes, articulations, dynamics
- Layout unchanged from previous versions

**Why eighteenth.py instead of first.py:**
- Uses modern `build_score_data()` with `original_snippets` dict
- Tests same code path as ninetyninth.py (bypass mechanism)
- Comprehensive feature set (better smoke test)
- first.py uses old manual parsing approach (not representative)

**If PASS:** Continue to Phase 2  
**If FAIL:** STOP - fix critical regression before proceeding

---

### Phase 2: Repetition Testing (Priority 1-2)
**Goal:** Verify smart stripping works with repetitions

```bash
# Run seventh.py - tests V1 * 3 repetition syntax
python studies/OLD/seventh.py

# Manual verification:
grep -o '\\tempo' outputs/seventh.ly | wc -l
# Should see: 1 tempo directive (at score start)
# NOT: Multiple tempo directives per repetition

grep -o '\\bar "||"' outputs/seventh.ly | wc -l
# Count should match number of sections
```

**Expected Results:**
- Repetitions don't duplicate `\key`, `\time`, `\tempo`
- PDF shows repeated content without metadata clutter
- Measure count correct for repetitions

**Critical Check:**
```lilypond
% CORRECT:
theme_content theme_content theme_content

% WRONG:
\tempo 4=120 theme_content \tempo 4=120 theme_content \tempo 4=120 theme_content
```

**If PASS:** Continue to Phase 3  
**If FAIL:** Smart stripping has regression - debug `_extract_clean_music_content()`

---

### Phase 3: Measure Bar Generation (Priority 3)
**Goal:** Verify rest sections have proper measure bars

```bash
# Run thirteenth.py - has auto-rest sections
python studies/OLD/thirteenth.py

# Check rest sections:
sed -n '/\\new Staff.*rest/,/\\bar "||"/p' outputs/thirteenth.ly | head -20
# Should see: r2. \bar "|" r2. \bar "|" r2. \bar "|" r2.
# NOT: r2. r2. r2. r2.
```

**Expected Results:**
- Generated rests have `\bar "|"` between measures
- Visual alignment with active staves
- No extra `\break` commands after measure bars

**Critical Check:**
```lilypond
% CORRECT:
r2. \bar "|" r2. \bar "|" r2. \bar "||"

% WRONG:
r2. \bar "|" \break r2. \bar "|" \break r2. \bar "||"
```

**If PASS:** Continue to Phase 4  
**If FAIL:** Check rest generation logic in `score_builder.py` lines 995-1010

---

### Phase 4: Section Break Logic (Priority 3)
**Goal:** Verify breaks only occur at section boundaries

```bash
# Run fifteenth.py - long composition with many sections
python studies/OLD/fifteenth.py

# Check break positions:
grep -B1 '\\break' outputs/fifteenth.ly | grep '\\bar'
# All \break commands should follow \bar "||" (section barlines)
# NEVER after \bar "|" (measure barlines)
```

**Expected Results:**
- `\break` only after `\bar "||"`
- No `\break` after `\bar "|"`
- Professional pagination with sections kept together

**Critical Check:**
```bash
# Count breaks after measure bars (should be 0):
grep -E '\bar "\|" \\break' outputs/fifteenth.ly | wc -l
# Expected: 0

# Count breaks after section bars (should be ~half of section bars):
grep -E '\bar "\|\|" \\break' outputs/fifteenth.ly | wc -l
# Expected: > 0
```

**If PASS:** Continue to Phase 5  
**If FAIL:** Check break logic in `project_template.py` lines 687-700

---

### Phase 5: Transformation Compatibility (Priority 2)
**Goal:** Verify changes don't interfere with transformations

```bash
# Run tenth.py - uses transpose_events(), invert_events()
python studies/OLD/tenth.py

# Check for errors:
# ✓ Compiles (even if QL values wrong - known Phase 2 limitation)
# ✓ Original snippets render correctly
# ✓ Generated voices appear in output
```

**Expected Results:**
- Compilation successful
- Original snippets use bypass (correct durations)
- Transformed snippets use parser (may have wrong QL - expected)
- No interference between bypass and parser paths

**Known Limitation:**
Transformations use parser which has QL bugs (Phase 2 fix). This is EXPECTED and documented in ROOT_CAUSE_FOUND.md.

**If PASS:** All regression tests complete! ✅  
**If FAIL:** Check interaction between bypass and parser paths

---

## Regression Test Checklist

Use this checklist when running each test:

### Compilation Check
- [ ] No Python errors during execution
- [ ] LilyPond compilation successful
- [ ] PDF generated (`outputs/<study>.pdf` exists)
- [ ] MIDI generated (`outputs/<study>.midi` exists)

### Metadata Check
```bash
# Count tempo directives (should be 1 per score, not per repetition)
grep -o '\\tempo' outputs/<study>.ly | wc -l

# Count key signatures (should be 1 per staff, not per snippet)
grep -o '\\key [a-g]' outputs/<study>.ly | wc -l
```

### Barline Check
```bash
# Count measure bars (should match internal | in snippets)
grep -o '\bar "|"' outputs/<study>.ly | wc -l

# Count section bars (should match number of sections × staves)
grep -o '\bar "||"' outputs/<study>.ly | wc -l
```

### Break Check
```bash
# Verify NO breaks after measure bars
grep -E '\bar "\|".*\\break' outputs/<study>.ly | wc -l
# Expected: 0

# Verify breaks only after section bars
grep -E '\bar "\|\|".*\\break' outputs/<study>.ly | wc -l
# Expected: > 0
```

### Visual Check (PDF)
- [ ] All staves render throughout composition
- [ ] No missing sections
- [ ] System breaks at logical positions (section boundaries)
- [ ] Professional appearance

---

## Expected Outcomes

### Success Criteria:
✅ All Priority 1 tests pass (first.py, seventh.py)  
✅ Repetitions don't duplicate metadata  
✅ Measure bars appear in rest sections  
✅ Breaks only after section barlines  
✅ Transformations compile (even with known QL issues)

### Acceptable Known Issues:
⚠️ Transformed snippets have wrong durations (parser QL bug - Phase 2)  
⚠️ Some warnings about approximate durations (expected with parser)

### Unacceptable Failures:
❌ Compilation errors  
❌ Missing staves in PDF  
❌ Breaks after measure bars  
❌ Duplicate metadata in repetitions  
❌ Original snippets rendering incorrectly

---

## Debugging Guide

### If first.py fails:
- **Problem:** Basic bypass broken
- **Check:** `_extract_clean_music_content()` function
- **Look for:** Regex pattern matching issues, content extraction errors

### If seventh.py fails:
- **Problem:** Repetition handling broken
- **Check:** Repetition detection in `score_builder.py` lines 825-850
- **Look for:** Base name extraction, content duplication

### If thirteenth.py fails:
- **Problem:** Measure bar generation broken
- **Check:** Rest generation in `score_builder.py` lines 995-1010
- **Look for:** Missing `\bar "|"` insertion logic

### If fifteenth.py fails:
- **Problem:** Break logic broken
- **Check:** Barline counting in `project_template.py` lines 416-424, 687-700
- **Look for:** Pattern matching `\bar "||"` vs `\bar "|"`

---

## Test Execution Order

**Recommended sequence:**

1. **eighteenth.py** → Comprehensive baseline (modern code path)
2. **seventh.py** → Repetition + smart stripping
3. **thirteenth.py** → Measure bar generation
4. **eleventh.py** → Multi-voice compatibility
5. **fifteenth.py** → Break logic stress test
6. **tenth.py** → Transformation compatibility

**⚠️ Excluded:** first.py - uses old parsing approach (manual parse_lilypond_to_data + build_score_from_blueprint). Not representative of current architecture.

Stop at first failure and debug before proceeding.

---

## Post-Testing Actions

After all tests pass:

1. **Update todo list:** Mark "Regression test" as completed
2. **Document results:** Create `REGRESSION_TEST_RESULTS.md` with:
   - Test execution log
   - Any warnings or issues found
   - Confirmation that all critical functionality works
3. **Clean up debug output:** Remove excessive print statements
4. **Update ROOT_CAUSE_FOUND.md:** Mark investigation closed with resolution summary

---

## Conclusion

This testing strategy ensures our smart stripping changes don't break existing functionality while confirming new features work correctly. The phased approach allows us to catch regressions early and isolate issues to specific components.

**Next Action:** Start with Phase 1 - Run `first.py` and verify baseline functionality.
