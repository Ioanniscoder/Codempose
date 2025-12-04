# Parser Enhancement Plan
**Date**: October 13, 2025  
**Status**: Implementation Roadmap

## Overview

This document outlines the enhancement strategy for the Codempose parser, focusing on user-friendly notation shortcuts and essential LilyPond features.

---

## Priority 1: Custom Tuplet Notation ⭐ QUICK WIN

### Current Syntax (LilyPond)
```lilypond
\tuplet 3/2 { c8 d8 e8 }  % Triplet of eighth notes
```

### Proposed Shorthand
```
[c d e]8                  % Triplet of eighth notes (auto-detect 3/2)
[c d e f]16               % Quadruplet of sixteenth notes (auto-detect 4/3)
[c d e f g]8              % Quintuplet (auto-detect 5/4)
```

### Implementation Strategy

**1. Tokenizer Enhancement** (`lily_tokenizer.py`)
- Add regex pattern to detect `[...]/duration` notation
- Pattern: `\[([^\]]+)\](\d+\.?)`
- Auto-calculate fraction based on note count:
  - 3 notes → 3/2 (triplet)
  - 4 notes → 4/3 (quadruplet)
  - 5 notes → 5/4 (quintuplet)
  - 6 notes → 6/4 (sextuplet)
  - 7 notes → 7/4 (septuplet)

**2. Parser Integration** (`lily_token_parser.py`)
- Expand square bracket notation into note tokens
- Add tuplet ratio metadata

**3. Benefits**
- ✅ **90% shorter** than `\tuplet 3/2 { ... }`
- ✅ More intuitive: duration at end (like normal notes)
- ✅ Less nesting, cleaner code
- ✅ Backward compatible (can still use `\tuplet`)

---

## Priority 2: Ties ~ (ESSENTIAL)

### Syntax
```lilypond
c4~ c4                    % Tie across barline or for long durations
```

### Importance: **CRITICAL**
- Required for notes longer than single measure
- Common in real music (held notes, suspensions)
- Simple to implement (just a `~` after note)

### Implementation
- **Tokenizer**: Detect `~` suffix on note tokens
- **Parser**: Set `tie_start` flag on event
- **music21**: Use `note.tie = music21.tie.Tie('start')` or `'stop'`
- **LilyPond Output**: Append `~` to note token

---

## Priority 3: Slurs ( ) (HIGH VALUE)

### Syntax
```lilypond
c4( d8 e8)                % Slur over phrase
```

### Importance: **HIGH**
- Defines musical phrasing
- Essential for expressive music
- Simple syntax

### Implementation
- **Tokenizer**: Detect `(` and `)` as separate tokens or suffixes
- **Parser**: Track slur state (open/close)
- **music21**: Use `note.addSpanner(music21.spanner.Slur())`
- **LilyPond Output**: Append `(` or `)` to note tokens

---

## Priority 4: Articulations (MEDIUM)

### Common Articulations
```lilypond
c4-.     % Staccato
c4->     % Accent
c4-^     % Marcato
c4-+     % Stopped (for brass)
c4-|     % Staccatissimo
```

### Importance: **MEDIUM**
- Adds expressive detail
- Common in sheet music
- Easy to parse (suffix pattern)

### Implementation
- **Tokenizer**: Detect `-[.^>+|]` suffixes
- **Parser**: Store articulation type
- **music21**: Use `note.articulations.append(music21.articulations.Staccato())`
- **LilyPond Output**: Append articulation marker

---

## Priority 5: Dynamics (MEDIUM-LOW)

### Syntax
```lilypond
\p         % Piano (soft)
\f         % Forte (loud)
\mf        % Mezzo-forte
\crescendo % Get louder
\diminuendo % Get softer
```

### Importance: **MEDIUM-LOW**
- Important for final scores
- Not critical for compositional experiments
- Can be added manually in MuseScore

### Implementation
- **Tokenizer**: Detect `\[pf]|mf|mp|ff|pp` as directive tokens
- **Parser**: Create dynamic event
- **music21**: Use `dynamics.Dynamic('mf')`

---

## Priority 6: Chords <> (ALREADY SUPPORTED ✅)

### Current Status
✅ **Already implemented** in parser
- `<c e g>4` → Chord object with 3 pitches
- Works in both input and output

---

## Priority 7: Grace Notes (LOW)

### Syntax
```lilypond
\grace { c16 d16 }        % Grace notes (no duration)
\acciaccatura { c8 }      % Acciaccatura (slashed grace note)
\appoggiatura { c8 }      % Appoggiatura
```

### Importance: **LOW**
- Ornamental, not structural
- Complex timing calculations
- Defer until basic features complete

---

## Priority 8: Advanced Rhythms (FUTURE)

### Features to Consider
- **Dots**: `c4.` (already supported ✅)
- **Double dots**: `c4..`
- **Scaling**: `c4*2/3` (duration multiplier)
- **Partial measures**: `\partial 4` (pickup measure)

---

## Implementation Order (Recommended)

### Phase 1: Essential Features (Week 1)
1. ✅ **Custom Tuplet Notation** `[a b c]8` - Biggest usability win
2. ✅ **Ties** `c4~ c4` - Essential for real music
3. ✅ **Slurs** `c4( d8)` - Phrasing support

### Phase 2: Expressive Features (Week 2)
4. **Articulations** `c4-. c4->` - Add detail
5. **Dynamics** `\p \f \crescendo` - Volume control

### Phase 3: Advanced Features (Future)
6. Grace notes, double dots, scaling

---

## Benefits Summary

| Feature | Complexity | Impact | Priority |
|---------|-----------|--------|----------|
| **Custom Tuplets `[]`** | Low | ⭐⭐⭐⭐⭐ HUGE | 1 |
| **Ties `~`** | Low | ⭐⭐⭐⭐⭐ Essential | 2 |
| **Slurs `()`** | Low | ⭐⭐⭐⭐ High | 3 |
| **Articulations `-. -> -^`** | Low | ⭐⭐⭐ Medium | 4 |
| **Dynamics `\p \f`** | Medium | ⭐⭐ Medium | 5 |
| **Grace Notes** | High | ⭐ Low | 6 |

---

## Quick Win Analysis: Custom Tuplet Notation

### Why This is the Best First Step

**1. Maximum Impact**
- Tuplets are extremely common in modern music
- Current syntax is verbose and hard to type
- 90% reduction in characters: `\tuplet 3/2 { c8 d8 e8 }` → `[c d e]8`

**2. Minimal Complexity**
- Simple regex pattern: `\[([^\]]+)\](\d+\.?)`
- Auto-calculate ratio from note count
- No complex state tracking

**3. Immediate Validation**
- Easy to test: `[c d e]8` should produce 3 eighth-note triplets
- Visual verification in LilyPond output
- Playback verification in MIDI

**4. Builds Parser Skills**
- Teaches pattern matching
- Demonstrates token expansion (1 token → N events)
- Foundation for other shorthand features

### Example Test Case

**Input**:
```python
SOURCE = r"\relative c' { \time 4/4 c4 [d e f]8 g4 r4 }"
```

**Expected Parsing**:
- `c4` → Note C4, 1.0 QL
- `[d e f]8` → Tuplet: 3 eighth notes in time of 2
  - `d` → Note D4, 0.667 QL (2/3 of quarter note)
  - `e` → Note E4, 0.667 QL
  - `f` → Note F4, 0.667 QL
- `g4` → Note G4, 1.0 QL
- `r4` → Rest, 1.0 QL

**Expected LilyPond Output**:
```lilypond
c4 \tuplet 3/2 { d8 e8 f8 } g4 r4
```

---

## Next Steps

1. Implement custom tuplet notation (`[...]duration`)
2. Test with `thirteenth.py` study
3. Add ties support (`~`)
4. Add slurs support (`()`)
5. Document in README

---

## Notes on Parser Isolation

**CRITICAL**: All enhancements must maintain parser isolation:
- ✅ Parser outputs event dictionaries ONLY
- ✅ NO direct LilyPond string generation in parser
- ✅ Output formatting stays in `project_template.py`
- ✅ New features add fields to event dict, not output code

**Event Dictionary Extensions**:
```python
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'ql': 0.667,
    'tuplet': {'ratio': (3, 2), 'type': 'start'},  # NEW
    'tie': 'start',  # NEW
    'slur': 'start',  # NEW
    'articulation': 'staccato',  # NEW
    'dynamic': 'mf',  # NEW
}
```

This ensures extensibility without breaking existing code.
