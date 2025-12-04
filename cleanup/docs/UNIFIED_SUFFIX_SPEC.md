# Unified Suffix Container Specification

**Version:** 1.0  
**Date:** October 13, 2025  
**Status:** Implementation Ready

---

## Mission Statement

Implement a unified musical shorthand parser with a **suffix container `()` for zero-duration modifiers**. This creates a clear, predictable grammar that enables rich musical expression without notation conflicts.

---

## Grammar Design Philosophy

**Core Principle:** All zero-duration modifiers are placed in a suffix container `()` after the note they affect.

**Exception:** Time-based events (grace notes, ties) use prefix/suffix `~` because they inherently modify duration or timing.

---

## Complete Syntax Table

| Feature Type | Description | Syntax Example | QL Value |
|:-------------|:------------|:---------------|:---------|
| **Suffix Container `()`** | Zero-duration modifiers | | |
| ➡️ Articulation | Staccato, Tenuto, Accent | `c4(.)` `d2(-)` `e8(>)` | normal |
| ➡️ Dynamics | Volume instructions | `g4(p)` `a4(f)` `b2(<)` | normal |
| ➡️ Tracking | Identifier tags | `c4(themeA)` | normal |
| ➡️ Combined | Multiple modifiers | `c4(themeA, ., p)` | normal |
| **Time-Based `~`** | Duration-affecting events | | |
| ➡️ Grace Note | Zero-duration ornament | `~g16 a2` | 0.0 (grace) |
| ➡️ Tie | Connect same pitches | `c4~ c4` | merged |

---

## Tokenizer Requirements

### Atomic Token Recognition

The tokenizer must recognize these as **single tokens**:

```python
# Valid tokens:
"c4"           # Plain note
"c4(.)"        # Note with articulation
"c4(p, .)"     # Note with dynamics and articulation
"c4(themeA, ., p)"  # Note with tracking, articulation, dynamics
"~g16"         # Grace note
"c4~"          # Tied note
"r4"           # Rest
```

### Tokenizer Pattern (Pseudocode)

```regex
# Pattern structure:
~?                  # Optional grace prefix
[a-g]               # Note letter
(accidentals)?      # Optional accidentals (is, es, #, b, etc.)
[',]*               # Optional octave markers
\d*\.?              # Optional duration
(\([^)]+\))?        # Optional suffix container
~?                  # Optional tie suffix
```

---

## Token Parser Requirements

### Parsing Steps

For a token like `c4(themeA, ., p)`:

1. **Extract base note:** `c4`
   - Pitch: `c`
   - Duration: `4`
   - QL: `1.0`

2. **Detect suffix container:** `(themeA, ., p)`
   - Extract content: `themeA, ., p`
   - Split by comma: `['themeA', ' .', ' p']`
   - Strip whitespace from each

3. **Classify modifiers:**
   ```python
   for modifier in modifiers:
       if modifier in ['.', '-', '>']:
           # Articulation
           articulations.append(ARTICULATION_MAP[modifier])
       elif modifier in ['p', 'pp', 'f', 'ff', 'mf', 'mp', '<', '>']:
           # Dynamic
           dynamics = modifier
       else:
           # Tracking identifier
           tracker = modifier
   ```

### Articulation Mapping

```python
ARTICULATION_MAP = {
    '.': 'staccato',
    '-': 'tenuto',
    '>': 'accent'
}
```

### Dynamic Symbols

```python
DYNAMIC_SYMBOLS = ['ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', '<', '>']
```

---

## Event Dictionary Structure

### Standard Note Event

```json
{
  "type": "note",
  "step": "C",
  "octave": 4,
  "ql": 1.0,
  "alter": 0,
  "original_token": "c4(themeA, ., p)",
  "position": 0,
  "articulations": ["staccato"],
  "dynamics": "p",
  "tracker": "themeA"
}
```

### Field Specifications

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `type` | string | ✓ | "note" or "rest" |
| `step` | string | ✓ | Note letter (A-G) |
| `octave` | int | ✓ | Octave number |
| `ql` | float | ✓ | Quarter length duration |
| `alter` | int | ✓ | Semitone alteration (-2, -1, 0, 1, 2) |
| `original_token` | string | ✓ | Original input token |
| `position` | int | ✓ | Token index in sequence |
| `articulations` | list | optional | List of articulation names |
| `dynamics` | string | optional | Dynamic symbol |
| `tracker` | string | optional | Tracking identifier |
| `tie` | string | optional | "start" or "stop" |

---

## Tie Handling (Stateful)

Ties require parser state:

```python
# Parser maintains state
tie_pending = None

# When parsing c4~:
if token ends with '~':
    note_event['tie'] = 'start'
    tie_pending = note_event
    # Don't add to events yet

# When parsing next note:
if tie_pending is not None:
    if pitches match:
        # Merge durations
        tie_pending['ql'] += current_note['ql']
        current_note['tie'] = 'stop'
        # Add merged note
        events.append(tie_pending)
        tie_pending = None
```

---

## Comprehensive Test Case

### Input

```python
snippet = r"\relative c' { ~g16 a2(p, themeA, >) a2~ a2(f) r4 }"
```

### Expected Output

```json
[
  {
    "type": "note", "step": "G", "octave": 4, "ql": 0.0,
    "original_token": "~g16", "position": 0
  },
  {
    "type": "note", "step": "A", "octave": 4, "ql": 2.0,
    "original_token": "a2(p, themeA, >)", "position": 1,
    "articulations": ["accent"],
    "dynamics": "p",
    "tracker": "themeA",
    "tie": "start"
  },
  {
    "type": "note", "step": "A", "octave": 4, "ql": 2.0,
    "original_token": "a2~", "position": 2,
    "tie": "stop"
  },
  {
    "type": "note", "step": "A", "octave": 4, "ql": 2.0,
    "original_token": "a2(f)", "position": 3,
    "dynamics": "f"
  },
  {
    "type": "rest", "ql": 1.0,
    "original_token": "r4", "position": 4
  }
]
```

---

## Implementation Checklist

### Phase 1: Tokenizer Update
- [ ] Update token regex to recognize `note(content)` as atomic
- [ ] Preserve `~` prefix for grace notes
- [ ] Preserve `~` suffix for ties
- [ ] Test: `c4(.)`, `c4(p, .)`, `~g16`, `c4~`

### Phase 2: Token Parser Update
- [ ] Add `parse_suffix_container()` function
- [ ] Implement comma-split logic
- [ ] Implement modifier classification
- [ ] Update `ParsedToken` dataclass with new fields
- [ ] Test: Parse `c4(themeA, ., p)` correctly

### Phase 3: Main Parser Update
- [ ] Extract modifiers from `ParsedToken`
- [ ] Add `articulations`, `dynamics`, `tracker` to event dict
- [ ] Preserve existing tie logic
- [ ] Test: Full snippet with all features

### Phase 4: Integration Testing
- [ ] Test simple cases individually
- [ ] Test combined modifiers
- [ ] Test with ties and grace notes
- [ ] Test edge cases (empty container, spaces, etc.)

---

## Validation Criteria

Implementation is complete when:

1. ✓ Tokenizer recognizes `note(modifiers)` as single token
2. ✓ Parser correctly splits comma-separated modifiers
3. ✓ Articulations, dynamics, tracking work individually
4. ✓ Combined modifiers work: `c4(theme, ., p)`
5. ✓ Ties still work: `c4~ c4`
6. ✓ Grace notes still work: `~g16`
7. ✓ All existing tests still pass
8. ✓ Comprehensive test case passes

---

## Next: Implementation in Code

Files to modify:
1. `lily_tokenizer.py` - Update token pattern
2. `lily_token_parser.py` - Add suffix container parsing
3. `lilypond_parser.py` - Update event dictionary creation
4. Create `test_suffix_container.py` - Comprehensive tests

---

**Status:** Ready for implementation  
**Estimated Time:** 60-90 minutes  
**Risk:** Low (well-specified, orthogonal to existing features)
