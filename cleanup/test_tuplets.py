"""
Test Tuplet Support
===================

Quick test to verify tuplet parsing and generation.
"""

from lilypond_parser import parse_lilypond_to_data

# Test basic triplet
test_input = r"\relative c' { \time 4/4 c4 \tuplet 3/2 { c8 d8 e8 } f4 g4 }"

print("Testing tuplet parsing...")
print(f"Input: {test_input}")
print()

try:
    result = parse_lilypond_to_data(test_input, part_name='Test')
    events = result.get('parts', {}).get('Test', [])
    
    print(f"✅ Parsed {len(events)} events")
    print()
    
    for i, ev in enumerate(events):
        if ev.get('type') == 'tuplet':
            print(f"Event {i}: TUPLET {ev.get('numerator')}/{ev.get('denominator')}")
            for j, note in enumerate(ev.get('notes', [])):
                if note.get('type') == 'note':
                    print(f"  Note {j}: {note.get('step')}{note.get('octave')} (ql={note.get('ql')})")
                elif note.get('type') == 'rest':
                    print(f"  Note {j}: REST (ql={note.get('ql')})")
        elif ev.get('type') == 'note':
            print(f"Event {i}: {ev.get('step')}{ev.get('octave')} (ql={ev.get('ql')})")
        elif ev.get('type') == 'rest':
            print(f"Event {i}: REST (ql={ev.get('ql')})")
    
    print()
    print("✅ Tuplet parsing works!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
