#!/usr/bin/env python3
"""Simple test for multi-voice functionality."""

from music_data import data_to_part, _event_to_music21
import music21

# Test 1: Can we convert a simple multi-voice section?
print("Test 1: Multi-voice section event handling")
print("=" * 60)

multi_voice_event = {
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
}

events = [multi_voice_event]
part = data_to_part(events)

print(f"Part created: {part}")
print(f"Part contains {len(part)} elements")

# Check what's in the part
for element in part:
    print(f"  Element: {element}, type: {type(element)}")

# Check for voices (they should be inside measures)
voices = part.flatten().getElementsByClass(music21.stream.Voice)
print(f"Found {len(voices)} voices (in flattened part)")

for v in voices:
    print(f"  Voice: {v.id}, contains {len(list(v.notes))} notes")

# Also check measures
measures = part.getElementsByClass(music21.stream.Measure)
print(f"Found {len(measures)} measures")
for m in measures:
    m_voices = m.getElementsByClass(music21.stream.Voice)
    print(f"  Measure contains {len(m_voices)} voices")
    for v in m_voices:
        notes = list(v.notes)
        print(f"    Voice '{v.id}': {len(notes)} notes")
        for n in notes:
            print(f"      - {n.nameWithOctave} {n.duration.quarterLength}QL, stem: {n.stemDirection}")

success = len(measures) == 1 and len(measures[0].getElementsByClass(music21.stream.Voice)) == 2
print("\n✅ Test passed!" if success else "\n❌ Test FAILED!")
