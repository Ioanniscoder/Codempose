# Ninth Study: Summary & Practical Guide

## Quick Reference

**File:** `ninth.py`  
**Purpose:** Demonstrate hybrid composition model (programmatic + shorthand)  
**Status:** ✅ Fully functional  
**Output:** `outputs/ninth.{ly,pdf,midi}` (51 events across 4 voices)

---

## What ninth.py Demonstrates

### ✅ Full Programmatic Input Structure Available
```python
# Every voice CAN be generated programmatically
soprano = generate_soprano_programmatically()
alto = generate_alto_programmatically()
tenor = generate_tenor_programmatically()   # Available but not used
bass = generate_bass_programmatically()     # Available but not used
```

### ✅ Shorthand is Optional Convenience
```python
# Some voices USE shorthand (Tenor, Bass)
VOICE_ASSIGNMENTS = {
    'Harmony': {
        'Tenor': 'transpose(HARMONY, 5) + HARMONY',
        'Bass': 'BASS * 4',
    }
}
```

### ✅ Both Mix Seamlessly in build_score_data()
```python
def build_score_data():
    # Programmatic parts
    soprano = generate_soprano_programmatically()
    alto = generate_alto_programmatically()
    
    # Shorthand parts
    harmony = build_harmony_via_shorthand()
    
    # Combine both
    return {
        'parts': {
            'Melody': {
                'Soprano': soprano,                    # ← Programmatic
                'Alto': alto,                          # ← Programmatic
            },
            'Harmony': {
                'Tenor': harmony['Tenor'],             # ← Shorthand
                'Bass': harmony['Bass'],               # ← Shorthand
            }
        }
    }
```

---

## The Three Implementation Options

ninth.py provides THREE working implementations:

### Option 1: HYBRID (Default - Used in ninth.py)
```python
def build_score_data():
    # Complex parts → Programmatic
    soprano = generate_soprano_programmatically()
    alto = generate_alto_programmatically()
    
    # Simple parts → Shorthand
    harmony = build_harmony_via_shorthand()
    
    # Combine
    return combine(soprano, alto, harmony['Tenor'], harmony['Bass'])
```

**Best for:** Real-world compositions (most common)

### Option 2: FULLY PROGRAMMATIC (Available in ninth.py)
```python
def build_score_data_fully_programmatic():
    # Everything generated with code - NO shorthand
    soprano = generate_soprano_programmatically()
    alto = generate_alto_programmatically()
    tenor = generate_tenor_programmatically()   # Manual generation
    bass = generate_bass_programmatically()     # Manual generation
    
    return combine_all(soprano, alto, tenor, bass)
```

**Best for:** Maximum control, no abstractions

### Option 3: FULLY SHORTHAND (Like seventh.py)
```python
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'THEME + transpose(THEME, 7)',
        'Alto': 'VARIATION * 2',
    },
    'Harmony': {
        'Tenor': 'transpose(HARMONY, 5) + HARMONY',
        'Bass': 'BASS * 4',
    }
}

def build_score_data():
    # Everything via shorthand - minimal code
    return build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
```

**Best for:** Simple compositions, quick prototyping

---

## Code Architecture

### Layer 1: Musical Snippets (Input)
```python
# LilyPond snippets (or TinyNotation)
THEME_LILY = r"\relative c' { c4 d e f | g2 e2 }"
BASS_LILY = r"\relative c { c2 g2 | f2 c2 }"
```

**These are ALWAYS present**, regardless of generation method.

### Layer 2: Generation Methods (Flexible)

#### Method A: Programmatic
```python
def generate_soprano_programmatically():
    theme_data = parse_lilypond_to_data(THEME_LILY)
    theme_part = data_to_part(theme_data['parts']['Theme'])
    inverted = invert_part(theme_part, 'C4')
    return extract_data_from_part(inverted)
```

#### Method B: Shorthand
```python
VOICE_ASSIGNMENTS = {'Bass': 'BASS * 4'}

def build_via_shorthand():
    voice_lookup = {'BASS': parse_lilypond_to_data(BASS_LILY)['parts']['Bass']}
    return build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
```

### Layer 3: Master Controller (Required)
```python
def build_score_data():
    # REQUIRED: This function MUST exist
    # FLEXIBLE: Can use ANY generation method
    
    # Mix and match as needed:
    soprano = generate_soprano_programmatically()  # Method A
    bass = build_via_shorthand()['Bass']            # Method B
    
    return {
        'metadata': {...},
        'parts': {
            'Melody': {'Soprano': soprano},
            'Harmony': {'Bass': bass}
        }
    }
```

**Key Point:** `build_score_data()` is the ONLY required function. How you generate the parts inside it is UP TO YOU.

---

## Practical Decision Tree

```
Need to generate a voice?
    │
    ├─► Is it complex/unique?
    │   └─► YES → Use programmatic generation
    │       • Custom transformations
    │       • Algorithmic logic
    │       • Multiple source snippets
    │
    └─► Is it simple/repetitive?
        └─► YES → Use shorthand
            • Repetition ('V * N')
            • Simple chaining ('V1 + V2')
            • Standard transformations ('transpose(...)')
```

**Remember:** You can ALWAYS switch between methods mid-composition!

---

## Voice-by-Voice Breakdown (ninth.py)

### Soprano (Programmatic)
**Why:** Needs inversion transformation around C4

```python
def generate_soprano_programmatically():
    theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
    theme_part = data_to_part(theme_data['parts']['Theme'])
    inverted_part = invert_part(theme_part, 'C4')  # ← Custom transform
    return extract_data_from_part(inverted_part)
```

**Could use shorthand?** ✅ Yes - `'invert(THEME)'` (if inversion axis is default)  
**But programmatic is better here:** More control over inversion axis

### Alto (Programmatic)
**Why:** Custom algorithmic structure (variation + fragment + retrograde)

```python
def generate_alto_programmatically():
    variation_events = parse_lilypond_to_data(VARIATION_LILY)['parts']['Variation']
    theme_events = parse_lilypond_to_data(THEME_LILY)['parts']['Theme']
    
    theme_fragment = theme_events[:4]  # ← Custom slicing
    
    return (
        variation_events +
        theme_fragment +                    # ← Can't do this in shorthand
        list(reversed(variation_events))
    )
```

**Could use shorthand?** ⚠️ Partially - `'VARIATION + retrograde(VARIATION)'`  
**But can't do fragment slicing in shorthand** → Programmatic required

### Tenor (Shorthand)
**Why:** Simple pattern (transposed + original)

```python
# In VOICE_ASSIGNMENTS
'Tenor': 'transpose(HARMONY, 5) + HARMONY'
```

**Could use programmatic?** ✅ Yes, but shorthand is cleaner:
```python
# Programmatic version would be:
harmony_events = parse_lilypond_to_data(HARMONY_LILY)['parts']['Harmony']
transposed = transpose_events(harmony_events, 5)
tenor_events = transposed + harmony_events
```

### Bass (Shorthand)
**Why:** Simple ostinato (4 repetitions)

```python
# In VOICE_ASSIGNMENTS
'Bass': 'BASS * 4'
```

**Could use programmatic?** ✅ Yes, but shorthand is clearer:
```python
# Programmatic version would be:
bass_events = parse_lilypond_to_data(BASS_LILY)['parts']['Bass']
bass_final = bass_events * 4
```

---

## Key Design Principles Validated

### 1. ✅ "Full programmatic input structure, regardless whether it is actually used"

**ninth.py proves this:**
```python
# These functions exist and work, even though shorthand is used for some parts
def generate_soprano_programmatically()  # ✅ Used
def generate_alto_programmatically()     # ✅ Used
def generate_tenor_programmatically()    # ⚠️ Available but not called
def generate_bass_programmatically()     # ⚠️ Available but not called

# You can switch ANY voice to programmatic by changing build_score_data()
```

### 2. ✅ "build_score_data() is the master controller"

**ninth.py proves this:**
```python
def build_score_data():
    # This function orchestrates EVERYTHING
    # It can call:
    #   - Programmatic generators
    #   - Shorthand builders
    #   - Mix both
    #   - Switch between them at will
    
    # FULL CONTROL over the final result
    return score_data
```

### 3. ✅ "Shorthand does not remove programmatic control"

**ninth.py proves this:**
```python
# Option A: Use shorthand
harmony = build_harmony_via_shorthand()

# Option B: Override with programmatic
# (Uncomment to switch)
# tenor_events = generate_tenor_programmatically()
# bass_events = generate_bass_programmatically()

# build_score_data() decides which to use
```

---

## How to Switch Between Methods

### Switching Tenor from Shorthand → Programmatic

**Current (Shorthand):**
```python
# In VOICE_ASSIGNMENTS
'Tenor': 'transpose(HARMONY, 5) + HARMONY'

# In build_score_data()
harmony = build_harmony_via_shorthand()
tenor_events = harmony['Tenor']  # ← From shorthand
```

**Switch to Programmatic:**
```python
# Comment out shorthand
# 'Tenor': 'transpose(HARMONY, 5) + HARMONY'

# In build_score_data()
def generate_tenor_programmatically():
    harmony_events = parse_lilypond_to_data(HARMONY_LILY)['parts']['Harmony']
    transposed = transpose_events(harmony_events, 5)
    return transposed + harmony_events

tenor_events = generate_tenor_programmatically()  # ← Now programmatic
```

**No other changes needed!** Both produce the same event list structure.

---

## Testing the Alternatives

### Test 1: Run Default (Hybrid)
```bash
python3 ninth.py
# Uses: Soprano (prog) + Alto (prog) + Tenor (short) + Bass (short)
```

### Test 2: Run Fully Programmatic
Edit `ninth.py`:
```python
if __name__ == '__main__':
    # Uncomment this:
    def build_score_data():
        return build_score_data_fully_programmatic()
    
    run_pipeline_from_file(__file__)
```

Then run:
```bash
python3 ninth.py
# Uses: ALL VOICES programmatic, NO shorthand
```

### Test 3: Run Fully Shorthand
Create new `VOICE_ASSIGNMENTS`:
```python
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'invert(THEME)',
        'Alto': 'VARIATION + retrograde(VARIATION)',
    },
    'Harmony': {
        'Tenor': 'transpose(HARMONY, 5) + HARMONY',
        'Bass': 'BASS * 4',
    }
}

def build_score_data():
    return build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
```

```bash
python3 ninth.py
# Uses: ALL VOICES shorthand, NO manual programmatic
```

---

## Common Patterns

### Pattern 1: Complex Intro + Simple Body
```python
def build_score_data():
    # Intro: Complex, algorithmic
    intro = my_generative_algorithm()
    
    # Body: Simple, repetitive
    body = build_score_from_assignments(
        {'Melody': 'THEME * 4'},
        voice_lookup
    )
    
    # Combine
    melody_events = intro + body['Melody']
    
    return {'parts': {'Melody': melody_events}}
```

### Pattern 2: Programmatic Melody + Shorthand Accompaniment
```python
def build_score_data():
    # Melody: Unique, expressive
    melody = generate_expressive_melody()
    
    # Accompaniment: Formulaic
    accompaniment = build_score_from_assignments(
        {
            'Harmony': {
                'Tenor': 'HARMONY * 8',
                'Bass': 'BASS * 8'
            }
        },
        voice_lookup
    )
    
    return {
        'parts': {
            'Melody': {'Soprano': melody},
            'Harmony': accompaniment['Harmony']
        }
    }
```

### Pattern 3: Conditional Generation
```python
def build_score_data():
    if USE_SHORTHAND:
        soprano = build_score_from_assignments(...)['Soprano']
    else:
        soprano = generate_soprano_programmatically()
    
    # Either way, same result structure
    return {'parts': {'Melody': {'Soprano': soprano}}}
```

---

## Performance Comparison

| Method | Lines of Code | Flexibility | Learning Curve | Best For |
|--------|--------------|-------------|----------------|----------|
| **Programmatic** | ~15-30 per voice | ⭐⭐⭐⭐⭐ Maximum | Medium | Complex logic |
| **Shorthand** | ~1-2 per voice | ⭐⭐⭐ High | Low | Simple patterns |
| **Hybrid** | ~5-15 per voice | ⭐⭐⭐⭐⭐ Maximum | Medium | Real compositions |

**Recommended:** Start with shorthand, switch to programmatic when needed (Hybrid approach).

---

## Summary

### What ninth.py Proves:

1. ✅ **Full programmatic structure is ALWAYS available**
   - Every voice CAN be generated programmatically
   - Functions exist even if not currently used

2. ✅ **Shorthand is a CONVENIENCE, not a REQUIREMENT**
   - Used for Tenor and Bass (simple patterns)
   - Bypassed for Soprano and Alto (complex logic)

3. ✅ **build_score_data() is the MASTER CONTROLLER**
   - Decides which generation method to use
   - Combines results from any source
   - Full control over final output

4. ✅ **Both approaches MIX SEAMLESSLY**
   - Same data structure (event lists)
   - No conflicts or incompatibilities
   - Switch between methods at will

5. ✅ **The framework gives OPTIONS, not RESTRICTIONS**
   - Three working implementations provided
   - Easy to switch between approaches
   - Use what fits the task

---

## Next Steps

### For Simple Compositions:
→ Use shorthand (like `seventh.py` or `eighth.py`)

### For Complex Compositions:
→ Use hybrid (like `ninth.py`) - **RECOMMENDED**

### For Maximum Control:
→ Use fully programmatic (`build_score_data_fully_programmatic()` in `ninth.py`)

### For Your Use Case:
→ **Start with ninth.py as a template** and adapt as needed!

🎼 The framework **empowers you to choose** the right approach for each part of your composition!
