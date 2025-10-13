# Codempose System Summary
## Quick Reference Guide

**Date**: October 7, 2025

---

## The Four Stations (Quick Reference)

### Station 1: LilyPond Shorthand
**When**: Starting a new composition, simple melodies  
**Syntax**: `SOURCE_MELODY_LILY = r"\relative c' { c4 d e f }"`  
**Output**: Parses to canonical score_data format

### Station 2: TinyNotation
**When**: After promotion, cleaner format preference  
**Syntax**: `SOURCE_MELODY_TINY = "4/4 c4 d4 e4 f4"`  
**Promotion**: Set `PROMOTE_TO_TINYNOTATION = True`

### Station 3: Programmatic Shorthand
**When**: Need transformations, algorithmic patterns  
**Syntax**: `'THEME + transpose(THEME, 7) + invert(THEME)'`  
**Available**: transpose(), invert(), retrograde(), chaining (+), repetition (*)

### Station 4: Full Music21 Programming
**When**: Complex algorithms, custom logic, analysis  
**Syntax**: Full Python with music21 library  
**Pattern**: parse → data_to_part → transform → extract → score_data

---

## Decision Tree: Which Station?

```
Need custom algorithms/analysis? 
├─ YES → Station 4 (Full Music21)
└─ NO ↓

Need transformations (transpose/invert)?
├─ YES ↓
│  ├─ Simple patterns? → Station 3 (Shorthand)
│  └─ Complex logic? → Station 4 (Music21)
└─ NO ↓

Starting from notation?
├─ YES → Station 1 (LilyPond)
└─ NO → Station 2 (TinyNotation)
```

---

## Key Data Structure: score_data

```python
score_data = {
    'metadata': {
        'title': str,
        'time_signature': str,
        'key_signature': {'tonic': str, 'mode': str},
        'tempo': int
    },
    'parts': {
        'Part Name': [
            {
                'type': 'note' | 'chord' | 'rest',
                'step': str,      # 'c', 'd', etc.
                'octave': int,    # 4 = middle C
                'alter': int,     # -1, 0, 1
                'ql': float       # Quarter lengths
            },
            # ... more events
        ]
    }
}
```

---

## Common Patterns

### Pattern 1: Station 1 Only (Simple)
```python
SOURCE_MELODY_LILY = r"\relative c' { c4 d e f }"
# That's it! Pipeline handles the rest.
```

### Pattern 2: Station 3 (Shorthand Transformations)
```python
THEME_LILY = r"\relative c' { c4 d e f }"

VOICE_ASSIGNMENTS = {
    'Melody': {
        'Soprano': 'THEME + transpose(THEME, 7)',
    }
}

def build_score_data():
    from composition_shorthand import build_score_from_assignments
    # Parse snippets
    voice_data = {...}
    return build_score_from_assignments(VOICE_ASSIGNMENTS, voice_data)
```

### Pattern 3: Station 4 (Music21 Transformations)
```python
def build_score_data():
    # Parse
    theme_data = parse_lilypond_to_data(SOURCE_THEME_LILY, 'Theme')
    
    # Convert to music21
    theme_part = data_to_part(theme_data['parts']['Theme'], metadata)
    
    # Transform
    transposed = theme_part.transpose('P5')
    
    # Extract back
    events = extract_data_from_part(transposed)
    
    return {'metadata': metadata, 'parts': {'Melody': events}}
```

### Pattern 4: Hybrid (Mix Station 3 + 4)
```python
def build_score_data():
    # Complex voice: Station 4 (full control)
    soprano_part = data_to_part(soprano_events, metadata)
    soprano = custom_algorithm(soprano_part)
    
    # Simple voice: Station 3 (brevity)
    bass = parse_voice_assignment('BASS * 4', voice_lookup)
    
    return {
        'parts': {
            'Soprano': extract_data_from_part(soprano),  # Station 4
            'Bass': bass                                  # Station 3
        }
    }
```

---

## Study File Progression

| Study | Focus | Station | Key Learning |
|-------|-------|---------|--------------|
| first.py | Basic template | 1, 4 | Melody + harmony, transformations |
| second.py | Chordify | 1, 4 | Generate harmony from melody |
| third.py | Reusable template | 1, 4 | build_part() pattern |
| fourth.py | Minor key | 1, 4 | Key-independent system |
| fifth.py | Tracking | 1 | Token-level provenance |
| sixth.py | Polyphony | 1, 3 | Multi-voice, manual chaining |
| seventh.py | Shorthand | 1, 3 | Declarative VOICE_ASSIGNMENTS |
| eighth.py | Transformations | 1, 3 | transpose(), invert(), retrograde() |
| **ninth.py** | **Hybrid** | **1, 3, 4** | **Mix stations in one composition** |
| **tenth.py** | **Documentation** | **1, 3, 4** | **Programmatic → LilyPond feedback** |

---

## Core Functions Reference

### Parsing (Station 1 → score_data)
```python
from lilypond_parser import parse_lilypond_to_data

score_data = parse_lilypond_to_data(lily_string, part_name='Melody')
# Returns: {'metadata': {...}, 'parts': {'Melody': [events...]}}
```

### Conversion (score_data ↔ music21.Part)
```python
from music_data import data_to_part, extract_data_from_part

# score_data → music21.Part
part = data_to_part(events, metadata)

# music21.Part → score_data
events = extract_data_from_part(part)
```

### Shorthand (Station 3)
```python
from composition_shorthand import parse_voice_assignment, transpose_events, invert_events

# Parse expression
soprano = parse_voice_assignment('THEME + transpose(THEME, 7)', voice_lookup)

# Direct transformation
transposed = transpose_events(events, 5)  # +5 semitones
inverted = invert_events(events, 'c4')    # Around C4
```

### Documentation (Station 4 → Station 1 feedback)
```python
from voice_documentation import register_and_document_voice

# Generate programmatically
alto_voice = transpose_events(soprano, -7)

# Document it (appears in .ly file)
register_and_document_voice('ALTO_GENERATED', alto_voice, voice_lookup, metadata)
```

---

## Pipeline Execution Priority

When you run `run_pipeline_from_file(__file__)`, it checks in this order:

1. **Priority 1**: `build_score_data()` function (Stations 3 or 4)
2. **Priority 2**: `SOURCE_MELODY_TINY` variable (Station 2)
3. **Priority 3**: `SOURCE_MELODY_LILY` variable (Station 1)
4. **Priority 4**: `build_part()` function (Alternative entry)

**Recommendation**: Use `build_score_data()` for composition logic (highest priority)

---

## Promotion Principle

### Start Simple, Promote as Needed

**Level 1**: Just notation → Station 1  
**Level 2**: Need simpler format → Station 2 (set PROMOTE_TO_TINYNOTATION)  
**Level 3**: Need transformations → Station 3 (add VOICE_ASSIGNMENTS)  
**Level 4**: Need custom logic → Station 4 (add build_score_data with music21)

### You can go backwards too!

**Station 4 → Station 1**: Use `register_and_document_voice()` (tenth.py)
- Generate programmatically
- Document output as LilyPond
- Copy snippet back to Station 1 for manual editing

---

## Critical Insights

### From Ninth Study (Hybrid Approach)
**Lesson**: Not all voices need the same approach!
- Complex parts → Station 4 (full Python control)
- Simple parts → Station 3 (declarative brevity)
- **Both can coexist in the same composition**

### From Tenth Study (Documentation Feedback)
**Lesson**: Programmatic results should be visible!
- Generate algorithmically (Station 4)
- Document as LilyPond (appears in .ly file)
- Study the output, copy to new composition (Station 1)
- **Closes the creative loop**

---

## Quick Troubleshooting

### "Parser error: Cannot parse pitch"
- Check LilyPond syntax (missing quotes, braces)
- Ensure `\relative` has base pitch: `\relative c' {`

### "No valid entry point found"
- Add one of: `build_score_data()`, `SOURCE_MELODY_LILY`, `SOURCE_MELODY_TINY`, or `build_part()`

### "Warning: Large leap detected"
- Relative mode calculated unexpected octave
- Check octave jumps in your melody
- Use explicit octave marks if needed: `c'4 c''4`

### Shorthand expression not working
- Ensure voices are in `voice_lookup` before using
- Check syntax: `'THEME + transpose(THEME, 5)'` (with quotes!)
- Available: +, *, transpose(), invert(), retrograde()

---

## File Organization

```
/workspaces/Codempose/
├── Core Library (don't edit unless extending)
│   ├── project_template.py       # Pipeline orchestrator
│   ├── music_data.py              # Bidirectional conversion
│   ├── lilypond_parser.py         # Main parser
│   ├── lily_to_tiny.py            # LilyPond → TinyNotation
│   ├── composition_shorthand.py   # Shorthand transformations
│   └── voice_documentation.py     # Documentation feedback
│
├── Study Files (learn from these)
│   ├── first.py - tenth.py        # Progressive examples
│   └── Read ninth.py and tenth.py for advanced patterns
│
└── Your Compositions
    ├── Start with Station 1 (LilyPond)
    ├── Add build_score_data() when needed
    └── Mix stations as appropriate
```

---

## Next Steps

1. **Read**: `CODE_FLOW_ANALYSIS.md` (comprehensive guide)
2. **Study**: Run `first.py` through `tenth.py` in order
3. **Practice**: Create your own composition starting with Station 1
4. **Experiment**: Try hybrid approach (ninth.py pattern)
5. **Document**: Use voice documentation (tenth.py pattern)

---

## Remember

- **Start at Station 1** (simple notation)
- **Promote when needed** (don't over-engineer)
- **Mix stations freely** (hybrid approach works!)
- **Document programmatic voices** (close the loop)
- **The system is complete** (all four stations implemented)

---

**For full details, see**: `CODE_FLOW_ANALYSIS.md`
