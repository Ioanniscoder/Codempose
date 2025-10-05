# Voice Chaining Guide

## Overview
This guide explains how to chain musical snippets programmatically at **Station 3** (composition logic) to build longer musical phrases from smaller building blocks.

## The Three Stations

### Station 1: Source Snippets (Top of File)
Define separate, reusable musical fragments:
```python
VOICE_1_LILY = r"\relative c'' { c4 d e f | g2 e4 c | }"
VOICE_1_TINY = "c'4 d'4 e'4 f'4 g'2 e'4 c'4"

VOICE_2_LILY = r"\relative c' { e4 f g a | b2 c4 g | }"
VOICE_2_TINY = "e4 f4 g4 a4 b2 c'4 g4"
```

**Key principle:** Snippets remain separate and independent. Each can be tested, modified, and reused individually.

### Station 2: Snippet Pairs
Both LILY and TINY formats coexist for visual correlation:
- `VOICE_X_LILY` - LilyPond format (relative notation)
- `VOICE_X_TINY` - TinyNotation format (absolute pitches)
- `PROMOTE_TO_TINYNOTATION` toggle controls which format is dominant

### Station 3: Composition Logic (build_score_data)
**This is where chaining happens programmatically:**

```python
def build_score_data():
    from lilypond_parser import parse_lilypond_to_data
    
    # Parse each snippet independently
    voice1_data = parse_lilypond_to_data(VOICE_1_LILY, part_name='Voice 1')
    voice2_data = parse_lilypond_to_data(VOICE_2_LILY, part_name='Voice 2')
    
    # Extract event lists
    voice1_events = voice1_data['parts']['Voice 1']
    voice2_events = voice2_data['parts']['Voice 2']
    
    # ========================================
    # PROGRAMMATIC CHAINING
    # ========================================
    # Chain snippets by concatenating event lists
    voice_chained = voice1_events + voice2_events  # 4 bars + 4 bars = 8 bars
    
    # Build score structure
    score_data = {
        'metadata': {...},
        'parts': {
            'Melody': {
                'Voice 1': voice1_events,      # Original (4 bars)
                'Voice 2': voice_chained,      # Chained (8 bars)
            }
        }
    }
    return score_data
```

## Chaining Patterns

### 1. Simple Concatenation
```python
# Chain two snippets sequentially
melody_AB = snippet_A_events + snippet_B_events
```

### 2. Repetition
```python
# Repeat a snippet
melody_repeated = snippet_A_events + snippet_A_events + snippet_A_events
```

### 3. Alternation (A-B-A form)
```python
# Create ABA structure
melody_aba = snippet_A_events + snippet_B_events + snippet_A_events
```

### 4. Multi-snippet Chain
```python
# Chain many snippets into long phrase
melody_chain = (snippet_intro_events + 
                snippet_theme_events + 
                snippet_variation_events + 
                snippet_coda_events)
```

### 5. Conditional Chaining
```python
# Build different structures based on composition rules
if use_variation:
    melody = theme_events + variation_events
else:
    melody = theme_events + theme_events  # Repeat instead
```

## Multi-Voice Chaining

Each voice in a multi-voice structure can be independently chained:

```python
score_data = {
    'parts': {
        'Melody': {
            # Soprano: intro + theme (chained)
            'Soprano': intro_events + theme_events,
            # Alto: theme repeated twice
            'Alto': theme_events + theme_events,
        },
        'Harmony': {
            # Tenor: variation chain
            'Tenor': var1_events + var2_events + var3_events,
            # Bass: simple bass line
            'Bass': bass_events,
        }
    }
}
```

## Benefits of Station 3 Chaining

### ✅ Advantages:
1. **Modular snippets** - Each snippet can be tested independently
2. **Reusability** - Same snippet can appear in multiple chains
3. **Flexibility** - Easy to rearrange, repeat, or modify structure
4. **Visibility** - Both LILY and TINY formats preserved in comments
5. **Programmatic control** - Use Python logic (loops, conditions, transformations)

### ❌ Avoid Snippet-Level Chaining:
```python
# DON'T do this at Station 1:
VOICE_CHAINED_LILY = VOICE_1_LILY + " " + VOICE_2_LILY  # ❌ Hard to maintain
```

**Why?** Loses modularity, harder to debug, obscures original snippets.

## Example: sixth.py

The `sixth.py` study file demonstrates this pattern:

**Station 1 (Snippets):**
- `VOICE_1_LILY` / `VOICE_1_TINY` - 4 bars
- `VOICE_2_LILY` / `VOICE_2_TINY` - 4 bars
- `VOICE_3_LILY` / `VOICE_3_TINY` - 4 bars
- `VOICE_4_LILY` / `VOICE_4_TINY` - 4 bars

**Station 3 (Chaining):**
```python
# Parse each independently
voice1_events = parse_lilypond_to_data(VOICE_1_LILY)['parts']['Voice 1']
voice2_events = parse_lilypond_to_data(VOICE_2_LILY)['parts']['Voice 2']

# Chain programmatically
voice_chained_events = voice1_events + voice2_events  # 8 bars total
```

**Result:**
- Voice 1: 4 bars (original)
- Voice Chained: 8 bars (Voice 1 + Voice 2)
- Both rendered in polyphonic texture on same staff

## Generated Output

The `.ly` file comments show:
- Original snippets (both LILY and TINY)
- Documentation of chaining logic
- Visual correlation between source and result

The `.pdf` shows:
- Chained voice has longer phrase (8 bars vs 4 bars)
- Proper polyphonic notation with stem directions

## Best Practices

1. **Keep snippets atomic** - Each snippet should be a complete musical idea
2. **Name clearly** - Use descriptive names (intro, theme, variation, coda)
3. **Comment chains** - Document the chaining logic in build_score_data()
4. **Test incrementally** - Parse and test each snippet before chaining
5. **Use metadata** - Preserve original snippet info in score_data['metadata']['original_input']

## Advanced Techniques

### Event Manipulation
```python
# Chain with transformations
voice_chain = (
    snippet_A_events +
    transpose_events(snippet_B_events, semitones=5) +  # Transpose before chaining
    snippet_A_events  # Return to original
)
```

### Dynamic Assembly
```python
# Build from pattern
pattern = ['A', 'B', 'A', 'C', 'A', 'B']
snippets = {'A': theme, 'B': var1, 'C': var2}
melody = sum([snippets[p] for p in pattern], [])  # Chain all
```

---

**Conclusion:** Programmatic chaining at Station 3 provides maximum flexibility while preserving snippet independence and dual-format visibility. This is the foundation for algorithmic composition in Codempose.
