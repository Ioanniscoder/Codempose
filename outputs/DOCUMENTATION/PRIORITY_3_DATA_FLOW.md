# PRIORITY 3: MULTI-VOICE DATA FLOW DIAGRAM

## Current State (Single-Voice Only)

```
INPUT BLUEPRINT:
┌─────────────────────────────────────────────────────────┐
│ VOICE_STAVE_DEF = "UpperStaff & LowerStaff"            │
│ VOICE_STAVE_DATA = "MELODY & HARMONY"                   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ parse_voice_stave_def() → layout                        │
│   [['UpperStaff'], ['LowerStaff']]                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ parse_voice_stave_data() → sections                     │
│   [[['MELODY'], ['HARMONY']]]                           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ build_score_from_blueprint() → parts dictionary         │
│   {                                                      │
│     'UpperStaff': [note, note, rest, barline],          │
│     'LowerStaff': [note, note, note, barline]           │
│   }                                                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ data_to_part() → music21.stream.Part                    │
│   Part: Note, Note, Rest, Barline                       │
└─────────────────────────────────────────────────────────┘
                           ↓
                      ✅ PDF OUTPUT
```

---

## Target State (Multi-Voice Support)

```
INPUT BLUEPRINT:
┌─────────────────────────────────────────────────────────┐
│ VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"    │
│ VOICE_STAVE_DATA = "SOP_A, ALT_A & TEN_A, BAS_A"       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ parse_voice_stave_def() → layout                        │
│   [                                                      │
│     ['Soprano', 'Alto'],    ← Staff 1 has 2 voices      │
│     ['Tenor', 'Bass']       ← Staff 2 has 2 voices      │
│   ]                                                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ parse_voice_stave_data() → sections                     │
│   [                                                      │
│     [                                 ← Section 1        │
│       [['SOP_A'], ['ALT_A']],        ← Staff 1 voices   │
│       [['TEN_A'], ['BAS_A']]         ← Staff 2 voices   │
│     ]                                                    │
│   ]                                                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ build_score_from_blueprint() → parts dictionary         │
│ 🔴 CURRENT: Only processes first voice                  │
│   {                                                      │
│     'Staff1': [SOP_A events only],   ❌ Missing ALT_A   │
│     'Staff2': [TEN_A events only]    ❌ Missing BAS_A   │
│   }                                                      │
│                                                          │
│ 🟢 REQUIRED: Process ALL voices                         │
│   {                                                      │
│     'Staff1': [                                          │
│       {                                                  │
│         'type': 'multi_voice_section',                  │
│         'voices': {                                      │
│           'Soprano': [note, note, note, note],          │
│           'Alto': [note, note, note, note]              │
│         }                                                │
│       },                                                 │
│       {'type': 'barline', 'style': '||'}                │
│     ],                                                   │
│     'Staff2': [                                          │
│       {                                                  │
│         'type': 'multi_voice_section',                  │
│         'voices': {                                      │
│           'Tenor': [note, note, note, note],            │
│           'Bass': [note, note, note, note]              │
│         }                                                │
│       },                                                 │
│       {'type': 'barline', 'style': '||'}                │
│     ]                                                    │
│   }                                                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ data_to_part() → music21.stream.Part                    │
│ 🔴 CURRENT: Doesn't handle multi_voice_section          │
│                                                          │
│ 🟢 REQUIRED: Create Voice objects                       │
│   Part (Staff1):                                         │
│     ├─ Voice('Soprano'): Note, Note, Note, Note         │
│     │    └─ stemDirection = 'up'                        │
│     └─ Voice('Alto'): Note, Note, Note, Note            │
│          └─ stemDirection = 'down'                      │
│   Part (Staff2):                                         │
│     ├─ Voice('Tenor'): Note, Note, Note, Note           │
│     │    └─ stemDirection = 'up'                        │
│     └─ Voice('Bass'): Note, Note, Note, Note            │
│          └─ stemDirection = 'down'                      │
└─────────────────────────────────────────────────────────┘
                           ↓
                   ✅ PDF OUTPUT (SATB)
                    
                    ═══════════════════
                      Treble Staff
                    ═══════════════════
                    ♪ ♪ ♪ ♪  (Soprano ↑)
                    ♪ ♪ ♪ ♪  (Alto ↓)
                    ═══════════════════
                      Bass Staff
                    ═══════════════════
                    ♪ ♪ ♪ ♪  (Tenor ↑)
                    ♪ ♪ ♪ ♪  (Bass ↓)
                    ═══════════════════
```

---

## Code Changes Required

### Change 1: score_builder.py (lines 149-180)

**BEFORE:**
```python
for staff_idx, staff_content in enumerate(section):
    staff_name = list(parts.keys())[staff_idx]
    
    # 🔴 PROBLEM: Only processes staff_content[0]
    if staff_content and isinstance(staff_content[0], list):
        snippet_names = staff_content[0]  # ❌ First voice only
    else:
        snippet_names = staff_content
    
    # Assemble events (only from first voice)
    staff_events = []
    for snippet_name in snippet_names:
        snippet_events = snippets[snippet_name]
        staff_events.extend(snippet_events)
    
    parts[staff_name].extend(staff_events)
```

**AFTER:**
```python
for staff_idx, staff_content in enumerate(section):
    staff_name = list(parts.keys())[staff_idx]
    
    # 🟢 SOLUTION: Process ALL voices
    if staff_content and isinstance(staff_content[0], list):
        # Multi-voice staff
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
            print(f"      {voice_name}: +{snippet_name} ({len(voice_events)} events)")
        
        # Create multi-voice section event
        parts[staff_name].append({
            'type': 'multi_voice_section',
            'voices': voice_events_dict
        })
    else:
        # Single-voice staff (existing logic)
        snippet_names = staff_content
        staff_events = []
        for snippet_name in snippet_names:
            snippet_events = snippets[snippet_name]
            staff_events.extend(snippet_events)
        
        parts[staff_name].extend(staff_events)
```

---

### Change 2: music_data.py (data_to_part function)

**BEFORE:**
```python
def data_to_part(events: List[Dict], part_name: str = "Part"):
    """Convert canonical event list to music21.stream.Part."""
    part = music21.stream.Part()
    part.partName = part_name
    
    for event in events:
        # 🔴 PROBLEM: Doesn't handle multi_voice_section
        if event['type'] == 'note':
            # ... create note ...
        elif event['type'] == 'rest':
            # ... create rest ...
        # No handler for multi_voice_section!
    
    return part
```

**AFTER:**
```python
def data_to_part(events: List[Dict], part_name: str = "Part"):
    """Convert canonical event list to music21.stream.Part.
    
    NEW: Supports multi-voice sections with voice dictionary.
    """
    part = music21.stream.Part()
    part.partName = part_name
    
    for event in events:
        # 🟢 NEW: Handle multi-voice sections
        if event.get('type') == 'multi_voice_section':
            voices_dict = event['voices']
            
            # Create Voice objects for each voice
            voice_objects = []
            for voice_idx, (voice_name, voice_events) in enumerate(voices_dict.items()):
                voice_stream = music21.stream.Voice()
                voice_stream.id = voice_name
                
                # Add events to this voice
                for v_event in voice_events:
                    element = _event_to_music21(v_event)
                    if element:
                        voice_stream.append(element)
                
                # Set stem direction
                if voice_idx % 2 == 0:
                    # Upper voice: stems up
                    for note in voice_stream.flatten().notes:
                        note.stemDirection = 'up'
                else:
                    # Lower voice: stems down
                    for note in voice_stream.flatten().notes:
                        note.stemDirection = 'down'
                
                voice_objects.append(voice_stream)
            
            # Create measure and insert all voices at offset 0
            measure = music21.stream.Measure()
            for voice_obj in voice_objects:
                measure.insert(0, voice_obj)
            
            part.append(measure)
        
        # 🟢 EXISTING: Single-event handling
        elif event['type'] == 'note':
            # ... existing note logic ...
        elif event['type'] == 'rest':
            # ... existing rest logic ...
        # ... other event types ...
    
    return part

def _event_to_music21(event: Dict):
    """Helper to convert single event to music21 element."""
    if event['type'] == 'note':
        # ... create note ...
    elif event['type'] == 'rest':
        # ... create rest ...
    # ... etc ...
```

---

## Visual: Parser Already Working ✅

```
INPUT: "(Soprano, Alto) & (Tenor, Bass)"
                ↓
       parse_voice_stave_def()
                ↓
         ┌─────────────┐
         │   layout    │
         └─────────────┘
                ↓
    [['Soprano', 'Alto'], ['Tenor', 'Bass']]
           ✅ CORRECT

INPUT: "SOP_A, ALT_A & TEN_A, BAS_A"
                ↓
       parse_voice_stave_data()
                ↓
         ┌─────────────┐
         │  sections   │
         └─────────────┘
                ↓
[
  [  # Section 1
    [['SOP_A'], ['ALT_A']],  # Staff 1 voices
    [['TEN_A'], ['BAS_A']]   # Staff 2 voices
  ]
]
           ✅ CORRECT
```

**Conclusion:** Parser is complete! Only assembly logic needs implementation.

---

## Visual: Assembly Gap 🔴

```
CURRENT ASSEMBLY (BROKEN):
┌──────────────────────────────────────┐
│ staff_content = [['SOP_A'], ['ALT_A']]│
│                      ↓                │
│ snippet_names = staff_content[0]     │  ← Takes only [0]
│               = ['SOP_A']             │  ← Missing ALT_A!
│                      ↓                │
│ staff_events = snippets['SOP_A']     │
│                      ↓                │
│ parts['Staff1'] = [SOP_A events]     │  ← Incomplete!
└──────────────────────────────────────┘

REQUIRED ASSEMBLY (FIXED):
┌──────────────────────────────────────┐
│ staff_content = [['SOP_A'], ['ALT_A']]│
│                      ↓                │
│ for voice_idx, voice_snippets:       │  ← Loop ALL voices
│   voice_name = layout[...][voice_idx]│
│   voice_events[voice_name] = [...]   │
│                      ↓                │
│ parts['Staff1'] = [                  │
│   {                                   │
│     'type': 'multi_voice_section',   │
│     'voices': {                       │
│       'Soprano': [SOP_A events],     │  ← Both voices!
│       'Alto': [ALT_A events]         │
│     }                                 │
│   }                                   │
│ ]                                     │
└──────────────────────────────────────┘
```

---

## Implementation Priority

### ⚡ HIGHEST PRIORITY
**File:** `score_builder.py` lines 149-180  
**Why:** Unblocks everything else  
**Effort:** 2-3 hours  
**Impact:** Enables multi-voice data structure

### 🔥 HIGH PRIORITY
**File:** `music_data.py` data_to_part()  
**Why:** Needed for output generation  
**Effort:** 2-3 hours  
**Impact:** Creates Voice objects in music21

### ⭐ MEDIUM PRIORITY
**File:** `fourteenth.py` (NEW)  
**Why:** Validates end-to-end workflow  
**Effort:** 1-2 hours  
**Impact:** Demonstrates SATB capability

### 📚 LOWER PRIORITY
**Files:** Documentation + Tests  
**Why:** Important but not blocking  
**Effort:** 3-4 hours  
**Impact:** Enables adoption and prevents regressions

---

## Success Validation Checklist

After implementation, verify:

```
✅ Console Output Shows All Voices:
   Section 1:
      Soprano: +SOP_A (4 events)
      Alto: +ALT_A (4 events)
      Tenor: +TEN_A (4 events)
      Bass: +BAS_A (4 events)

✅ Data Structure Correct:
   parts['Staff1'][0]['type'] == 'multi_voice_section'
   parts['Staff1'][0]['voices']['Soprano'] == [4 events]
   parts['Staff1'][0]['voices']['Alto'] == [4 events]

✅ music21 Voice Objects Created:
   part.getElementsByClass(Voice) == 2 voices
   voice[0].id == 'Soprano'
   voice[1].id == 'Alto'

✅ PDF Output Correct:
   - 2 staves (treble and bass)
   - Upper staff: 2 overlaid voices
   - Lower staff: 2 overlaid voices
   - Stems point correct directions
   - No LilyPond warnings

✅ MIDI Playback:
   - 4 independent voices audible
   - Proper harmony (SATB)

✅ No Regressions:
   - thirteenth.py still works
   - second.py still works
   - eleventh.py still works
```

---

**End of Data Flow Diagram**  
**Next Step:** Implement Change 1 (score_builder.py)
