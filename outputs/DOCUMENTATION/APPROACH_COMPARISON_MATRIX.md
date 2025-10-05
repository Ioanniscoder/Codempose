# Composition Approach Comparison: sixth.py vs seventh.py vs eighth.py vs ninth.py

## Visual Comparison Matrix

| Study | Approach | Complexity | Use Case | Lines of Code |
|-------|----------|------------|----------|---------------|
| **sixth.py** | Pure Programmatic Chaining | Medium | Manual voice construction | ~300 |
| **seventh.py** | Pure Shorthand (Basic) | Low | Simple patterns, quick prototypes | ~250 |
| **eighth.py** | Pure Shorthand (Advanced) | Medium | Transformations in shorthand | ~170 |
| **ninth.py** | **HYBRID (Recommended)** | High | Real-world compositions | ~380 |

---

## Side-by-Side Code Comparison

### Building the Same Musical Idea in All Four Approaches

**Goal:** Soprano with inverted theme, Bass with 4× repetition

#### sixth.py (Pure Programmatic)
```python
# Parse snippets
theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
bass_data = parse_lilypond_to_data(BASS_LILY, part_name='Bass')

# Convert to music21 Parts
theme_part = data_to_part(theme_data['parts']['Theme'])
bass_part = data_to_part(bass_data['parts']['Bass'])

# Apply transformations manually
inverted_soprano_part = invert_part(theme_part, 'C4')

# Extract events
soprano_events = extract_data_from_part(inverted_soprano_part)
bass_events = extract_data_from_part(bass_part)

# Manual repetition
bass_events_repeated = bass_events * 4

# Assemble score
score_data = {
    'metadata': {'title': 'Study'},
    'parts': {
        'Melody': {'Soprano': soprano_events},
        'Harmony': {'Bass': bass_events_repeated}
    }
}
```

**Pros:** Full control, step-by-step visibility  
**Cons:** Verbose, repetitive boilerplate  
**Lines:** ~20

---

#### seventh.py (Pure Shorthand - Basic)
```python
# Can't do inversion in seventh.py (no transformation support)
# Would have to pre-invert the snippet or skip this feature

VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'THEME',  # ← Can't invert
    },
    'Harmony': {
        'Bass': 'BASS * 4',  # ← Simple repetition works
    }
}

def build_score_data():
    voice_lookup = {
        'THEME': parse_lilypond_to_data(THEME_LILY)['parts']['Theme'],
        'BASS': parse_lilypond_to_data(BASS_LILY)['parts']['Bass'],
    }
    
    return build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
```

**Pros:** Concise, readable  
**Cons:** **Can't do inversion** (no transformation support)  
**Lines:** ~15

---

#### eighth.py (Pure Shorthand - Advanced)
```python
# NOW inversion is possible!
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'invert(THEME)',  # ← Transformation in shorthand
    },
    'Harmony': {
        'Bass': 'BASS * 4',
    }
}

def build_score_data():
    voice_lookup = {
        'THEME': parse_lilypond_to_data(THEME_LILY)['parts']['Theme'],
        'BASS': parse_lilypond_to_data(BASS_LILY)['parts']['Bass'],
    }
    
    return build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
```

**Pros:** Concise, supports transformations  
**Cons:** Limited to available transformations (can't customize inversion axis)  
**Lines:** ~15

---

#### ninth.py (HYBRID - Recommended)
```python
# Complex part (Soprano) → Programmatic
def generate_soprano_programmatically():
    theme_data = parse_lilypond_to_data(THEME_LILY, part_name='Theme')
    theme_part = data_to_part(theme_data['parts']['Theme'])
    inverted_part = invert_part(theme_part, 'C4')  # ← Custom axis
    return extract_data_from_part(inverted_part)

# Simple part (Bass) → Shorthand
VOICE_ASSIGNMENTS = {
    'Harmony': {
        'Bass': 'BASS * 4',
    }
}

def build_score_data():
    # Programmatic for complex
    soprano_events = generate_soprano_programmatically()
    
    # Shorthand for simple
    bass_data = parse_lilypond_to_data(BASS_LILY)['parts']['Bass']
    voice_lookup = {'BASS': bass_data}
    harmony = build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
    
    return {
        'metadata': {'title': 'Study'},
        'parts': {
            'Melody': {'Soprano': soprano_events},      # Programmatic
            'Harmony': {'Bass': harmony['Harmony']['Bass']}  # Shorthand
        }
    }
```

**Pros:** Best of both worlds - control + convenience  
**Cons:** Slightly more code than pure shorthand  
**Lines:** ~25

---

## Feature Support Matrix

| Feature | sixth.py | seventh.py | eighth.py | ninth.py |
|---------|----------|------------|-----------|----------|
| **Basic Chaining** | ✅ Manual | ✅ Shorthand | ✅ Shorthand | ✅ Both |
| **Repetition** | ✅ `* N` | ✅ `* N` | ✅ `* N` | ✅ Both |
| **Transpose** | ✅ Manual | ❌ No | ✅ `transpose()` | ✅ Both |
| **Inversion** | ✅ Manual | ❌ No | ✅ `invert()` | ✅ Both |
| **Retrograde** | ✅ Manual | ❌ No | ✅ `retrograde()` | ✅ Both |
| **Custom Transform** | ✅ Yes | ❌ No | ⚠️ Limited | ✅ Yes |
| **Custom Algorithms** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Snippet Slicing** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Pre-Validation** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Mix Approaches** | ❌ No | ❌ No | ❌ No | ✅ **YES** |

---

## When to Use Each Approach

### Use sixth.py Style When:
- ✅ Learning the framework
- ✅ Need to see every step explicitly
- ✅ Debugging complex transformations
- ✅ Building custom helper functions

**Example Scenario:** "I'm experimenting with a new transformation algorithm and want to see each step."

---

### Use seventh.py Style When:
- ✅ Quick prototypes
- ✅ Simple compositions (no transformations)
- ✅ Educational examples
- ✅ Testing basic structure

**Example Scenario:** "I need to quickly sketch a 4-bar phrase with simple repetition."

---

### Use eighth.py Style When:
- ✅ Need transformations but want concise code
- ✅ Standard transformations are sufficient
- ✅ All voices follow similar patterns
- ✅ Readability is priority

**Example Scenario:** "I'm creating a fugue with transposed and inverted entries."

---

### Use ninth.py Style When:
- ✅ **Real-world compositions** ← MOST COMMON
- ✅ Mix simple + complex parts
- ✅ Need custom logic for some voices
- ✅ Want both control and convenience
- ✅ Building production-ready pieces

**Example Scenario:** "My melody needs a custom algorithm, but the accompaniment is just a simple ostinato."

---

## Evolution Timeline

```
sixth.py (2024)
    ↓
    Identified: "Manual chaining is verbose for simple patterns"
    ↓
seventh.py (2024)
    ↓
    Identified: "Shorthand is great, but can't do transformations"
    ↓
eighth.py (Oct 2025)
    ↓
    Identified: "Transformations work in shorthand, but need programmatic control too"
    ↓
ninth.py (Oct 2025) ← CURRENT RECOMMENDED APPROACH
    ↓
    Proved: "Both approaches can coexist seamlessly"
```

---

## Complexity vs. Flexibility Chart

```
Flexibility ↑
    │
    │  ninth.py ●────────────────── (Hybrid: Maximum flexibility)
    │            │
    │            │
    │  sixth.py ●                   (Pure programmatic)
    │       │    │
    │       │    │  eighth.py ●     (Shorthand + transformations)
    │       │         │
    │       │         │
    │  seventh.py ●───┘             (Pure shorthand)
    │
    └──────────────────────────────→ Conciseness
```

**Key Insight:** ninth.py provides **maximum flexibility** (like sixth.py) while maintaining **conciseness** for simple parts (like seventh.py/eighth.py).

---

## Migration Guide

### From sixth.py → ninth.py

**Before (sixth.py):**
```python
# Everything programmatic
soprano_part = data_to_part(soprano_data)
alto_part = data_to_part(alto_data)
tenor_part = data_to_part(tenor_data)
bass_part = data_to_part(bass_data)

# Manual repetition
bass_events = extract_data_from_part(bass_part) * 4
```

**After (ninth.py):**
```python
# Complex parts: Keep programmatic
soprano_events = generate_soprano_programmatically()
alto_events = generate_alto_programmatically()

# Simple parts: Switch to shorthand
harmony = build_score_from_assignments(
    {'Tenor': 'TENOR', 'Bass': 'BASS * 4'},
    voice_lookup
)
```

**Benefit:** Reduced code for simple parts, keep control for complex parts.

---

### From seventh.py → ninth.py

**Before (seventh.py):**
```python
# All shorthand, but can't do custom transformations
VOICE_ASSIGNMENTS = {
    'Soprano': 'THEME',  # ← Want to invert, but seventh.py can't
    'Bass': 'BASS * 4'
}
```

**After (ninth.py):**
```python
# Complex part: Use programmatic
soprano_events = generate_soprano_with_inversion()

# Simple part: Keep shorthand
VOICE_ASSIGNMENTS = {'Bass': 'BASS * 4'}
bass = build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
```

**Benefit:** Gain transformations and custom logic while keeping shorthand for simple parts.

---

### From eighth.py → ninth.py

**Before (eighth.py):**
```python
# All shorthand, but limited to available transformations
VOICE_ASSIGNMENTS = {
    'Soprano': 'invert(THEME)',  # ← Can't specify inversion axis
    'Bass': 'BASS * 4'
}
```

**After (ninth.py):**
```python
# When need custom args: Use programmatic
def generate_soprano():
    # Invert around G4 instead of default C4
    return invert_part(theme_part, 'G4')

# When shorthand is enough: Keep shorthand
VOICE_ASSIGNMENTS = {'Bass': 'BASS * 4'}
```

**Benefit:** Gain custom parameters and algorithms while keeping shorthand convenience.

---

## Real-World Scenarios

### Scenario 1: Fugue
```python
# ninth.py approach (HYBRID)
def build_score_data():
    # Subject: Custom algorithm
    subject = generate_fugue_subject()
    
    # Entries: Shorthand transformations
    entries = build_score_from_assignments(
        {
            'Voices': {
                'Alto': 'transpose(SUBJECT, -5)',
                'Tenor': 'transpose(SUBJECT, -12)',
                'Bass': 'transpose(SUBJECT, -19)',
            }
        },
        {'SUBJECT': subject}
    )
    
    # Combine
    return combine_all(subject, entries)
```

**Why hybrid?** Subject needs custom generation, but entries are standard transpositions.

---

### Scenario 2: Minimalist Piece
```python
# eighth.py approach (PURE SHORTHAND)
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Piano RH': 'PATTERN * 16',
        'Piano LH': 'BASS * 16',
    }
}

def build_score_data():
    return build_score_from_assignments(VOICE_ASSIGNMENTS, voice_lookup)
```

**Why pure shorthand?** Simple repetitive patterns, no custom logic needed.

---

### Scenario 3: Experimental Piece
```python
# sixth.py approach (PURE PROGRAMMATIC)
def build_score_data():
    # Every voice generated by custom algorithm
    soprano = markov_chain_generator()
    alto = cellular_automaton()
    tenor = lindenmayer_system()
    bass = fractal_generator()
    
    return combine_all(soprano, alto, tenor, bass)
```

**Why pure programmatic?** Everything is algorithmic, no standard patterns.

---

## Summary Table

| Aspect | sixth.py | seventh.py | eighth.py | **ninth.py** |
|--------|----------|------------|-----------|--------------|
| **Philosophy** | Show all steps | Declarative simplicity | Transformations | **Best of both** |
| **Learning Curve** | Medium | Low | Low | Medium |
| **Code Length** | Longest | Shortest | Short | **Optimal** |
| **Flexibility** | High | Low | Medium | **Highest** |
| **Transformations** | Manual | None | Built-in | **Both** |
| **Custom Logic** | Yes | No | Limited | **Yes** |
| **Pre-Validation** | No | No | Yes | **Yes** |
| **Recommended For** | Learning | Prototypes | Simple pieces | **Production** |

---

## Final Recommendation

### For New Users:
1. Start with **seventh.py** (understand shorthand)
2. Try **eighth.py** (learn transformations)
3. Graduate to **ninth.py** (mix both approaches)

### For Production:
→ **Use ninth.py as your template**

### For Teaching:
→ **Show sixth.py first**, then seventh.py, then ninth.py (progression)

### For Quick Sketches:
→ **Use eighth.py** (fastest for simple pieces)

---

## The Bottom Line

**ninth.py proves that Codempose gives you OPTIONS, not RESTRICTIONS:**

- ✅ Want pure programmatic? → Available
- ✅ Want pure shorthand? → Available
- ✅ Want to mix both? → **Recommended**
- ✅ Want to switch mid-composition? → Easy

**The framework adapts to YOUR needs, not the other way around.** 🎼
