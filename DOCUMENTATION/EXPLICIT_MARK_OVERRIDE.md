# Explicit Mark Override Design

**Date:** October 20, 2025  
**Feature:** Allow snippets to contain explicit `\mark` directives as override

---

## User Requirement

> "I considered, that the snippets could have a \mark "title" in the snippet. That gives further control. Should this be implemented as an override?"

**Answer:** YES! Explicit marks in snippets override automatic mark injection.

---

## Hierarchy of Mark Placement

### Priority Order (Highest to Lowest):

1. **Explicit `\mark` in snippet** (composer's intent)
   - If snippet contains `\mark`, use it verbatim
   - Skip automatic mark injection
   - Full control over position and formatting

2. **Auto-generated from name** (convention-based)
   - If snippet name has underscore: `THEME_A` → `\mark "A"`
   - Injected at beginning of snippet events
   - Standard boxed format

3. **No mark** (default)
   - Lowercase names without underscore: `bass`
   - Transformations: `transpose_part(...)`
   - Repeats: `THEME_A * 2`

---

## Implementation Strategy

### Detection Phase (During Parsing)

When parsing LilyPond snippets, detect if `\mark` directive exists:

```python
def snippet_contains_explicit_mark(lily_string: str) -> bool:
    """
    Check if snippet already contains a \mark directive.
    
    Examples:
        r'\mark "Intro"' → True
        r'\mark \default' → True
        r'\mark \markup { ... }' → True
        r'd4 e4 f4 g4' → False
    """
    import re
    # Match \mark followed by:
    # - quoted string: \mark "text"
    # - \default: \mark \default
    # - \markup: \mark \markup { ... }
    pattern = r'\\mark\s+(".*?"|\\\w+|\\\markup)'
    return bool(re.search(pattern, lily_string))
```

### Injection Phase (During Assembly)

Skip automatic mark injection if snippet has explicit mark:

```python
# In src/score_builder.py
for snippet_name in snippet_names:
    # Check if snippet has explicit mark
    snippet_lily = metadata.get('original_snippets', {}).get(snippet_name, '')
    has_explicit_mark = snippet_contains_explicit_mark(snippet_lily)
    
    # Only inject automatic mark if:
    # 1. Is top staff
    # 2. Naming convention matches
    # 3. No explicit mark in snippet
    mark_text = get_snippet_mark_text(snippet_name)
    if (is_top_staff and 
        mark_text and 
        not has_explicit_mark and
        snippet_name not in section_marks_added):
        mark_event = {
            'type': 'text_mark',
            'text': mark_text,
            'ql': 0.0
        }
        staff_events.append(mark_event)
        section_marks_added.add(snippet_name)
```

---

## Usage Examples

### Example 1: Explicit Mark with Custom Formatting

```python
INTRO_LILY = r"""
\relative c' {
    \mark \markup { \italic \small "Introduction" }
    c2 d2 e2 f2 |
    g1
}
"""
```

**Result:**
- ✓ Snippet parsed normally
- ✓ `\mark \markup { \italic \small "Introduction" }` appears in LilyPond output
- ✗ No automatic `\mark "INTRO"` injected (overridden)

### Example 2: Explicit Mark with Simple Text

```python
THEME_A_LILY = r"""
\relative c'' {
    \mark "Main Theme"
    d4 e4 f4 g4 |
    a1
}
"""
```

**Result:**
- ✓ `\mark "Main Theme"` appears (not `\mark "A"`)
- Explicit mark overrides naming convention

### Example 3: No Explicit Mark (Uses Convention)

```python
THEME_B_LILY = r"""
\relative c' {
    g4 a4 b4 c'4 |
    d'1
}
"""
```

**Result:**
- ✓ Automatic `\mark "B"` injected at start
- Naming convention applies

### Example 4: Explicit Mark Positioned Mid-Snippet

```python
DEVELOPMENT_LILY = r"""
\relative c'' {
    d4 e4 f4 g4 |
    \mark "Climax"
    a4 b4 c''4 d''4 |
    e''1
}
"""
```

**Result:**
- ✓ `\mark "Climax"` appears mid-snippet (composer's choice)
- ✗ No automatic mark at beginning

### Example 5: Multiple Marks in One Snippet

```python
SONATA_EXPOSITION_LILY = r"""
\relative c' {
    \mark "Exposition"
    c4 d4 e4 f4 |
    g4 a4 b4 c'4 |
    \mark "Bridge"
    d'4 c'4 b4 a4 |
    g1
}
"""
```

**Result:**
- ✓ Both marks appear exactly where placed
- Full composer control over structure

---

## Detection Algorithm Details

### Regex Pattern Breakdown

```python
pattern = r'\\mark\s+(".*?"|\\\w+|\\\markup)'
```

**Matches:**
1. `\mark "Text"` - Quoted string
2. `\mark \default` - Auto-numbering
3. `\mark \markup { ... }` - Complex formatting

**Does NOT match:**
- `mark` (no backslash)
- `% \mark "commented out"`
- `\markup` alone (not following `\mark`)

### Edge Cases

**Case 1: Mark in Comment**
```lilypond
% \mark "This is commented out"
d4 e4 f4 g4
```
**Solution:** Strip comments before checking:
```python
def snippet_contains_explicit_mark(lily_string: str) -> bool:
    # Remove comments first
    import re
    cleaned = re.sub(r'%.*$', '', lily_string, flags=re.MULTILINE)
    pattern = r'\\mark\s+(".*?"|\\\w+|\\\markup)'
    return bool(re.search(pattern, cleaned))
```

**Case 2: Mark with Complex Markup**
```lilypond
\mark \markup { 
    \bold \box { 
        \concat { "A" \small " - Main Theme" }
    }
}
```
**Solution:** Simplified regex matches `\markup` keyword, not full structure

---

## Implementation Checklist

- [ ] Add `snippet_contains_explicit_mark()` utility function
- [ ] Store original snippet LilyPond text in metadata (already done)
- [ ] Modify mark injection to check for explicit marks
- [ ] Test with explicit marks in various positions
- [ ] Document in SNIPPET_MARKS_DESIGN.md
- [ ] Add examples to generate_study.py template

---

## Benefits

1. **Fine-Grained Control**
   - Composer chooses exact position
   - Custom formatting per section
   - Override automatic convention when needed

2. **Flexibility**
   - Simple text: `\mark "A"`
   - Auto-numbering: `\mark \default`
   - Rich formatting: `\mark \markup { \bold \box "Climax" }`

3. **Backward Compatible**
   - Existing snippets without marks → use convention
   - New snippets with marks → use explicit marks
   - Mixed usage allowed

4. **Professional Scores**
   - Match publisher formatting standards
   - Consistent with traditional engraving
   - Full LilyPond feature access

---

## Testing Strategy

### Test 1: Explicit Override
```python
INTRO_LILY = r'\mark "Introduction" c2 d2'
# Expected: \mark "Introduction" appears, no \mark "INTRO"
```

### Test 2: No Explicit Mark
```python
THEME_A_LILY = r'c2 d2 e2 f2'
# Expected: \mark "A" injected automatically
```

### Test 3: Mid-Snippet Mark
```python
DEVELOPMENT_LILY = r'c2 d2 \mark "Climax" e2 f2'
# Expected: \mark "Climax" appears mid-snippet, no auto-injection
```

### Test 4: Complex Markup
```python
CODA_LILY = r'\mark \markup { \italic "Coda" } c1'
# Expected: \markup version appears, no auto-injection
```

---

## Summary

**Explicit marks in snippets override automatic naming convention.**

**Hierarchy:**
1. Snippet contains `\mark` → Use it (full control)
2. Name has underscore → Inject `\mark` (convention)
3. Otherwise → No mark (hidden)

**Detection:** Regex pattern finds `\mark` directives in snippet source  
**Injection:** Skipped if explicit mark detected  
**Benefit:** Best of both worlds - automation + manual override
