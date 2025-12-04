# STATION 3 REFACTORING - PAIRED SNIPPET STRUCTURE
Date: October 14, 2025

## CURRENT PROBLEM IN STATION 3

thirteenth.py Station 3 has VOICE_ASSIGNMENTS:

```python
VOICE_ASSIGNMENTS = {
    'MainLine': {
        'ThemeA_Original': 'THEME_A',
        'Intermezzo_1': 'HARMONY_1',
        'ThemeA_Transposed': 'THEME_A_TRANSPOSED_P5',
        # ...
    }
}
```

**Issues:**
1. Single voice structure - doesn't represent two-stave system
2. Not actually used in build_score_data()
3. No clear upper/lower pairing
4. 'HARMONY_1' references don't match actual snippet names

---

## PROPOSED FIX: PAIRED SNIPPET STRUCTURE

Replace VOICE_ASSIGNMENTS with a clear two-stave structure:

```python
# ============================================================================
# STATION 3: TWO-STAVE STRUCTURE (PAIRED SNIPPETS)
# ============================================================================

SCORE_STRUCTURE = [
    # Section 1: Theme A Original
    {
        'name': 'Theme A Original',
        'upper': 'THEME_A',
        'lower': 'r'  # Whole-bar rests
    },
    
    # Intermezzo 1
    {
        'name': 'Intermezzo 1',
        'upper': 'r',
        'lower': 'INTERMEZZO'
    },
    
    # Section 2: Theme A Transposed
    {
        'name': 'Theme A Transposed',
        'upper': 'THEME_A_TRANSPOSED',
        'lower': 'r'
    },
    
    # Intermezzo 2
    {
        'name': 'Intermezzo 2',
        'upper': 'r',
        'lower': 'INTERMEZZO'
    },
    
    # Section 3: Theme A Inverted
    {
        'name': 'Theme A Inverted',
        'upper': 'THEME_A_INVERTED',
        'lower': 'r'
    },
    
    # Intermezzo 3
    {
        'name': 'Intermezzo 3',
        'upper': 'r',
        'lower': 'INTERMEZZO'
    },
    
    # Finale: Theme A Harmonized
    {
        'name': 'Finale',
        'upper': 'THEME_A_HARMONIZED',
        'lower': 'r'
    }
]
```

---

## VISUAL COMPARISON

**BEFORE (Current VOICE_ASSIGNMENTS):**
- Single voice 'MainLine'
- Mixed themes and intermezzos in one list
- Not clear which goes on which staff
- References 'HARMONY_1' that doesn't exist

**AFTER (SCORE_STRUCTURE):**
- Clear upper/lower pairing
- Each section shows both staves
- 'r' marker for rest generation
- References actual snippet names

---

## IMPLEMENTATION IN build_score_data()

**Current approach (lines 285-395):**
```python
def bar_line(style="||"):
    return {'type': 'barline', 'style': style, 'ql': 0.0}

def create_bar_rests(events, time_sig='4/4'):
    # ... 20 lines ...

upper_staff = []
lower_staff = []

# === SECTION 1: THEME A ORIGINAL ===
upper_staff.extend(theme_a_events)
upper_staff.append(bar_line("||"))
lower_staff.extend(create_bar_rests(theme_a_events))
lower_staff.append(bar_line("||"))

# === INTERMEZZO 1 ===
upper_staff.append({'type': 'rest', 'ql': intermezzo_duration})
upper_staff.append(bar_line("||"))
lower_staff.extend(intermezzo_events)
lower_staff.append(bar_line("||"))

# ... repeated 5 more times ...
```

**Proposed approach:**
```python
def build_score_data() -> Dict[str, Dict]:
    # Parse snippets
    snippets = {
        'THEME_A': theme_a_events,
        'THEME_A_TRANSPOSED': theme_a_transposed,
        'THEME_A_INVERTED': theme_a_inverted,
        'THEME_A_HARMONIZED': theme_a_harmony,
        'INTERMEZZO': intermezzo_events
    }
    
    # Build score from SCORE_STRUCTURE
    upper_staff = []
    lower_staff = []
    time_sig = '4/4'
    
    for section in SCORE_STRUCTURE:
        # Get upper events
        if section['upper'] == 'r':
            lower_events = snippets[section['lower']]
            upper_events = create_bar_rests(lower_events, time_sig)
        else:
            upper_events = snippets[section['upper']]
        
        # Get lower events
        if section['lower'] == 'r':
            lower_events = create_bar_rests(upper_events, time_sig)
        else:
            lower_events = snippets[section['lower']]
        
        # Add to staves with barlines
        upper_staff.extend(upper_events)
        upper_staff.append(create_barline("||"))
        
        lower_staff.extend(lower_events)
        lower_staff.append(create_barline("||"))
    
    # Remove last barlines
    upper_staff = upper_staff[:-1]
    lower_staff = lower_staff[:-1]
    
    return {
        'parts': {
            'UpperStaff': upper_staff,
            'LowerStaff': lower_staff
        },
        'metadata': {...}
    }
```

---

## KEY IMPROVEMENTS

1. **Station 3 becomes declarative**
   - Just defines structure
   - No transformation logic
   - Clear upper/lower pairing

2. **Station 4 becomes execution**
   - Parses snippets
   - Applies transformations
   - Builds from SCORE_STRUCTURE

3. **Separation of concerns**
   - SCORE_STRUCTURE = WHAT
   - build_score_data() = HOW

4. **Easy to modify**
   - Add section: append to SCORE_STRUCTURE
   - Reorder: change SCORE_STRUCTURE order
   - No code changes needed

---

## MINIMAL IMPLEMENTATION

Don't need new library functions. Just refactor existing code:

1. Replace VOICE_ASSIGNMENTS with SCORE_STRUCTURE in Station 3
2. Update build_score_data() to iterate over SCORE_STRUCTURE
3. Keep create_bar_rests() as local helper (for now)

This is much simpler than the previous proposal!

---

## PROPOSED CHANGES TO thirteenth.py

**Station 3 (lines 133-171):**
```python
# ============================================================================
# STATION 3: TWO-STAVE STRUCTURE (PAIRED SNIPPETS)
# ============================================================================

SCORE_STRUCTURE = [
    {'name': 'Theme A Original',    'upper': 'THEME_A',            'lower': 'r'},
    {'name': 'Intermezzo 1',        'upper': 'r',                  'lower': 'INTERMEZZO'},
    {'name': 'Theme A Transposed',  'upper': 'THEME_A_TRANSPOSED', 'lower': 'r'},
    {'name': 'Intermezzo 2',        'upper': 'r',                  'lower': 'INTERMEZZO'},
    {'name': 'Theme A Inverted',    'upper': 'THEME_A_INVERTED',   'lower': 'r'},
    {'name': 'Intermezzo 3',        'upper': 'r',                  'lower': 'INTERMEZZO'},
    {'name': 'Finale',              'upper': 'THEME_A_HARMONIZED', 'lower': 'r'}
]
```

**Station 4 build_score_data() refactor:**
- Loop over SCORE_STRUCTURE instead of manual assembly
- Keep all existing snippet parsing/transformation logic
- Just change the assembly loop

This is a focused, minimal change that makes the structure clear!
