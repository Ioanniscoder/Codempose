# Blueprint String Framework Restoration Plan

## Executive Summary

The **Blueprint String Framework** (with `VOICE_STAVE_DEF` header and `VOICE_STAVE_DATA` content) was the elegant "non-Python-like" shorthand developed for Codempose. It was successfully used in studies 13-14 but mysteriously disappeared from the default templates in studies 18+.

**The Framework is NOT lost** - it still exists in `score_builder.py` and works perfectly. We just need to restore it as the **default/recommended composition method**.

---

## What is the Blueprint String Framework?

### The Original Vision (Studies 13-14)

```python
# HEADER: Define staff layout
VOICE_STAVE_DEF = "UpperStaff & LowerStaff"

# DATA: Define what each staff plays in each section
VOICE_STAVE_DATA = """
    THEME_A & r;
    r & INTERMEZZO;
    THEME_A_TRANSPOSED & r;
    r & INTERMEZZO;
    THEME_A_INVERTED & r
"""

# BUILD: One function call
score_data = build_score_from_blueprint(
    VOICE_STAVE_DEF,
    VOICE_STAVE_DATA,
    SNIPPETS,
    metadata
)
```

### Delimiters (The "Musical Language")

- `;` (semicolon) = **Section separator** (like double barlines)
- `&` (ampersand) = **Staff separator** (vertical stacking)
- `|` (pipe) = **Snippet concatenator** (horizontal "then")
- `,` (comma) = **Voice separator** (multi-voice staves)
- `'r'` = **Auto-rest placeholder** (matches other staff durations)

### Multi-Voice Example (Study 14)

```python
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"

VOICE_STAVE_DATA = """
    SOPRANO_A, ALTO_A & TENOR_A, BASS_A;
    SOPRANO_B, ALTO_B & TENOR_B, BASS_B
"""
```

**This is much clearer than nested Python dictionaries!**

---

## Problem Analysis

### What Happened?

Studies 13-14 used Blueprint Strings successfully, but:

1. **Study 15-17**: Shifted focus to harmonic analysis features (no shorthand at all)
2. **Study 18+**: Template reverted to Python dict-based `SHORTHAND_ASSIGNMENTS`
3. **generate_study.py**: Uses dict-based approach as default template
4. **CODEMPOSE_STUDY_TEMPLATES.py**: Has NO Blueprint Strings template

### Current State

| Component | Blueprint Strings Support | Status |
|-----------|---------------------------|--------|
| `score_builder.py` | ✅ Full implementation | **Active, working** |
| Studies 13-14 | ✅ Uses successfully | **Proven working** |
| Studies 18, 20 | ❌ Uses dict approach | Commented alternatives |
| `generate_study.py` | ❌ Missing from template | **Needs restoration** |
| `CODEMPOSE_STUDY_TEMPLATES.py` | ❌ No template | **Needs addition** |
| `composition_shorthand.py` | ⚠️ No documentation | **Needs docs** |

---

## Restoration Plan

### Phase 1: Template Creation ✅ (Ready to execute)

**File**: `CODEMPOSE_STUDY_TEMPLATES.py`

**Action**: Add new `TEMPLATE_BLUEPRINT` showing:
- Simple two-staff example with VOICE_STAVE_DEF/DATA
- Multi-voice example (SATB style)
- Transformations integrated with snippets library
- Clear delimiter usage examples

### Phase 2: Default Template Update ✅ (Ready to execute)

**File**: `generate_study.py`

**Changes**:
1. Replace `STUDY_TEMPLATE` with Blueprint Strings approach
2. Move current dict-based approach to "APPROACH 3: Composition Shorthand (Uncomment)"
3. Make Blueprint Strings the **APPROACH 1** default
4. Update docstrings to explain delimiter syntax

**Before** (current):
```python
# APPROACH 1: Simple Single Melody
melody_data = parse_lilypond_to_data(MELODY_LILY)
```

**After** (restored):
```python
# APPROACH 1: Blueprint Strings (Recommended)
VOICE_STAVE_DEF = "Melody & Bass"
VOICE_STAVE_DATA = """
    INTRO & r;
    THEME & HARMONY;
    THEME_TRANSPOSED & HARMONY
"""
score_data = build_score_from_blueprint(...)
```

### Phase 3: Documentation Enhancement ✅ (Ready to execute)

**File**: `composition_shorthand.py`

**Action**: Add module-level docstring section:

```python
"""
COMPOSITION METHODS IN CODEMPOSE
=================================

METHOD 1: Blueprint Strings (RECOMMENDED for composers)
--------------------------------------------------------
The most intuitive, non-Python-like approach:

    VOICE_STAVE_DEF = "Melody & Bass"
    VOICE_STAVE_DATA = "INTRO & HARMONY; THEME & r"
    
    score_data = build_score_from_blueprint(
        VOICE_STAVE_DEF, VOICE_STAVE_DATA, SNIPPETS, metadata
    )

See: score_builder.py, studies/thirteenth.py, studies/fourteenth.py


METHOD 2: Dictionary-Based Shorthand (for programmers)
-------------------------------------------------------
Python-dict approach with transformation support:

    VOICE_ASSIGNMENTS = {
        'Melody': {'Soprano': 'THEME + transpose(THEME, 5)'},
        'Bass': {'Bass': 'HARMONY * 2'}
    }
    
    score_data = build_score_from_assignments(
        VOICE_ASSIGNMENTS, voice_data, metadata
    )

See: composition_shorthand.py (this file)


METHOD 3: Direct LilyPond Parsing (simplest)
---------------------------------------------
For single-voice or simple multi-part scores:

    melody_data = parse_lilypond_to_data(MELODY_LILY)
    return {'parts': {'Melody': melody_data['parts']['Part 1']}}


METHOD 4: Programmatic (maximum control)
-----------------------------------------
For complex transformations using music21:

    melody_part = data_to_part(melody_events)
    transformed = transpose_part(melody_part, 'P5')
    return {'parts': {'Melody': part_to_data(transformed)}}


RECOMMENDATION
--------------
Use Blueprint Strings (Method 1) unless you need:
- Complex conditional logic → Method 4 (Programmatic)
- Inline transformations in expressions → Method 2 (Dict-based)
"""
```

### Phase 4: Example Study Creation ✅ (Ready to execute)

**File**: `studies/twentyfirst.py` (or similar)

**Purpose**: Comprehensive Blueprint Strings showcase demonstrating:
1. Simple two-staff layout
2. Multi-voice SATB layout
3. All delimiters in action
4. Auto-rest generation
5. Snippet concatenation with `|`
6. Transformations integrated with snippets

### Phase 5: Project Documentation ✅ (Ready to execute)

Create or update:
- `docs/COMPOSITION_METHODS.md` - Full guide comparing all 4 methods
- Update main README.md with Blueprint Strings quick start
- Add visual examples of delimiter hierarchy

---

## Implementation Checklist

### Critical Files to Modify

1. **CODEMPOSE_STUDY_TEMPLATES.py**
   - [ ] Add `TEMPLATE_BLUEPRINT` with clear examples
   - [ ] Add delimiter reference guide
   - [ ] Show single-staff and multi-voice patterns

2. **generate_study.py**
   - [ ] Replace `STUDY_TEMPLATE` with Blueprint approach
   - [ ] Add VOICE_STAVE_DEF and VOICE_STAVE_DATA variables
   - [ ] Update imports to include `build_score_from_blueprint`
   - [ ] Move dict-based approach to commented section

3. **composition_shorthand.py**
   - [ ] Add comprehensive module docstring comparing methods
   - [ ] Add "When to use Blueprint Strings" section
   - [ ] Add cross-references to score_builder.py

4. **studies/twentyfirst.py** (new file)
   - [ ] Create comprehensive Blueprint Strings example
   - [ ] Document all delimiter types
   - [ ] Show transformation integration
   - [ ] Include both simple and complex layouts

5. **Documentation**
   - [ ] Create `docs/BLUEPRINT_STRINGS_GUIDE.md`
   - [ ] Update README.md quick start
   - [ ] Add examples to main docs

---

## Why This Matters

### Composer-First Philosophy

The Blueprint String Framework embodies the **composer-first** design:

1. **Readable**: Looks like musical structure, not code
2. **Declarative**: "What" not "how"
3. **Visual**: Layout mirrors score structure
4. **Intuitive**: Delimiters have musical meaning
5. **Powerful**: Handles complex multi-voice arrangements

### Comparison

**Blueprint Strings** (Composer-friendly):
```python
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
VOICE_STAVE_DATA = """
    INTRO, r & r, INTRO_BASS;
    THEME_A, THEME_A_ALTO & THEME_A_TENOR, THEME_A_BASS;
    THEME_B, THEME_B_ALTO & THEME_B_TENOR, THEME_B_BASS
"""
```

**Dict-Based Shorthand** (Programmer-friendly):
```python
VOICE_ASSIGNMENTS = {
    'Staff1': {
        'Soprano': 'INTRO + THEME_A + THEME_B',
        'Alto': 'r + THEME_A_ALTO + THEME_B_ALTO',
    },
    'Staff2': {
        'Tenor': 'r + THEME_A_TENOR + THEME_B_TENOR',
        'Bass': 'INTRO_BASS + THEME_A_BASS + THEME_B_BASS',
    }
}
```

**The Blueprint version is:**
- Shorter (less repetition)
- More visual (sections are obvious)
- Less nested (flatter structure)
- More musical (delimiters = musical concepts)

---

## Technical Details

### score_builder.py Functions (Already Working!)

```python
# Main function
build_score_from_blueprint(voice_stave_def, voice_stave_data, snippets, metadata)
  ↓
  Calls:
    - parse_voice_stave_def(def_string) → layout structure
    - parse_voice_stave_data(data_string, layout) → content structure
  ↓
  Returns: score_data dict (canonical format)
```

### Supported Features

- ✅ Single-voice staves
- ✅ Multi-voice staves (polyphony)
- ✅ Auto-rest generation with `'r'`
- ✅ Snippet concatenation with `|`
- ✅ Section separation with `;`
- ✅ Staff layout with `&`
- ✅ Voice grouping with `(voice1, voice2)`
- ✅ Duration mismatch warnings
- ✅ Multi-voice section events

### Integration Points

Blueprint Strings work seamlessly with:
- LilyPond parser (for snippets)
- Transformation library (snippets can be transformed)
- Harmonic engine (can harmonize snippets)
- Export pipeline (canonical → all formats)

---

## Success Metrics

After restoration, composers should:

1. **See Blueprint Strings in examples**: First thing in generated studies
2. **Understand delimiter syntax**: Clear documentation everywhere
3. **Choose it by default**: Template makes it obvious
4. **Find working examples**: Studies 13-14 + new example study
5. **Get help when needed**: Comprehensive docs and error messages

---

## Migration Path for Existing Studies

For studies that want to migrate:

1. Identify their structure (single-voice, multi-voice, etc.)
2. Extract snippets into variables (`THEME_A_LILY`, etc.)
3. Define layout: `VOICE_STAVE_DEF = "..."`
4. Define content: `VOICE_STAVE_DATA = """..."""`
5. Replace dict-based code with `build_score_from_blueprint()`

**Example migration** (eighteenth.py):

Before:
```python
score_data = build_score_from_assignments(SHORTHAND_ASSIGNMENTS, voice_data)
```

After:
```python
VOICE_STAVE_DEF = "Soprano & Alto & Tenor & Bass"
VOICE_STAVE_DATA = "MELODY & transpose(MELODY, -5) & HARMONY & BASS"
score_data = build_score_from_blueprint(VOICE_STAVE_DEF, VOICE_STAVE_DATA, SNIPPETS, metadata)
```

---

## Next Steps

**READY TO EXECUTE - NO CODE ANALYSIS NEEDED**

All the code exists and works. We just need to:

1. ✅ Add template to `CODEMPOSE_STUDY_TEMPLATES.py`
2. ✅ Update `generate_study.py` default
3. ✅ Add docs to `composition_shorthand.py`
4. ✅ Create example study
5. ✅ Write comprehensive documentation

**Awaiting your approval to proceed with implementation.**

---

## Questions for Consideration

1. Should we deprecate the dict-based shorthand, or keep both?
   - **Recommendation**: Keep both, but make Blueprint Strings the default

2. Should we migrate existing studies 18, 20?
   - **Recommendation**: No, leave as-is (show evolution). Create new example.

3. Should we add more delimiter types (e.g., for repeats)?
   - **Recommendation**: Later, after Blueprint is established as default

4. Should we create a visual diagram of delimiter hierarchy?
   - **Recommendation**: Yes! Add to documentation

---

## Conclusion

The Blueprint String Framework represents **significant creative work** that should not be lost. It's the most composer-friendly input method in Codempose, and it deserves to be the **standard way of composing**.

**The code exists. It works. We just need to make it visible again.**
