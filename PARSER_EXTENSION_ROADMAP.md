# Parser Extension Roadmap

## Current Architecture (Isolated & Extensible)

The LilyPond parser is now cleanly isolated from output formatting:

```
Input: LilyPond String
  ↓
lily_tokenizer.py       → Tokenizes input into strings
  ↓
lily_token_parser.py    → Parses tokens into ParsedToken objects
  ↓
relative_octave_logic.py → Resolves relative octaves
  ↓
lily_to_tiny.py         → Generates ParseResult (tokens + TinyNotation inspector)
  ↓
lilypond_parser.py      → Converts tokens to event dicts
  ↓
Output: Event Dictionaries → music21 Objects
```

**Key Principle**: The parser outputs **event dictionaries**, NOT LilyPond strings. This keeps it isolated from output formatting (`project_template.py`).

---

## Parser Capabilities (Current)

### ✅ Supported Features

1. **Basic Notes**: `c4 d8 e2.`
2. **Rests**: `r4 r2.`
3. **Octave Markers**: `c' d, e''`
4. **Relative Octaves**: `\relative c' { ... }`
5. **Accidentals**: `cis des fisis beses`
6. **Durations**: `1 2. 4 8 16` (with dots)
7. **Time Signature**: `\time 6/4`
8. **Key Signature**: `\key c \major`
9. **Tempo**: `\tempo 4=90`
10. **Bar Lines**: `|` (converted to barline events)

### ❌ NOT Yet Supported (Extension Targets)

1. **Tuplets/Triplets**: `\tuplet 3/2 { c8 d8 e8 }`
2. **Grace Notes**: `\grace { c16 d16 }`
3. **Ties**: `c4~ c4`
4. **Slurs**: `c4( d8 e8)`
5. **Articulations**: `c4-. d4-> e4-^`
6. **Dynamics**: `\p \f \ff \crescendo`
7. **Chord Names**: `c4:maj7 d4:m`
8. **Complex Rhythms**: Quintuplets, sextuplets
9. **Repeats**: `\repeat volta 2 { ... }`
10. **Polyphonic Voices**: `<< { ... } \\ { ... } >>`

---

## Extension Plan: Adding Tuplet Support

### Example Target: Triplets

**LilyPond Syntax**:
```lilypond
\tuplet 3/2 { c8 d8 e8 }
```

**Expected Output**: Three eighth notes with `tuplet` metadata indicating 3:2 ratio

### Implementation Steps

#### Step 1: Extend Tokenizer (`lily_tokenizer.py`)

Current tokenizer splits on spaces. Need to recognize `\tuplet` as a special token.

**Modify**: Add pattern recognition for `\tuplet N/M { ... }`

```python
def tokenize_lilypond(lily_str):
    """Enhanced tokenizer with tuplet support."""
    tokens = []
    i = 0
    while i < len(lily_str):
        # Check for tuplet directive
        if lily_str[i:].startswith('\\tuplet'):
            # Extract: \tuplet 3/2 { c8 d8 e8 }
            match = re.match(r'\\tuplet\s+(\d+)/(\d+)\s*\{([^}]+)\}', lily_str[i:])
            if match:
                num = int(match.group(1))
                denom = int(match.group(2))
                content = match.group(3).strip()
                
                # Create a tuplet token
                tokens.append({
                    'type': 'tuplet',
                    'ratio': (num, denom),
                    'content': content,
                    'original': match.group(0)
                })
                i += len(match.group(0))
                continue
        
        # ... existing tokenization logic ...
    
    return tokens
```

#### Step 2: Extend Token Parser (`lily_token_parser.py`)

Add tuplet parsing to `ParsedToken`:

```python
@dataclass
class ParsedToken:
    original: str
    is_rest: bool
    is_tuplet: bool = False  # NEW
    tuplet_ratio: Optional[Tuple[int, int]] = None  # NEW (num, denom)
    tuplet_notes: Optional[List['ParsedToken']] = None  # NEW
    pitch_letter: str = ''
    accidental: str = ''
    octave_markers: str = ''
    duration: str = ''
    warnings: List[str] = field(default_factory=list)
```

#### Step 3: Convert to Event Dicts (`lilypond_parser.py`)

Add tuplet handling in `parse_lilypond_to_data()`:

```python
for token_info in parse_result.tokens:
    parsed = parse_token(token_info.original)
    
    if parsed.is_tuplet:
        # Process each note in the tuplet
        for tuplet_note in parsed.tuplet_notes:
            octave = _extract_octave_from_tiny(tuplet_note.converted)
            ql = _parse_duration_to_ql(tuplet_note.duration)
            
            # Apply tuplet ratio to duration
            num, denom = parsed.tuplet_ratio
            actual_ql = ql * (denom / num)  # e.g., 0.5 * (2/3) = 0.333...
            
            events.append({
                'type': 'note',
                'step': tuplet_note.pitch_letter.upper(),
                'octave': octave,
                'alter': _accidental_to_alter(tuplet_note.accidental),
                'ql': actual_ql,
                'tuplet': {'type': f'{num}:{denom}', 'normal': ql, 'actual': actual_ql},
                'original_token': tuplet_note.original,
            })
    elif parsed.is_rest:
        # ... existing rest handling ...
    else:
        # ... existing note handling ...
```

#### Step 4: Convert to music21 Objects (`music_data.py`)

Update `data_to_part()` to handle tuplet metadata:

```python
def data_to_part(events, metadata):
    """Convert event dicts to music21.Part."""
    part = music21.stream.Part()
    
    for ev in events:
        ql = ev.get('ql', 1.0)
        
        if ev.get('type') == 'rest':
            el = music21.note.Rest(quarterLength=ql)
        elif ev.get('type') == 'note':
            pitch = music21.pitch.Pitch()
            pitch.step = ev.get('step', 'C')
            pitch.octave = ev.get('octave', 4)
            pitch.alter = ev.get('alter', 0)
            
            el = music21.note.Note(pitch, quarterLength=ql)
            
            # **NEW**: Apply tuplet if present
            if 'tuplet' in ev:
                tuplet_info = ev['tuplet']
                # Parse ratio (e.g., "3:2" → 3 notes in space of 2)
                num, denom = map(int, tuplet_info['type'].split(':'))
                tuplet = music21.duration.Tuplet(numberNotesActual=num, 
                                                   numberNotesNormal=denom)
                el.duration.appendTuplet(tuplet)
        
        part.append(el)
    
    return part
```

---

## Testing Strategy

### Test Case 1: Simple Triplet
```lilypond
\relative c' { \tuplet 3/2 { c8 d8 e8 } }
```

**Expected**:
- 3 events, each with ql ≈ 0.333 (eighth note triplet)
- Each event has `tuplet: {'type': '3:2', 'normal': 0.5, 'actual': 0.333...}`

### Test Case 2: Triplet in Context
```lilypond
\relative c' { c4 \tuplet 3/2 { d8 e8 f8 } g4 }
```

**Expected**:
- Event 0: C4, ql=1.0 (no tuplet)
- Events 1-3: D4, E4, F4, ql≈0.333 each (tuplet)
- Event 4: G4, ql=1.0 (no tuplet)

---

## Parser Isolation Checklist

To ensure the parser remains isolated and extensible:

### ✅ Parser Outputs Event Dicts Only
- NO direct LilyPond string generation in parser
- Parser returns structured data: `{'type': 'note', 'step': 'C', 'octave': 4, ...}`

### ✅ Output Formatting is Separate
- `project_template.py` handles LilyPond output generation
- Parser doesn't know about `.ly` file format

### ✅ TinyNotation is Inspector Only
- Generated for diagnostic purposes
- Stored in `metadata['tinynotation_inspector']`
- NOT used in data pipeline

### ✅ Extensibility
- New features added to parser don't affect output formatting
- Can add tuplets, grace notes, etc. without changing `project_template.py`

---

## Next Extensions (Priority Order)

1. **Tuplets** (High Priority)
   - Essential for complex rhythms
   - Well-defined syntax in LilyPond
   - Clean mapping to music21

2. **Ties** (Medium Priority)
   - Common in musical notation
   - Syntax: `c4~ c4`
   - music21 has native tie support

3. **Slurs** (Medium Priority)
   - Phrasing markers
   - Syntax: `c4( d8 e8)`
   - music21 Spanner object

4. **Articulations** (Low Priority)
   - Staccato, accent, etc.
   - Syntax: `c4-. d4->`
   - music21 Articulation objects

5. **Dynamics** (Low Priority)
   - Volume markings
   - Syntax: `\p \f \crescendo`
   - music21 Dynamic objects

---

## Implementation Guidelines

### Adding a New Feature

1. **Identify Syntax**: Study LilyPond documentation for exact syntax
2. **Extend Tokenizer**: Add pattern recognition in `lily_tokenizer.py`
3. **Extend Parser**: Add fields to `ParsedToken` in `lily_token_parser.py`
4. **Convert to Events**: Add handling in `lilypond_parser.py`
5. **Convert to music21**: Update `data_to_part()` in `music_data.py`
6. **Test**: Create test cases with expected output
7. **Document**: Add to this roadmap

### Keeping Parser Isolated

- **DO**: Return event dictionaries with rich metadata
- **DON'T**: Generate LilyPond strings in parser
- **DO**: Add new event types (e.g., `'type': 'tuplet'`)
- **DON'T**: Modify output formatting code when adding features
- **DO**: Store diagnostic info in metadata
- **DON'T**: Use diagnostic info in data pipeline

---

## Summary

The parser is now:
✅ **Isolated**: Outputs event dicts, not format-specific strings
✅ **Extensible**: Can add features without breaking output
✅ **Documented**: TinyNotation inspector shows pitch resolution
✅ **Robust**: Direct token → event dict conversion (no intermediary)

**Next Step**: Implement tuplet support following the roadmap above.
