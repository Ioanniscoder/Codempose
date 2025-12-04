# Parser Debug Output Documentation

**Date:** October 20, 2025  
**Feature:** Comprehensive debug output for parser failures  
**Status:** ✅ COMPLETE

## Overview

The parser now generates **comprehensive diagnostic output** whenever parsing fails. This enables rapid identification and fixing of parser bugs without needing to manually instrument code.

## What Triggers Debug Output

Debug output is automatically generated when:
1. **Tokenization fails** (invalid syntax, unexpected characters)
2. **Octave resolution fails** (barline handling, relative pitch errors)
3. **TinyNotation conversion fails** (duration inheritance, tuplet errors)
4. **Transformation fails** (music21 errors, data conversion issues)

## Debug Output Structure

When a parsing failure occurs, you'll see:

```
======================================================================
⚠️  PARSER FAILURE DETECTED
======================================================================
Snippet name: THEME_A
Base name: THEME_A
Is original: True
Is transformation: False

Error type: AttributeError
Error message: 'NoneType' object has no attribute 'lower'

--- Original LilyPond Input ---
\relative c'' {
    \tempo "Allegro"
    d4 fis8 g | a4~ a4
    % Comment with special chars
}
--- End Input (length: 89 chars) ---

--- Attempting Manual Tokenization Debug ---
✓ Tokenization succeeded:
  Directives: {'time': '4/4', 'tempo': 'Allegro'}
  Relative base: c''
  Tokens (7): ['d4', 'fis8', 'g', '|', 'a4~', 'a4']

--- Full Traceback ---
Traceback (most recent call last):
  File "/workspaces/Codempose/src/score_builder.py", line 842, in <lambda>
    snippet_events = _get_or_create_snippet_events(snippet_name, snippets)
  File "/workspaces/Codempose/src/lilypond_parser.py", line 125, in parse_lilypond_to_data
    octave_results = process_relative_sequence(base_pitch, base_octave, parsed_tokens)
  File "/workspaces/Codempose/src/relative_octave_logic.py", line 315, in process_relative_sequence
    if token.pitch_letter.lower() == 'r':
AttributeError: 'NoneType' object has no attribute 'lower'
======================================================================

      ✓ Piano: +THEME_A (BYPASS successful: using original LilyPond)
```

## Using Debug Output to Fix Parser Bugs

### Example: Fixing Barline Handling Bug

**Debug output revealed:**
```
Error type: AttributeError
Error message: 'NoneType' object has no attribute 'lower'

Tokens (7): ['d4', 'fis8', 'g', '|', 'a4~', 'a4']

Traceback:
  File "relative_octave_logic.py", line 315
    if token.pitch_letter.lower() == 'r':
AttributeError: 'NoneType' object has no attribute 'lower'
```

**Diagnosis:**
- Tokenization succeeded (7 tokens including barline `|`)
- Error occurred in `relative_octave_logic.py` line 315
- Barlines have `pitch_letter = None`
- Code tried to call `.lower()` on `None`

**Fix:**
```python
# Add check BEFORE line 315:
elif token.pitch_letter is None:
    # Barlines or unparseable tokens - skip
    results.append((token, 0, False))
```

### Example: Fixing Comment Extraction Bug

**Debug output revealed:**
```
Error type: ValueError
Error message: too many values to unpack (expected 2)

Tokens (33): ['d4', 'fis8', 'g', 'a4', 'C', 'o', 'm', 'm', 'e', 'n', 't', ...]

Traceback:
  File "lily_tokenizer.py", line 145
    for match in pattern.finditer(snippet):
```

**Diagnosis:**
- Tokenization extracted **individual letters** from comments
- Expected ~13 tokens, got 33
- Comments not being stripped before tokenization

**Fix:**
```python
# Add at START of tokenize_body():
note_body = re.sub(r'%.*$', '', note_body, flags=re.MULTILINE)
```

## Key Debug Information Provided

| Field | Purpose | Example |
|-------|---------|---------|
| **Snippet name** | Full snippet reference (may include transformations) | `transpose_part(THEME_A, 'P4')` |
| **Base name** | Base snippet without repetition/transformation | `THEME_A` |
| **Is original** | Whether bypass is possible | `True` / `False` |
| **Error type** | Python exception class | `AttributeError`, `ValueError` |
| **Error message** | Short description | `'NoneType' object has no attribute 'lower'` |
| **Original input** | Exact LilyPond source (if original snippet) | Full snippet text |
| **Tokenization test** | Attempts tokenization in isolation | Shows tokens or tokenization error |
| **Full traceback** | Complete call stack | Shows exact line and file where error occurred |
| **Bypass result** | Whether fallback succeeded | `✓ BYPASS successful` / `❌ COMPLETE FAILURE` |

## Workflow for Parser Updates

When you see parser debug output:

1. **Identify the stage** where failure occurred:
   - ✓ Tokenization succeeded → Error is in octave logic or TinyNotation conversion
   - ✗ Tokenization failed → Error is in tokenizer regex or preamble handling

2. **Read the error type and message**:
   - `AttributeError: 'NoneType'` → Missing null check
   - `ValueError: too many values` → Wrong unpacking assumption
   - `KeyError: 'ql'` → Missing required field in data structure

3. **Examine the traceback**:
   - Note the **exact file and line number**
   - Read the code at that location
   - Understand what assumption was violated

4. **Check the input**:
   - Original LilyPond shows what **should** be parsed
   - Token list shows what **was** extracted
   - Compare to identify discrepancy

5. **Implement fix**:
   - Add null checks for barlines/unparseable tokens
   - Add comment stripping if letters extracted from comments
   - Add duration inheritance if duration missing

6. **Verify fix**:
   - Run study again
   - Should see: `✓ Piano: +THEME_A (13 events)` instead of bypass
   - PDF should have correct transformed notes

## Integration with Bypass Mechanism

The debug output is **integrated with the bypass fallback**:

1. **Parse attempt** → If fails, generates debug output
2. **Bypass attempt** → If original snippet, tries to inject raw LilyPond
3. **Final status** → Shows whether bypass succeeded or complete failure

This means:
- **Parser bugs don't crash the build** (bypass catches them)
- **You still get full diagnostic info** (debug output shows what went wrong)
- **You can fix parser incrementally** (study continues generating PDF via bypass)

## Testing the Debug Output

Use the test script:

```bash
python3 test_parser_debug.py
```

This creates intentionally broken snippets to trigger debug output, demonstrating:
- Full diagnostic information
- Tokenization isolation testing
- Bypass fallback behavior

## Best Practices

### ✅ DO:
- Read debug output carefully before making changes
- Note the **exact line number** from traceback
- Test with simple snippets first (like `THEME_A`)
- Add comments explaining what caused the bug and how fix addresses it

### ❌ DON'T:
- Ignore tokenization success/failure indicator
- Make assumptions about what went wrong without reading traceback
- Fix symptoms without understanding root cause
- Disable debug output (it's essential for maintenance)

## Example Bug Fix Session

**Starting point:** Section 2 showing 15-16 measures instead of 4

**Step 1: Observe debug output**
```
Tokens (33): ['d4', 'fis8', 'g', 'a4', 'C', 'o', 'm', 'm', 'e', 'n', 't', ...]
```
→ **Diagnosis:** Extracting individual letters from comments

**Step 2: Check tokenizer**
```python
# lily_tokenizer.py line 145
pattern = re.compile(r'(?<!\\)[a-gr]')  # Allow-list pattern
```
→ **Problem:** Comments not stripped before tokenization

**Step 3: Add fix**
```python
# Strip comments BEFORE tokenization
note_body = re.sub(r'%.*$', '', note_body, flags=re.MULTILINE)
```

**Step 4: Re-run**
```
✓ Tokenization succeeded:
  Tokens (13): ['d4', 'fis8', 'g8', 'a4', 'a4', 'g4', ...]
✓ Piano: +THEME_A (13 events)
```
→ **Success:** Parser now extracts correct 13 events

## Related Files

- **src/score_builder.py** (lines 851-920) - Debug output generator
- **src/lily_tokenizer.py** - Tokenization logic
- **src/relative_octave_logic.py** - Octave resolution
- **src/lily_to_tiny.py** - TinyNotation conversion
- **test_parser_debug.py** - Test script for debug output
- **debug_transformation.py** - End-to-end transformation tester

## Future Enhancements

Possible improvements:
1. **Token-by-token breakdown** showing where each token came from in input
2. **Regex match visualization** showing what pattern matched what text
3. **State machine trace** for octave resolution showing pitch calculations
4. **Music21 object inspection** for transformation failures

## Conclusion

The comprehensive debug output makes parser updates **fast and reliable**:
- **Before:** Manual print statement insertion, guesswork, trial-and-error
- **After:** Automatic diagnostics, exact error location, clear fix path

This was essential for fixing the cascade of bugs:
1. Comment stripping (revealed by token count mismatch)
2. Barline handling (revealed by NoneType traceback)
3. Duration inheritance (revealed by TinyNotation output)

**Status:** ✅ Production-ready, documented, tested
