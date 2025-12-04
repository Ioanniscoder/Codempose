# Stave Synchronicity Issue - Full Analysis & Evaluation Plan

**Date:** October 20, 2025  
**Issue:** Melody staff has all sections concatenated; Bass staff is correct  
**Status:** INVESTIGATION REQUIRED BEFORE FIXES

---

## Problem Statement

### Observed Symptoms
1. **Bass staff**: Correct structure with proper section breaks (`\bar "||"`)
   - Section 1: 4 bars (12 QL) - bass_figure
   - Section 2: 4 bars (12 QL) - bass_figure  
   - Section 3: 4 bars (12 QL) - rests
   - Section 4: 8 bars (24 QL) - bass_figure * 2
   
2. **Melody staff**: Corrupted - all sections run together without proper breaks
   - Contains `d'1` (whole note in 3/4 time - impossible!)
   - Has `\mark "B"` in wrong position
   - Much longer than expected
   - Lacks proper section boundaries

3. **Duration calculations**:
   - Barline-based: Reports correct durations (12, 12, 12, 24 QL)
   - Event summing: Reports wrong totals (Melody: 194.0 QL, Bass: 60.0 QL)

---

## Architecture Overview

### Current Data Flow

```
LILYPOND SOURCE (Station 1)
    ↓
parse_lilypond_to_data() → music21 parser
    ↓
EVENT DICTIONARY (Station 2)
    {'type': 'note', 'pitch': 'd', 'ql': 1.0, ...}
    ↓
build_score_from_blueprint() → Assembly (Station 3)
    ↓
PARTS DICTIONARY
    {'Melody': [events...], 'Bass': [events...]}
    ↓
events_to_lily() → Conversion
    ↓
LILYPOND OUTPUT (.ly file)
    ↓
LilyPond compiler
    ↓
PDF
```

### Execution Paths in build_score_from_blueprint()

There are **THREE** distinct code paths for processing staves:

#### Path 1: Multi-Voice Staff (Multiple voices in parentheses)
**Example:** `(Soprano, Alto) & (Tenor, Bass)`

**Location:** `src/score_builder.py` lines ~620-680

**Logic:**
```python
if staff_content and isinstance(staff_content[0], list):
    if len(voice_names) > 1:
        # MULTI-VOICE PATH
        voice_events_dict = {}
        for voice_idx, voice_snippets in enumerate(staff_content):
            # Collect events for each voice
            # Create multi_voice_section event
        parts[staff_name].append({'type': 'multi_voice_section', 'voices': voice_events_dict})
```

**Key characteristic:** Creates a special `multi_voice_section` event containing nested voice dictionaries

#### Path 2: Single Voice in Parentheses (Edge case)
**Example:** `(Melody) & Bass`

**Location:** `src/score_builder.py` lines ~682-704

**Logic:**
```python
else:
    # Single voice in parentheses (treat as simple single-voice)
    snippet_names = staff_content[0]
    # Process as simple list
```

**Key characteristic:** Unwraps the parentheses and treats as Path 3

#### Path 3: Simple Single-Voice Staff (No parentheses)
**Example:** `Melody & Bass` ← **THIS IS WHAT ninetyninth.py USES**

**Location:** `src/score_builder.py` lines ~705-750

**Logic:**
```python
else:
    # Single-voice staff (simple list)
    snippet_names = staff_content
    staff_events = []
    for snippet_name in snippet_names:
        # Inject marks
        # Get snippet events
        # Append to staff_events
    parts[staff_name].extend(staff_events)
```

**Key characteristic:** Directly extends the parts list with accumulated events

---

## Critical Questions for Investigation

### Question 1: Event Accumulation
**Where are events collected and how?**

- [ ] Path 3 (single-voice): Uses `staff_events = []` then `staff_events.extend(snippet_events)`
- [ ] Is `staff_events` cleared between sections? **CHECK LINE ~705**
- [ ] Does `parts[staff_name].extend(staff_events)` happen per section or once at end?

**Expected:** Each section should append its events to `parts[staff_name]`, with barlines between sections

**Hypothesis:** Events might be accumulating in wrong variable or not being sectioned properly

### Question 2: Section Loop Structure
**How does the section loop work?**

- [ ] Where does section loop start? **CHECK LINE ~608**
- [ ] How many times does it iterate? (Should be 4 for ninetyninth.py)
- [ ] Are barlines added between sections? **CHECK LINE ~818**

**Expected:** Loop processes each section from `VOICE_STAVE_DATA.split(';')`, adds barline after each

### Question 3: Parser vs Barline Duration Mismatch
**Why do we have TWO different duration calculations?**

1. **Parser-based (event summing)**:
   - Location: `sum(e.get('ql', 0) for e in events)`
   - Result for THEME_A: 46.0 QL (WRONG - includes grace notes, articulations)
   
2. **Barline-based (regex counting)**:
   - Location: `calculate_snippet_duration_from_barlines(lily_string)`
   - Result for THEME_A: 12.0 QL (CORRECT - counts bars × time signature)

**Current state:**
- Barline calculation used for **section duration matching** (padding rests)
- Event ql values used for **rendering notes** (wrong durations in output!)

**Critical issue:** Events have wrong `ql` values from parser, so when converted back to LilyPond, they produce wrong note durations!

### Question 4: Why is Bass Correct but Melody Wrong?
**Same code path, different results - WHY?**

Possibilities:
- [ ] Different snippets parsed differently?
- [ ] Order of processing (Melody first, Bass second)?
- [ ] Variable not cleared between staves?
- [ ] Mark injection interfering only with Melody (top staff)?

---

## Investigation Steps (Before Any Fixes)

### Step 1: Trace Execution Path for ninetyninth.py
**Goal:** Confirm which code path is actually executing

```python
# Add debug output at each path entry:
print(f"DEBUG: Processing staff {staff_name} via PATH X")
```

**Questions:**
- Does Melody use Path 3 (simple single-voice)?
- Does Bass use Path 3 (simple single-voice)?
- Are both using the same path?

**Action items:**
- [ ] Add path markers in score_builder.py
- [ ] Run ninetyninth.py
- [ ] Verify both staves use same path

### Step 2: Trace Section Loop
**Goal:** Understand how sections are processed

```python
# Add debug output in section loop:
print(f"DEBUG: Section {section_idx}, staff {staff_name}, snippets: {snippet_names}")
print(f"DEBUG: staff_events length before: {len(staff_events)}")
print(f"DEBUG: staff_events length after: {len(staff_events)}")
print(f"DEBUG: parts[{staff_name}] total events: {len(parts[staff_name])}")
```

**Expected output (4 sections, 2 staves = 8 debug blocks):**
```
Section 0, Melody: THEME_A → staff_events: 0 → 45 → parts['Melody']: 45
Section 0, Bass: bass_figure → staff_events: 0 → 9 → parts['Bass']: 9
Section 1, Melody: transpose_part(...) → staff_events: 0 → 45 → parts['Melody']: 90
Section 1, Bass: bass_figure → staff_events: 0 → 9 → parts['Bass']: 18
...
```

**Action items:**
- [ ] Add section/staff debug output
- [ ] Run and capture output
- [ ] Check if Melody accumulates correctly across sections
- [ ] Check if staff_events is cleared between sections

### Step 3: Inspect Event Structure
**Goal:** Understand what's actually in the events

```python
# Add detailed event inspection:
print(f"DEBUG: First event in staff_events: {staff_events[0]}")
print(f"DEBUG: Last event in staff_events: {staff_events[-1]}")
print(f"DEBUG: Event types: {Counter(e.get('type') for e in staff_events)}")
```

**Action items:**
- [ ] Print event samples
- [ ] Check for unexpected event types
- [ ] Look for corruption (wrong pitches, durations, etc.)

### Step 4: Examine Barline Insertion
**Goal:** Verify barlines are added between sections

```python
# After section processing:
print(f"DEBUG: Adding barline after section {section_idx}")
print(f"DEBUG: parts[{staff_name}][-1] = {parts[staff_name][-1]}")  # Should be barline
```

**Expected:** Each section should end with `{'type': 'barline', 'barline_type': '||'}`

**Action items:**
- [ ] Verify barline events exist
- [ ] Check barline placement
- [ ] Confirm both staves get barlines

### Step 5: Compare Parser Output
**Goal:** Understand parser behavior for THEME_A vs bass_figure

```python
# In parsing phase:
from lilypond_parser import parse_lilypond_to_data
for name, lily in snippets_to_parse.items():
    parsed = parse_lilypond_to_data(lily, part_name=name)
    events = parsed['parts'][name]
    print(f"DEBUG: {name}: {len(events)} events, total QL: {sum(e.get('ql', 0) for e in events)}")
    print(f"DEBUG: First 3 events: {events[:3]}")
```

**Action items:**
- [ ] Print parser output for all snippets
- [ ] Check if THEME_A has extra events (grace notes, articulations)
- [ ] Check if bass_figure parses cleanly

### Step 6: Review LilyPond Rendering
**Goal:** Understand how events → LilyPond conversion works

**Key files:**
- `src/lily_converter.py`: Converts events to LilyPond strings
- `src/project_template.py`: Assembles final .ly file

**Questions:**
- [ ] Does converter use event `ql` values directly?
- [ ] Are there any transformations applied during conversion?
- [ ] How are barlines rendered?

**Action items:**
- [ ] Read `events_to_lily()` function
- [ ] Trace how `parts['Melody']` becomes LilyPond
- [ ] Check if sections are properly separated in output

---

## Data Points to Collect

### From Console Output
- [ ] Section-by-section event counts (Melody vs Bass)
- [ ] Barline-based durations (should be 12, 12, 12, 24)
- [ ] Event-summed durations (currently shows 194 vs 60)
- [ ] Path markers (which code path executed)

### From Generated .ly File
- [ ] Count `\bar "||"` in Melody staff (should be 4)
- [ ] Count `\bar "||"` in Bass staff (should be 4)
- [ ] Measure count per section (should be 4, 4, 4, 8)
- [ ] Note durations (check if `d'1` really appears)

### From Code Inspection
- [ ] How many times is `parts[staff_name].extend()` called per staff?
- [ ] Is `staff_events` a local variable or reused?
- [ ] Where are barline events inserted?
- [ ] How are multi-staff layouts synchronized?

---

## Hypotheses to Test

### Hypothesis 1: Variable Not Cleared Between Sections
**Claim:** `staff_events` accumulates across sections for Melody but not Bass

**Test:** Add `print(f"staff_events cleared: {len(staff_events)}")` at start of section loop

**Expected if true:** Melody would show increasing values (45, 90, 95, 185), Bass always starts at 0

### Hypothesis 2: Different Code Paths
**Claim:** Melody and Bass take different execution paths

**Test:** Add path markers at each branch

**Expected if true:** Different "PATH X" messages for Melody vs Bass

### Hypothesis 3: Parser Corruption
**Claim:** THEME_A parses into corrupt events that include duplicate or phantom notes

**Test:** Print THEME_A parsed events and compare to LilyPond source

**Expected if true:** More events than actual notes in source

### Hypothesis 4: Rendering Issue
**Claim:** Events are correct, but converter produces wrong LilyPond

**Test:** Print `parts['Melody']` before conversion, check structure

**Expected if true:** Events would be correctly sectioned, but output file wrong

### Hypothesis 5: Barline Insertion Failure
**Claim:** Barlines not inserted for Melody, causing sections to run together

**Test:** Check `parts['Melody']` for barline events

**Expected if true:** Bass has 4 barline events, Melody has fewer or none

---

## Success Criteria for Investigation

Before implementing any fixes, we need to answer:

1. **Which execution path is used?** (Path 1, 2, or 3)
2. **How many times does section loop execute?** (Should be 4)
3. **How many events in parts['Melody'] after each section?** (45, 90, 95, 185 total)
4. **How many events in parts['Bass'] after each section?** (9, 18, 18+rest, 60 total)
5. **How many barline events in each staff?** (Should be 4 each)
6. **What are the actual QL values in parsed events?** (Document the parser bug)
7. **Why does Bass render correctly but Melody doesn't?** (Root cause)

---

## Proposed Debugging Session

### Phase 1: Add Instrumentation (15 min)
- Add print statements at critical points
- Mark execution paths
- Track variable states

### Phase 2: Run and Capture (5 min)
- Execute ninetyninth.py with debug output
- Save console output to file
- Examine generated .ly file

### Phase 3: Analysis (30 min)
- Review debug output
- Map execution flow
- Identify divergence point (where Melody goes wrong)

### Phase 4: Root Cause Determination (20 min)
- Test hypotheses
- Pinpoint exact bug location
- Document findings

### Phase 5: Solution Design (30 min)
- Propose fix strategy
- Evaluate impact
- Plan implementation

---

## Next Steps

**DO NOT IMPLEMENT FIXES YET**

Instead:
1. Review this analysis plan
2. Add the proposed debug instrumentation
3. Run investigation phase
4. Document findings
5. Discuss root cause before fixing

---

## Open Questions

1. **Parser vs Barline**: Should we bypass parser entirely and use original LilyPond strings?
2. **Event QL values**: Can we recalculate/correct them after parsing?
3. **Architecture**: Should we refactor to avoid parse-and-reconvert cycle?
4. **Backward compatibility**: Will fixes break existing studies?

---

## Files to Review

Priority order:
1. `src/score_builder.py` lines 600-820 (blueprint assembly)
2. `src/lily_converter.py` (events → LilyPond)
3. `src/lilypond_parser.py` (LilyPond → events)
4. `src/snippet_utils.py` (barline counting)
5. `src/project_template.py` (final .ly generation)
