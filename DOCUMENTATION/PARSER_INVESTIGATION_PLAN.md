# Parser Investigation Plan - Duration Mismatch Issue

**Date:** October 20, 2025  
**Problem:** Parser creates 35 events (36 QL) from snippet that should be 12-16 QL  
**Impact:** Staves go out of sync, rest padding fails, metadata misleading

---

## Evidence Summary

### Input Snippet (THEME_A_LILY)
```lilypond
\relative c'' {
    \key g \major
    \time 3/4
    \tempo "Andante" 4=90
    d4-.\p( fis8 g) a4~ |      % Bar 1: 1 + 0.5 + 0.5 + 1 = 3 QL
    a4 g4->( fis) |             % Bar 2: 1 + 1 + 1 = 3 QL
    e4.( d8~ d4) |              % Bar 3: 1.5 + 0.5 + 1 = 3 QL
    b'4\f c4 d4                 % Bar 4: 1 + 1 + 1 = 3 QL
}
```
**Expected:** 12 notes, 12 QL total (4 bars × 3 QL/bar)

### Parser Output
- **31 note events** (32.0 QL)
- **4 rest events** (4.0 QL)
- **Total: 35 events, 36.0 QL**

### Anomaly
First event shows `'step': 'E'` but source starts with `d4`  
This suggests parser is including notes from elsewhere or has state corruption.

---

## Investigation Steps

### Phase 1: Isolate the Parser (IMMEDIATE)

**EMPHASIS AREAS (from user feedback):**
- **Tie Consolidation (~):** Check if `a4~ | a4` creates 1 event (2.0 QL) or 2 events (1.0 + 1.0)
- **Slurs/Parentheses:** Verify `( fis8 g)` doesn't create extra events
- **First Note Anomaly:** Investigate why first event is 'E' instead of 'd' (state bleeding?)

**1.1 Test Parser in Isolation**
```bash
# Create minimal test case
cd /workspaces/Codempose
python3 -c "
from src.lilypond_parser import parse_lilypond_to_data

# Single snippet, fresh parse
snippet = r'''
\\relative c'' {
    d4 e4 f4
}
'''.strip()

result = parse_lilypond_to_data(snippet, part_name='TEST')
events = result['parts']['TEST']

print(f'Input: 3 notes (d4 e4 f4)')
print(f'Output: {len(events)} events')
for i, e in enumerate(events):
    print(f'  {i}: {e}')
"
```

**Expected:** 3 note events  
**If we get more:** Parser has internal state or expansion bug

**1.2 Test Multiple Parses**
```bash
# Parse same snippet twice - check for state pollution
python3 -c "
from src.lilypond_parser import parse_lilypond_to_data

snippet = r'\\relative c'' { d4 e4 f4 }'

# First parse
result1 = parse_lilypond_to_data(snippet, part_name='TEST1')
events1 = result1['parts']['TEST1']

# Second parse
result2 = parse_lilypond_to_data(snippet, part_name='TEST2')
events2 = result2['parts']['TEST2']

print(f'Parse 1: {len(events1)} events')
print(f'Parse 2: {len(events2)} events')
print(f'Same result: {events1 == events2}')
"
```

**Expected:** Both should be identical  
**If different:** Parser has global state that isn't being cleared

**1.3 Test in Study Context**
```bash
# Parse within study context (like ninetyninth.py does)
cd /workspaces/Codempose
python3 -c "
import sys
sys.path.insert(0, 'studies')
import _study_path
from src.lilypond_parser import parse_lilypond_to_data

# Parse THEME_A exactly as study does
THEME_A = r'''\\relative c'\'' { d4 e4 f4 }'''

# Simulate study's multi-parse scenario
snippets = {
    'THEME_A': THEME_A,
    'THEME_B': THEME_A,  # Same snippet, different name
}

for name, snippet in snippets.items():
    parsed = parse_lilypond_to_data(snippet, part_name=name)
    events = parsed['parts'][name]
    print(f'{name}: {len(events)} events')
"
```

---

### Phase 2: Examine Parser Implementation (IF NEEDED)

**2.1 Read Parser Source**
```bash
# Check parser for global state, caches, accumulators
grep -n "global\|class\|cache" src/lilypond_parser.py | head -20
```

**Look for:**
- Global variables that accumulate across calls
- Class instances that retain state
- Caches that aren't cleared between parses

**2.2 Check for Event Expansion**
```bash
# Find where events are created
grep -n "append.*event\|events\\.append\|events =" src/lilypond_parser.py | head -20
```

**Look for:**
- Loops that expand notes (e.g., ties creating multiple events)
- Articulation/dynamic processing that adds events
- Voice splitting logic

**2.3 Check Rest Insertion**
```bash
# Find where rests are auto-inserted
grep -n "rest\|fill.*bar\|pad" src/lilypond_parser.py
```

---

### Phase 3: Fix or Workaround

**Scenario A: Parser Has Global State**
- **Fix:** Add `clear_parser_state()` function, call before each parse
- **Location:** Top of `parse_lilypond_to_data()`
- **Validation:** Re-run tests from Phase 1

**Scenario B: Parser Expands Events Incorrectly**
- **Fix:** Modify event creation logic to preserve original durations
- **Alternative:** Add `original_duration` field to events for metadata
- **Validation:** Check that `sum(event['ql'])` matches expected bars × time_sig

**Scenario C: Rest Padding is Broken**
- **Fix:** Improve rest padding logic in score_builder.py
- **Check:** Section mismatch warnings in blueprint assembly
- **Validation:** Ensure auto-rests fill to max_duration, not arbitrary amounts

**Scenario D: Multiple Issues**
- **Strategy:** Fix in order: State → Expansion → Padding
- **Test after each fix**

---

## Deliverables

### Immediate (Phase 1)
- [ ] Run 3 isolation tests
- [ ] Identify if issue is: State pollution, Event expansion, or Rest padding
- [ ] Document findings in this file

### Short-term (Phase 2 + 3)
- [ ] Locate bug in parser source
- [ ] Implement fix
- [ ] Verify fix with ninetyninth.py test case
- [ ] Update .ly header to show correct durations

### Long-term
- [ ] Add parser unit tests to prevent regression
- [ ] Document parser behavior in DOCUMENTATION/
- [ ] Add duration validation to blueprint assembly

---

## Success Criteria

✅ **Parsing THEME_A produces:**
- 11-13 note events (one per written note, ties consolidated)
- 12.0 QL total (4 bars × 3 QL/bar)
- 0 auto-inserted rests (unless explicitly needed for padding)

✅ **Staves stay synchronized:**
- THEME_A (12 QL) + BASS_FIGURE (12 QL) → no mismatch warnings
- Auto-rest padding only used for explicit `r` in blueprint

✅ **.ly header shows accurate metadata:**
- THEME_A (~12.0 QL, ~4.0 bars)
- Matches actual engraved duration

---

## Next Steps

**Execute Phase 1 tests now to identify root cause.**

Once we know whether it's:
1. **State pollution** → Clear state between parses
2. **Event expansion** → Fix event creation logic  
3. **Rest padding** → Improve padding algorithm

We can proceed with the targeted fix.

**User requested:** "Please provide a plan to continue"  
**This is the plan.** Shall I execute Phase 1 tests?
