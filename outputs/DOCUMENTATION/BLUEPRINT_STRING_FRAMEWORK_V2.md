# BLUEPRINT STRING FRAMEWORK v2.0
**Final Design Specification**
Date: October 15, 2025

---

## OVERVIEW

The Blueprint String Framework provides a **musically intuitive shorthand** for defining multi-stave scores. It uses delimiter characters that align with musical concepts:

- **`;` (semicolon)** = Section separator (horizontal time flow)
- **`&` (ampersand)** = Staff separator (vertical stacking)
- **`|` (pipe)** = Measure/snippet concatenation (horizontal within a staff)

This creates a "score table" where composers can visually see the structure.

---

## SYNTAX SPECIFICATION

### 1. VOICE_STAVE_DEF (The Header)

**Purpose:** Define the staves and voice groupings.

**Syntax:**
```
StaffName & StaffName & ...
(Voice1, Voice2) & StaffName & ...
```

**Rules:**
- `&` separates staves (vertical dimension)
- `(Voice1, Voice2)` groups multiple voices on a single staff
- Voice names are arbitrary identifiers (e.g., Soprano, UpperStaff, Melody)

**Examples:**
```python
# Single staff
"Piano"

# Two staves
"UpperStaff & LowerStaff"

# SATB on two staves
"(Soprano, Alto) & (Tenor, Bass)"

# String quartet (4 staves)
"Violin1 & Violin2 & Viola & Cello"
```

---

### 2. VOICE_STAVE_DATA (The Body)

**Purpose:** Define the musical content section-by-section.

**Syntax:**
```
UpperContent & LowerContent;
UpperContent & LowerContent;
...
```

**Delimiter Hierarchy (outermost to innermost):**
1. **`;`** - Splits sections (rows of the table)
2. **`&`** - Splits staves within a section (columns of the table)
3. **`|`** - Concatenates snippets within a staff's part (cells of the table)

**Special Tokens:**
- `r` = Generate rests matching the duration of other active staves
- `SNIPPET_NAME` = Reference to a snippet in the SNIPPETS dictionary
- `SNIPPET_A | SNIPPET_B` = Concatenate multiple snippets

**Multi-Voice Syntax:**
If a staff has multiple voices (defined in header), separate their content with `,`:
```
Voice1Content, Voice2Content
```

**Examples:**
```python
# Simple two-stave, two-section
"""
MELODY_A & HARMONY_A;
MELODY_B & HARMONY_B
"""

# With rests
"""
MELODY & r;
r & BASS_LINE
"""

# With concatenation
"""
INTRO | THEME_A & HARMONY_INTRO | HARMONY_A;
VARIATION_1 | VARIATION_2 & r
"""

# Multi-voice (SATB)
"""
SOPRANO_THEME, ALTO_THEME & TENOR_THEME, BASS_THEME;
SOPRANO_VAR, ALTO_VAR & TENOR_VAR, BASS_VAR
"""
```

---

## MUSICAL INTERPRETATION

This syntax maps directly to how composers think:

### Reading Like a Score Table

```
Section 1:  INTRO | THEME     &  BASS_PEDAL
Section 2:  VARIATION         &  HARMONY_A | HARMONY_B
Section 3:  r                 &  INTERMEZZO
```

Reads as:
1. **Section 1:** Upper staff plays INTRO then THEME; Lower staff plays BASS_PEDAL
2. **Section 2:** Upper staff plays VARIATION; Lower staff plays HARMONY_A then HARMONY_B
3. **Section 3:** Upper staff rests; Lower staff plays INTERMEZZO

### The `|` as a Musical "Then"

```
THEME_A | THEME_B | CODA
```
= "Play THEME_A, **then** THEME_B, **then** CODA"

This is the **horizontal flow** within a single part.

### The `&` as a Musical "While"

```
MELODY & HARMONY
```
= "Play MELODY **while** HARMONY plays below"

This is the **vertical alignment** of simultaneous staves.

### The `;` as a Musical "Next Section"

```
INTRO & BASS; VERSE & HARMONY
```
= "First section: INTRO over BASS. **Next section:** VERSE over HARMONY"

This is the **temporal progression** through the piece.

---

## IMPLEMENTATION REQUIREMENTS

### Parser Hierarchy

```
parse_blueprint_string(voice_stave_data)
  └─> split by ';' → sections[]
       └─> for each section:
            └─> split by '&' → staff_contents[]
                 └─> for each staff_content:
                      └─> split by '|' → snippet_names[]
                           └─> if multi-voice staff:
                                └─> split by ',' → voice_snippets[]
```

### Data Structure Output

```python
ParsedBlueprint = {
    'layout': [
        ['Soprano', 'Alto'],  # Staff 1 (multi-voice)
        ['Tenor', 'Bass']     # Staff 2 (multi-voice)
    ],
    'sections': [
        {  # Section 1
            'staff_0': {
                'Soprano': ['SOP_INTRO', 'SOP_THEME'],
                'Alto': ['ALT_INTRO', 'ALT_THEME']
            },
            'staff_1': {
                'Tenor': ['r'],
                'Bass': ['r']
            }
        },
        # ... more sections
    ]
}
```

### Rest Generation Logic

When `'r'` is encountered:
1. Calculate total duration of all other active staves in that section
2. Generate rest events matching that duration
3. Use appropriate rest notation (r1, r2, r4, etc.)

---

## ADVANTAGES OF THIS DESIGN

### 1. **Musically Intuitive**
- `|` feels like a barline (horizontal separation)
- `&` feels like stacking staves (vertical alignment)
- `;` feels like a double barline (section break)

### 2. **Visually Clear**
The string itself reads like a table:
```python
VOICE_STAVE_DATA = """
    INTRO | THEME_A  & BASS_INTRO;
    THEME_B          & BASS_THEME;
    r                & INTERMEZZO
"""
```

### 3. **Unambiguous Parsing**
Three distinct delimiters with clear hierarchy prevents parsing conflicts.

### 4. **Flexible**
Works for:
- Single staff: Just content, no `&` needed
- Two staves: `Upper & Lower`
- Multi-voice: `(Sop, Alt) & (Ten, Bas)` with `SopContent, AltContent & TenContent, BasContent`
- Complex scores: Any number of staves

### 5. **Fast to Write**
Minimal syntax overhead. Compare:

**Old (75 lines):**
```python
upper_intro = melody_intro_events
upper_theme = melody_theme_events
lower_intro_rests = create_bar_rests(...)
# ... 70 more lines
```

**New (8 lines):**
```python
VOICE_STAVE_DEF = "UpperStaff & LowerStaff"
VOICE_STAVE_DATA = """
    INTRO | THEME  & r;
    r              & INTERMEZZO
"""
```

---

## EDGE CASES & RULES

### Whitespace Handling
- Strip leading/trailing whitespace from all parsed tokens
- Ignore blank lines in VOICE_STAVE_DATA
- Comments with `#` should be stripped before parsing

### Empty Sections
```python
# This is valid (empty section = measure of rest)
"""
THEME & HARMONY;
;
CODA & BASS
"""
```

### Mismatched Staff Counts
```python
# ERROR: Header defines 2 staves, but section only has 1
VOICE_STAVE_DEF = "Upper & Lower"
VOICE_STAVE_DATA = "THEME"  # Missing '&' separator
```
→ Parser should raise clear error: "Section 1 defines 1 staff but layout requires 2"

### Voice Count Mismatch
```python
# ERROR: Staff 1 has 2 voices but section only provides 1
VOICE_STAVE_DEF = "(Soprano, Alto) & Bass"
VOICE_STAVE_DATA = "THEME & BASS_LINE"  # Soprano/Alto need 2 snippets
```
→ Parser should raise error: "Staff 1 has 2 voices but section only provides 1"

---

## MIGRATION PATH

### Phase 1: Implement Parser
1. Create `parse_voice_stave_def()` function
2. Create `parse_voice_stave_data()` function
3. Create `build_score_from_blueprint()` orchestrator
4. Add comprehensive unit tests

### Phase 2: Refactor thirteenth.py
1. Define VOICE_STAVE_DEF
2. Define VOICE_STAVE_DATA
3. Replace manual assembly with `build_score_from_blueprint()`
4. Validate output matches original

### Phase 3: Migrate Other Studies
1. Refactor eleventh.py (multi-voice showcase)
2. Refactor other complex studies
3. Update documentation

### Phase 4: Add Helpers
1. Auto-alignment helpers (e.g., `align_sections()`)
2. Validation helpers (e.g., `validate_blueprint()`)
3. Duration calculation helpers

---

## VALIDATION CRITERIA

A successful implementation must:

1. ✅ Parse all delimiter levels correctly (`;`, `&`, `|`)
2. ✅ Handle single-staff, two-stave, and N-stave layouts
3. ✅ Support multi-voice staves with comma separation
4. ✅ Generate rests for `'r'` tokens matching section duration
5. ✅ Produce identical musical output to manual assembly
6. ✅ Provide clear error messages for malformed blueprints
7. ✅ Handle whitespace and comments gracefully
8. ✅ Work with all existing transformation functions

---

## EXAMPLE: thirteenth.py Refactored

```python
# ============================================================
# Station 3: SCORE STRUCTURE (Blueprint String v2.0)
# ============================================================

VOICE_STAVE_DEF = "UpperStaff & LowerStaff"

VOICE_STAVE_DATA = """
    # Section 1: Introduction (Upper melody, lower rests)
    MELODY_INTRO | MELODY_THEME_A  &  r;
    
    # Section 2: Intermezzo (Upper rests, lower harmony)
    r  &  INTERMEZZO_PART1 | INTERMEZZO_PART2;
    
    # Section 3: Variation (Upper transposed, lower rests)
    MELODY_THEME_A_TRANSPOSED  &  r;
    
    # Section 4: Finale (Both active)
    MELODY_CODA  &  HARMONY_CODA
"""

SNIPPETS = {
    'MELODY_INTRO': melody_intro_events,
    'MELODY_THEME_A': melody_theme_a_events,
    'MELODY_THEME_A_TRANSPOSED': transpose_part(melody_theme_a_events, 4),
    'MELODY_CODA': melody_coda_events,
    'INTERMEZZO_PART1': intermezzo_part1_events,
    'INTERMEZZO_PART2': intermezzo_part2_events,
    'HARMONY_CODA': harmony_coda_events,
}

# Build the score
score_data = build_score_from_blueprint(
    VOICE_STAVE_DEF,
    VOICE_STAVE_DATA,
    SNIPPETS,
    metadata
)
```

**Result:** 20 lines instead of 95 lines. Crystal clear structure. Identical output.

---

## STATUS

- **Design:** ✅ FINALIZED
- **Parser Implementation:** ⏳ READY TO START
- **Validation:** ⏳ PENDING
- **Migration:** ⏳ PENDING

**Next Step:** Implement the parser functions.
