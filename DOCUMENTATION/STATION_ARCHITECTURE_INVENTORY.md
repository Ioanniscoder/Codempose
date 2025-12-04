# Station Architecture Inventory & Analysis

**Date:** October 19, 2025  
**Purpose:** Ensure consistent 4-station architecture across all study files

---

## The Canonical Station Model

### ✅ CORRECT ARCHITECTURE (Stations 1-2-3-4)

```python
# ============================================================================
# STATION 1: COMPOSING INPUT (LilyPond Snippets)
# ============================================================================
# Clean musical input - composer's domain
# Variables end with _LILY

THEME_LILY = r"\relative c'' { c4 d4 e4 f4 | g2 f2 }"
BASS_LILY = r"\relative c { c2 g2 | f2 c2 }"


# ============================================================================
# STATION 2: VALIDATING & GENERATED INPUT
# ============================================================================
# TWO FORMATS:
#
# 1. TINYNOTATION (pitch verification - absolute pitches)
# 2. LILYPOND (reusable snippets - ready for composition)
#
# Variables end with _TINY or _LILY

# TinyNotation (pitch verification)
THEME_TINY = None                 # Auto-generated or hand-written
THEME_TRANSPOSED_TINY = None      # Generated from transformations

# LilyPond (reusable snippets)
THEME_TRANSPOSED_LILY = None      # Generated from transformations
THEME_INVERTED_LILY = None        # Generated from transformations


# ============================================================================
# STATION 3: STRUCTURING INPUT (Blueprint Strings)
# ============================================================================
# Declarative score assembly - shorthand composition

VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    THEME & BASS;
    transpose_part(THEME, 'P5') & BASS;
    invert_part(THEME, 'C4') & BASS
"""


# ============================================================================
# STATION 4: PROGRAMMATIC CONTEXT (Full Programming)
# ============================================================================
# Optional custom transformation functions
# This section is ACCESSED via promotion toggling, not required

def custom_transformation(part):
    """Piece-specific logic."""
    return modified_part

# ============================================================================
# PROCESSING ENGINE (Hands-Off)
# ============================================================================

def build_score_data() -> Dict:
    """
    Execute the composition plan.
    
    This function:
    1. Parses Station 1 (LilyPond snippets)
    2. Populates Station 2 (TinyNotation + transformed LilyPond)
    3. Executes Station 3 (Blueprint assembly)
    4. Uses Station 4 (if needed for custom logic)
    """
    # ... implementation ...
```

---

## Current Study File Inventory

### ✅ Files Following Canonical Architecture

#### **test_transformations_blueprint.py**
- ✅ Station 1: LilyPond snippets (THEME_LILY, BASS_LILY)
- ✅ Station 2: TWO FORMATS (THEME_TINY, THEME_TRANSPOSED_LILY, etc.)
- ✅ Station 3: Blueprint Strings (VOICE_STAVE_DEF, VOICE_STAVE_DATA with transformations)
- ✅ Station 4: Implicit (build_score_data() uses library transformations)
- **Status:** ✅ CORRECT - Reference implementation

#### **test_station2_reuse.py**
- ✅ Station 1: LilyPond snippets (THEME_LILY)
- ✅ Station 2: TWO FORMATS (THEME_TINY, THEME_P5_LILY, THEME_P5_TINY, etc.)
- ✅ Station 3: Blueprint Strings (with transformation syntax + cascaded demo)
- ✅ Station 4: Implicit (build_score_data() demonstrates Station 2 population)
- **Status:** ✅ CORRECT - Demonstrates Station 2 workflow

#### **OLD/thirteenth.py**
- ✅ Station 1: LilyPond snippets (THEME_A_LILY, INTERMEZZO_LILY)
- ✅ Station 2: TinyNotation validation (THEME_A_TINY, INTERMEZZO_TINY) + generated placeholders
- ✅ Station 3: Blueprint Strings (VOICE_STAVE_DEF, VOICE_STAVE_DATA)
- ✅ Station 4: Custom transformations (uses transpose_part, invert_part, chordify_part)
- **Status:** ✅ CORRECT - BUT needs TinyNotation for transformed snippets (only has LILY format)
- **Note:** Pre-dates new transformation syntax (uses explicit transformation in build_score_data())

#### **OLD/fourteenth.py**
- ✅ Station 1: LilyPond snippets (SOPRANO_*, ALTO_*, TENOR_*, BASS_*)
- ⚠️ Station 2: Only mentions "Real-time validation" - no explicit variables
- ✅ Station 3: Blueprint Strings (multi-voice: `(Soprano, Alto) & (Tenor, Bass)`)
- ✅ Station 4: None needed (multi-voice demo)
- **Status:** ⚠️ NEEDS UPDATE - Station 2 should have TinyNotation placeholders

---

### ⚠️ Files With Variant Architectures

#### **OLD/twelfth.py**
- ✅ Station 1: LilyPond snippet
- ✅ Station 2: TinyNotation equivalent
- ✅ Station 3: Shorthand structure
- ✅ Station 4: Programmatic generation
- **Status:** ✅ CORRECT - Follows 1-2-3-4 model

#### **OLD/tenth.py**
- ✅ Station 1: LilyPond snippets
- ✅ Station 2: TinyNotation equivalents
- ✅ Station 3: Shorthand structure
- ✅ Station 4: Programmatic generation
- **Status:** ✅ CORRECT - Follows 1-2-3-4 model

#### **OLD/eighteenth.py, twentyth.py, twentyfirst.py**
- ✅ Station 1: LilyPond snippets
- ❌ Station 2: "Programmatic Voice Generation" (WRONG - should be validation!)
- ❌ Station 3: "Composition Shorthand" (CORRECT label but out of order)
- ❌ Station 4: "Harmonic Intelligence" (should be programmatic context)
- ❌ Station 5: "Build Score Data" (should be Station 4!)
- **Status:** ❌ INCORRECT ARCHITECTURE - 5-station model, wrong Station 2

#### **OLD/fifteenth.py, sixteenth.py, seventeenth.py**
- ✅ Station 1: LilyPond snippets
- ✅ Station 2: Real-time validation
- ❌ Station 3: "Harmonic Analysis" or "Harmonization" (should be Blueprint Strings!)
- ❌ Station 4: "Execution" (should be programmatic context)
- **Status:** ❌ INCORRECT - Station 3 is not Blueprint Strings

#### **OLD/ninetyninth.py, 100th.py**
- ✅ Station 1: LilyPond snippets
- ✅ Station 2: Blueprint Strings - structure definition (CORRECT!)
- ⚠️ Station 3: "Build Score Data" (should be Station 4)
- ⚠️ Station 4: "Execution" (should be implicit in Station 4)
- **Status:** ⚠️ CLOSE - Has Blueprint Strings at Station 2, but numbering is off

---

## Omissions Found

### 1. **Missing TinyNotation in Station 2 (Transformed Snippets)**

**Files Affected:**
- `OLD/thirteenth.py` - Has TinyNotation for original snippets, but NOT for transformed ones

**Issue:**
```python
# Current (OLD/thirteenth.py)
THEME_A_TINY = "..."  # ✅ Original has TinyNotation
THEME_A_TRANSPOSED_LILY = None  # ❌ Transformed only has LILY, no TINY

# Should be:
THEME_A_TINY = "..."
THEME_A_TRANSPOSED_TINY = None  # ✅ Add TinyNotation for verification
THEME_A_TRANSPOSED_LILY = None  # ✅ Keep LilyPond for reuse
```

**Why It Matters:**
Without TinyNotation for transformed snippets, composers can't easily verify that octave resolution worked correctly after transformations.

---

### 2. **Station 2 Not Clearly Separated from Build Logic**

**Files Affected:**
- `OLD/fourteenth.py` - Station 2 just says "Real-time validation happens during build_score_data()"
- Most older files - Station 2 variables not clearly marked

**Issue:**
Station 2 should have **explicit placeholder variables** at the top of the file, not just a comment saying "validation happens later."

**Correct Pattern:**
```python
# ============================================================================
# STATION 2: VALIDATING & GENERATED INPUT
# ============================================================================
#
# TinyNotation Validation Strings
SOPRANO_A_TINY = None  # Will be populated during parsing
ALTO_A_TINY = None
TENOR_A_TINY = None
BASS_A_TINY = None

# Generated Snippet Placeholders (if any transformations)
SOPRANO_A_TRANSPOSED_LILY = None
SOPRANO_A_TRANSPOSED_TINY = None
```

---

### 3. **Transformation Syntax Not Used in Old Files**

**Files Affected:**
- `OLD/thirteenth.py` - Uses explicit transformation code in `build_score_data()`

**Old Approach:**
```python
# Station 3
VOICE_STAVE_DATA = """
    THEME_A & r;
    THEME_A_TRANSPOSED & r;  # ← Pre-computed snippet name
"""

# Station 4 (build_score_data)
theme_a_transposed_part = transpose_part(theme_a_part, 'P5')  # ← Explicit code
theme_a_transposed = extract_data_from_part(theme_a_transposed_part)
SNIPPETS['THEME_A_TRANSPOSED'] = theme_a_transposed
```

**New Approach (Canonical):**
```python
# Station 3
VOICE_STAVE_DATA = """
    THEME_A & r;
    transpose_part(THEME_A, 'P5') & r;  # ← Transformation IN blueprint
"""

# Station 4 (build_score_data)
# Transformations happen automatically in framework!
score_data = build_score_from_blueprint(...)
# Just populate Station 2 with results
THEME_A_TRANSPOSED_LILY = events_to_lily(SNIPPETS["transpose_part(THEME_A, 'P5')"], ...)
```

**Why It Matters:**
The new syntax makes transformations **visible in the blueprint** (Station 3), keeping Station 4 clean and declarative.

---

### 4. **5-Station Architecture in Some Files**

**Files Affected:**
- `OLD/eighteenth.py`, `twentyth.py`, `twentyfirst.py`

**Issue:**
These files have **5 stations** with a confusing model:
- Station 2: "Programmatic Voice Generation" ❌ (should be validation!)
- Station 5: "Build Score Data" ❌ (should be part of Station 4!)

**Correct Model:**
Only **4 stations**:
1. Input (LilyPond)
2. Validation/Generated (TinyNotation + transformed snippets)
3. Structure (Blueprint Strings)
4. Programmatic Context (optional custom code)

Processing engine (`build_score_data()`) is **not a station** - it's the hands-off executor.

---

### 5. **Station 3 Not Using Blueprint Strings**

**Files Affected:**
- `OLD/fifteenth.py`, `sixteenth.py`, `seventeenth.py`

**Issue:**
These files have "Harmonic Analysis" or "Harmonization" at Station 3, but this should be **Blueprint Strings**!

**Current (WRONG):**
```python
# STATION 3: HARMONIZATION
def harmonize_melody(melody_part):
    """Generate harmonization."""
    # ... code ...
```

**Correct:**
```python
# STATION 3: STRUCTURING INPUT (Blueprint Strings)
VOICE_STAVE_DEF = "Melody & Harmony"
VOICE_STAVE_DATA = """
    MELODY & HARMONY;
    MELODY_VAR & HARMONY_VAR
"""
```

---

## Station 4: Promotion Toggling Model

### What Is "Promotion"?

**Promotion** = Moving from **declarative Station 1-3** to **programmatic Station 4** when needed.

### The Toggle Concept

Most studies don't need Station 4! They can work purely in Stations 1-3:
- Station 1: Write music (LilyPond)
- Station 2: Verify & inspect (TinyNotation + generated snippets)
- Station 3: Structure composition (Blueprint Strings)

**Station 4 is accessed only when:**
- Custom transformations needed (not in library)
- Complex algorithmic generation required
- Piece-specific logic needed

### Current Implementation

**Explicit Promotion:**
```python
# Station 4 is accessed when you write custom code
def custom_transformation(part):
    """Piece-specific logic not in library."""
    # ... custom code here ...
    return modified_part
```

**Implicit Promotion:**
```python
# If you use only library transformations, Station 4 is implicit
# No custom code needed - everything happens in build_score_data()
```

### What Might Be Missing

The **PROMOTE_TO_TINYNOTATION** toggle mentioned in `project_template.py` is a **different concept**:
- It promotes **TinyNotation to be dominant format** (instead of LilyPond)
- This is a **format toggle**, not a "Station 4 access" toggle

**Clarification needed:**
Is there supposed to be a **PROMOTE_TO_STATION4** toggle that enables/disables custom code sections?

Currently, Station 4 is just:
- **Implicit** if you use library functions
- **Explicit** if you write custom transformation functions

There's no **toggle** to "promote to full programmatic context" - you just write code there if needed.

---

## Recommendations

### 1. ✅ Standardize All Study Files

**Action:** Update all files in `studies/OLD/` to follow canonical 4-station model:

```python
# STATION 1: COMPOSING INPUT (LilyPond)
# STATION 2: VALIDATING & GENERATED INPUT (TinyNotation + LilyPond)
# STATION 3: STRUCTURING INPUT (Blueprint Strings)
# STATION 4: PROGRAMMATIC CONTEXT (Custom Tools) [Optional]
```

### 2. ✅ Add TinyNotation to All Transformed Snippets

**Action:** Ensure Station 2 has **both formats** for all snippets:

```python
# Original
THEME_TINY = "..."
THEME_LILY = "..."

# Transformed
THEME_TRANSPOSED_TINY = None  # ✅ Add this
THEME_TRANSPOSED_LILY = None  # ✅ Keep this
```

### 3. ✅ Migrate to Transformation Syntax

**Action:** Update `OLD/thirteenth.py` to use new transformation syntax:

**Current:**
```python
VOICE_STAVE_DATA = """
    THEME_A & r;
    THEME_A_TRANSPOSED & r
"""
# ... explicit transformation in build_score_data()
```

**New:**
```python
VOICE_STAVE_DATA = """
    THEME_A & r;
    transpose_part(THEME_A, 'P5') & r
"""
# ... automatic transformation in framework
```

### 4. ✅ Clarify "Promotion Toggling"

**Action:** Document what "promotion" means:

**Option A: No Toggle Needed**
- Stations 1-3 are always visible and clean
- Station 4 is optional - only add it if custom code needed
- No toggle required - just add/remove Station 4 section

**Option B: Add Station 4 Toggle**
```python
# At top of file
ENABLE_STATION_4 = False  # Toggle to show/hide custom code section

# In file structure
if ENABLE_STATION_4:
    # STATION 4: PROGRAMMATIC CONTEXT
    def custom_transformation(part):
        # ... custom code ...
        pass
```

### 5. ✅ Update Documentation

**Action:** Create clear documentation:
- Station model diagram
- Examples of each station
- When to use Station 4
- Migration guide for old files

---

## Summary

### Canonical Architecture ✅

```
┌─────────────────────────────────────────────────────────────┐
│ STATION 1: COMPOSING INPUT                                  │
│ • LilyPond snippets (THEME_LILY, BASS_LILY, etc.)          │
│ • Composer's domain - clean musical notation                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ STATION 2: VALIDATING & GENERATED INPUT                     │
│ • TinyNotation (THEME_TINY) - pitch verification            │
│ • Generated LilyPond (THEME_TRANSPOSED_LILY) - reuse        │
│ • Generated TinyNotation (THEME_TRANSPOSED_TINY) - verify   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ STATION 3: STRUCTURING INPUT                                │
│ • Blueprint Strings (VOICE_STAVE_DEF, VOICE_STAVE_DATA)    │
│ • Declarative shorthand composition                         │
│ • Transformation syntax: transpose_part(THEME, 'P5')        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ STATION 4: PROGRAMMATIC CONTEXT (Optional)                  │
│ • Custom transformation functions                           │
│ • Piece-specific algorithms                                 │
│ • Accessed via "promotion" (just write code here)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PROCESSING ENGINE (Hands-Off)                               │
│ • build_score_data() function                               │
│ • Executes Stations 1-3, uses Station 4 if present          │
│ • Populates Station 2 with generated snippets               │
└─────────────────────────────────────────────────────────────┘
```

### Files Status

| File | Station 1 | Station 2 | Station 3 | Station 4 | Status |
|------|-----------|-----------|-----------|-----------|--------|
| `test_transformations_blueprint.py` | ✅ | ✅✅ (both) | ✅ | ✅ | ✅ REFERENCE |
| `test_station2_reuse.py` | ✅ | ✅✅ (both) | ✅ | ✅ | ✅ REFERENCE |
| `OLD/thirteenth.py` | ✅ | ✅⚠️ (LILY only) | ✅ | ✅ | ⚠️ NEEDS TINY |
| `OLD/fourteenth.py` | ✅ | ⚠️ (no vars) | ✅ | ✅ | ⚠️ NEEDS STATION 2 |
| `OLD/twelfth.py` | ✅ | ✅ | ✅ | ✅ | ✅ CORRECT |
| `OLD/tenth.py` | ✅ | ✅ | ✅ | ✅ | ✅ CORRECT |
| `OLD/eighteenth.py` | ✅ | ❌ | ❌ | ❌ | ❌ 5-STATION MODEL |
| `OLD/fifteenth.py` | ✅ | ✅ | ❌ | ❌ | ❌ NO BLUEPRINT |

### Key Omissions

1. **TinyNotation missing for transformed snippets** (thirteenth.py, fourteenth.py)
2. **Station 2 not explicit** (fourteenth.py - just mentions validation)
3. **5-station architecture** (eighteenth.py, twentyth.py, twentyfirst.py) - WRONG MODEL
4. **No Blueprint Strings at Station 3** (fifteenth.py, sixteenth.py, seventeenth.py)
5. **Transformation syntax not used** (thirteenth.py - uses old explicit approach)

### Station 4 Promotion Model

**Current Understanding:**
- Station 4 is **optional** (not always present)
- "Promotion" = choosing to write custom code in Station 4
- No explicit toggle needed - just add Station 4 section if needed
- Stations 1-3 stay clean and declarative
- Station 4 accessed when library transformations aren't enough

**Clarification Needed:**
- Is there supposed to be a `PROMOTE_TO_STATION4 = True` toggle?
- Or is "promotion" just the act of writing custom code there?
- Currently appears to be implicit (no toggle mechanism)

---

## Next Steps

1. ✅ **Confirm architecture** with user
2. **Update old study files** to canonical 4-station model
3. **Add TinyNotation** to all transformed snippets in Station 2
4. **Document promotion model** clearly
5. **Migrate thirteenth.py** to new transformation syntax (optional)
