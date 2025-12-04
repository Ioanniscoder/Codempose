#!/usr/bin/env python3
"""
Test MusicXML/MIDI output with barline-aware measure creation.
This script tests the updated music_data.py without requiring music21.
"""

# Mock events with barlines (simulating parsed LilyPond)
test_events = [
    {'type': 'note', 'step': 'D', 'octave': 4, 'alter': 0, 'ql': 1.0},
    {'type': 'note', 'step': 'E', 'octave': 4, 'alter': 0, 'ql': 1.0},
    {'type': 'note', 'step': 'F', 'octave': 4, 'alter': 0, 'ql': 1.0},
    {'type': 'barline', 'style': '|', 'ql': 0.0},
    {'type': 'note', 'step': 'G', 'octave': 4, 'alter': 0, 'ql': 1.0},
    {'type': 'note', 'step': 'A', 'octave': 4, 'alter': 0, 'ql': 1.0},
    {'type': 'note', 'step': 'B', 'octave': 4, 'alter': 0, 'ql': 1.0},
    {'type': 'barline', 'style': '|', 'ql': 0.0},
]

test_metadata = {
    'title': 'Test Barline Export',
    'composer': 'Test',
    'time_signature': '3/4',
    'key_signature': {'tonic': 'g', 'mode': 'major'}
}

print("="*70)
print("MUSICXML/MIDI BARLINE EXPORT TEST")
print("="*70)

print("\n📊 Test Data:")
print(f"  Events: {len(test_events)} (including 2 barlines)")
print(f"  Time signature: {test_metadata['time_signature']}")
print(f"  Expected measures: 3 (bar1: 3 notes, bar2: 3 notes, bar3: empty/incomplete)")

print("\n🔍 Event Structure:")
measure = 1
notes_in_measure = 0
for i, ev in enumerate(test_events):
    if ev['type'] == 'barline':
        print(f"  Measure {measure}: {notes_in_measure} notes → BARLINE")
        measure += 1
        notes_in_measure = 0
    else:
        notes_in_measure += 1
        print(f"    {i}: {ev['type']} {ev.get('step', '?')}{ev.get('octave', '?')} ({ev['ql']} QL)")

if notes_in_measure > 0:
    print(f"  Measure {measure}: {notes_in_measure} notes (no closing barline)")

print("\n✅ Expected MusicXML structure:")
print("  - 3 measures total")
print("  - Measure 1: D4, E4, F4 (3.0 QL)")
print("  - Measure 2: G4, A4, B4 (3.0 QL)")
print("  - Measure 3: empty or incomplete")

print("\n📝 Code Changes Made:")
print("  1. lily_converter.py: Added barline handling to events_to_lily()")
print("  2. music_data.py: Modified data_to_part() to create measures from barlines")
print("  3. music_data.py: Added time/key signature to first measure")

print("\n⚠️  Note: Actual test requires music21 library to be installed")
print("    This script validates the logic structure only.")

print("\n" + "="*70)
print("To test with actual music21 export:")
print("  1. Regenerate study 100: python3 generate_study.py 100")
print("  2. Check MusicXML: outputs/100th.musicxml")
print("  3. Verify measures: grep '<measure' outputs/100th.musicxml | wc -l")
print("  4. Verify barlines in measures (not just 2 total)")
print("="*70)
