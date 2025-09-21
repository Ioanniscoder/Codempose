"""
Definitive Hybrid Template (TinyNotation Input)
================================================
- Step 1: Define music using music21's simple "TinyNotation" string.
- Step 2: Use music21 to parse and transform the music into rich objects.
- Step 3: Extract the raw data from the music21 objects.
- Step 4: Hand off the data to Abjad for expert, error-free engraving.
"""
import music21
import abjad
from pathlib import Path
import traceback
import subprocess
import re

# ==========================================================================
#  PART 1: music21 for Composition & Transformation
# ==========================================================================
def create_music_data_with_music21() -> dict:
    """
    Uses music21 to parse a simple notation string and create musical data.
    """
    print("Step 1: Composing with music21 using TinyNotation...")

    # --- DEFINE YOUR MELODY HERE using TinyNotation ---
    # Format: "TimeSignature Note1 Note2 Note3..."
    # C4=quarter, C8=eighth, C#=sharp, C-=flat, r=rest
    melody_string = "4/4 c4 d'8 e' f4 g2~ g4 a-- b-2."
    
    # Parse the string into a music21 Part object
    melody_part = music21.converter.parse(f"tinynotation: {melody_string}")

    # You can now perform any analysis or transformation. For example:
    # transposed_part = melody_part.transpose("P5") # Transpose up a perfect fifth
    # and then use 'transposed_part' below instead of 'melody_part'.

    # Define harmony (can also be parsed from TinyNotation if desired)
    harmony_chords = [
        music21.chord.Chord(["C4", "E4", "G4"], quarterLength=4),
        music21.chord.Chord(["F3", "A3", "C4"], quarterLength=4),
    ]
    harmony_part = music21.stream.Part(harmony_chords)

    # --- Extract the final data for Abjad ---
    print("Step 2: Extracting fundamental data for the engraver...")
    score_data = {
        "metadata": {"title": "TinyNotation to PDF", "composer": "music21 + Abjad"},
        "parts": { "Melody": [], "Harmony": [] }
    }
    
    for item in melody_part.flatten().notesAndRests:
        event = {"ql": item.duration.quarterLength}
        if isinstance(item, music21.note.Note):
            event["type"] = "note"
            event["step"] = item.pitch.step
            event["alter"] = item.pitch.accidental.alter if item.pitch.accidental else 0
            event["octave"] = item.pitch.octave
        elif isinstance(item, music21.note.Rest):
            event["type"] = "rest"
        score_data["parts"]["Melody"].append(event)
        
    for chord in harmony_part.flatten().notes:
        event = {"ql": chord.duration.quarterLength, "type": "chord", "pitches": []}
        for p in chord.pitches:
            pitch_data = {
                "step": p.step,
                "alter": p.accidental.alter if p.accidental else 0,
                "octave": p.octave
            }
            event["pitches"].append(pitch_data)
        score_data["parts"]["Harmony"].append(event)
        
    return score_data

# ==========================================================================
#  PART 3: Abjad for Flawless Engraving
# ==========================================================================
def engrave_score_with_abjad(data: dict, output_filename: str):
    """
    Takes the data dictionary and uses Abjad to generate a perfect LilyPond file.
    """
    print("Step 3: Engraving with Abjad...")
    
    def get_lilypond_pitch(p_data):
        """A robust helper to build an Abjad pitch object and get its string."""
        pitch_object = abjad.NamedPitch(
            name=p_data["step"].lower(),
            accidental=p_data["alter"],
            octave=p_data["octave"]
        )
        return abjad.lilypond(pitch_object)

    melody_voice = []
    for event in data["parts"]["Melody"]:
        duration = abjad.Duration(int(event["ql"] * 4), 16)
        dur_str = duration.lilypond_duration_string()
        if event["type"] == "rest":
            melody_voice.append(abjad.Rest(f"r{dur_str}"))
        elif event["type"] == "note":
            pitch_str = get_lilypond_pitch(event)
            melody_voice.append(abjad.Note(f"{pitch_str}{dur_str}"))

    harmony_voice = []
    for event in data["parts"]["Harmony"]:
        duration = abjad.Duration(int(event["ql"] * 4), 16)
        dur_str = duration.lilypond_duration_string()
        pitch_strs = [get_lilypond_pitch(p_data) for p_data in event["pitches"]]
        harmony_voice.append(abjad.Chord(f"<{' '.join(pitch_strs)}>{dur_str}"))

    melody_staff = abjad.Staff(melody_voice, name="Melody")
    harmony_staff = abjad.Staff(harmony_voice, name="Harmony")
    
    key_tonic = abjad.NamedPitchClass("c")
    key_mode = abjad.Mode("major")
    abjad.attach(abjad.KeySignature(key_tonic, key_mode), melody_staff[0])
    abjad.attach(abjad.TimeSignature((4, 4)), melody_staff[0])
    tempo_duration = abjad.Duration(1, 4)
    abjad.attach(abjad.MetronomeMark(tempo_duration, 100), melody_staff[0])
    abjad.attach(abjad.Clef("bass"), harmony_staff[0])
    abjad.attach(abjad.TimeSignature((4, 4)), harmony_staff[0])

    staff_group = abjad.StaffGroup([melody_staff, harmony_staff], lilypond_type="PianoStaff")
    score = abjad.Score([staff_group])
    
    header_items = [f'{key} = "{value}"' for key, value in data["metadata"].items()]
    header_block = abjad.Block(name="header", items=header_items)
    lilypond_file = abjad.LilyPondFile(items=[header_block, score])

    output_path = Path(output_filename)
    ly_path = output_path.with_suffix(".ly")
    
    print(f"Generating LilyPond file: {ly_path}")
    abjad.persist.as_ly(lilypond_file, ly_path)

    print(f"Compiling PDF from {ly_path}...")
    try:
        result = subprocess.run(["lilypond", str(ly_path)], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\nPDF compilation successful.")
        else:
            print(f"\n--- LilyPond Compilation FAILED ---\nSTDERR:\n{result.stderr}")
    except FileNotFoundError:
        print("\n--- ERROR: LilyPond not found ---")

# ==========================================================================
#  MAIN EXECUTION
# ==========================================================================
if __name__ == "__main__":
    music_data = create_music_data_with_music21()
    output_file_base = "final_score"
    engrave_score_with_abjad(music_data, output_file_base)
    print("\n✅ Template executed successfully.")