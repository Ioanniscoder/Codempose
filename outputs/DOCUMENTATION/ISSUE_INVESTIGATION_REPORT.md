# Issue Investigation Report: Tuplets and Chords

**Date**: October 13, 2025  
**Investigation Focus**: Two critical parser issues

---

## Issue 1: Tuplet Handling - INCOMPLETE ARCHITECTURE

### Current State Analysis

The framework has **TWO DIFFERENT tuplet parsing paths** that are in conflict:

#### Path A: Legacy Individual Note Approach (Lines 143-198)
```python
# In lilypond_parser.py line 143-198
if token_info.converted.startswith('[') and ']' in token_info.converted:
    # Parse: [d e f]8 → creates 3 SEPARATE note events
    # Each note gets: ql = actual_ql (0.333 for triplet eighths)
    # Result: 3 independent events with tuplet_ratio metadata
```

**Problems with Path A:**
- Creates individual note events, not grouped tuplets
- Loses tuplet structure - can't reconstruct `\tuplet 3/2 { }` syntax
- Just stores `tuplet_ratio: "3/2"` metadata on separate notes
- music21 export sees individual notes, approximates as dotted durations

#### Path B: Structured Tuplet Approach (Lines 205-233)
```python
# In lilypond_parser.py line 205-233
elif parsed.is_tuplet:
    # Creates ONE tuplet event containing nested notes
    events.append({
        'type': 'tuplet',
        'numerator': parsed.tuplet_ratio[0],
        'denominator': parsed.tuplet_ratio[1],
        'notes': tuplet_events,  # Nested note events
        'original_token': token_info.original
    })
```

**Path B is CORRECT but NEVER EXECUTED:**
- `parsed.is_tuplet` is never True because...
- Path A's `if token_info.converted.startswith('[')` catches tuplets first
- This code is **unreachable dead code**

### The Flow Problem

```
LilyPond Input: [d e f]8
         ↓
lily_tokenizer → TokenInfo(original="[d e f]8", converted="[d e f]8")
         ↓
Line 143: if token_info.converted.startswith('['):  ← CATCHES HERE
         ↓
Path A: Creates 3 separate note events with tuplet_ratio metadata
         ↓
lily_converter.py: Doesn't recognize tuplets (no type='tuplet')
         ↓
music_data.py: Processes as 3 individual notes
         ↓
music21: Approximates 0.333 QL as dotted 16th (0.375 QL)
         ↓
LilyPond Output: d''16. e''16. f''16.  ← WRONG (dotted notes, no tuplet bracket)
```

### Why Tuplets Appear Dotted

1. Path A creates notes with `ql: 0.333` (triplet eighth duration)
2. music21's `quarterLength=0.333` has no exact LilyPond equivalent
3. music21 approximates: `0.333 → 0.375` (dotted 16th)
4. Warning: `requested ql=1/3 approximated as 0.375 (LilyPond: 16.)`

### The Correct Solution

**Option 1: Fix Path A to create structured tuplets**
```python
# Instead of creating 3 separate notes, create:
{
    'type': 'tuplet',
    'numerator': 3,
    'denominator': 2,
    'notes': [
        {'type': 'note', 'step': 'D', 'octave': 4, 'ql': 0.5},  # notated duration
        {'type': 'note', 'step': 'E', 'octave': 4, 'ql': 0.5},
        {'type': 'note', 'step': 'F', 'octave': 4, 'ql': 0.5}
    ]
}
```

**Option 2: Make Path B reachable**
- Remove Path A's early catch
- Let `lily_token_parser.parse_token()` detect tuplets
- Use Path B's structured approach

**Then fix lily_converter.py** to output:
```python
if ev.get('type') == 'tuplet':
    n = ev.get('numerator', 3)
    d = ev.get('denominator', 2)
    notes = ev.get('notes', [])
    note_tokens = [f"{pitch}{duration}" for note in notes]
    return f"\\tuplet {n}/{d} {{ {' '.join(note_tokens)} }}"
```

### Recommendation

**Use Option 1**: Fix Path A in place because:
- Path A already works for octave resolution
- Less disruptive to existing code
- Just needs to store structured tuplet instead of flat notes

---

## Issue 2: Chord Handling - DELIBERATELY SKIPPED

### Current State

```python
# lilypond_parser.py line 253-254
elif parsed.pitch_letter and parsed.pitch_letter.startswith('<'):
    # Chord - skip for now (needs special handling)
    continue
```

**Status**: Chords are **intentionally disabled** with a TODO comment.

### Why This Exists

Looking at the codebase history:
1. `lily_to_tiny.py` HAS chord parsing (line 188-202)
2. `lily_converter.py` HAS chord export (line 23-29)
3. `music_data.py` HAS chord support (type='chord')
4. BUT `lilypond_parser.py` SKIPS chords

**This suggests**: Feature was started, then disabled during development.

### What Chord Support Requires

#### 1. Parse chord tokens: `<c e g>2`
```python
# Instead of 'continue', do:
match = re.match(r'<([^>]+)>(\d+\.?)?', token_info.original)
if match:
    pitches_str = match.group(1)  # "c e g"
    duration_str = match.group(2)  # "2"
    
    pitch_tokens = pitches_str.split()
    pitches = []
    for p_tok in pitch_tokens:
        # Parse each pitch: handle accidentals, octaves
        # Need relative octave resolution for each pitch
        pitches.append({
            'step': ...,
            'octave': ...,
            'alter': ...
        })
    
    events.append({
        'type': 'chord',
        'pitches': pitches,
        'ql': _parse_duration_to_ql(duration_str)
    })
```

#### 2. Challenges

**A. Octave Resolution in Chords**
```lilypond
\relative c' { <c e g>2 }  
```
- First pitch `c`: relative to c'
- Second pitch `e`: relative to previous pitch (c)
- Third pitch `g`: relative to previous pitch (e)
- Must apply relative octave logic WITHIN the chord

**B. Integration Points**
- `lily_token_parser.py`: Already has chord detection
- `relative_octave_logic.py`: Must handle multiple pitches
- `lilypond_parser.py`: Must implement the actual parsing

**C. Testing Required**
- Absolute chords: `<c e g>2`
- Relative chords: `\relative c' { <c e g>2 <d f a>2 }`
- Chords with accidentals: `<cis e gis>2`
- Chords spanning octaves: `<c e g c'>1`

### Implementation Options

**Option A: Quick Fix (Absolute Mode Only)**
- Parse `<c e g>2` in absolute mode
- Skip relative mode chords for now
- Gets INTERMEZZO working (it's in relative but simple)
- ~50 lines of code

**Option B: Full Implementation**
- Parse chords in both absolute and relative modes
- Apply proper octave resolution
- Handle all edge cases
- ~200 lines of code + extensive testing

**Option C: Use music21 Parser**
- Let music21.converter.parse handle LilyPond chords
- Parse with music21, then extract to events
- May lose some control over representation
- ~30 lines but delegates complexity

### Recommendation

**Start with Option A**: Get chords working for the immediate use case:
1. Detect chord tokens `<...>`
2. Parse pitches in absolute mode
3. Apply simple relative resolution (assume pitches are close)
4. Skip complex cases (document limitations)
5. This gets INTERMEZZO working TODAY

**Then consider Option B** after we validate the architecture fits.

---

## Issue 3: Two-Stave Setup Request

### Current Architecture

Framework currently supports:
- Single voice per file
- Multiple parts through voice assignments
- But all parts go to ONE staff in output

### What's Needed for Two Staves

#### 1. Data Structure Changes

**Current**:
```python
{
    'parts': {
        'MainLine': [event1, event2, ...]
    }
}
```

**Two-Stave**:
```python
{
    'parts': {
        'UpperStaff': [theme_a_events...],
        'LowerStaff': [intermezzo_chords...]
    }
}
```

#### 2. Export Changes

**LilyPond** (`project_template.py` line ~320):
```lilypond
\score {
    \new StaffGroup <<
        \new Staff { \clef treble ... upper_events ... }
        \new Staff { \clef bass ... lower_events ... }
    >>
}
```

**MusicXML** (`music_data.py` line ~150):
- Create multiple `<part>` elements
- Each part becomes a staff in MuseScore

#### 3. Voice Assignment Strategy

```python
VOICE_ASSIGNMENTS = {
    'UpperStaff': {
        'ThemeA_Original': 'THEME_A',
        'ThemeA_Transposed': 'THEME_A_TRANSPOSED',
        # ... all Theme A variations
    },
    'LowerStaff': {
        'Intermezzo_1': 'INTERMEZZO',
        'Intermezzo_2': 'INTERMEZZO',
        # ... repeat intermezzo between sections
        'Rest_1': 'REST_DURING_THEMES',  # Silent when upper plays
    }
}
```

### Test File Setup

Create `thirteenth_two_staves.py`:

**Structure**:
- **Upper Staff**: Theme A progression (melody line)
- **Lower Staff**: Intermezzo chords (harmonic support)
- **Alignment**: Chords play during transitions, rest during themes

**Expected Output**:
```
Upper: ThemeA | Intermezzo | ThemeA_Transposed | Intermezzo | ThemeA_Inverted
Lower: Rest   | Chords     | Rest              | Chords      | Rest
```

### Implementation Steps

1. **Fix chord parsing first** (Option A above)
2. **Create test file** with two-stave structure
3. **Modify project_template.py** to detect multiple parts
4. **Update LilyPond export** to create StaffGroup
5. **Update MusicXML export** to create multiple parts
6. **Test and document** the new capability

---

## Summary and Next Steps

### Tuplets: ARCHITECTURAL ISSUE
- **Problem**: Two conflicting code paths, wrong one executes
- **Impact**: Tuplets become dotted notes, lose bracket notation
- **Complexity**: Medium - needs careful refactoring
- **Priority**: High - affects output quality significantly

### Chords: FEATURE DISABLED
- **Problem**: Intentionally skipped with `continue` statement
- **Impact**: All chord events lost (INTERMEZZO has 0 events)
- **Complexity**: High - needs octave resolution, testing
- **Priority**: HIGH - blocks two-stave work

### Two-Stave: NEW FEATURE REQUEST
- **Problem**: Architecture assumes single staff
- **Impact**: Can't create piano-style scores
- **Complexity**: Medium - needs export layer changes
- **Priority**: Medium - nice to have, depends on chords

### Recommended Sequence

1. **TODAY**: Fix chord parsing (Option A - simple absolute mode)
   - Gets INTERMEZZO working
   - ~1 hour work
   
2. **NEXT**: Create two-stave test file
   - Uses newly working chords
   - Tests multi-part export
   - ~2 hours work
   
3. **THEN**: Fix tuplet architecture (refactor Path A)
   - Preserves tuplet structure
   - Outputs proper `\tuplet` syntax
   - ~3 hours work

4. **FINALLY**: Full chord support (Option B - relative mode)
   - After validating architecture with simple version
   - ~4 hours work

### Questions for Review

1. **Tuplets**: Should we fix Path A or switch to Path B?
2. **Chords**: Start with simple (Option A) or go full (Option B)?
3. **Two-Stave**: Should lower staff be bass clef? What about time alignment?
4. **Architecture**: Does multi-part output fit the current pipeline design?

