#!/usr/bin/env python3
"""
Tenth Study: Demonstrating Programmatic Voice Documentation

Based on ninth.py, this study demonstrates the new documentation system
where programmatically generated voices are captured in the .ly file comments.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from composition_shorthand import parse_voice_assignment, transpose_events, invert_events
from voice_documentation import register_and_document_voice
from music_data import build_lilypond_file
import subprocess

# Declarative materials (from ninth.py)
VOICE_ASSIGNMENTS = {
    'REST': 'lily("r1")',
    'SOPRANO_THEME': 'lily("e\'\'4 d\'\'8 c\'\'8 b\'4 a\'4 | g\'2 a\'2 |")',
    'ALTO_THEME': 'lily("c\'4 b8 a8 g4 f4 | e2 f2 |")',
}

def build_score_data():
    """
    Hybrid composition: declarative + programmatic with documentation.
    """
    metadata = {
        'title': 'Tenth Study: Programmatic Voice Documentation',
        'composer': 'Codempose Framework',
        'subtitle': 'Demonstrating register_and_document_voice()'
    }
    
    # Parse declarative voices
    voice_lookup = {}
    for name, expr in VOICE_ASSIGNMENTS.items():
        voice_lookup[name] = parse_voice_assignment(expr, voice_lookup)
    
    print("\n" + "="*70)
    print("TENTH STUDY: Programmatic Voice Documentation")
    print("="*70)
    
    # === PROGRAMMATIC GENERATION WITH DOCUMENTATION ===
    print("\nGenerating programmatic voices...")
    
    # Soprano: use the theme as-is
    soprano_voice = voice_lookup['SOPRANO_THEME']
    
    # Alto: transpose soprano down a fifth
    alto_voice = transpose_events(voice_lookup['SOPRANO_THEME'], -7)
    register_and_document_voice('ALTO_GENERATED', alto_voice, voice_lookup, metadata)
    
    # Tenor: invert the alto theme
    tenor_voice = invert_events(voice_lookup['ALTO_THEME'], 'c\'')
    register_and_document_voice('TENOR_GENERATED', tenor_voice, voice_lookup, metadata)
    
    # Bass: transpose tenor down an octave
    bass_voice = transpose_events(tenor_voice, -12)
    register_and_document_voice('BASS_GENERATED', bass_voice, voice_lookup, metadata)
    
    print("\n" + "="*70)
    print("All programmatic voices registered and documented!")
    print("Check outputs/tenth.ly for the documentation block.")
    print("="*70)
    
    return {
        'metadata': metadata,
        'parts': {
            'Soprano': [soprano_voice],
            'Alto': [voice_lookup['ALTO_GENERATED']],
            'Tenor': [voice_lookup['TENOR_GENERATED']],
            'Bass': [voice_lookup['BASS_GENERATED']],
        }
    }

if __name__ == "__main__":
    print("\n🎵 Building Tenth Study...")
    
    data = build_score_data()
    output_file = "outputs/tenth"
    
    print(f"\nGenerating {output_file}.ly...")
    build_lilypond_file(data, output_file)
    
    print(f"\nCompiling with LilyPond...")
    result = subprocess.run(
        ["lilypond", "-o", output_file, f"{output_file}.ly"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ PDF: {output_file}.pdf")
        print(f"✅ MIDI: {output_file}.midi")
        print(f"\n📄 Open {output_file}.ly to see the documentation block!")
    else:
        print(f"❌ LilyPond compilation failed:")
        print(result.stderr)
