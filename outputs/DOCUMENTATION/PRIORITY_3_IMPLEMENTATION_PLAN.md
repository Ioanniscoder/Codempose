# PRIORITY 3: MULTI-VOICE BLUEPRINT FRAMEWORK - COMPLETE IMPLEMENTATION PLAN
**Date:** October 15, 2025  
**Status:** Ready to Begin  
**Prerequisites:** ✅ Priorities 1 & 2 Complete

---

## 📋 EXECUTIVE SUMMARY

**Objective:** Extend the Blueprint String Framework to fully support polyphonic (multi-voice) staves, enabling composers to write SATB choir music, piano music with independent voices per hand, and other polyphonic structures.

**Current State:**
- ✅ Parser recognizes multi-voice syntax: `"(Soprano, Alto) & (Tenor, Bass)"`
- ✅ Parser extracts comma-separated voice content
- ❌ Assembly logic only processes first voice in multi-voice staves
- ❌ No voice layer creation in music21 output
- ❌ No test file demonstrating SATB capability

**Target State:**
- ✅ Complete multi-voice assembly in `build_score_from_blueprint()`
- ✅ Proper voice overlay in music21.stream.Part objects
- ✅ Test file `fourteenth.py` showcasing SATB hymn/chorale
- ✅ Documentation for multi-voice blueprint syntax

**Impact:** Unlocks polyphonic composition capability for the entire Codempose system.

---

## 🎯 SPECIFIC GOALS

### Goal 1: Complete Multi-Voice Assembly Logic
**File:** `score_builder.py`  
**Function:** `build_score_from_blueprint()` (lines 119-217)

**Current Behavior:**
```python
# Lines 149-180 in score_builder.py
for staff_idx, staff_content in enumerate(section):
    staff_name = list(parts.keys())[staff_idx]
    
    # 🔴 PROBLEM: Only processes staff_content[0]
    if staff_content and isinstance(staff_content[0], list):
        snippet_names = staff_content[0]  # Takes only first voice!
    else:
        snippet_names = staff_content
    
    # Only assembles events from first voice
    staff_events = []
    for snippet_name in snippet_names:
        snippet_events = snippets[snippet_name]
        staff_events.extend(snippet_events)
    
    parts[staff_name].extend(staff_events)
```

**Required Behavior:**
```python
# When multi-voice (staff_content is list of lists):
for staff_idx, staff_content in enumerate(section):
    staff_name = list(parts.keys())[staff_idx]
    
    if staff_content and isinstance(staff_content[0], list):
        # 🟢 SOLUTION: Process ALL voices
        voice_count = len(staff_content)
        voice_events_dict = {}
        
        for voice_idx, voice_snippets in enumerate(staff_content):
            voice_name = layout[staff_idx][voice_idx]
            voice_events = []
            
            for snippet_name in voice_snippets:
                if snippet_name == 'r':
                    continue  # Handle rests later
                snippet_events = snippets[snippet_name]
                voice_events.extend(snippet_events)
            
            voice_events_dict[voice_name] = voice_events
        
        # Store as dictionary for multi-voice assembly
        parts[staff_name].append({
            'type': 'multi_voice_section',
            'voices': voice_events_dict
        })
    else:
        # Single voice (current logic)
        # ... existing code ...
```

---

### Goal 2: Multi-Voice Data Structure Extension
**File:** `music_data.py`  
**Function:** `data_to_part()` (needs enhancement)

**Current Limitation:**
- `data_to_part()` assumes flat list of events
- Cannot handle voice layers within a single staff

**Required Enhancement:**
```python
def data_to_part(events: List[Dict], part_name: str = "Part") -> music21.stream.Part:
    """
    Convert canonical event list to music21.stream.Part.
    
    NEW: Supports multi-voice sections with voice dictionary.
    """
    part = music21.stream.Part()
    part.partName = part_name
    
    for event in events:
        if event.get('type') == 'multi_voice_section':
            # 🟢 NEW: Handle multi-voice overlay
            voices = event['voices']
            
            # Create voice objects
            voice_objects = []
            for voice_name, voice_events in voices.items():
                voice_stream = music21.stream.Voice()
                voice_stream.id = voice_name
                
                # Add events to voice
                for v_event in voice_events:
                    element = _event_to_music21(v_event)
                    if element:
                        voice_stream.append(element)
                
                voice_objects.append(voice_stream)
            
            # Create measure and insert all voices
            measure = music21.stream.Measure()
            for voice_obj in voice_objects:
                measure.insert(0, voice_obj)
            
            part.append(measure)
        else:
            # 🟢 EXISTING: Single-voice event handling
            element = _event_to_music21(event)
            if element:
                part.append(element)
    
    return part
```

---

### Goal 3: Create `fourteenth.py` SATB Showcase
**File:** `fourteenth.py` (NEW)  
**Purpose:** Demonstrate SATB capability with real hymn fragment

**Required Structure:**
```python
"""Fourteenth study file - SATB Hymn Demonstration.

Showcases multi-voice Blueprint String Framework with four-part harmony.
Uses hymn-style texture: Soprano and Alto on upper staff, Tenor and Bass on lower.
"""

# ============================================================================
# STATION 1: COMPOSING INPUT (LilyPond Snippets)
# ============================================================================

SOPRANO_PHRASE_A = r"\relative c'' { \time 4/4 \key g \major g4 g a b }"
ALTO_PHRASE_A = r"\relative c' { \time 4/4 \key g \major d4 d d d }"
TENOR_PHRASE_A = r"\relative c' { \time 4/4 \key g \major b4 b a g }"
BASS_PHRASE_A = r"\relative c { \time 4/4 \key g \major g4 g fis g }"

SOPRANO_PHRASE_B = r"\relative c'' { c4 b a2 }"
ALTO_PHRASE_B = r"\relative c' { e4 d d2 }"
TENOR_PHRASE_B = r"\relative c' { g4 g fis2 }"
BASS_PHRASE_B = r"\relative c { c4 g d2 }"

# ============================================================================
# STATION 2: VALIDATING INPUT (TinyNotation + Generated Placeholders)
# ============================================================================

# Real-time validation (printed during build_score_data())
# Shows LilyPond → TinyNotation conversion for verification

# ============================================================================
# STATION 3: STRUCTURING INPUT (Blueprint Strings)
# ============================================================================

# Layout: Two staves, each with two voices
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"

# Content: Two phrases (sections)
VOICE_STAVE_DATA = """
    SOPRANO_A, ALTO_A & TENOR_A, BASS_A;
    SOPRANO_B, ALTO_B & TENOR_B, BASS_B
"""

# ============================================================================
# PROCESSING ENGINE
# ============================================================================

def build_score_data():
    """Build SATB score using Blueprint String Framework."""
    
    # Parse all voice snippets
    from lilypond_parser import parse_lilypond_to_data
    
    sop_a = parse_lilypond_to_data(SOPRANO_PHRASE_A, 'Soprano')['parts']['Soprano']
    alt_a = parse_lilypond_to_data(ALTO_PHRASE_A, 'Alto')['parts']['Alto']
    ten_a = parse_lilypond_to_data(TENOR_PHRASE_A, 'Tenor')['parts']['Tenor']
    bas_a = parse_lilypond_to_data(BASS_PHRASE_A, 'Bass')['parts']['Bass']
    
    sop_b = parse_lilypond_to_data(SOPRANO_PHRASE_B, 'Soprano')['parts']['Soprano']
    alt_b = parse_lilypond_to_data(ALTO_PHRASE_B, 'Alto')['parts']['Alto']
    ten_b = parse_lilypond_to_data(TENOR_PHRASE_B, 'Tenor')['parts']['Tenor']
    bas_b = parse_lilypond_to_data(BASS_PHRASE_B, 'Bass')['parts']['Bass']
    
    # Build snippet library
    SNIPPETS = {
        'SOPRANO_A': sop_a,
        'ALTO_A': alt_a,
        'TENOR_A': ten_a,
        'BASS_A': bas_a,
        'SOPRANO_B': sop_b,
        'ALTO_B': alt_b,
        'TENOR_B': ten_b,
        'BASS_B': bas_b,
    }
    
    metadata = {
        'title': 'SATB Hymn Fragment',
        'composer': 'Codempose Multi-Voice Demo',
        'time_signature': '4/4',
        'key_signature': {'tonic': 'g', 'mode': 'major'}
    }
    
    # Call blueprint framework
    from score_builder import build_score_from_blueprint
    return build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        SNIPPETS,
        metadata
    )
```

**Expected Output:**
- PDF with 2 staves (treble and bass clefs)
- Upper staff: Soprano (stems up) and Alto (stems down) overlaid
- Lower staff: Tenor (stems up) and Bass (stems down) overlaid
- Proper voice separation with correct stem directions

---

### Goal 4: Multi-Voice Engraving Support
**File:** `main.py` (engraving pipeline)  
**Function:** Needs to handle multi-voice music21 Parts

**Current State:**
- Engraver expects flat Part objects
- Voice layers not explicitly handled

**Required Enhancement:**
```python
# In engraving workflow (main.py or music_data.py)

def prepare_part_for_engraving(part: music21.stream.Part) -> music21.stream.Part:
    """
    Prepare Part for LilyPond engraving.
    Ensures voices have correct stem directions and IDs.
    """
    # Check if part has voice layers
    voices = part.getElementsByClass(music21.stream.Voice)
    
    if voices:
        # Multi-voice: Set stem directions
        for idx, voice in enumerate(voices):
            if idx % 2 == 0:
                # Upper voice: stems up
                for note in voice.flatten().notes:
                    note.stemDirection = 'up'
            else:
                # Lower voice: stems down
                for note in voice.flatten().notes:
                    note.stemDirection = 'down'
    
    return part
```

---

## 🔧 TECHNICAL SPECIFICATIONS

### Data Structure Changes

**Current `parts` dictionary (single-voice):**
```python
{
    'UpperStaff': [
        {'type': 'note', 'step': 'E', 'octave': 4, 'ql': 1.0},
        {'type': 'rest', 'ql': 2.0},
        {'type': 'barline', 'style': '||'}
    ],
    'LowerStaff': [...]
}
```

**Extended `parts` dictionary (multi-voice):**
```python
{
    'Staff1': [
        {
            'type': 'multi_voice_section',
            'voices': {
                'Soprano': [
                    {'type': 'note', 'step': 'G', 'octave': 5, 'ql': 1.0},
                    {'type': 'note', 'step': 'A', 'octave': 5, 'ql': 1.0}
                ],
                'Alto': [
                    {'type': 'note', 'step': 'D', 'octave': 4, 'ql': 1.0},
                    {'type': 'note', 'step': 'D', 'octave': 4, 'ql': 1.0}
                ]
            }
        },
        {'type': 'barline', 'style': '||'}
    ],
    'Staff2': [...]
}
```

### Blueprint Parsing Flow (Multi-Voice)

```
INPUT:
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
VOICE_STAVE_DATA = "SOP_A, ALT_A & TEN_A, BAS_A"

STEP 1: parse_voice_stave_def()
→ layout = [
    ['Soprano', 'Alto'],   # Staff 1 has 2 voices
    ['Tenor', 'Bass']      # Staff 2 has 2 voices
]

STEP 2: parse_voice_stave_data()
→ sections = [
    [  # Section 1
        [['SOP_A'], ['ALT_A']],     # Staff 1: 2 voice snippet lists
        [['TEN_A'], ['BAS_A']]      # Staff 2: 2 voice snippet lists
    ]
]

STEP 3: build_score_from_blueprint()
→ For each section:
    For each staff:
        IF staff has multiple voices:
            For each voice:
                Collect events from snippets
                Store in voice_events_dict[voice_name]
            Create multi_voice_section event
        ELSE:
            Collect events (existing single-voice logic)

STEP 4: data_to_part()
→ For each event:
    IF event.type == 'multi_voice_section':
        Create Voice objects
        Add events to each Voice
        Insert all Voices at same offset in Measure
    ELSE:
        Add event to Part (existing logic)
```

---

## 📝 IMPLEMENTATION STEPS (Detailed Action Plan)

### Step 1: Extend `build_score_from_blueprint()` for Multi-Voice Assembly
**File:** `score_builder.py`  
**Lines to Modify:** 149-180

**Action Items:**
1. ✅ Identify multi-voice staff (check `isinstance(staff_content[0], list)`)
2. ✅ Loop through all voices in `staff_content` (not just first)
3. ✅ Build `voice_events_dict` with all voice names and events
4. ✅ Create `multi_voice_section` event type
5. ✅ Handle rests in multi-voice context (duration matching)
6. ✅ Update debug output to show all voices

**Estimated Lines:** +30 lines (expand existing loop)

**Test Criteria:**
- Parser should extract events for all 4 voices in SATB layout
- Console output should show: "Soprano: +SNIPPET_A", "Alto: +SNIPPET_A", etc.
- `parts` dictionary should contain `multi_voice_section` events

---

### Step 2: Enhance `data_to_part()` for Voice Layer Creation
**File:** `music_data.py`  
**Function:** `data_to_part()` (around line 50-80)

**Action Items:**
1. ✅ Add conditional check for `event.get('type') == 'multi_voice_section'`
2. ✅ Create `music21.stream.Voice()` objects for each voice
3. ✅ Populate each Voice with its events (call existing conversion logic)
4. ✅ Set voice IDs and stem directions
5. ✅ Create containing Measure and insert all Voices
6. ✅ Append Measure to Part

**Estimated Lines:** +35 lines (new branch in event processing)

**Test Criteria:**
- `part.getElementsByClass(music21.stream.Voice)` should return 2+ voices
- Each voice should have correct number of notes
- Voices should overlay at same time offset

---

### Step 3: Create `fourteenth.py` SATB Study File
**File:** `fourteenth.py` (NEW)  
**Template:** Follow `thirteenth.py` four-station structure

**Action Items:**
1. ✅ Write 4 voice parts (Soprano, Alto, Tenor, Bass) in LilyPond
2. ✅ Use simple hymn-style harmony (G major, 4/4 time)
3. ✅ Define multi-voice blueprint: `"(Soprano, Alto) & (Tenor, Bass)"`
4. ✅ Parse all voices with `lilypond_parser`
5. ✅ Build SNIPPETS library with all 4 voices
6. ✅ Call `build_score_from_blueprint()`
7. ✅ Add metadata (title, composer, key, time)
8. ✅ Document in docstring

**Estimated Lines:** ~200 lines

**Test Criteria:**
- File should run without errors
- Should generate PDF with 2 staves
- Upper staff should show 2 overlaid voices (stems up/down)
- Lower staff should show 2 overlaid voices (stems up/down)
- MIDI should play 4-part harmony

---

### Step 4: Update Engraving Pipeline for Voice Separation
**File:** `main.py` or `music_data.py`  
**Location:** Before LilyPond export

**Action Items:**
1. ✅ Add `prepare_part_for_engraving()` function
2. ✅ Detect if Part has Voice objects
3. ✅ Set stem directions (alternating up/down)
4. ✅ Ensure voice IDs are preserved
5. ✅ Call this function before `part_to_lilypond()`

**Estimated Lines:** +25 lines

**Test Criteria:**
- LilyPond output should have `\voiceOne`, `\voiceTwo` contexts
- Stems should point correctly (up for voice 1, down for voice 2)
- No voice crossing warnings in LilyPond compilation

---

### Step 5: Write Multi-Voice Documentation
**File:** `MULTI_VOICE_BLUEPRINT_GUIDE.md` (NEW)

**Action Items:**
1. ✅ Explain multi-voice syntax with examples
2. ✅ Show SATB layout pattern: `"(Sop, Alt) & (Ten, Bas)"`
3. ✅ Document voice separation rules
4. ✅ Provide piano example (independent hands)
5. ✅ Show data structure internals
6. ✅ Include troubleshooting tips

**Estimated Lines:** ~150 lines

**Test Criteria:**
- Composer can understand multi-voice syntax from examples
- Clear distinction between single-voice and multi-voice blueprints
- Troubleshooting section addresses common errors

---

### Step 6: Create Test Cases for Multi-Voice Scenarios
**File:** `tests/test_multi_voice.py` (NEW)

**Action Items:**
1. ✅ Test 2-voice staff (simple case)
2. ✅ Test 4-voice SATB (complex case)
3. ✅ Test mixed: single-voice staff + multi-voice staff
4. ✅ Test voice duration matching
5. ✅ Test voice rest handling

**Estimated Lines:** ~150 lines

**Test Criteria:**
- All tests passing
- Voice count validation
- Event count validation per voice
- Duration matching validation

---

## 🎯 ACCEPTANCE CRITERIA

### Functional Requirements
- [ ] `fourteenth.py` generates valid PDF with 2 staves
- [ ] Upper staff shows Soprano (stems up) + Alto (stems down) overlaid
- [ ] Lower staff shows Tenor (stems up) + Bass (stems down) overlaid
- [ ] MIDI playback has 4 independent voices
- [ ] MusicXML export preserves voice separation
- [ ] No LilyPond compilation errors or warnings

### Code Quality Requirements
- [ ] Multi-voice logic in `score_builder.py` is commented and clear
- [ ] Voice layer creation in `music_data.py` handles edge cases
- [ ] No code duplication (reuse existing event conversion)
- [ ] Follows project patterns (matches `thirteenth.py` structure)

### Documentation Requirements
- [ ] `MULTI_VOICE_BLUEPRINT_GUIDE.md` created with examples
- [ ] `fourteenth.py` docstring explains SATB showcase
- [ ] `PRIORITY_PROGRESS.md` updated with completion status
- [ ] Code comments explain multi-voice data flow

### Testing Requirements
- [ ] `tests/test_multi_voice.py` created with 5+ test functions
- [ ] All tests passing
- [ ] Edge cases covered (rests, duration mismatches, single voice mixed with multi)

---

## 📊 ESTIMATED EFFORT

### Time Breakdown
1. **Step 1** (score_builder.py): 2-3 hours
   - Multi-voice assembly logic
   - Testing and debugging

2. **Step 2** (music_data.py): 2-3 hours
   - Voice layer creation
   - music21 integration

3. **Step 3** (fourteenth.py): 1-2 hours
   - Write SATB content
   - Test and validate

4. **Step 4** (engraving pipeline): 1 hour
   - Stem direction logic
   - Testing

5. **Step 5** (documentation): 1-2 hours
   - Write guide
   - Examples and diagrams

6. **Step 6** (test cases): 2 hours
   - Write tests
   - Validate coverage

**Total Estimated Time:** 9-13 hours of focused development

### Risk Assessment

**Low Risk:**
- Parser already extracts multi-voice content correctly
- music21 has built-in Voice class
- Template structure already established

**Medium Risk:**
- Voice overlay timing (need to ensure all voices start at offset 0)
- Stem direction automation (may need manual adjustment)
- Duration matching across voices (rests need careful handling)

**Mitigation:**
- Incremental testing (test 2-voice before 4-voice)
- Reference music21 documentation for Voice best practices
- Study existing polyphonic music21 examples

---

## 🔍 TECHNICAL DEEP DIVE

### Current Parser Output (Already Working)

Given this input:
```python
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"
VOICE_STAVE_DATA = "SOP_A, ALT_A & TEN_A, BAS_A"
```

The parser already produces:
```python
# parse_voice_stave_def() output:
layout = [
    ['Soprano', 'Alto'],
    ['Tenor', 'Bass']
]

# parse_voice_stave_data() output:
sections = [
    [  # Section 1
        [['SOP_A'], ['ALT_A']],  # Staff 1: 2 voices
        [['TEN_A'], ['BAS_A']]   # Staff 2: 2 voices
    ]
]
```

✅ **Parser is complete and tested** (validated in `score_builder.py` lines 60-95)

### Gap: Assembly Logic (Needs Implementation)

Current assembly (lines 149-180):
```python
# 🔴 PROBLEM: Only uses staff_content[0]
if staff_content and isinstance(staff_content[0], list):
    snippet_names = staff_content[0]  # ❌ Takes ONLY first voice
```

Required assembly:
```python
# 🟢 SOLUTION: Process ALL voices
if staff_content and isinstance(staff_content[0], list):
    voice_events = {}
    for voice_idx, voice_snippets in enumerate(staff_content):
        voice_name = layout[staff_idx][voice_idx]
        voice_events[voice_name] = []
        for snippet_name in voice_snippets:
            events = snippets[snippet_name]
            voice_events[voice_name].extend(events)
    
    # Create multi-voice section event
    parts[staff_name].append({
        'type': 'multi_voice_section',
        'voices': voice_events
    })
```

**This is the core implementation gap that Priority 3 addresses.**

---

## 🎼 MUSIC THEORY CONSIDERATIONS

### Voice Leading
- Soprano: Highest voice, stems up
- Alto: Lower voice on treble staff, stems down
- Tenor: Higher voice on bass staff, stems up
- Bass: Lowest voice, stems down

### Clef Assignment
- Staves with Soprano/Alto: Treble clef
- Staves with Tenor/Bass: Bass clef (or treble clef with octave transposition)

### Duration Alignment
- All voices in a section must have matching total duration
- If one voice has fewer notes, it should have rests
- Blueprint Framework should validate duration matching

---

## 📚 REFERENCES

### Existing Documentation
- `BLUEPRINT_IMPLEMENTATION_COMPLETE.md` - Framework specification
- `BLUEPRINT_QUICK_REFERENCE.md` - Syntax guide
- `thirteenth.py` - Single-voice template

### music21 Documentation
- [music21.stream.Voice](https://web.mit.edu/music21/doc/moduleReference/moduleStream.html#music21.stream.Voice)
- [Polyphonic Examples](https://web.mit.edu/music21/doc/usersGuide/usersGuide_22_graphing.html)

### LilyPond Voice Syntax
- `\voiceOne`, `\voiceTwo` contexts
- Stem direction: `stemUp`, `stemDown`

---

## ✅ SUCCESS METRICS

### Primary Metric
**Can a composer write a 4-part SATB hymn using blueprint strings and generate a professional-quality PDF?**

**Yes** → Priority 3 complete  
**No** → Additional work required

### Secondary Metrics
1. Code reduction: Multi-voice assembly should be <50 lines
2. No manual voice wrangling: Framework handles stem directions automatically
3. Blueprint clarity: Non-programmers can understand SATB syntax
4. Test coverage: All multi-voice scenarios have automated tests

---

## 🚀 NEXT ACTIONS (Start Here)

### Immediate First Step
```bash
# 1. Open score_builder.py
# 2. Navigate to lines 149-180 (assembly loop)
# 3. Add multi-voice branch
```

### Implementation Order
1. ✅ **Modify `build_score_from_blueprint()`** - This unlocks everything else
2. ✅ **Enhance `data_to_part()`** - Converts multi-voice events to music21
3. ✅ **Create `fourteenth.py`** - Validates end-to-end workflow
4. ✅ **Test and debug** - Ensure PDF/MIDI output is correct
5. ✅ **Write documentation** - Enable other composers to use it
6. ✅ **Create test suite** - Prevent regressions

---

## 📞 SUPPORT & QUESTIONS

### Common Questions

**Q: Why not use separate parts for each voice?**  
A: Soprano+Alto share a staff, as do Tenor+Bass. They must overlay, not stack.

**Q: Can I mix single-voice and multi-voice staves?**  
A: Yes! Example: `"Piano & (Soprano, Alto)"` - Piano is single-voice, choir is multi-voice.

**Q: What if voice durations don't match?**  
A: Framework should validate and warn. Shorter voices need rests added.

**Q: How many voices can one staff have?**  
A: Technically unlimited, but 2-3 voices per staff is typical for readability.

---

**End of Implementation Plan**  
**Status:** Ready to Begin  
**Next Step:** Modify `score_builder.py` lines 149-180
