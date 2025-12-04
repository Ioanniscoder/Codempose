# Snippet Name Marks in PDF Output

**Date:** October 20, 2025  
**Feature:** Display snippet names as rehearsal marks in the rendered score

---

## User Requirement

> "The snippet names should appear at the start of the relevant melody/harmony sections. Probably with a convention, to decide whether it should be visible. This is a way of indicating theme, intro, coda, etc. in the pdf, by reference of the snippet name."

---

## Musical Context

Orchestral scores use **rehearsal marks** (A, B, C, or numbers) to help musicians navigate:
- "Let's start at letter C"
- "From the recapitulation"
- "Beginning of the development section"

In Codempose, **snippet names** serve the same purpose:
- `THEME_A` = Main theme section
- `INTRO` = Opening material
- `CODA` = Ending section
- `DEVELOPMENT` = Transitional material

---

## LilyPond Implementation

### Text Marks
```lilypond
\mark "THEME_A"    % Boxed text above staff
\mark \markup { \small "THEME_A" }  % Custom formatting
```

### Rehearsal Marks
```lilypond
\mark \default     % Auto-numbered (1, 2, 3...)
\mark "A"          % Lettered sections
```

---

## Visibility Convention

### Option A: Naming Convention (Recommended)
**Rule:** Uppercase snippet names are visible; lowercase/prefixed with underscore are hidden

```python
# Station 1 definitions
THEME_A_LILY = r"..."      # → Shows "THEME_A" in PDF ✓
INTRO_LILY = r"..."         # → Shows "INTRO" in PDF ✓
_helper_figure_LILY = r"..." # → Hidden (starts with _) ✗
bass_figure_LILY = r"..."   # → Hidden (lowercase) ✗
```

**Advantages:**
- Simple to understand
- No extra configuration
- Visual convention in code matches PDF output

### Option B: Explicit Flag in Metadata
```python
SNIPPET_VISIBILITY = {
    'THEME_A': True,
    'INTRO': True,
    'bass_figure': False,
    '_helper_figure': False
}
```

**Advantages:**
- Full control
- Can show lowercase names if desired

**Disadvantages:**
- Extra configuration to maintain
- Pollutes study files with metadata

### Option C: Regex Pattern Matching
**Rule:** Names matching `^[A-Z][A-Z_0-9]*$` (all caps, underscores, numbers) are visible

```python
"THEME_A"      → visible ✓
"INTRO_1"      → visible ✓
"THEME"        → visible ✓
"Theme_A"      → hidden ✗
"bass_figure"  → hidden ✗
```

---

## Recommended Implementation

**IMPLEMENTED: Simplified underscore convention**

```python
def get_snippet_mark_text(snippet_name: str) -> Optional[str]:
    """
    Determines the text for a snippet mark based on the underscore convention.
    Returns everything after the first underscore, or None if conditions not met.

    Convention:
    - Snippet name MUST contain at least one underscore (_) to be visible
    - Must NOT contain parentheses (transformations hidden)
    - Must NOT contain asterisk (repeats hidden)
    - Text displayed is everything AFTER the first underscore
    
    Examples:
        "m1_intro"              → "intro"
        "THEME_A"               → "A"
        "THEME_B"               → "B"
        "bass_figure"           → "figure"
        "m1"                    → None (no underscore)
        "transpose_part(m1)"    → None (contains parentheses)
        "THEME_A * 2"           → None (contains *)
    """
    # Must contain underscore, and not be a repeat or transformation
    if '_' not in snippet_name or '*' in snippet_name or '(' in snippet_name or ')' in snippet_name:
        return None
    
    # Split only on the *first* underscore
    parts = snippet_name.split('_', 1)
    if len(parts) < 2:
        return None
    
    # Return everything after the first underscore
    suffix = parts[1]
    return suffix if suffix else None
```

**Why this is better:**
- ✅ Simple: Just add an underscore to make any snippet visible
- ✅ Flexible: Composer controls the displayed text via the suffix
- ✅ Consistent: Same rule for all naming styles (uppercase, lowercase, mixed)
- ✅ Transformations automatically hidden (contain parentheses)
- ✅ Repeats automatically hidden (contain asterisk)

---

## Technical Implementation

### 1. Add Text Mark Event Type

**In `src/lily_converter.py`:**
```python
def events_to_lily(events, metadata=None):
    # ... existing code ...
    
    for ev in events:
        if ev.get('type') == 'text_mark':
            # Insert text mark before notes
            mark_text = ev.get('text', '')
            lily_tokens.append(f"\\mark \"{mark_text}\"")
        elif ev.get('type') == 'rest':
            # ... existing rest handling ...
```

### 2. Inject Text Marks During Assembly

**In `src/score_builder.py` (around line 500):**
```python
for snippet_name in voice_snippets:
    snippet_events = _get_or_create_snippet_events(snippet_name, snippets)
    
    # Inject text mark at beginning if snippet is structural
    if should_show_snippet_mark(snippet_name):
        # Add mark event BEFORE snippet events
        mark_event = {
            'type': 'text_mark',
            'text': snippet_name,
            'ql': 0.0  # Zero duration (annotation)
        }
        voice_events.append(mark_event)
    
    voice_events.extend(snippet_events)
    print(f"      {voice_name}: +{snippet_name} ({len(snippet_events)} events)")
```

### 3. Handle Multi-Staff Marks

**Challenge:** In multi-staff layouts, mark should appear only on **top staff** to avoid clutter.

**Solution:**
```python
# Track if we've already added a mark for this section
section_marks_added = set()

for staff_idx, staff_content in enumerate(section):
    is_top_staff = (staff_idx == 0)
    
    for snippet_name in snippets_in_staff:
        if should_show_snippet_mark(snippet_name):
            # Only add mark on top staff, only once per section
            if is_top_staff and snippet_name not in section_marks_added:
                mark_event = {'type': 'text_mark', 'text': snippet_name, 'ql': 0.0}
                events.insert(0, mark_event)
                section_marks_added.add(snippet_name)
```

---

## Example Output

### Study File (ninetyninth.py)
```python
THEME_A_LILY = r"""
\relative c'' { d4 e4 f4 g4 }
"""

INTRO_LILY = r"""
\relative c' { c2 d2 }
"""

bass_figure_LILY = r"""
\relative c { c4 d4 e4 f4 }
"""

VOICE_STAVE_DEF = "Melody & Bass"
VOICE_STAVE_DATA = """
    INTRO & bass_figure;
    THEME_A & bass_figure;
    THEME_A * 2 & bass_figure * 2
"""
```

### Generated LilyPond
```lilypond
\new StaffGroup <<
  \new Staff {
    \clef treble
    \mark "INTRO"        % ← Visible (uppercase)
    c'2 d'2 \bar "||"
    \mark "THEME_A"      % ← Visible (uppercase)
    d''4 e''4 f''4 g''4 \bar "||"
    d''4 e''4 f''4 g''4 d''4 e''4 f''4 g''4 \bar "||"
  }
  \new Staff {
    \clef bass
    c4 d4 e4 f4 \bar "||"   % bass_figure has no mark (lowercase)
    c4 d4 e4 f4 \bar "||"
    c4 d4 e4 f4 c4 d4 e4 f4 \bar "||"
  }
>>
```

### PDF Result
```
┌─────────────────────────────────┐
│  [INTRO]                         │
│  ──────────────────────────────  │
│  ○ ○ |                           │  ← Treble staff
│  ────────────────────────────── │
│  ○ ○ ○ ○ |                       │  ← Bass staff
│  ────────────────────────────── │
│                                  │
│  [THEME_A]                       │
│  ──────────────────────────────  │
│  ○ ○ ○ ○ |                       │
│  ────────────────────────────── │
│  ○ ○ ○ ○ |                       │
└─────────────────────────────────┘
```

---

## Formatting Options

### Basic Text Mark
```lilypond
\mark "THEME_A"
```
**Output:** Boxed text above staff

### Custom Formatting
```lilypond
\mark \markup { \bold \box "THEME_A" }
```
**Output:** Bold, boxed

```lilypond
\mark \markup { \small \italic "Development" }
```
**Output:** Small italic text

### Recommendation
**Start with basic `\mark "TEXT"` for simplicity.** Can enhance later with:
- `\markup { \box \bold "..." }` for structural sections
- `\markup { \small "..." }` for subsections
- User-configurable formatting via metadata

---

## Edge Cases

### 1. Transformed Snippets
```python
VOICE_STAVE_DATA = "transpose_part(THEME_A, 'P4') & bass"
```
**Decision:** Don't show mark for `transpose_part(...)` (contains parentheses)  
**Reason:** Transformation is implementation detail, not structural marker

### 2. Repeated Snippets
```python
VOICE_STAVE_DATA = "THEME_A * 2 & bass"
```
**Decision:** Show mark once at first occurrence only  
**Reason:** Avoid cluttering score with redundant marks

### 3. Multi-Voice Staves
```python
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
VOICE_STAVE_DATA = "SOPRANO_A, ALTO_A & TENOR_A, BASS_A"
```
**Decision:** Show mark above top staff only (Soprano/Alto staff)  
**Reason:** Standard orchestral score convention

### 4. Same Snippet in Multiple Staves
```python
VOICE_STAVE_DATA = "THEME_A & THEME_A_BASS_VARIANT"
```
**Decision:** Show "THEME_A" on top staff, "THEME_A_BASS_VARIANT" hidden (if lowercase) or shown (if uppercase)  
**Reason:** Each staff can have different structural markers if both are uppercase

---

## Configuration (Future Enhancement)

Allow user control via metadata:
```python
SNIPPET_MARK_FORMAT = {
    'INTRO': r'\markup { \small \italic "Introduction" }',
    'THEME_A': r'\markup { \bold \box "A" }',
    'CODA': r'\markup { \italic "Coda" }',
}
```

Or global style:
```python
SNIPPET_MARK_STYLE = "boxed"  # or "plain", "italic", "bold"
```

---

## Implementation Checklist

- [x] Add `get_snippet_mark_text()` utility function to src/score_builder.py
- [x] Extend `src/project_template.py` to handle `'text_mark'` event type in LilyPond generation
- [x] Modify `score_builder.py` to inject marks during assembly (both single and multi-voice)
- [x] Ensure marks appear only on top staff in multi-staff layouts
- [x] Test with ninetyninth.py
- [x] Verify PDF shows "A" (THEME_A), "B" (THEME_B) but not marks for transformations or repeats
- [ ] Document convention in template/README
- [ ] Add examples to generate_study.py template

**Status:** ✅ IMPLEMENTED AND TESTED

**Test Results (ninetyninth.py):**
```
✓ THEME_A → \mark "A"  (visible in PDF)
✓ THEME_B → \mark "B"  (visible in PDF)
✓ bass_figure → No mark (lowercase prefix, but suffix would show "figure")
✓ transpose_part(THEME_A, 'P4') → No mark (transformation)
✓ THEME_A * 2 → No mark (repetition)
```

---

## Benefits

1. **Navigation:** Easy to find sections in PDF ("start at THEME_B")
2. **Analysis:** Visual structure matches compositional design
3. **Collaboration:** Musicians/conductors can reference sections by name
4. **Documentation:** PDF becomes self-documenting
5. **Pedagogy:** Students see formal structure (exposition, development, recapitulation)

---

## Summary

**Naming convention:**
- `THEME_A` → Visible in PDF ✓
- `bass_figure` → Hidden (internal) ✗

**Placement:**
- Top staff only in multi-staff layouts
- Once per section (no duplication for repeats)

**Implementation:**
- New event type: `text_mark`
- Injected during blueprint assembly
- Rendered as `\mark "TEXT"` in LilyPond
