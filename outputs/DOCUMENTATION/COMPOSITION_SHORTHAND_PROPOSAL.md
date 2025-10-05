# Musical Structure Shorthand - Design Proposal

## Overview
A simple, human-readable notation to declare musical structures that automatically generates the programmatic chaining code.

## Proposed Shorthand Syntax

### Basic Format
```python
# COMPOSITION_STRUCTURE: Human-readable musical blueprint
COMPOSITION_STRUCTURE = """
Melody:
  Soprano = V1
  Alto = V1 + V2

Harmony:
  Tenor = V3
  Bass = V4
"""
```

### Shorthand Operators

| Operator | Meaning | Python Equivalent |
|----------|---------|-------------------|
| `V1` | Voice 1 snippet | `voice1_events` |
| `V1 + V2` | Sequential chain | `voice1_events + voice2_events` |
| `V1 * 3` | Repeat 3 times | `voice1_events * 3` |
| `[V1, V2, V1]` | Explicit sequence | `voice1_events + voice2_events + voice1_events` |
| `V1 \| V2` | Alternating bars | (custom logic) |

## Examples

### Example 1: Simple SATB
```python
COMPOSITION_STRUCTURE = """
Melody:
  Soprano = V1
  Alto = V2

Harmony:
  Tenor = V3
  Bass = V4
"""
```

**Generates:**
```python
score_data['parts'] = {
    'Melody': {
        'Soprano': voice1_events,
        'Alto': voice2_events,
    },
    'Harmony': {
        'Tenor': voice3_events,
        'Bass': voice4_events,
    }
}
```

### Example 2: Chain with Repetition
```python
COMPOSITION_STRUCTURE = """
Melody:
  Soprano = V1 + V2 + V1
  Alto = V2 * 2

Harmony:
  Bass = V3
"""
```

**Generates:**
```python
score_data['parts'] = {
    'Melody': {
        'Soprano': voice1_events + voice2_events + voice1_events,  # ABA form
        'Alto': voice2_events * 2,  # Repeat twice
    },
    'Harmony': {
        'Bass': voice3_events,
    }
}
```

### Example 3: Complex Chaining
```python
COMPOSITION_STRUCTURE = """
Melody:
  Soprano = V_intro + V_theme * 2 + V_coda
  Alto = V_theme * 4

Harmony:
  Tenor = V_harmony_a + V_harmony_b
  Bass = V_bass * 2
"""
```

**Generates:**
```python
score_data['parts'] = {
    'Melody': {
        'Soprano': v_intro_events + (v_theme_events * 2) + v_coda_events,
        'Alto': v_theme_events * 4,
    },
    'Harmony': {
        'Tenor': v_harmony_a_events + v_harmony_b_events,
        'Bass': v_bass_events * 2,
    }
}
```

## Alternative Shorthand: JSON-like

### Compact Object Notation
```python
COMPOSITION_STRUCTURE = {
    'Melody': {
        'Soprano': ['V1', 'V2', 'V1'],  # List = sequential chain
        'Alto': ['V2', 'repeat:2'],      # Special directive
    },
    'Harmony': {
        'Tenor': ['V3'],
        'Bass': ['V4'],
    }
}
```

## Alternative Shorthand: Pattern String

### Musical Pattern Language
```python
# Compact one-liner patterns
MELODY_SOPRANO = "V1 + V2 + V1"        # ABA form
MELODY_ALTO = "V2 * 2"                 # Repeat
HARMONY_TENOR = "V3"                   # Single snippet
HARMONY_BASS = "V4a + V4b"             # Chain two bass patterns
```

## Recommended: Hybrid Approach

Combine readability with Python's natural syntax:

```python
# ============================================================================
# COMPOSITION STRUCTURE (Station 3 Shorthand)
# ============================================================================

# Define voice assignments using simple expressions
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'V1 + V2',          # Chain Voice 1 + Voice 2
        'Alto': 'V2 * 2',              # Repeat Voice 2 twice
    },
    'Harmony': {
        'Tenor': 'V3',                 # Single voice
        'Bass': 'V4',                  # Single voice
    }
}

# Auto-generate build_score_data() from this structure
```

## Converter Function

```python
def parse_voice_assignment(expression: str, voice_lookup: dict) -> list:
    """
    Convert shorthand expression to event list.
    
    Examples:
        'V1' -> voice1_events
        'V1 + V2' -> voice1_events + voice2_events
        'V1 * 3' -> voice1_events * 3
        'V1 + V2 + V1' -> voice1_events + voice2_events + voice1_events
    
    Args:
        expression: Shorthand string (e.g., 'V1 + V2')
        voice_lookup: Dict mapping 'V1' -> voice1_events
    
    Returns:
        Combined event list
    """
    import re
    
    # Split by + operator
    parts = [p.strip() for p in expression.split('+')]
    result = []
    
    for part in parts:
        # Check for repetition (V1 * 3)
        if '*' in part:
            voice_name, count = part.split('*')
            voice_name = voice_name.strip()
            count = int(count.strip())
            result.extend(voice_lookup[voice_name] * count)
        else:
            # Simple voice reference
            result.extend(voice_lookup[part])
    
    return result


def build_score_from_assignments(voice_assignments: dict, voice_data: dict) -> dict:
    """
    Auto-generate score_data from VOICE_ASSIGNMENTS shorthand.
    
    Args:
        voice_assignments: Structure definition (see above)
        voice_data: Parsed voice data {'V1': voice1_events, ...}
    
    Returns:
        Complete score_data structure
    """
    parts = {}
    
    for staff_name, voices in voice_assignments.items():
        parts[staff_name] = {}
        for voice_name, expression in voices.items():
            parts[staff_name][voice_name] = parse_voice_assignment(expression, voice_data)
    
    return {'parts': parts}
```

## Usage Pattern

### In Study File (e.g., sixth.py)

```python
# ============================================================================
# VOICE SNIPPETS (Station 1)
# ============================================================================
VOICE_1_LILY = r"\relative c'' { c4 d e f | }"
VOICE_1_TINY = "c'4 d'4 e'4 f'4"

VOICE_2_LILY = r"\relative c' { e4 f g a | }"
VOICE_2_TINY = "e4 f4 g4 a4"

# ... more voices ...


# ============================================================================
# COMPOSITION STRUCTURE (Station 3 Shorthand)
# ============================================================================
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'V1',           # 4 bars
        'Alto': 'V1 + V2',         # 8 bars (chained)
    },
    'Harmony': {
        'Tenor': 'V3',
        'Bass': 'V4',
    }
}


# ============================================================================
# COMPOSITION FUNCTION (Auto-generated from shorthand)
# ============================================================================
def build_score_data():
    from lilypond_parser import parse_lilypond_to_data
    from project_template import build_score_from_assignments  # Helper
    
    # Parse all voices
    voice_data = {
        'V1': parse_lilypond_to_data(VOICE_1_LILY, 'Voice 1')['parts']['Voice 1'],
        'V2': parse_lilypond_to_data(VOICE_2_LILY, 'Voice 2')['parts']['Voice 2'],
        'V3': parse_lilypond_to_data(VOICE_3_LILY, 'Voice 3')['parts']['Voice 3'],
        'V4': parse_lilypond_to_data(VOICE_4_LILY, 'Voice 4')['parts']['Voice 4'],
    }
    
    # Auto-build from assignments
    score_data = build_score_from_assignments(VOICE_ASSIGNMENTS, voice_data)
    
    # Add metadata
    score_data['metadata'] = {
        'title': 'Generated from VOICE_ASSIGNMENTS',
        # ...
    }
    
    return score_data
```

## Benefits

### ✅ Advantages:
1. **Readable** - Musical structure visible at a glance
2. **Declarative** - Say "what" not "how"
3. **Maintainable** - Easy to modify structure
4. **Pythonic** - Uses familiar operators (`+`, `*`)
5. **Auto-documented** - Structure is self-documenting

### 📊 Comparison:

**Before (Programmatic):**
```python
voice_chained = voice1_events + voice2_events
soprano = voice1_events
alto = voice_chained
```

**After (Shorthand):**
```python
VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'V1',
        'Alto': 'V1 + V2',
    }
}
```

## Recommended Implementation

### Phase 1: Simple String Parser
- Support: `V1`, `V1 + V2`, `V1 * 3`
- Add to `project_template.py`

### Phase 2: Enhanced Syntax
- Support: `[V1, V2, V1]` for explicit sequences
- Support: Variables like `theme`, `variation`

### Phase 3: Musical Operations
- Support: `transpose(V1, +5)` for transposition
- Support: `invert(V1)` for melodic inversion
- Support: `retrograde(V1)` for reverse playback

## Question for You

Which shorthand style do you prefer?

**Option A: String Expression**
```python
'V1 + V2'
'V1 * 3'
```

**Option B: List Notation**
```python
['V1', 'V2', 'V1']  # ABA
['V2', 'repeat:2']
```

**Option C: Dict with Directives**
```python
{'chain': ['V1', 'V2'], 'repeat': 'V3:2'}
```

I recommend **Option A** (string expressions) because it's:
- Most readable
- Closest to mathematical notation
- Easy to parse with simple split/eval logic
- Extensible for future operations

Would you like me to implement the parser and integrate it into `sixth.py` as a demonstration?
