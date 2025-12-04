"""
Test MusicXML/MIDI Export with Barline-Aware Parsing
====================================================

This test creates a simple study WITHOUT bypass mode to verify that:
1. Barlines are parsed into events correctly
2. MusicXML export creates proper measures from barlines
3. Time signature and key signature propagate correctly
"""

import sys
sys.path.insert(0, 'src')

from lilypond_parser import parse_lilypond_to_data
from music_data import data_to_part
import music21

# Simple snippet with explicit barlines
TEST_SNIPPET = r"""
\relative c' {
    \key d \major
    \time 3/4
    d4 e fis |
    g4 a b |
    a4 g fis |
    d2.
}
"""

print("=" * 70)
print("TESTING BARLINE-AWARE MUSICXML EXPORT")
print("=" * 70)

# Parse the snippet
print("\n1. Parsing LilyPond snippet...")
parsed_data = parse_lilypond_to_data(TEST_SNIPPET, part_name='TestPart')
metadata = parsed_data['metadata']
events = parsed_data['parts']['TestPart']

print(f"   ✓ Parsed {len(events)} events")
print(f"   ✓ Time signature: {metadata.get('time_signature', 'N/A')}")
print(f"   ✓ Key signature: {metadata.get('key_signature', 'N/A')}")

# Count different event types
note_count = sum(1 for e in events if e.get('type') == 'note')
barline_count = sum(1 for e in events if e.get('type') == 'barline')
rest_count = sum(1 for e in events if e.get('type') == 'rest')

print(f"\n   Event breakdown:")
print(f"     - Notes: {note_count}")
print(f"     - Barlines: {barline_count}")
print(f"     - Rests: {rest_count}")

# Convert to music21 Part
print("\n2. Converting to music21.Part...")
part = data_to_part(events, metadata)

print(f"   ✓ Created music21.Part with {len(part.getElementsByClass('Measure'))} measures")

# Check measure contents
measures = part.getElementsByClass('Measure')
for i, measure in enumerate(measures, 1):
    notes = measure.getElementsByClass('GeneralNote')
    print(f"     Measure {i}: {len(notes)} notes/rests")

# Check time signature
first_measure = measures[0] if len(measures) > 0 else None
if first_measure:
    ts = first_measure.timeSignature
    ks = first_measure.keySignature
    print(f"\n   First measure metadata:")
    print(f"     Time signature: {ts if ts else 'None'}")
    print(f"     Key signature: {ks if ks else 'None'}")

# Export to MusicXML
print("\n3. Exporting to MusicXML...")
score = music21.stream.Score()
score.metadata = music21.metadata.Metadata()
score.metadata.title = "Barline Test"
score.metadata.composer = "Test"
score.insert(0, part)

xml_path = "outputs/test_barline_export.musicxml"
score.write('musicxml', fp=xml_path)
print(f"   ✓ Exported to {xml_path}")

# Verify the output
import xml.etree.ElementTree as ET
tree = ET.parse(xml_path)
root = tree.getroot()

# Count measures in XML
xml_measures = root.findall(".//{*}measure")
print(f"\n4. Verification:")
print(f"   ✓ MusicXML contains {len(xml_measures)} measures")

# Check time signature in XML
time_elem = root.find(".//{*}time")
if time_elem is not None:
    beats = time_elem.find("{*}beats")
    beat_type = time_elem.find("{*}beat-type")
    if beats is not None and beat_type is not None:
        print(f"   ✓ Time signature: {beats.text}/{beat_type.text}")

# Check key signature in XML
key_elem = root.find(".//{*}key")
if key_elem is not None:
    fifths = key_elem.find("{*}fifths")
    mode = key_elem.find("{*}mode")
    if fifths is not None:
        print(f"   ✓ Key signature: {fifths.text} sharps/flats, {mode.text if mode is not None else 'major'}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
print(f"\nOpen in MuseScore: {xml_path}")
print("Expected: 4 measures in 3/4 time, D major (2 sharps)")
