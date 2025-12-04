# Explicit Mark Override - Implementation Complete

**Date:** October 20, 2024  
**Feature:** Allow explicit `\mark` directives in snippets to override automatic mark injection  
**Status:** ✅ COMPLETE AND TESTED

## Summary

The Codempose framework now supports a three-tier hierarchy for rehearsal marks:

1. **Explicit mark** (highest priority): `\mark` directive in snippet source
2. **Automatic mark** (medium priority): Generated from naming convention `PREFIX_SUFFIX`
3. **No mark** (lowest priority): Transformations, repeats, or no underscore in name

## What Changed

### Files Modified

1. **`studies/ninetyninth.py`**
   - Added `'original_snippets': snippets_to_parse` to metadata dict
   - Modified THEME_A_LILY to include explicit mark: `\mark \markup { \bold \box "Main Theme" }`
   - **Result:** System detects explicit mark and skips auto-injection

2. **`src/score_builder.py`**
   - Added `snippet_contains_explicit_mark(lily_string)` function
   - Modified mark injection logic to check for explicit marks
   - Removed debug print statements
   - **Result:** Automatic `\mark "A"` NOT injected for THEME_A

3. **`generate_study.py` (template)**
   - Added `'original_snippets': snippets_to_parse` to metadata example
   - Added documentation comments explaining mark override feature
   - **Result:** Future studies will have override capability by default

4. **`DOCUMENTATION/SNIPPET_MARKS_COMPLETE.md` (NEW)**
   - Comprehensive feature documentation
   - Usage examples for automatic, explicit, and mixed scenarios
   - Migration guide for existing studies
   - Troubleshooting section

## Implementation Details

### Detection Function
```python
def snippet_contains_explicit_mark(lily_string: str) -> bool:
    """Check if snippet already contains a \\mark directive."""
    # Remove comments to avoid false positives
    cleaned = re.sub(r'%.*$', '', lily_string, flags=re.MULTILINE)
    
    # Match: \mark "text" | \mark \default | \mark \markup { ... }
    pattern = r'\\mark\s+(".*?"|\\\w+)'
    
    return bool(re.search(pattern, cleaned))
```

### Metadata Flow
```python
# Study file (ninetyninth.py)
snippets_to_parse = {
    'THEME_A': THEME_A_LILY,  # Contains explicit \mark
    'THEME_B': THEME_B_LILY,  # No explicit mark
}

metadata = {
    'title': TITLE,
    # ... other fields ...
    'original_snippets': snippets_to_parse,  # ← CRITICAL: Pass original LilyPond
}

# Blueprint assembly (score_builder.py)
snippet_lily = metadata['original_snippets'].get(snippet_name, '')
has_explicit_mark = snippet_contains_explicit_mark(snippet_lily)

if has_explicit_mark:
    print(f"🔒 Snippet '{snippet_name}' has explicit \\mark - skipping auto-inject")
elif mark_text:
    # Inject automatic mark
    mark_event = {'type': 'text_mark', 'text': mark_text, 'ql': 0.0}
```

## Test Results

### ninetyninth.py Output
```
Section 1:
    🔒 Snippet 'THEME_A' has explicit \mark - skipping auto-inject
    Melody: +THEME_A (45 events)

Section 3:
    Melody: +THEME_B (5 events)
    # Automatic \mark "B" injected (no console message for auto-marks)
```

### Generated LilyPond
```lilypond
% Line 105 in outputs/ninetyninth.ly
\mark "B" g'4 d'1 e'4 fis'4 g'2.
```

### PDF Verification
- **Section 1 (THEME_A):** No automatic `\mark "A"` (explicit mark took precedence)
- **Section 3 (THEME_B):** Shows `\mark "B"` (automatic injection)
- **File size:** 102K (successfully compiled)

## Edge Cases Handled

1. ✅ **Comments with "\mark" keyword:** Regex ignores `% \mark` in comments
2. ✅ **Missing original_snippets:** `metadata.get('original_snippets', {})` returns empty dict
3. ✅ **Snippet not in original_snippets:** `has_explicit_mark = False` (safe default)
4. ✅ **Empty snippet string:** `if snippet_lily else False` prevents errors
5. ✅ **Multiple mark styles:** Pattern matches `"text"`, `\default`, `\markup { ... }`

## Known Limitations

### Parser Does Not Extract Explicit Marks
- **Current Behavior:** Parser (`parse_lilypond_to_data()`) ignores `\mark` directives
- **Workaround:** Explicit marks must remain in original snippet source
- **Impact:** Marks appear in PDF but not as events in `SNIPPETS` dict
- **Future:** Could add mark parsing to extract as `{'type': 'text_mark', ...}` events

### Metadata Timing Dependency
- **Requirement:** `original_snippets` must be in metadata BEFORE `build_score_from_blueprint()`
- **Reason:** Blueprint assembly needs original LilyPond strings for detection
- **Solution:** Template updated to include `original_snippets` in metadata dict
- **Migration:** Existing studies need one-line addition (see docs)

## Integration with Existing Features

### Works With:
- ✅ Barline-based duration calculation (`calculate_snippet_duration_from_barlines`)
- ✅ Time signature-aware rest padding
- ✅ Underscore naming convention (`get_snippet_mark_text`)
- ✅ Multi-staff scores (marks on top staff only)
- ✅ Blueprint transformations (`transpose_part`, `invert_part`)
- ✅ Repetition syntax (`THEME_A * 2`)

### Compatible With:
- ✅ All LilyPond markup commands: `\bold`, `\box`, `\italic`, `\large`, etc.
- ✅ Numbered marks: `\mark \default` (auto-increment)
- ✅ Custom text: `\mark "Coda"`, `\mark "D.S."`
- ✅ Complex formatting: `\markup { \column { "Line 1" "Line 2" } }`

## Usage Recommendation

**Use automatic marks for:**
- Standard section labels (A, B, C, ...)
- Numbered sections (1, 2, 3, ...)
- Simple descriptive labels (Intro, Verse, Chorus)

**Use explicit marks for:**
- Custom formatting (bold, boxed, large text)
- Special instructions (D.C., D.S., Coda)
- Multi-line markup
- Non-standard positioning

## Migration Checklist

For existing studies to gain explicit mark override capability:

- [ ] Add `original_snippets` to metadata dict
- [ ] Pass `snippets_to_parse` dictionary to metadata
- [ ] Verify placement BEFORE `build_score_from_blueprint()` call
- [ ] Test: Snippet with explicit mark should print `🔒 ... skipping auto-inject`
- [ ] Test: Snippet without explicit mark should get automatic mark
- [ ] Regenerate PDF and verify marks appear correctly

## Next Steps

### Completed ✅
- [x] Barline-based duration calculation
- [x] Time signature-aware rest padding
- [x] Automatic mark injection from naming convention
- [x] Explicit mark override detection
- [x] Template updates
- [x] Comprehensive documentation

### Potential Future Enhancements
- [ ] Parse `\mark` directives into events (requires parser update)
- [ ] Support mark positioning attributes (`\mark \halign #2 "Text"`)
- [ ] Add mark preview in console output (show detected marks)
- [ ] Create visual guide showing mark hierarchy
- [ ] Add unit tests for `snippet_contains_explicit_mark()`

## References

- **Design Document:** `DOCUMENTATION/EXPLICIT_MARK_OVERRIDE.md`
- **Complete Guide:** `DOCUMENTATION/SNIPPET_MARKS_COMPLETE.md`
- **Test File:** `studies/ninetyninth.py`
- **Template:** `generate_study.py`
- **Implementation:** `src/score_builder.py::snippet_contains_explicit_mark()`
