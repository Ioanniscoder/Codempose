"""
Test Bypass Mode MusicXML Export
=================================

Verify that bypass-mode studies can now export to MusicXML by re-parsing
the raw LilyPond snippets.
"""

import xml.etree.ElementTree as ET

print("=" * 70)
print("VERIFYING BYPASS MODE MUSICXML EXPORT")
print("=" * 70)

# Parse the MusicXML file
xml_path = "outputs/100th.musicxml"
tree = ET.parse(xml_path)
root = tree.getroot()

# Get basic info
title_elem = root.find(".//{*}work-title")
title = title_elem.text if title_elem is not None else "Unknown"

# Count measures
measures = root.findall(".//{*}measure")
print(f"\n✓ Title: {title}")
print(f"✓ Total measures: {len(measures)}")

# Count notes vs rests
notes_with_pitch = root.findall(".//{*}note/{*}pitch")
rests = root.findall(".//{*}note/{*}rest")
print(f"✓ Notes with pitch: {len(notes_with_pitch)}")
print(f"✓ Rests: {len(rests)}")

# Check time signature
time_elem = root.find(".//{*}time")
if time_elem is not None:
    beats = time_elem.find("{*}beats")
    beat_type = time_elem.find("{*}beat-type")
    if beats is not None and beat_type is not None:
        print(f"✓ Time signature: {beats.text}/{beat_type.text}")

# Check key signature
key_elem = root.find(".//{*}key")
if key_elem is not None:
    fifths = key_elem.find("{*}fifths")
    mode = key_elem.find("{*}mode")
    if fifths is not None:
        sharps_flats = int(fifths.text)
        key_name = "G major" if sharps_flats == 1 else f"{sharps_flats} sharps/flats"
        print(f"✓ Key signature: {key_name}")

# Check first few pitches
print(f"\nFirst 10 pitches:")
for i, pitch_elem in enumerate(notes_with_pitch[:10], 1):
    step = pitch_elem.find("{*}step")
    octave = pitch_elem.find("{*}octave")
    alter = pitch_elem.find("{*}alter")
    
    pitch_str = step.text if step is not None else "?"
    if alter is not None:
        pitch_str += "#" if alter.text == "1" else "b"
    pitch_str += octave.text if octave is not None else "?"
    
    print(f"  {i}. {pitch_str}")

print("\n" + "=" * 70)

# Verify quality
if len(notes_with_pitch) > 50:
    print("✅ SUCCESS: MusicXML contains substantial note content")
    print("   Bypass mode raw_lilypond snippets were successfully re-parsed!")
else:
    print("⚠️  WARNING: MusicXML has few notes - may have export issues")

if len(measures) > 20:
    print("✅ SUCCESS: Measure structure looks correct")
else:
    print("⚠️  WARNING: Few measures - may be incomplete")

print("\n💡 Open in MuseScore to verify:")
print(f"   {xml_path}")
print("=" * 70)
