# SCORE STRUCTURE ANALYSIS & SPECIFICATION
**Date:** October 14, 2025  
**Context:** Step 2 of chord parsing validation → refactoring roadmap

## PROBLEM STATEMENT

Current thirteenth.py has **manual assembly** (lines 320-395, ~75 lines) that:
- Hardcodes two-stave structure
- Duplicates pattern logic (upper/lower pairing)
- Makes VOICE_ASSIGNMENTS (lines 143-171) unused decoration
- Doesn't scale to 1-stave or N-stave systems
- Obscures musical intent with low-level event manipulation

**Goal:** Create a **flexible, declarative SCORE_STRUCTURE** that works for:
- 1-stave systems (melody only)
- 2-stave systems (melody + harmony)
- N-stave systems (SATB, orchestral, etc.)
- Any combination of real snippets and auto-generated rests

---

## ARCHITECTURAL PATTERNS FROM CODEBASE

### Pattern 1: Single-Stave (first.py, third.py)
```python
# Returns: {'metadata': {...}, 'parts': {'Main Melody': [events]}}
score_data = {
    'metadata': metadata,
    'parts': {
        'Melody': melody_events,  # Single part, single voice
    }
}
```
**Characteristics:**
- One part = one voice (list of events)
- Simplest structure
- Works for solo pieces

### Pattern 2: Multi-Stave Single-Voice (second.py, thirteenth.py current)
```python
# Returns: {'metadata': {...}, 'parts': {'Melody': [...], 'Harmony': [...]}}
score_data = {
    'metadata': metadata,
    'parts': {
        'Melody': melody_events,   # Part 1: list of events
        'Harmony': harmony_events,  # Part 2: list of events
    }
}
```
**Characteristics:**
- Multiple parts, each with one voice
- Parts are **dict keys** (alphabetical → reverse order in LilyPond)
- Each part is a **list of events**
- Current thirteenth.py uses this (manual assembly)

### Pattern 3: Multi-Voice Polyphonic (project_template.py lines 340-365)
```python
# Returns polyphonic structure with multiple voices per staff
score_data = {
    'metadata': metadata,
    'parts': {
        'UpperStaff': {  # Part with multiple voices (dict)
            'Voice1': voice1_events,
            'Voice2': voice2_events,
        },
        'LowerStaff': {  # Part with multiple voices (dict)
            'Voice3': voice3_events,
            'Voice4': voice4_events,
        }
    }
}
```
**Characteristics:**
- Part is a **dict of voice names → event lists**
- Multiple voices rendered on same staff
- Used for counterpoint, polyphony
- Rendered as `<< {...} \\ {...} >>` in LilyPond

---

## UNIFIED FLEXIBLE STRUCTURE

### Core Principles

1. **Snippet-First:** All musical content defined as named snippets
2. **Declarative Assembly:** SCORE_STRUCTURE describes composition, not implementation
3. **Auto-Rest Generation:** Use `'r'` marker to auto-generate matching rests
4. **Flexible Nesting:** Support 1-N staves, 1-N voices per staff
5. **Part Names Control Order:** Alphabetical part names → reverse visual order

### Data Structure Specification

```python
SCORE_STRUCTURE = [
    # Format 1: Single snippet (creates one-stave score)
    {'snippet': 'MELODY'},
    
    # Format 2: Named section with single snippet
    {'name': 'Introduction', 'snippet': 'INTRO'},
    
    # Format 3: Multi-stave with explicit staff assignment
    {
        'name': 'Theme A',
        'staves': {
            'UpperStaff': 'THEME_A',      # Snippet name
            'LowerStaff': 'r',             # Auto-generate rests
        }
    },
    
    # Format 4: Multi-voice per staff (polyphonic)
    {
        'name': 'Fugue',
        'staves': {
            'UpperStaff': {
                'Voice1': 'SOPRANO',
                'Voice2': 'ALTO',
            },
            'LowerStaff': {
                'Voice3': 'TENOR',
                'Voice4': 'BASS',
            }
        }
    },
    
    # Format 5: Mixed - some staves have voices, some don't
    {
        'name': 'Intermezzo',
        'staves': {
            'Piano_RH': 'MELODY',          # Single voice
            'Piano_LH': {                  # Multi-voice
                'Voice1': 'HARMONY_HIGH',
                'Voice2': 'HARMONY_LOW',
            }
        }
    }
]
```

### Rest Auto-Generation Rules

When snippet value is `'r'`:
1. Find reference snippet (first non-'r' snippet in same section)
2. Calculate total duration from reference events
3. Generate bar-by-bar rests: `[{'type': 'rest', 'ql': bar_duration}, ...]`
4. Match measure count (not individual note durations)

### Staff Naming Convention

**Alphabetical order → Reverse visual order in score:**
- `'UpperStaff'` appears above `'LowerStaff'` (U > L alphabetically)
- `'Melody'` appears above `'Harmony'` (M > H alphabetically)
- `'Piano_RH'` appears above `'Piano_LH'` (RH > LH alphabetically)

**Rationale:** LilyPond renders staves in reverse order, so alphabetical sorting gives intuitive top-to-bottom visual order.

---

## IMPLEMENTATION DESIGN

### Builder Function Signature

```python
def build_score_from_structure(
    score_structure: List[Dict],
    snippets: Dict[str, List[Dict]],
    metadata: Dict,
    time_signature: str = '4/4'
) -> Dict[str, Dict]:
    """
    Build score_data from declarative SCORE_STRUCTURE.
    
    Args:
        score_structure: List of section definitions (see spec above)
        snippets: Dict mapping snippet names to event lists
        metadata: Score metadata (title, key, tempo, etc.)
        time_signature: Default time signature for rest generation
        
    Returns:
        Standard score_data dict: {'metadata': {...}, 'parts': {...}}
    """
```

### Algorithm

```
FOR each section in SCORE_STRUCTURE:
    IF section has 'snippet' key (Format 1/2):
        → Add to default part
    
    ELSE IF section has 'staves' key (Format 3/4/5):
        FOR each staff_name, staff_content in section['staves']:
            IF staff_content == 'r':
                → Generate rests matching reference duration
            
            ELSE IF staff_content is string (snippet name):
                → Append snippets[staff_content] to parts[staff_name]
            
            ELSE IF staff_content is dict (multi-voice):
                → Initialize parts[staff_name] as dict if needed
                FOR each voice_name, voice_snippet in staff_content:
                    IF voice_snippet == 'r':
                        → Generate rests
                    ELSE:
                        → Append snippets[voice_snippet] to parts[staff_name][voice_name]
    
    Add barline between sections

RETURN {'metadata': metadata, 'parts': parts}
```

### Helper Functions

```python
def calculate_snippet_duration(events: List[Dict]) -> float:
    """Calculate total quarter-length duration of event list."""
    return sum(e.get('ql', 0) for e in events if e.get('type') != 'barline')

def create_bar_rests(duration_ql: float, time_sig: str = '4/4') -> List[Dict]:
    """Generate whole-bar rests matching total duration."""
    bar_duration = parse_time_signature(time_sig)  # e.g., 4.0 for 4/4
    num_measures = int(duration_ql / bar_duration)
    return [{'type': 'rest', 'ql': bar_duration} for _ in range(num_measures)]

def find_reference_snippet(staves: Dict) -> List[Dict]:
    """Find first non-'r' snippet to use as duration reference."""
    for staff_content in staves.values():
        if isinstance(staff_content, str) and staff_content != 'r':
            return snippets[staff_content]
        elif isinstance(staff_content, dict):
            for voice_snippet in staff_content.values():
                if voice_snippet != 'r':
                    return snippets[voice_snippet]
    return []  # No reference found
```

---

## THIRTEENTH.PY REFACTORING PLAN

### Before (Current - 75 lines)
```python
# Lines 320-395: Manual assembly
upper_staff = []
lower_staff = []

# Section 1
upper_staff.extend(theme_a_events)
upper_staff.append(bar_line("||"))
lower_staff.extend(create_bar_rests(theme_a_events))
lower_staff.append(bar_line("||"))

# Section 2  
upper_staff.append({'type': 'rest', 'ql': intermezzo_duration})
upper_staff.append(bar_line("||"))
lower_staff.extend(intermezzo_events)
lower_staff.append(bar_line("||"))

# ... 60 more lines of repetitive pattern ...

score_data = {
    'metadata': metadata,
    'parts': {
        'UpperStaff': upper_staff,
        'LowerStaff': lower_staff,
    }
}
```

### After (Declarative - ~30 lines)
```python
# Station 3: SCORE_STRUCTURE (replaces lines 143-171 VOICE_ASSIGNMENTS)
SCORE_STRUCTURE = [
    {
        'name': 'Theme A Original',
        'staves': {
            'UpperStaff': 'THEME_A',
            'LowerStaff': 'r',
        }
    },
    {
        'name': 'Intermezzo 1',
        'staves': {
            'UpperStaff': 'r',
            'LowerStaff': 'INTERMEZZO',
        }
    },
    {
        'name': 'Theme A Transposed',
        'staves': {
            'UpperStaff': 'THEME_A_TRANSPOSED',
            'LowerStaff': 'r',
        }
    },
    {
        'name': 'Intermezzo 2',
        'staves': {
            'UpperStaff': 'r',
            'LowerStaff': 'INTERMEZZO',
        }
    },
    {
        'name': 'Theme A Inverted',
        'staves': {
            'UpperStaff': 'THEME_A_INVERTED',
            'LowerStaff': 'r',
        }
    },
    {
        'name': 'Intermezzo 3',
        'staves': {
            'UpperStaff': 'r',
            'LowerStaff': 'INTERMEZZO',
        }
    },
    {
        'name': 'Finale: Harmonized',
        'staves': {
            'UpperStaff': 'THEME_A_HARMONIZED',
            'LowerStaff': 'r',
        }
    },
]

# Build score (replaces 75 lines of manual assembly)
snippets = {
    'THEME_A': theme_a_events,
    'THEME_A_TRANSPOSED': theme_a_transposed,
    'THEME_A_INVERTED': theme_a_inverted,
    'THEME_A_HARMONIZED': theme_a_harmony,
    'INTERMEZZO': intermezzo_events,
}

score_data = build_score_from_structure(
    SCORE_STRUCTURE,
    snippets,
    metadata,
    time_signature='4/4'
)
```

**Benefits:**
- ✅ 75 lines → ~30 lines (60% reduction)
- ✅ Musical structure clear at a glance
- ✅ Easy to reorder, add, or remove sections
- ✅ Auto-rest generation removes boilerplate
- ✅ Scales to N-stave systems without code changes

---

## VALIDATION CRITERIA

### Must Support

1. **Single-stave scores** (melody only)
   ```python
   SCORE_STRUCTURE = [{'snippet': 'MELODY'}]
   ```

2. **Two-stave scores** (melody + harmony)
   ```python
   SCORE_STRUCTURE = [{
       'staves': {'Upper': 'MELODY', 'Lower': 'HARMONY'}
   }]
   ```

3. **Auto-rest generation**
   ```python
   {'staves': {'Upper': 'MELODY', 'Lower': 'r'}}
   # → Lower automatically gets rests matching MELODY duration
   ```

4. **Mixed sections** (some staves active, some resting)
   ```python
   # Section 1: melody only
   {'staves': {'Upper': 'INTRO', 'Lower': 'r'}},
   # Section 2: harmony only
   {'staves': {'Upper': 'r', 'Lower': 'CHORDS'}},
   ```

5. **Polyphonic staves** (multiple voices per staff)
   ```python
   {
       'staves': {
           'Piano_RH': {
               'Voice1': 'SOPRANO',
               'Voice2': 'ALTO',
           }
       }
   }
   ```

### Backward Compatibility

- Existing studies (first.py, second.py) continue working
- `score_data` format unchanged: `{'metadata': {...}, 'parts': {...}}`
- No changes to parser, converter, or engraving pipeline

---

## NEXT STEPS

1. **Implement `build_score_from_structure()`** in new file `score_builder.py`
2. **Refactor thirteenth.py** to use SCORE_STRUCTURE
3. **Test** with existing output (should match exactly)
4. **Document** usage patterns for future studies
5. **Migrate** other multi-stave studies (eleventh.py, etc.)

---

## DESIGN DECISION LOG

**Q: Why not use VOICE_ASSIGNMENTS directly?**  
A: VOICE_ASSIGNMENTS uses expression syntax (`'A + B'`, `'transpose(X, 5)'`) which requires eval() or complex parsing. SCORE_STRUCTURE is pure data (JSON-serializable), safer and simpler.

**Q: Why 'r' instead of null/None?**  
A: 'r' is LilyPond's rest notation, familiar to musicians. Also prevents accidental omission (None could be unintended).

**Q: Why alphabetical ordering for staff names?**  
A: LilyPond renders staves in reverse order. Alphabetical naming (UpperStaff > LowerStaff) gives intuitive visual order without magic indices.

**Q: Why not auto-detect single vs multi-stave?**  
A: Explicit is better than implicit. Structure should clearly show composer's intent, not rely on inference.

**Q: Performance considerations?**  
A: Negligible. Structure assembly is O(n) where n = number of sections. Dominated by parsing/engraving time.

---

**STATUS:** Analysis complete. Ready for implementation.
