# Snippet Rehearsal Marks - Complete Feature Documentation

## Overview

The Codempose framework automatically generates rehearsal marks (section labels) in PDF output based on snippet names, with support for manual override when needed.

## Feature: Automatic Mark Injection

**What it does:** Snippets following the `PREFIX_SUFFIX` naming convention automatically display `\mark "SUFFIX"` at the start of the section in the PDF.

**Examples:**
```python
THEME_A_LILY = r"""..."""        # → Displays \mark "A"
INTRO_Main_LILY = r"""..."""     # → Displays \mark "Main" 
VERSE_1_LILY = r"""..."""        # → Displays \mark "1"
bass_figure_LILY = r"""..."""    # → Displays \mark "figure"
```

**Hidden cases (no mark injected):**
```python
transpose_part(THEME_A, 'P4')    # Contains parentheses → no mark
THEME_A * 2                       # Contains asterisk → no mark
invert_part(MELODY, 'P8')         # Transformation → no mark
```

## Feature: Explicit Mark Override

**What it does:** If a snippet contains an explicit `\mark` directive in the LilyPond source, the automatic mark injection is skipped.

**Priority:** Explicit mark > Auto-generated mark > No mark

**Example:**
```python
THEME_A_LILY = r"""
\relative c'' {
    \key g \major
    \time 3/4
    \mark \markup { \bold \box "Main Theme" }  # ← Explicit mark
    d4 e4 f4 |
    g2.
}
"""
```

**Result:** 
- Automatic `\mark "A"` is **NOT** injected
- The custom `\markup { \bold \box "Main Theme" }` appears in the snippet's original position
- System detects the explicit mark and prints: `🔒 Snippet 'THEME_A' has explicit \mark - skipping auto-inject`

## Implementation Details

### Detection Logic

The system uses regex pattern matching to detect explicit marks:
```python
pattern = r'\\mark\s+(".*?"|\\\w+)'
```

This matches:
- `\mark "A"` (simple string marks)
- `\mark \default` (auto-numbered marks)
- `\mark \markup { ... }` (formatted markup blocks)

### Integration Points

1. **Snippet Definition (Station 1):**
   ```python
   snippets_to_parse = {
       'THEME_A': THEME_A_LILY,
       'THEME_B': THEME_B_LILY,
   }
   ```

2. **Metadata Setup (Before Station 3):**
   ```python
   metadata = {
       'title': TITLE,
       'composer': COMPOSER,
       # ... other fields ...
       'original_snippets': snippets_to_parse,  # ← Required for override detection
   }
   ```

3. **Blueprint Assembly (Station 3):**
   - System checks `metadata['original_snippets']` for each snippet
   - Detects explicit `\mark` using regex
   - Skips auto-injection if explicit mark found
   - Injects `\mark "SUFFIX"` otherwise (if naming convention met)

### Mark Injection Rules

**Condition 1: Top staff only**
- Marks only appear on the first staff of multi-staff scores
- Prevents duplicate marks across piano staves

**Condition 2: Naming convention**
- Name must contain underscore: `PREFIX_SUFFIX`
- Name must NOT contain parentheses or asterisk
- Suffix after first underscore becomes mark text

**Condition 3: No explicit mark**
- Snippet source must NOT contain `\mark` directive
- Override takes precedence

**Condition 4: Once per section**
- Mark injected at start of snippet events
- Not repeated if snippet appears multiple times in same section

## Usage Examples

### Example 1: Full Automatic Marks
```python
# Snippet definitions
INTRO_A_LILY = r"""\relative c' { c4 d e f }"""
VERSE_B_LILY = r"""\relative c' { g4 a b c }"""
CHORUS_C_LILY = r"""\relative c'' { d4 e f g }"""

# Blueprint
VOICE_STAVE_DATA = """
    INTRO_A;
    VERSE_B;
    CHORUS_C
"""

# Result in PDF:
# - Section 1: \mark "A" c d e f
# - Section 2: \mark "B" g a b c  
# - Section 3: \mark "C" d e f g
```

### Example 2: Mixed Automatic and Explicit
```python
# Snippet with explicit mark
THEME_Main_LILY = r"""
\relative c'' {
    \mark \markup { \bold \box "Main Theme" }
    d4 e f g
}
"""

# Snippet with automatic mark
BRIDGE_Development_LILY = r"""
\relative c' {
    c4 d e f
}
"""

# Blueprint
VOICE_STAVE_DATA = """
    THEME_Main;
    BRIDGE_Development
"""

# Result in PDF:
# - Section 1: \markup { \bold \box "Main Theme" } d e f g  (explicit)
# - Section 2: \mark "Development" c d e f  (automatic)
```

### Example 3: Hiding Transformation Marks
```python
MELODY_A_LILY = r"""\relative c' { c4 d e f }"""

VOICE_STAVE_DATA = """
    MELODY_A;
    transpose_part(MELODY_A, 'P5');
    invert_part(MELODY_A, 'P8')
"""

# Result in PDF:
# - Section 1: \mark "A" c d e f  (original gets mark)
# - Section 2: g a b c  (transposition has NO mark)
# - Section 3: c b a g  (inversion has NO mark)
```

## Technical Notes

### Parser Limitations
- **Current:** Explicit `\mark` directives are NOT parsed into event data
- **Detection:** System detects explicit marks in original LilyPond strings
- **Behavior:** Detection prevents automatic injection, but mark must be in snippet source
- **Future:** Parser could extract marks as `{'type': 'text_mark', 'text': '...'}` events

### Metadata Flow
1. Snippets parsed: `LILY → parse_lilypond_to_data() → events`
2. Metadata populated: `metadata['original_snippets'] = snippets_to_parse`
3. Blueprint assembly: `build_score_from_blueprint(snippets, metadata)`
4. Mark detection: Check `original_snippets[name]` for `\mark` pattern
5. Mark injection: Add `text_mark` event if no explicit mark found

### File Locations
- **Detection:** `src/score_builder.py::snippet_contains_explicit_mark()`
- **Extraction:** `src/score_builder.py::get_snippet_mark_text()`
- **Rendering:** `src/project_template.py` (converts text_mark events to LilyPond)
- **Template:** `generate_study.py` (includes setup instructions)

## Migration Guide

### Updating Existing Studies

**Step 1:** Add `original_snippets` to metadata
```python
# Before (old)
metadata = {
    'title': TITLE,
    'composer': COMPOSER,
}

# After (new)
metadata = {
    'title': TITLE,
    'composer': COMPOSER,
    'original_snippets': snippets_to_parse,  # ← Add this line
}
```

**Step 2:** Use naming convention for snippets
```python
# Before: No marks
melody_LILY = r"""..."""
bass_LILY = r"""..."""

# After: Automatic marks
MELODY_A_LILY = r"""..."""  # → \mark "A"
BASS_B_LILY = r"""..."""    # → \mark "B"
```

**Step 3:** Add explicit marks where needed
```python
# For custom formatting
INTRO_Main_LILY = r"""
\relative c'' {
    \mark \markup { 
        \bold \box \large "Introduction" 
    }
    c4 d e f
}
"""
```

## Best Practices

1. **Use descriptive suffixes:** `THEME_Exposition` is clearer than `THEME_A`
2. **Reserve explicit marks for special cases:** Custom formatting, complex markup
3. **Keep transformations unmarked:** Let automatic system hide technical operations
4. **Test mark appearance:** Generate PDF and verify section labels
5. **Document override usage:** Comment why explicit mark needed

## Troubleshooting

**Problem:** Automatic mark not appearing
- Check naming convention: Must have underscore `_`
- Verify not transformation: Remove parentheses/asterisks from name
- Confirm single staff: Marks only on top staff
- Check metadata: Ensure `original_snippets` in metadata dict

**Problem:** Explicit mark not working (automatic mark still appears)
- Verify metadata: `'original_snippets': snippets_to_parse` must be set BEFORE `build_score_from_blueprint()`
- Check mark syntax: Use `\mark \markup { ... }` or `\mark "text"`
- Test detection: Look for `🔒 Snippet has explicit \mark` message in output

**Problem:** Both marks appearing
- Not possible with current implementation
- If you see this, file a bug report

## Related Documentation
- `DOCUMENTATION/BARLINE_BASED_DURATION.md` - Duration calculation
- `DOCUMENTATION/HYBRID_SUFFIX_MODEL.md` - String framework architecture
- `DOCUMENTATION/EXPLICIT_MARK_OVERRIDE.md` - Original design doc
