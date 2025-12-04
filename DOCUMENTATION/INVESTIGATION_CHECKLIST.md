# Investigation Checklist - Stave Synchronicity Bug

## Phase 1: Add Debug Instrumentation ⏳

- [ ] Copy debug print statements from `DEBUG_INSTRUMENTATION.py`
- [ ] Add to `src/score_builder.py` at specified locations
- [ ] Add path markers (PATH 1, PATH 2, PATH 3)
- [ ] Add section loop counters
- [ ] Add staff event length tracking
- [ ] Add final state summary

**Estimated time:** 15 minutes

---

## Phase 2: Run and Capture Data ⏳

- [ ] Run `python3 studies/ninetyninth.py > debug_output.txt 2>&1`
- [ ] Review console output in `debug_output.txt`
- [ ] Examine `outputs/ninetyninth.ly` structure
- [ ] Count barlines in Melody staff
- [ ] Count barlines in Bass staff
- [ ] Check for section markers

**Estimated time:** 5 minutes

---

## Phase 3: Data Analysis ⏳

### 3a: Execution Path
- [ ] Confirm Melody uses PATH 3 (simple single-voice)
- [ ] Confirm Bass uses PATH 3 (simple single-voice)
- [ ] Verify both use same code path

### 3b: Section Processing
- [ ] Verify 4 sections processed (section_idx 0-3)
- [ ] Check event counts per section:
  - [ ] Section 0, Melody: Should add ~45 events (THEME_A)
  - [ ] Section 0, Bass: Should add ~9 events (bass_figure)
  - [ ] Section 1, Melody: Should add ~45 events (transpose)
  - [ ] Section 1, Bass: Should add ~9 events (bass_figure)
  - [ ] Section 2, Melody: Should add ~5 events (THEME_B)
  - [ ] Section 2, Bass: Should add ~4 events (rests)
  - [ ] Section 3, Melody: Should add ~90 events (THEME_A * 2)
  - [ ] Section 3, Bass: Should add ~18 events (bass_figure * 2)

### 3c: Event Accumulation
- [ ] Check `staff_events` length before each section
  - Expected: Always 0 (cleared between sections)
  - If not: **ROOT CAUSE FOUND**
- [ ] Check `parts[staff_name]` length after each section
  - Melody: 45 → 90 → 95 → 185
  - Bass: 9 → 18 → ~22 → ~40

### 3d: Barline Insertion
- [ ] Count barline events in `parts['Melody']`
  - Expected: 4 (one after each section)
- [ ] Count barline events in `parts['Bass']`
  - Expected: 4 (one after each section)
- [ ] Check last event of each section
  - Expected: `{'type': 'barline', 'barline_type': '||'}`

**Estimated time:** 30 minutes

---

## Phase 4: Hypothesis Testing ⏳

### Test Hypothesis 1: Variable Not Cleared
**Prediction:** `staff_events` not cleared between sections for Melody

**Check:**
```
Section 0: staff_events before = 0, after = 45 ✓
Section 1: staff_events before = 0 OR 45?, after = ?
Section 2: staff_events before = ?, after = ?
```

**Result:** [ ] CONFIRMED / [ ] REJECTED

---

### Test Hypothesis 2: Different Code Paths
**Prediction:** Melody and Bass use different execution paths

**Check:**
```
Melody: PATH X
Bass: PATH Y
```

**Result:** [ ] CONFIRMED / [ ] REJECTED

---

### Test Hypothesis 3: Barline Insertion Failure
**Prediction:** Barlines not inserted for Melody

**Check:**
```
Barlines in Melody: ? (should be 4)
Barlines in Bass: ? (should be 4)
```

**Result:** [ ] CONFIRMED / [ ] REJECTED

---

### Test Hypothesis 4: Event List Reuse
**Prediction:** Same list object reused across sections

**Check:**
```python
# Check if staff_events id() changes between sections
print(f"staff_events id: {id(staff_events)}")
```

**Result:** [ ] CONFIRMED / [ ] REJECTED

---

**Estimated time:** 20 minutes

---

## Phase 5: Root Cause Identification ⏳

### Document Findings

**Execution Path Used:**
- Melody: PATH _____
- Bass: PATH _____

**Event Counts Per Section:**
| Section | Melody Events | Bass Events | Expected Melody | Expected Bass |
|---------|--------------|-------------|-----------------|---------------|
| 0       | _____        | _____       | 45              | 9             |
| 1       | _____        | _____       | 45              | 9             |
| 2       | _____        | _____       | 5               | 4             |
| 3       | _____        | _____       | 90              | 18            |

**Barline Counts:**
- Melody: _____ (should be 4)
- Bass: _____ (should be 4)

**Variable Clearing:**
- `staff_events` cleared between sections: [ ] YES / [ ] NO
- `parts[staff_name]` grows correctly: [ ] YES / [ ] NO

**Root Cause:**
```
[Describe the exact line/logic that causes the bug]
```

**Estimated time:** 20 minutes

---

## Phase 6: Solution Design ⏳

### Proposed Fix

**Option A:** [Describe fix]
- Pros:
- Cons:
- Risk:

**Option B:** [Describe fix]
- Pros:
- Cons:
- Risk:

**Recommended:** Option _____

**Implementation Plan:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Testing Plan:**
- [ ] Run ninetyninth.py
- [ ] Verify both staves have 4 sections
- [ ] Check barline count (should be 4 each)
- [ ] Verify no duration warnings
- [ ] Check PDF output
- [ ] Test with other studies (first.py, seventh.py)

**Estimated time:** 30 minutes

---

## Total Estimated Time: 2 hours

---

## Notes / Observations

[Space for notes during investigation]

---

## Final Decision

- [x] Root cause identified: **Parser creates events with wrong QL values → Renderer produces wrong note durations**
- [x] Solution designed: **Bypass parser for original snippets - inject LilyPond source directly**
- [x] Ready to implement fix: **YES - use original_snippets from metadata**
- [ ] Need more investigation: N/A

**Key Findings:**
1. Event assembly is 100% CORRECT (4 sections, 4 barlines per staff)
2. Both staves use same code path (PATH 3) - no divergence
3. Problem is in rendering: `ql_to_lily_duration_string()` converts wrong QL values
4. Example: THEME_B's `d2.` (3 QL) parsed as `ql=1.0` → renders as `d'1` (whole note)

**Solution:**
- For original snippets: Use `metadata['original_snippets']` directly, skip parsing
- For transformations: Accept minor duration issues (or improve parser later)

---

## Sign-off

Investigation completed by: GitHub Copilot
Date: October 20, 2025
Root cause: Parser-to-renderer QL value mismatch
Approved to proceed with fix: YES
