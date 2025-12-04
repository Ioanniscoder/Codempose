# Tenth.py Implementation Analysis
**Date**: October 9, 2025  
**Status**: Needs Implementation

---

## Current Status: ninth.py vs tenth.py

### ✅ ninth.py - FULLY OPERATIONAL

**What Works:**
- ✅ Hybrid composition model (programmatic + declarative)
- ✅ Soprano/Alto: Generated programmatically
- ✅ Tenor/Bass: Generated via shorthand
- ✅ Compiles to PDF/MIDI/MusicXML successfully
- ✅ Multi-voice staff rendering

**What's Missing:**
- ❌ No documentation comments in .ly file
- ❌ No feedback loop showing programmatic results

**Output Structure:** (`outputs/ninth.ly`)
```lilypond
\version "2.24.1"
\header { title = "Ninth Study - Hybrid Composition" }
\score {
  <<
  \new Staff { \clef treble << {...} \\ {...} >> }
  \new Staff { \clef bass << {...} \\ {...} >> }
  >>
  \layout { }
  \midi { }
}
```

**Key Observation:** No documentation block showing what was generated programmatically!

---

### ❌ tenth.py - PARTIALLY IMPLEMENTED

**What Exists:**
- ✅ Study file structure (`tenth.py`)
- ✅ Uses `register_and_document_voice()` pattern
- ✅ `voice_documentation.py` module
- ✅ `lily_converter.py` module (stub)

**What's Broken:**
1. ❌ Import error: `build_lilypond_file` doesn't exist in `music_data.py`
2. ❌ `lily_converter.py` has wrong implementation (uses wrong event format)
3. ❌ No documentation block integration in `engrave_with_abjad()`

---

## Gap Analysis: What tenth.py Adds Over ninth.py

### The Innovation: Documentation Feedback Loop

**Objective:** Make programmatically generated music **visible and reusable**

**Current Problem:**
```python
# In ninth.py, this generates music:
soprano_events = generate_soprano_programmatically()

# Question: What notes did this ACTUALLY produce?
# Answer: You have to:
# 1. Run the program
# 2. Open outputs/ninth.pdf 
# 3. Visually inspect the staff
# 4. Manually transcribe if you want to reuse it
```

**Tenth.py Solution:**
```python
# Generate programmatically
alto_voice = transpose_events(soprano_theme, -7)

# DOCUMENT IT - capture as LilyPond notation
register_and_document_voice('ALTO_GENERATED', alto_voice, voice_lookup, metadata)

# Result: outputs/tenth.ly contains:
# % ALTO_GENERATED:
# %   a'4 g'8 f'8 e'4 d'4 | c'2 d'2 |
#
# Now you can COPY this snippet into a new composition!
```

**This closes the creative loop:**
```
Station 1 (LilyPond) → Station 4 (Programmatic) → 
Documentation → Back to Station 1 (Manual editing)
```

---

## Required Implementations

### 1. Fix `lily_converter.py` - events_to_lily()

**Current Implementation (WRONG):**
```python
def events_to_lily(events):
    lily_parts = []
    for event in events:
        pitch = event.get('pitch', 'c')      # ❌ Wrong key
        duration = event.get('duration', 4)  # ❌ Wrong key
        lily_parts.append(f"{pitch}{duration}")
    return ' '.join(lily_parts)
```

**Problem:** Canonical event format uses:
- `'step'`, `'octave'`, `'alter'` (not `'pitch'`)
- `'ql'` for quarter length (not `'duration'`)
- `'type'` for note/chord/rest discrimination

**Required Implementation:**
```python
def events_to_lily(events):
    """Convert canonical event dictionaries to LilyPond notation."""
    lily_tokens = []
    
    for ev in events:
        ql = ev.get('ql', 1.0)
        dur_str = _ql_to_lily_duration(ql)
        
        if ev.get('type') == 'rest':
            lily_tokens.append(f"r{dur_str}")
            
        elif ev.get('type') == 'chord':
            # Format: <c e g>4
            pitches = []
            for p in ev.get('pitches', []):
                pitch_str = _pitch_to_lily(p['step'], p['octave'], p.get('alter', 0))
                pitches.append(pitch_str)
            lily_tokens.append(f"<{' '.join(pitches)}>{dur_str}")
            
        elif ev.get('type') == 'note':
            # Format: c'4
            pitch_str = _pitch_to_lily(
                ev.get('step', 'c'),
                ev.get('octave', 4),
                ev.get('alter', 0)
            )
            lily_tokens.append(f"{pitch_str}{dur_str}")
    
    return ' '.join(lily_tokens)


def _ql_to_lily_duration(ql: float) -> str:
    """Convert quarter lengths to LilyPond duration."""
    duration_map = {
        4.0: '1',   # whole note
        3.0: '2.',  # dotted half
        2.0: '2',   # half note
        1.5: '4.',  # dotted quarter
        1.0: '4',   # quarter note
        0.75: '8.', # dotted eighth
        0.5: '8',   # eighth note
        0.25: '16', # sixteenth note
    }
    return duration_map.get(ql, '4')  # Default to quarter


def _pitch_to_lily(step: str, octave: int, alter: int) -> str:
    """Convert pitch components to LilyPond notation."""
    step_lower = step.lower()
    
    # Add accidental
    if alter == 1:
        step_lower += 'is'
    elif alter == -1:
        step_lower += 'es'
    elif alter == 2:
        step_lower += 'isis'
    elif alter == -2:
        step_lower += 'eses'
    
    # Add octave markers
    if octave == 4:
        # Middle octave (c4 = c') - add one tick
        return step_lower + "'"
    elif octave > 4:
        # Higher octaves
        ticks = "'" * (octave - 3)
        return step_lower + ticks
    else:
        # Lower octaves (use commas)
        commas = "," * (4 - octave)
        return step_lower + commas
```

**Why This Implementation:**
- Uses correct canonical event dictionary keys
- Handles all three event types (note, chord, rest)
- Converts octaves to LilyPond notation (`'` for higher, `,` for lower)
- Maps accidentals to LilyPond format (`is` for sharp, `es` for flat)
- Converts quarter lengths to standard durations

---

### 2. Add `build_lilypond_file()` to music_data.py

**Option A - Simple Wrapper:**
```python
def build_lilypond_file(score_data: dict, output_basename: str):
    """
    Build and write LilyPond file with documentation.
    
    This is a wrapper around engrave_with_abjad() for backward compatibility
    with tenth.py's expected interface.
    """
    from project_template import engrave_with_abjad
    from pathlib import Path
    
    # Extract basename without extension
    basename = Path(output_basename).stem
    
    # Delegate to existing function
    engrave_with_abjad(score_data, basename)
```

**Option B - Fix tenth.py imports instead:**
```python
# In tenth.py, change:
from music_data import build_lilypond_file  # ❌ Doesn't exist

# To:
from project_template import engrave_with_abjad  # ✅ Exists

# Then call:
engrave_with_abjad(data, "tenth")
```

**Recommendation:** Option A (add wrapper) - maintains abstraction and matches Gemini design

---

### 3. Add Documentation Block to engrave_with_abjad()

**Location:** `project_template.py`, around line 248

**Step 1 - Add Helper Function:**
```python
def _build_documentation_block(metadata: dict) -> str:
    """
    Build LilyPond comment block documenting programmatic voices.
    
    This enables the feedback loop: programmatic output → human-readable notation.
    """
    if 'programmatic_voices' not in metadata:
        return ""
    
    lines = [
        "% ========================================",
        "% PROGRAMMATICALLY GENERATED VOICES",
        "% ========================================",
        "%",
        "% The following voices were generated algorithmically.",
        "% Copy these snippets to reuse in new compositions.",
        "%",
    ]
    
    for voice_name, voice_data in metadata['programmatic_voices'].items():
        lily_notation = voice_data.get('lilypond', '')
        lines.append(f"% {voice_name}:")
        lines.append(f"%   {lily_notation}")
        lines.append("%")
    
    lines.extend([
        "% To reuse:",
        "% 1. Copy the notation above",
        "% 2. Paste into new study file as SOURCE_xxx_LILY",
        "% 3. Edit manually or apply further transformations",
        "%",
        "% ========================================",
        "",
    ])
    
    return "\n".join(lines)
```

**Step 2 - Modify engrave_with_abjad():**

Find this section (around line 248):
```python
# Build comment section with original LilyPond snippets if available
comment_section = ""
original_input = score_data.get('metadata', {}).get('original_input', '')
if original_input:
    comment_section = f"""% ========================================
% ORIGINAL LILYPOND INPUT (for reference)
% ========================================
% {original_input.replace(chr(10), chr(10) + '% ')}
%
"""
```

Add after this:
```python
# ADD: Documentation block for programmatic voices
programmatic_doc = _build_documentation_block(metadata)
if programmatic_doc:
    comment_section += programmatic_doc
```

---

## Expected Output After Implementation

### outputs/tenth.ly (with documentation):

```lilypond
\version "2.24.1"

% ========================================
% PROGRAMMATICALLY GENERATED VOICES
% ========================================
%
% The following voices were generated algorithmically.
% Copy these snippets to reuse in new compositions.
%
% ALTO_GENERATED:
%   a'4 g'8 f'8 e'4 d'4 g'2 a'2
%
% TENOR_GENERATED:
%   c'4 d'4 e'4 f'4 e2 f2
%
% BASS_GENERATED:
%   c4 d4 e4 f4 e,2 f,2
%
% To reuse:
% 1. Copy the notation above
% 2. Paste into new study file as SOURCE_xxx_LILY
% 3. Edit manually or apply further transformations
%
% ========================================

\header { title = "Tenth Study: Programmatic Voice Documentation" }
\score {
  <<
  \new Staff { \clef treble ... }
  \new Staff { \clef treble ... }
  \new Staff { \clef treble ... }
  \new Staff { \clef bass ... }
  >>
  \layout { }
  \midi { }
}
```

---

## Implementation Steps (Priority Order)

### Phase 1: Get tenth.py Running (Minimum Viable)

1. **Fix lily_converter.py**
   - Replace `events_to_lily()` with correct implementation
   - Add helper functions `_ql_to_lily_duration()` and `_pitch_to_lily()`
   - Test: `python3 -c "from lily_converter import events_to_lily; print(events_to_lily([{'type': 'note', 'step': 'c', 'octave': 4, 'alter': 0, 'ql': 1.0}]))"`

2. **Add build_lilypond_file() wrapper**
   - Add to `music_data.py`
   - Simple delegation to `engrave_with_abjad()`
   - Test: `from music_data import build_lilypond_file`

3. **Test tenth.py execution**
   - Run: `python3 tenth.py`
   - Should complete without errors
   - Check: `outputs/tenth.ly` exists

### Phase 2: Add Documentation Block

4. **Add _build_documentation_block() helper**
   - Add to `project_template.py` before `engrave_with_abjad()`
   - Extract programmatic_voices from metadata
   - Format as LilyPond comments

5. **Integrate into engrave_with_abjad()**
   - Call helper after original_input section
   - Append to comment_section
   - Include in ly_content

6. **Verify complete workflow**
   - Run: `python3 tenth.py`
   - Open: `outputs/tenth.ly`
   - Verify: Documentation comments appear
   - Verify: PDF compiles correctly

### Phase 3: Validation & Documentation

7. **Test feedback loop**
   - Copy generated snippet from tenth.ly
   - Create eleventh.py with copied snippet
   - Verify it compiles

8. **Update documentation**
   - Add to CODE_FLOW_ANALYSIS.md
   - Update SYSTEM_SUMMARY.md
   - Create TENTH_STUDY_GUIDE.md

---

## Testing Checklist

- [ ] `lily_converter.py` handles all event types (note, chord, rest)
- [ ] `lily_converter.py` handles all octaves (commas and ticks)
- [ ] `lily_converter.py` handles accidentals (sharp, flat, natural)
- [ ] `build_lilypond_file()` delegates correctly to `engrave_with_abjad()`
- [ ] `tenth.py` imports succeed
- [ ] `tenth.py` executes without errors
- [ ] `outputs/tenth.ly` contains documentation block
- [ ] Documentation block shows correct LilyPond notation
- [ ] Documentation block appears BEFORE `\header`
- [ ] PDF/MIDI compile successfully
- [ ] Copied snippets from .ly work in new files

---

## Design Validation

This implementation aligns with:
- ✅ **Gemini conversation** - Exact architecture proposed
- ✅ **CODE_FLOW_ANALYSIS.md** - Tenth study design
- ✅ **Four-station model** - Feedback loop (Station 4 → 1)
- ✅ **Existing patterns** - Uses canonical event format
- ✅ **ninth.py model** - Extends hybrid approach

**The key innovation:** Programmatic output becomes **visible** and **reusable**, closing the creative feedback loop.

---

## Next Actions

Ready to implement? The fixes are well-defined and surgical:
1. Fix `lily_converter.py` (~60 lines)
2. Add wrapper to `music_data.py` (~10 lines)
3. Add helper to `project_template.py` (~30 lines)
4. Modify `engrave_with_abjad()` (~3 lines)

**Total:** ~103 lines of code to complete the tenth.py innovation.

Shall we proceed with the implementation?
