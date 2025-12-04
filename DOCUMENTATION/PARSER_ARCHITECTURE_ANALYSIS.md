# Parser Architecture Analysis
**Date:** October 20, 2025  
**Purpose:** Identify upparser vs downparser code for evaluation and fixing

---

## Terminology

- **UPPARSER**: Converts LilyPond strings → music21 objects (or event dicts)
- **DOWNPARSER**: Converts music21 objects (or event dicts) → LilyPond strings

---

## Architecture Map

### 1. UPPARSER Components

#### Primary Upparser: `src/lilypond_parser.py`
**Entry Point:** `parse_lilypond_to_data(lily_string, part_name)`

**Call Chain:**
```
parse_lilypond_to_data()
  ↓
lily_to_tiny_notation()  [from lily_to_tiny.py]
  ↓
tokenize_body()  [from lily_tokenizer.py]
  ↓
parse_token()  [from lily_token_parser.py]
  ↓
Returns: {"metadata": {...}, "parts": {part_name: [events...]}}
```

**Dependencies:**
- `src/lily_to_tiny.py` - Tokenizer and relative octave resolver
- `src/lily_tokenizer.py` - Low-level tokenization
- `src/lily_token_parser.py` - Token parsing (pitch, duration, accidentals)
- `src/relative_octave_logic.py` - Resolves `\relative` notation to absolute octaves

**Output Format:** Event dictionaries
```python
{
    'type': 'note',      # or 'rest', 'chord', 'tuplet'
    'step': 'D',         # Note name (C-G)
    'octave': 6,         # Absolute octave
    'alter': 1,          # Accidental (-1=flat, 0=natural, 1=sharp)
    'ql': 1.0,           # Quarter length
    'original_token': 'd4'
}
```

**Status:** 
- ✅ Implicit duration handling: FIXED (Oct 20, 2025)
- ❌ Metadata tokenization bug: CRITICAL BUG FOUND
  - Tokenizer extracts letters from `\key`, `\time`, `\tempo` commands
  - Example: `\key g \major` → tokens "e", "a" (from k**e**y, m**a**jor)
  - This completely corrupts the parse when metadata is present

---

### 2. DOWNPARSER Components

#### Standalone Downparser: `src/lily_converter.py`
**Entry Point:** `events_to_lily(events, metadata)`

**Functions:**
- `events_to_lily()` - Main converter (events → complete LilyPond snippet)
- `events_to_tinynotation()` - Debug converter (events → TinyNotation for verification)
- `_pitch_to_lily()` - Pitch conversion helper
- `_ql_to_lily_duration()` - Duration conversion helper
- `_add_articulations_and_dynamics()` - Articulation/dynamics attachment

**Output Format:** LilyPond string
```lilypond
\relative c'' { \time 3/4 \key g \major d4 fis8 g a4 }
```

**Status:** ❓ UNKNOWN - Not currently used in production

---

#### Inline Downparser: `src/project_template.py`
**Entry Point:** Embedded in `run_pipeline_from_file()` function

**Location:** Lines 630-700 (approximately)

**Functions:**
- `ql_to_lily_duration_string()` - Duration converter (line 25)
- Inline pitch rendering (lines 655-666)
- Inline chord rendering (lines 630-650)
- **Uses:** `_add_articulations_and_dynamics` from `lily_converter.py`

**Output Format:** LilyPond strings embedded in score template

**Status:** ✅ PRODUCTION CODE - Currently used for all LilyPond output

**Issue:** Duplicate code with `lily_converter.py` - potential maintenance problem

---

### 3. music21 Bridge: `src/music_data.py`

**Purpose:** Converts between event dicts and music21 objects

**Functions:**
- `data_to_part(events, metadata)` - Events → music21.Part
- `extract_data_from_part(part, token_infos)` (alias: `part_to_data()`) - music21.Part → Events

**Status:** ✅ WORKING CORRECTLY
- Verified with transformation test (Oct 20, 2025)
- Pitches and durations preserved correctly through music21
- **Does NOT extract barlines/measures** - only notes and rests

---

## Current Bugs

### Bug #1: Implicit Duration Handling ✅ FIXED
**Location:** `src/lilypond_parser.py` - `_parse_duration_to_ql()`

**Issue:** Parser didn't inherit durations from previous notes when duration omitted

**Example:**
```lilypond
d4 fis8 g    % 'g' should inherit eighth note duration from 'fis8'
```

**Before Fix:** `g` parsed as quarter note (1.0 QL)  
**After Fix:** `g` correctly parsed as eighth note (0.5 QL)

**Fix Applied:** Added `last_ql` parameter and state tracking (Oct 20, 2025)

---

### Bug #2: Metadata Tokenization ❌ CRITICAL
**Location:** `src/lily_to_tiny.py` (tokenizer)

**Issue:** Tokenizer extracts individual letters from metadata commands and treats them as notes

**Example:**
```lilypond
\relative c'' {
    \key g \major
    \time 3/4
    d4 fis8 g
}
```

**Tokens Generated:**
```
0: orig="e" conv="e''4"      ← From k**e**y
1: orig="d" conv="d''4"      ← From  **d** (random?)
2: orig="a" conv="a'4"       ← From m**a**jor
3: orig="e" conv="e'4"       ← From tim**e**
4: orig="d4" conv="d'4"      ← ACTUAL NOTE (finally!)
5: orig="fis8" conv="f#'8"   ← ACTUAL NOTE
6: orig="g" conv="g'8"       ← ACTUAL NOTE
```

**Result:** First 4 events are garbage (E6, D6, A5, E5), completely wrong pitches

**Impact:** 
- **Bypass mechanism works** - injects original LilyPond directly, avoids parser
- **Transformations FAIL** - must go through parse → music21 → transform → downparse chain

**Test Results:**
- Simple snippet (no metadata): ✅ D6, F#6, G6 (correct)
- With metadata: ❌ E6, D6, A5, E5, D5, F#5, G5 (wrong!)

---

## Evaluation Project Structure

To provide a comprehensive evaluation to your supervisor, I recommend:

### Upparser Evaluation Package
**Files:**
```
upparser_evaluation/
├── README.md                    # Explanation of upparser architecture
├── upparser.py                  # Consolidated upparser code
│   ├── parse_lilypond_to_data() # Main entry point
│   ├── _parse_duration_to_ql()  # Duration converter (FIXED)
│   └── ... helper functions
├── upparser_dependencies/
│   ├── lily_to_tiny.py          # Tokenizer (HAS BUG #2)
│   ├── lily_tokenizer.py
│   ├── lily_token_parser.py
│   └── relative_octave_logic.py
├── tests/
│   ├── test_implicit_duration.py     # Bug #1 test (PASSING)
│   ├── test_metadata_tokenization.py # Bug #2 test (FAILING)
│   └── test_transformations.py       # End-to-end test
└── BUG_REPORT.md                # Detailed bug analysis
```

### Downparser Evaluation Package
**Files:**
```
downparser_evaluation/
├── README.md                   # Explanation of downparser architecture
├── downparser_standalone.py    # lily_converter.py (isolated)
├── downparser_inline.py        # Extracted from project_template.py
├── tests/
│   ├── test_pitch_rendering.py
│   ├── test_duration_rendering.py
│   └── test_metadata_rendering.py
└── COMPARISON.md               # Compare standalone vs inline
```

---

## Recommendations

### Immediate Actions

1. **Isolate Upparser** ✅ Easy
   - `lilypond_parser.py` is already isolated
   - Dependencies are clear
   - Bug #1 fixed, Bug #2 identified

2. **Isolate Downparser** ⚠️ Requires extraction
   - `lily_converter.py` exists but UNUSED
   - Production code in `project_template.py` is inline
   - Need to extract and consolidate

3. **Fix Priority**
   - Bug #1: ✅ FIXED
   - Bug #2: ❌ CRITICAL - Requires tokenizer rewrite
   - Downparser: ❓ Status unknown until tested

### Long-term Strategy

1. **Use standalone `lily_converter.py` for all downparsing**
   - Replace inline code in `project_template.py`
   - Single source of truth
   - Easier to test and maintain

2. **Fix tokenizer metadata bug**
   - Rewrite `lily_to_tiny.py` to properly skip/handle metadata
   - Add regex patterns for `\key`, `\time`, `\tempo`, `\mark`
   - Comprehensive test suite

3. **Bypass as temporary solution**
   - Continue using bypass for original snippets
   - Works around both upparser bugs
   - Transformations still broken until Bug #2 fixed

---

## Questions for Supervisor

1. **Should we fix the tokenizer now (major refactor) or defer to Phase 2?**
   - Scope: Complete rewrite of metadata handling
   - Impact: Enables transformations
   - Risk: May introduce new bugs

2. **Should we consolidate downparser code?**
   - Currently duplicated between `lily_converter.py` and `project_template.py`
   - Which implementation is "correct"?
   - Should we test and validate lily_converter.py first?

3. **Evaluation format preference?**
   - Separate packages for up/down parsers?
   - Jupyter notebook for interactive evaluation?
   - Test suite with detailed output?

---

## Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Upparser Core | ✅ Working | Bug #1 fixed |
| Implicit Durations | ✅ Fixed | Oct 20, 2025 |
| Metadata Tokenization | ❌ Broken | Critical bug |
| music21 Bridge | ✅ Working | Verified correct |
| Downparser (standalone) | ❓ Unknown | Exists but unused |
| Downparser (inline) | ✅ Production | Needs consolidation |
| Bypass Mechanism | ✅ Working | Workaround for bugs |
| Transformations | ❌ Broken | Due to Bug #2 |

---

**Next Steps:**
1. Create upparser evaluation package
2. Test and validate lily_converter.py downparser
3. Create downparser evaluation package
4. Submit to supervisor for review

