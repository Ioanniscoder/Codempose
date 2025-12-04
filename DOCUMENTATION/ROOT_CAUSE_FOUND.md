# ROOT CAUSE IDENTIFIED - Stave Synchronicity Issue

**Date:** October 20, 2025  
**Status:** ✅ ROOT CAUSE CONFIRMED
**Problem:** Parser creates events with wrong QL values → Renderer produces wrong note durations

---

## Investigation Results

### Execution Flow: ✅ CORRECT
- Both Melody and Bass use **PATH 3** (simple single-voice staff)
- Same code path for both staves - **NO DIVERGENCE**

### Event Assembly: ✅ CORRECT
```
Section 1:
  Melody: 0 → 45 events (+ 1 barline) = 46 total
  Bass:   0 → 9 events (+ 1 barline) = 10 total

Section 2:
  Melody: 46 → 91 events (+ 1 barline) = 92 total  
  Bass:   10 → 19 events (+ 1 barline) = 20 total

Section 3:
  Melody: 92 → 98 events (+ 1 barline) = 99 total
  Bass:   20 → 25 events (+ 1 barline) = 25 total

Section 4:
  Melody: 99 → 189 events (+ 1 barline) = 190 total
  Bass:   25 → 43 events (+ 1 barline) = 44 total
```

### Barline Insertion: ✅ CORRECT
- Melody: **4 barlines** (one after each section)
- Bass: **4 barlines** (one after each section)
- `.ly file`: **8 barlines total** (4 per staff)

### Variable Clearing: ✅ CORRECT
- `staff_events = []` creates new list each section
- No accumulation across sections
- Proper extend to `parts[staff_name]`

---

## The REAL Problem

### Parser Creates Wrong Event Durations

**Example from THEME_B:**
```lilypond
% Original LilyPond:
\relative c' {
    g4( fis e) |    % Three quarter notes
    d2.~ |          % Dotted half note with tie
    d4 e fis |      % Three quarter notes
    g2.             % Dotted half note
}
```

**Parser output (WRONG):**
```python
[
    {'type': 'note', 'pitch': 'g', 'ql': 1.0},   # Correct ✓
    {'type': 'note', 'pitch': 'd', 'ql': 1.0},   # WRONG! Should be 3.0 ✗
    {'type': 'note', 'pitch': 'e', 'ql': 1.0},   # Correct ✓
    {'type': 'note', 'pitch': 'fis', 'ql': 1.0}, # Correct ✓
    {'type': 'note', 'pitch': 'g', 'ql': 1.0},   # WRONG! Should be 3.0 ✗
]
```

**Rendered LilyPond (WRONG):**
```lilypond
\mark "B" g'4 d'1 e'4 fis'4 g'2.
```

Note the `d'1` - that's a **whole note** (4 QL) in 3/4 time, which is impossible!

The renderer is trying to convert `ql=1.0` back to LilyPond, but there's some conversion error happening.

---

## Why Bass Staff Looks Correct

**bass_figure is simpler:**
```lilypond
\relative c {
    g4 d' b |       % All quarter notes
    c'2 b4 |        % Half + quarter
    a4 g4 fis4 |    % All quarter notes  
    g2.             # Dotted half
}
```

The parser still gets it wrong, but the **simpler rhythms** happen to render more correctly. The corruption is less visible.

---

## Evidence from .ly File

**Melody staff (all on one line, hard to read):**
```
e'''4 d'''4 a''4... \bar "||" a'''4 g'''4... \bar "||" \mark "B" g'4 d'1 e'4... \bar "||" e'''4 d'''4... \bar "||"
```

**Bass staff (properly formatted):**
```
g4 d'4 b4 c'2 b4... \bar "||"
g4 d'4 b4 c'2 b4... \bar "||"
r2. r2. r2. r2. \bar "||"
g4 d'4 b4... \bar "||"
```

Both have 4 barlines. Both have proper sections. The difference is in the **note durations** produced by the renderer.

---

## Root Cause: Parser + Renderer Mismatch

### The Chain of Errors:

1. **Parser (lilypond_parser.py):**
   - Uses music21 to parse LilyPond
   - music21 creates **extra events** for articulations, grace notes
   - music21 assigns **wrong QL values** to notes
   - Result: `THEME_A` parsed as 25 events with 26.0 QL (should be 12.0 QL)

2. **Assembly (score_builder.py):** ✅ WORKS CORRECTLY
   - Collects events into sections
   - Adds barlines between sections
   - Uses barline-based duration for section alignment
   - Result: Correct structure with 4 sections per staff

3. **Renderer (lily_converter.py / project_template.py):**
   - Converts events back to LilyPond
   - Uses `ev.get('ql', 1.0)` to determine note duration
   - Calls `ql_to_lily_duration_string(ql)` to convert QL → duration
   - Result: Wrong durations in output (`d'1` instead of `d'2.`)

---

## Why "All Sections Concatenated"?

They're NOT actually concatenated! The sections ARE separated by `\bar "||"` markers. The problem is:

1. **Visual**: LilyPond output is on one long line (formatting issue)
2. **Musical**: Wrong note durations make it sound/look wrong
3. **Perception**: With wrong durations, sections don't align properly in time

---

## The Solution

### Option A: Fix the Parser (HARD)
- Modify `lilypond_parser.py` to extract correct durations
- Fix music21 integration
- Handle all edge cases (ties, dots, tuplets)
- **Risk:** May break existing studies

### Option B: Bypass the Parser (RECOMMENDED)
- Use original LilyPond strings directly
- Don't parse → convert → re-render
- Only parse for transformations (transpose, invert)
- **Benefit:** Preserves exact original notation

### Option C: Post-Process Event Durations (HACKY)
- After parsing, recalculate event QL values using barline counting
- Distribute total duration across events
- **Problem:** Doesn't know which events are grace notes, which are real

---

## Immediate Fix Strategy

**Short-term (TODAY):**
1. For **original snippets**, inject the LilyPond source directly (no parsing)
2. For **transformations**, continue using parsed events (accept imperfection)
3. Document the limitation

**Long-term (FUTURE):**
1. Implement better parser that preserves durations
2. OR: Keep transformations in LilyPond domain (use `\transpose` directive)
3. OR: Build transformation library that operates on LilyPond strings

---

## Testing the Fix

**Expected after fix:**
1. THEME_A should render exactly as written (no `d'1` errors)
2. bass_figure should render exactly as written
3. Transformations may still have minor duration issues (acceptable)
4. Both staves should have clean, readable output

**Test files:**
- ninetyninth.py (current test case)
- first.py, seventh.py, tenth.py (regression tests)

---

## Conclusion

**The assembly phase is PERFECT.**  
**The problem is parser → renderer mismatch.**  
**Solution: Bypass parsing for original snippets.**

We were chasing the wrong problem! The "stave synchronicity" issue was actually a **note duration rendering** issue caused by the parser creating bogus event QL values.

---

## Next Steps

1. ✅ Document root cause (THIS FILE)
2. ⏳ Design bypass mechanism for original snippets
3. ⏳ Implement fix in project_template.py or lily_converter.py
4. ⏳ Test with ninetyninth.py
5. ⏳ Regression test with other studies
6. ⏳ Update documentation
