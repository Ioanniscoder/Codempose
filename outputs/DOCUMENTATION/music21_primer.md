# Music21 Primer for Codempose

A practical guide to using music21 functions in your study files.

## Table of Contents
1. [Basic Concepts](#basic-concepts)
2. [Creating Notes and Rests](#creating-notes-and-rests)
3. [Building Streams](#building-streams)
4. [Transformations](#transformations)
5. [Harmony and Chords](#harmony-and-chords)
6. [Rhythm Manipulation](#rhythm-manipulation)
7. [Analysis](#analysis)
8. [Common Patterns](#common-patterns)

---

## Basic Concepts

### Core Objects

```python
import music21

# Note: pitch + duration
note = music21.note.Note('C4', quarterLength=1.0)

# Rest: silence
rest = music21.note.Rest(quarterLength=1.0)

# Chord: multiple pitches simultaneously
chord = music21.chord.Chord(['C4', 'E4', 'G4'], quarterLength=2.0)

# Stream: container for musical elements
stream = music21.stream.Stream()
stream.append(note)
```

### Quarter Length (Duration)

```python
# Quarter length = 1.0 is a quarter note
note1 = music21.note.Note('C4', quarterLength=1.0)   # quarter
note2 = music21.note.Note('D4', quarterLength=2.0)   # half
note3 = music21.note.Note('E4', quarterLength=0.5)   # eighth
note4 = music21.note.Note('F4', quarterLength=4.0)   # whole
note5 = music21.note.Note('G4', quarterLength=1.5)   # dotted quarter
```

---

## Creating Notes and Rests

### Pitches

```python
# Different ways to specify pitch
note1 = music21.note.Note('C4')           # Middle C
note2 = music21.note.Note('C#4')          # C sharp
note3 = music21.note.Note('D-5')          # D flat, octave 5
note4 = music21.note.Note('E##3')         # E double sharp

# Using MIDI numbers (C4 = 60)
note5 = music21.note.Note()
note5.pitch.midi = 60

# Modifying pitch
note6 = music21.note.Note('C4')
note6.pitch.transpose(5, inPlace=True)    # Now F4
```

### Rests

```python
# Simple rest
rest = music21.note.Rest(quarterLength=2.0)

# Add to stream
part = music21.stream.Part()
part.append(music21.note.Note('C4', quarterLength=1))
part.append(music21.note.Rest(quarterLength=1))
part.append(music21.note.Note('D4', quarterLength=1))
```

---

## Building Streams

### Stream Types

```python
# Measure: single bar
measure = music21.stream.Measure()
measure.append(music21.note.Note('C4', quarterLength=1))
measure.append(music21.note.Note('D4', quarterLength=1))

# Part: single voice/instrument
part = music21.stream.Part()
part.append(measure)

# Score: multiple parts
score = music21.stream.Score()
score.append(part)
```

### Adding Metadata

```python
part = music21.stream.Part()

# Time signature
ts = music21.meter.TimeSignature('6/4')
part.insert(0, ts)

# Key signature
ks = music21.key.KeySignature(0)  # C major (0 sharps/flats)
part.insert(0, ks)

# Tempo
tempo = music21.tempo.MetronomeMark(number=90)
part.insert(0, tempo)

# Notes
part.append(music21.note.Note('C4', quarterLength=2))
part.append(music21.note.Note('D4', quarterLength=2))
```

---

## Transformations

### Transpose

```python
# Transpose up 5 semitones (perfect fourth)
original = music21.stream.Part()
original.append(music21.note.Note('C4', quarterLength=1))
original.append(music21.note.Note('E4', quarterLength=1))

transposed = original.transpose(5)
# Result: F4, A4

# Transpose down an octave
down_octave = original.transpose(-12)
# Result: C3, E3

# Transpose by interval name
up_fifth = original.transpose('P5')  # Perfect fifth
```

### Augmentation/Diminution

```python
# Double all durations (augmentation)
melody = music21.stream.Part()
melody.append(music21.note.Note('C4', quarterLength=1))
melody.append(music21.note.Note('D4', quarterLength=1))

augmented = melody.augmentOrDiminish(2)
# Durations: 2.0, 2.0 (half notes)

# Halve all durations (diminution)
diminished = melody.augmentOrDiminish(0.5)
# Durations: 0.5, 0.5 (eighth notes)
```

### Retrograde

```python
# Reverse the order of notes
melody = music21.stream.Part()
melody.append(music21.note.Note('C4', quarterLength=1))
melody.append(music21.note.Note('D4', quarterLength=1))
melody.append(music21.note.Note('E4', quarterLength=1))

retrograde = melody.flatten().notesAndRests.stream()
retrograde_list = list(reversed([n for n in retrograde]))
retrograde_stream = music21.stream.Part()
for note in retrograde_list:
    retrograde_stream.append(note)
# Result: E4, D4, C4
```

### Inversion

```python
# Mirror pitches around an axis
melody = music21.stream.Part()
melody.append(music21.note.Note('C4', quarterLength=1))
melody.append(music21.note.Note('E4', quarterLength=1))
melody.append(music21.note.Note('G4', quarterLength=1))

# Invert around C4
inverted = music21.stream.Part()
for note in melody.flatten().notes:
    interval = music21.interval.Interval(
        music21.pitch.Pitch('C4'), note.pitch)
    inverted_note = music21.note.Note(quarterLength=note.quarterLength)
    inverted_note.pitch = music21.pitch.Pitch('C4')
    inverted_note.pitch.transpose(-interval.semitones, inPlace=True)
    inverted.append(inverted_note)
# Result: C4, G#3, E3
```

---

## Harmony and Chords

### Creating Chords

```python
# From note names
chord1 = music21.chord.Chord(['C4', 'E4', 'G4'])

# C major triad from roman numeral
key = music21.key.Key('C')
chord2 = music21.roman.RomanNumeral('I', key).pitches

# Build chord from intervals
root = music21.pitch.Pitch('C4')
chord3 = music21.chord.Chord([root, 
                              root.transpose('M3'),  # Major third
                              root.transpose('P5')])  # Perfect fifth
```

### Chordify

```python
# Combine multiple parts into chords
soprano = music21.stream.Part()
soprano.append(music21.note.Note('E4', quarterLength=1))
soprano.append(music21.note.Note('D4', quarterLength=1))

alto = music21.stream.Part()
alto.append(music21.note.Note('C4', quarterLength=1))
alto.append(music21.note.Note('B3', quarterLength=1))

score = music21.stream.Score([soprano, alto])
chords = score.chordify()
# Result: Two chords [E4,C4], [D4,B3]
```

### Chord Analysis

```python
chord = music21.chord.Chord(['C4', 'E4', 'G4', 'B4'])

# Properties
chord.isDominantSeventh()   # True
chord.root()                # C4
chord.bass()                # C4
chord.quality               # 'major seventh'

# Get notes
for pitch in chord.pitches:
    print(pitch.nameWithOctave)  # C4, E4, G4, B4
```

---

## Rhythm Manipulation

### Duration

```python
note = music21.note.Note('C4')
note.duration.quarterLength = 1.5  # Dotted quarter

# Tuplets
note.duration.appendTuplet(music21.duration.Tuplet(3, 2))  # Triplet
```

### Meter and Beats

```python
# Create measures with time signature
measure = music21.stream.Measure()
measure.timeSignature = music21.meter.TimeSignature('3/4')

# Add notes (auto-fills to beat)
measure.append(music21.note.Note('C4', quarterLength=1))
measure.append(music21.note.Note('D4', quarterLength=1))
measure.append(music21.note.Note('E4', quarterLength=1))

# Check if measure is full
measure.isFull  # True
measure.barDuration  # 3.0 quarter lengths
```

---

## Analysis

### Intervals

```python
note1 = music21.note.Note('C4')
note2 = music21.note.Note('G4')

interval = music21.interval.Interval(note1, note2)
interval.name            # 'P5' (perfect fifth)
interval.niceName        # 'Perfect Fifth'
interval.semitones       # 7
interval.direction       # 1 (ascending)
```

### Key Detection

```python
melody = music21.stream.Part()
melody.append(music21.note.Note('C4', quarterLength=1))
melody.append(music21.note.Note('D4', quarterLength=1))
melody.append(music21.note.Note('E4', quarterLength=1))
melody.append(music21.note.Note('G4', quarterLength=1))

key = melody.analyze('key')
print(key)  # C major or a minor (depends on context)
```

### Ambitus (Range)

```python
melody = music21.stream.Part()
melody.append(music21.note.Note('C4', quarterLength=1))
melody.append(music21.note.Note('E5', quarterLength=1))

# Find highest and lowest
highest = melody.flatten().notes.highestNote()  # E5
lowest = melody.flatten().notes.lowestNote()    # C4
```

---

## Common Patterns

### Pattern 1: Create Melody from List

```python
def create_melody(pitches, durations):
    """Create a melody from pitch and duration lists"""
    part = music21.stream.Part()
    for pitch, dur in zip(pitches, durations):
        part.append(music21.note.Note(pitch, quarterLength=dur))
    return part

# Usage
melody = create_melody(
    ['C4', 'D4', 'E4', 'F4', 'G4'],
    [1, 1, 1, 1, 2]
)
```

### Pattern 2: Bass Line from Melody

```python
def create_bass_from_melody(melody, octaves_down=2):
    """Transpose melody down for bass line"""
    return melody.transpose(-12 * octaves_down)

# Usage
soprano = music21.stream.Part()
soprano.append(music21.note.Note('E4', quarterLength=2))
bass = create_bass_from_melody(soprano, octaves_down=2)
# Result: E2
```

### Pattern 3: Harmonize with Thirds

```python
def harmonize_with_thirds(melody):
    """Add harmony a third below each note"""
    harmony = music21.stream.Part()
    for note in melody.flatten().notes:
        harmony_note = music21.note.Note(quarterLength=note.quarterLength)
        harmony_note.pitch = note.pitch.transpose(-4)  # Major third down
        harmony.append(harmony_note)
    return harmony

# Usage
melody = music21.stream.Part()
melody.append(music21.note.Note('E4', quarterLength=1))
melody.append(music21.note.Note('G4', quarterLength=1))

harmony = harmonize_with_thirds(melody)
# Result: C4, E4
```

### Pattern 4: Create Sequence

```python
def create_sequence(motif, transpositions):
    """Repeat motif at different transpositions"""
    result = music21.stream.Part()
    for semitones in transpositions:
        transposed = motif.transpose(semitones)
        for element in transposed:
            result.append(element)
    return result

# Usage
motif = music21.stream.Part()
motif.append(music21.note.Note('C4', quarterLength=1))
motif.append(music21.note.Note('E4', quarterLength=1))

sequence = create_sequence(motif, [0, 2, 4, 5])
# Repeats motif at C, D, E, F
```

### Pattern 5: Extract and Transform

```python
def extract_every_other_note(melody):
    """Extract alternating notes"""
    result = music21.stream.Part()
    notes = list(melody.flatten().notes)
    for i in range(0, len(notes), 2):
        result.append(notes[i])
    return result

# Usage
melody = music21.stream.Part()
for pitch in ['C4', 'D4', 'E4', 'F4', 'G4', 'A4']:
    melody.append(music21.note.Note(pitch, quarterLength=1))

filtered = extract_every_other_note(melody)
# Result: C4, E4, G4
```

---

## Working with Codempose

### Integration Pattern

```python
def build_score_data():
    """Example from first.py"""
    from lilypond_parser import parse_lilypond_to_data
    from music_data import extract_data_from_part, data_to_part
    import music21
    
    # 1. Parse LilyPond input
    melody_data = parse_lilypond_to_data(SOURCE_MELODY_LILY, part_name='Melody')
    melody_events = melody_data['parts']['Melody']
    
    # 2. Convert to music21.Part
    melody_part = data_to_part(melody_events, metadata=melody_data['metadata'])
    
    # 3. Apply transformations
    transformed = melody_part.transpose(5)  # Up a fourth
    
    # 4. Convert back to score_data
    final_events = extract_data_from_part(transformed)
    
    score_data = {
        'metadata': {
            'title': 'My Composition',
            'time_signature': '6/4',
        },
        'parts': {
            'Melody': final_events
        }
    }
    
    return score_data
```

---

## Quick Reference

### Common Intervals (semitones)
- `0` - Unison
- `1` - Minor second
- `2` - Major second
- `3` - Minor third
- `4` - Major third
- `5` - Perfect fourth
- `6` - Tritone
- `7` - Perfect fifth
- `12` - Octave

### Interval Names
- `'m2'` - Minor second
- `'M2'` - Major second
- `'m3'` - Minor third
- `'M3'` - Major third
- `'P4'` - Perfect fourth
- `'P5'` - Perfect fifth
- `'P8'` - Octave

### Common Durations
- `0.25` - Sixteenth note
- `0.5` - Eighth note
- `1.0` - Quarter note
- `1.5` - Dotted quarter
- `2.0` - Half note
- `4.0` - Whole note

---

## Resources

- **music21 Documentation**: https://web.mit.edu/music21/doc/
- **User's Guide**: https://web.mit.edu/music21/doc/usersGuide/
- **Module Reference**: https://web.mit.edu/music21/doc/moduleReference/

---

**Created**: October 5, 2025  
**For**: Codempose composition workflow  
**Version**: 1.0
