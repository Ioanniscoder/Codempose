# Note Tracking in Codempose

This guide explains how to track individual notes through transformations in the Codempose framework.

## Levels of Tracking

### 1. **Voice-Level Tracking** (Section Tracking)
Tracks entire transformation sections (already implemented in twelfth.py):

```python
voice_tracking = {
    '01_Original': {
        'source': 'SOURCE_MELODY_LILY',
        'transformation': 'identity',
        'description': 'Original melodic snippet',
        'events': 15,
    },
}
```

**Where to find it**: In the LilyPond output comments under "VOICE TRACKING (Station 4 - Detailed)"

### 2. **Event-Level Tracking** (Note-by-Note)
Each event dictionary can carry tracking metadata:

```python
event = {
    'type': 'note',
    'step': 'E',
    'octave': 4,
    'ql': 2.0,
    'alter': 0,
    
    # Tracking metadata:
    'original_token': 'e2',              # Original LilyPond token
    'position': 0,                        # Position in source snippet
    'source_snippet': 'SOURCE_MELODY',    # Which snippet it came from
    'transformation_history': [           # Chain of transformations
        {'type': 'identity', 'section': '01_Original'},
        {'type': 'transpose', 'interval': 'P5', 'section': '03_Transposed_P5'},
    ],
}
```

## How to Track a Specific Note

### Example 1: Track Note Position Through Transformations

```python
def track_note_position(events, position):
    """Find a note at a specific position and show its properties."""
    if position < len(events):
        note = events[position]
        print(f"Note at position {position}:")
        print(f"  Type: {note.get('type')}")
        if note.get('type') == 'note':
            print(f"  Pitch: {note['step']}{note['octave']}")
            print(f"  Duration: {note['ql']} quarter notes")
            print(f"  Original token: {note.get('original_token', 'N/A')}")
        return note
    return None

# Usage:
from twelfth import build_score_data
score = build_score_data()
events = score['parts']['SingleLine']

# Track the first note through all sections
print("First note of each section:")
note_0 = track_note_position(events, 0)    # Original section
note_15 = track_note_position(events, 15)  # Harmony section (after first barline)
note_30 = track_note_position(events, 30)  # Transposed section
```

### Example 2: Enhanced Tracking with Transformation History

Add this to your `twelfth.py` to track transformation lineage:

```python
def add_tracking_metadata(events, source_name, transformation, section_id):
    """Add tracking metadata to each event."""
    tracked = []
    for i, ev in enumerate(events):
        # Copy event and add tracking
        tracked_ev = ev.copy()
        tracked_ev['source_snippet'] = source_name
        tracked_ev['transformation'] = transformation
        tracked_ev['section_id'] = section_id
        tracked_ev['section_position'] = i
        tracked.append(tracked_ev)
    return tracked

# Usage in build_score_data():
snippet_events_tracked = add_tracking_metadata(
    snippet_events, 
    'SOURCE_MELODY', 
    'identity', 
    '01_Original'
)

transposed_tracked = add_tracking_metadata(
    transposed,
    'SOURCE_MELODY',
    'transpose(P5)',
    '03_Transposed_P5'
)
```

### Example 3: Find All Instances of a Pitch

```python
def find_all_pitches(events, step, octave=None):
    """Find all occurrences of a specific pitch."""
    matches = []
    for i, ev in enumerate(events):
        if ev.get('type') == 'note' and ev.get('step') == step:
            if octave is None or ev.get('octave') == octave:
                matches.append({
                    'position': i,
                    'pitch': f"{ev['step']}{ev['octave']}",
                    'duration': ev['ql'],
                    'original_token': ev.get('original_token', 'N/A'),
                    'section': ev.get('section_id', 'unknown'),
                })
    return matches

# Usage:
from twelfth import build_score_data
score = build_score_data()
events = score['parts']['SingleLine']

# Find all E4 notes
e4_notes = find_all_pitches(events, 'E', 4)
print(f"Found {len(e4_notes)} E4 notes:")
for note in e4_notes[:5]:  # Show first 5
    print(f"  Position {note['position']}: {note['pitch']} (ql={note['duration']}) - {note.get('section')}")
```

### Example 4: Voice Documentation System (Already Implemented)

The `voice_documentation.py` module provides automatic tracking:

```python
from voice_documentation import register_and_document_voice

# Register a voice with full documentation
register_and_document_voice(
    voice_name='TransposedMelody',
    source_snippet='SOURCE_MELODY_LILY',
    transformation='transpose(P5)',
    events=transposed_events,
    description='Melody transposed up by perfect fifth'
)
```

This creates a "voice card" in the documentation that shows:
- Source snippet (LilyPond and TinyNotation)
- Transformation applied
- All events in the voice
- Event count and statistics

## Practical Note Tracking Workflow

### Step 1: Parse with tracking
```python
from lilypond_parser import parse_lilypond_to_data

parsed = parse_lilypond_to_data(SOURCE_MELODY_LILY, part_name='Melody')
events = parsed['parts']['Melody']

# Each event already has 'original_token' and 'position'
print(events[0])  
# {'type': 'note', 'step': 'E', 'octave': 4, 'ql': 2.0, 
#  'original_token': 'e2', 'position': 0}
```

### Step 2: Preserve tracking through transformations
```python
from music_data import data_to_part, extract_data_from_part

# Convert to music21 Part
part = data_to_part(events, metadata)

# Apply transformation
transposed_part = part.transpose('P5')

# Extract back - tracking is lost here, so add it back
transposed_events = extract_data_from_part(transposed_part)

# Manually add tracking
for i, ev in enumerate(transposed_events):
    ev['derived_from'] = events[i].get('original_token', '?')
    ev['transformation'] = 'transpose(P5)'
```

### Step 3: Query tracked notes
```python
# Find note by original token
def find_by_token(events, token):
    for ev in events:
        if ev.get('original_token') == token:
            return ev
    return None

original_e2 = find_by_token(events, 'e2')
print(f"Original e2 is now: {original_e2['step']}{original_e2['octave']}")
```

## Automated Tracking Example

Here's a complete example that tracks every transformation:

```python
def build_tracked_score():
    """Build score with complete note tracking."""
    parsed = parse_lilypond_to_data(SOURCE_MELODY_LILY, part_name='Melody')
    original = parsed['parts']['Melody']
    
    # Track original
    for i, ev in enumerate(original):
        ev['note_id'] = f"note_{i}"
        ev['transformation_chain'] = ['identity']
    
    # Track transpose
    transposed_part = data_to_part(original, {}).transpose('P5')
    transposed = extract_data_from_part(transposed_part)
    for i, ev in enumerate(transposed):
        ev['note_id'] = original[i].get('note_id')
        ev['transformation_chain'] = original[i].get('transformation_chain', []) + ['transpose(P5)']
        ev['derived_from'] = f"{original[i]['step']}{original[i]['octave']}"
    
    return original, transposed

original, transposed = build_tracked_score()

# Now you can trace any note's lineage
print(f"Note 0 original: {original[0]['step']}{original[0]['octave']}")
print(f"Note 0 after transpose: {transposed[0]['step']}{transposed[0]['octave']}")
print(f"Note 0 transformation chain: {transposed[0]['transformation_chain']}")
```

## Summary

**Available tracking mechanisms:**

1. **`original_token`** - Original LilyPond token (e.g., "e2")
2. **`position`** - Original position in snippet (0-indexed)
3. **`section_id`** - Which transformation section (e.g., "03_Transposed_P5")
4. **`voice_tracking`** - Section-level metadata (transformation type, event count)
5. **Custom tracking** - Add your own fields like `note_id`, `transformation_chain`, `derived_from`

**Where to see tracking:**
- LilyPond output comments: Voice tracking section
- Event dictionaries: `original_token`, `position` fields
- Custom queries: Use Python to filter/search events

**Best practice**: If you need detailed note-by-note tracking, add custom metadata fields to events after each transformation to preserve lineage.
