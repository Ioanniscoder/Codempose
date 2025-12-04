# BLUEPRINT STRING QUICK REFERENCE
Date: October 15, 2025

---

## SYNTAX AT A GLANCE

```python
# 1. Define the layout (which staves/voices)
VOICE_STAVE_DEF = "UpperStaff & LowerStaff"

# 2. Define the content (what plays when)
VOICE_STAVE_DATA = """
    INTRO | THEME  & r;
    r              & INTERMEZZO;
    VARIATION      & HARMONY
"""

# 3. Define the snippets (the musical material)
SNIPPETS = {
    'INTRO': intro_events,
    'THEME': theme_events,
    'VARIATION': variation_events,
    'INTERMEZZO': intermezzo_events,
    'HARMONY': harmony_events,
}

# 4. Build the score
from score_builder import build_score_from_blueprint

score_data = build_score_from_blueprint(
    VOICE_STAVE_DEF,
    VOICE_STAVE_DATA,
    SNIPPETS,
    metadata
)
```

---

## DELIMITER MEANING

| Symbol | Name | Meaning | Example |
|--------|------|---------|---------|
| `;` | Semicolon | Separates **sections** (rows) | `SECTION_1; SECTION_2` |
| `&` | Ampersand | Separates **staves** (columns) | `UPPER & LOWER` |
| `|` | Pipe | Concatenates **snippets** (cells) | `INTRO | THEME` |
| `,` | Comma | Separates **voices** (multi-voice) | `SOP, ALT` |

**Think of it as a musical table:**
- `;` = Next row (next section)
- `&` = Next column (next staff)
- `|` = Join cells (concatenate snippets)
- `,` = Split cell (multiple voices)

---

## EXAMPLES

### **Single Staff**
```python
VOICE_STAVE_DEF = "Piano"
VOICE_STAVE_DATA = "INTRO; VERSE; CHORUS; BRIDGE; OUTRO"
```

### **Two Staves**
```python
VOICE_STAVE_DEF = "UpperStaff & LowerStaff"
VOICE_STAVE_DATA = """
    MELODY & HARMONY;
    VARIATION & r;
    r & BASS_LINE
"""
```

### **SATB (Multi-Voice)**
```python
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
VOICE_STAVE_DATA = """
    SOP_THEME, ALT_THEME & TEN_THEME, BAS_THEME;
    SOP_VAR, ALT_VAR & TEN_VAR, BAS_VAR
"""
```

### **String Quartet (Four Staves)**
```python
VOICE_STAVE_DEF = "Violin1 & Violin2 & Viola & Cello"
VOICE_STAVE_DATA = """
    VLN1_A & VLN2_A & VLA_A & VC_A;
    VLN1_B & VLN2_B & VLA_B & VC_B
"""
```

### **Snippet Concatenation**
```python
VOICE_STAVE_DATA = """
    INTRO | THEME_A | THEME_B | CODA & r
"""
# Upper plays INTRO, then THEME_A, then THEME_B, then CODA
# Lower rests throughout
```

---

## SPECIAL TOKENS

### **`r` = Automatic Rest**

When you use `'r'` in the blueprint, the framework:
1. Calculates the duration of all other active staves in that section
2. Generates whole-bar rests (r1) matching that duration
3. Adds barlines automatically

```python
VOICE_STAVE_DATA = "THEME_A & r"
# If THEME_A is 16 QL (4 bars), lower staff gets:
# r1 r1 r1 r1 (4 whole-bar rests)
```

### **Comments**

Use `#` for comments in blueprint strings:

```python
VOICE_STAVE_DATA = """
    # Introduction
    INTRO & r;
    
    # Main theme with harmony
    THEME & HARMONY;
    
    # Development
    VARIATION_1 | VARIATION_2 & r
"""
```

---

## READING BLUEPRINT STRINGS

Think of the string as a **score table**:

```python
VOICE_STAVE_DATA = """
    INTRO | THEME  & HARMONY_A | HARMONY_B;
    VARIATION      & r;
    r              & BASS_LINE
"""
```

Reads as:

| Section | UpperStaff | LowerStaff |
|---------|------------|------------|
| 1 | INTRO then THEME | HARMONY_A then HARMONY_B |
| 2 | VARIATION | (rest) |
| 3 | (rest) | BASS_LINE |

---

## VALIDATION

The framework validates your blueprint and provides clear error messages:

### **Staff Count Mismatch**
```python
VOICE_STAVE_DEF = "Upper & Lower"
VOICE_STAVE_DATA = "THEME"  # ❌ Missing &
```
```
ValueError: Section 1 has 1 staff but layout defines 2 staves.
```

### **Missing Snippet**
```python
SNIPPETS = {'THEME_A': [...]}
VOICE_STAVE_DATA = "THEME_B & r"  # ❌ THEME_B not defined
```
```
KeyError: Snippet 'THEME_B' not found.
Available: ['THEME_A']
```

### **Voice Count Mismatch**
```python
VOICE_STAVE_DEF = "(Soprano, Alto) & Bass"
VOICE_STAVE_DATA = "SOP_THEME & BASS_THEME"  # ❌ Missing comma for Alto
```
```
ValueError: Staff 1 has 2 voices but provides 1
Expected: ['Soprano', 'Alto']
```

---

## COMMON PATTERNS

### **Alternating Sections**
```python
VOICE_STAVE_DATA = """
    MELODY_A & r;
    r & HARMONY_A;
    MELODY_B & r;
    r & HARMONY_B
"""
```

### **Gradual Build-Up**
```python
VOICE_STAVE_DATA = """
    MELODY & r & r;
    MELODY & HARMONY & r;
    MELODY & HARMONY & BASS
"""
```

### **Call and Response**
```python
VOICE_STAVE_DATA = """
    CALL_1 & r;
    r & RESPONSE_1;
    CALL_2 & r;
    r & RESPONSE_2
"""
```

---

## INTEGRATION WITH TRANSFORMATIONS

Transformations are applied **before** the blueprint:

```python
from transformations import transpose_part, invert_part

# Generate variations
theme_transposed = extract_data_from_part(transpose_part(theme_part, 'P5'))
theme_inverted = extract_data_from_part(invert_part(theme_part, 'C4'))

# Use in blueprint
SNIPPETS = {
    'THEME': theme_events,
    'THEME_TRANSPOSED': theme_transposed,
    'THEME_INVERTED': theme_inverted,
}

VOICE_STAVE_DATA = """
    THEME & r;
    THEME_TRANSPOSED & r;
    THEME_INVERTED & r
"""
```

---

## FILES

- **`score_builder.py`** - Blueprint framework implementation
- **`thirteenth.py`** - Example usage (refactored study file)
- **`BLUEPRINT_STRING_FRAMEWORK_V2.md`** - Complete specification
- **`BLUEPRINT_IMPLEMENTATION_COMPLETE.md`** - Implementation summary

---

## STATUS

✅ **Production Ready**

- Implemented: October 15, 2025
- Validated: thirteenth.py generates identical output
- Code Reduction: 77% (130 lines → 30 lines)
- Supports: 1-N staves, single/multi-voice, automatic rests

---

## NEXT STEPS

1. ✅ **COMPLETE:** Blueprint framework working
2. ⏳ **OPTIONAL:** Migrate other study files (eleventh.py, second.py)
3. ⏳ **READY:** Begin Tonal Harmony Roadmap (Step 3 of user plan)
