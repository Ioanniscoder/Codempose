# Parser Bypass Implementation Plan

**Date:** October 20, 2025  
**Status:** 🔧 IMPLEMENTING  
**Goal:** Use original LilyPond snippets directly to bypass parser QL errors

---

## Implementation Strategy

### Where to Implement

**File:** `src/project_template.py`  
**Function:** `engrave_with_abjad()`  
**Location:** Line ~507 (single-voice event processing loop)

### Current Flow (BROKEN)

```
Original Snippet (THEME_A)
    ↓
Parser (lilypond_parser.py) → Creates events with WRONG QL values
    ↓
Event Assembly (score_builder.py) → Collects events (uses wrong QL)
    ↓
Renderer (project_template.py) → Converts events → LilyPond
    ↓
Output: Wrong durations (d'1 in 3/4 time)
```

### New Flow (FIXED)

```
Original Snippet (THEME_A)
    ↓
Parser (lilypond_parser.py) → Creates events (for section tracking only)
    ↓
Event Assembly (score_builder.py) → Marks sections with snippet names
    ↓
Renderer (project_template.py) → Checks if original snippet exists
    ├─ YES → Inject original LilyPond string directly ✅
    └─ NO  → Convert events to LilyPond (transformations)
    ↓
Output: Correct durations for originals
```

---

## Implementation Details

### Step 1: Pass snippet metadata to renderer

**File:** `src/score_builder.py`  
**Action:** Already passing `metadata['original_snippets']` ✅

**Verification:**
```python
# Line ~40 in score_builder.py
metadata.setdefault('original_snippets', {})
if original_snippets:
    metadata['original_snippets'] = original_snippets
```

### Step 2: Track snippet names in events

**Current:** Events have `type`, `ql`, `pitch`, etc.  
**Need:** Events need `snippet_name` field to identify which original snippet they came from

**Modify:** `src/lilypond_parser.py` or `src/score_builder.py`  
**Solution:** Add `snippet_name` to events when parsing original snippets

**Code change in `src/score_builder.py` (around line 700):**
```python
# After parsing snippet
parsed_events = SNIPPETS[snippet_name]

# Tag events with their snippet name (for bypass detection)
for ev in parsed_events:
    ev['snippet_name'] = snippet_name  # NEW FIELD
```

### Step 3: Detect and inject original snippets in renderer

**File:** `src/project_template.py`  
**Function:** `engrave_with_abjad()`  
**Location:** Inside the event processing loop (~line 507)

**Current code:**
```python
for ev in events:
    if ev.get('type') == 'text_mark':
        mark_text = ev.get('text', '')
        part_tokens.append(f"\\mark \"{mark_text}\"")
        continue
    
    ql = ev.get('ql', 1.0)
    dur_str = ql_to_lily_duration_string(ql)
    # ... convert event to LilyPond
```

**New code:**
```python
# Group consecutive events by snippet_name
current_snippet = None
snippet_buffer = []

for ev in events:
    snippet_name = ev.get('snippet_name')
    
    # If snippet changes or is None, flush buffer
    if snippet_name != current_snippet:
        if snippet_buffer:
            # Process buffered events
            _flush_snippet_buffer(
                part_tokens, 
                snippet_buffer, 
                current_snippet, 
                metadata.get('original_snippets', {})
            )
            snippet_buffer = []
        current_snippet = snippet_name
    
    # Buffer this event
    snippet_buffer.append(ev)

# Flush remaining buffer
if snippet_buffer:
    _flush_snippet_buffer(
        part_tokens, 
        snippet_buffer, 
        current_snippet, 
        metadata.get('original_snippets', {})
    )
```

**Helper function:**
```python
def _flush_snippet_buffer(part_tokens, events, snippet_name, original_snippets):
    """
    Process a group of events, using original LilyPond if available.
    """
    # Check if this is an original (non-transformed) snippet
    if snippet_name and snippet_name in original_snippets:
        # BYPASS: Use original LilyPond string directly
        lily_source = original_snippets[snippet_name]
        
        # Extract just the music content (remove \relative c' { ... })
        import re
        match = re.search(r'\\relative\s+[^\{]*\{(.*)\}', lily_source, re.DOTALL)
        if match:
            music_content = match.group(1).strip()
            # Inject directly into output
            part_tokens.append(music_content)
        else:
            # Fallback: convert events
            _convert_events_to_lily(part_tokens, events)
    else:
        # Transformations: convert events (accept minor QL errors)
        _convert_events_to_lily(part_tokens, events)
```

---

## Testing Strategy

### Test 1: Original snippets render correctly

**File:** `studies/ninetyninth.py`  
**Snippets:** `THEME_A`, `bass_figure`, `THEME_B`  
**Expected:**
- THEME_A: `\mark \markup { \bold \box "Main Theme" } e'4 d'4 ...` (exact original)
- bass_figure: `g4 d'4 b4 | c'2 b4 | ...` (exact original)
- THEME_B: `g4( fis e) | d2.~ | d4 e fis | g2.` (NO `d'1` errors!)

### Test 2: Transformations still work

**Blueprint:** `transpose_part(THEME_A, 'P4')`  
**Expected:**
- Uses converted events (may have minor QL issues)
- Still produces valid LilyPond output
- Document limitation in header comment

### Test 3: Barlines and marks preserved

**Expected:**
- 4 barlines per staff (section separators)
- \mark "B" on THEME_B section
- No marks on THEME_A (has explicit mark)

---

## Risks and Mitigation

### Risk 1: Snippet name tracking fails

**Symptom:** All events have `snippet_name=None`  
**Mitigation:** Add debug prints to verify tagging works  
**Fallback:** Events render using old method (no worse than current)

### Risk 2: \relative context breaks

**Symptom:** Wrong octaves when injecting raw LilyPond  
**Mitigation:** Keep \relative wrapper, only inject music content  
**Alternative:** Use absolute pitch notation in injected content

### Risk 3: Transformations break entirely

**Symptom:** Transposed sections render as rests or error out  
**Mitigation:** Keep event conversion path intact for non-original snippets  
**Testing:** Verify seventh.py, tenth.py still render

---

## Success Criteria

✅ THEME_A renders exactly as written (no parser corruption)  
✅ bass_figure renders exactly as written  
✅ THEME_B renders correctly (no `d'1` in 3/4 time)  
✅ Both staves have 4 sections with proper barlines  
✅ Marks appear correctly (\mark "B" on THEME_B only)  
✅ Transformations still produce valid output (documented limitation)  
✅ Existing studies (first.py, seventh.py) don't regress

---

## Next Steps

1. ✅ Create implementation plan (THIS FILE)
2. ⏳ Add `snippet_name` tagging in score_builder.py
3. ⏳ Implement bypass logic in project_template.py
4. ⏳ Test with ninetyninth.py
5. ⏳ Regression test with first.py, seventh.py
6. ⏳ Remove debug instrumentation
7. ⏳ Update documentation

---

## Notes

- This is a **surgical fix** - changes only rendering, not parsing
- Parser still runs (needed for transformations and event counting)
- Original snippets bypass the buggy QL values
- Transformations continue using events (accept minor issues until parser fix)
- Two-phase approach: Bypass now, fix parser later
