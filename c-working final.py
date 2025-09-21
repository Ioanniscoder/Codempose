"""
Expanded LilyPond-to-music21 Hybrid Template (relative mode + chords fixed)
==========================================================================

- Step 1: Parse LilyPond snippets (absolute or relative) into music21 objects.
- Step 2: Use music21 for transformations (transpose, invert, etc.).
- Step 3: Export with Abjad to LilyPond/PDF.
"""

import re
import music21
import abjad
from pathlib import Path
import subprocess


# ================================================================
# LilyPond Parser with Relative Mode
# ================================================================
def parse_lilypond_snippet(snippet: str) -> music21.stream.Part:
    """
    Convert a LilyPond snippet into a music21 Part.
    Supports:
      - Absolute notes: c'4 d'4
      - Relative mode: \relative c' { e4 f g a }
      - Chords: <c e g>2
      - Rests: r4
      - Accidentals: cis, des
      - Octaves: ', ,
    """
    # Detect relative mode
    m = re.match(r"\\relative\s+([a-g][eis]*[,']*)\s*\{(.+)\}", snippet, re.DOTALL)
    if m:
        base_pitch = m.group(1).strip()
        body = m.group(2).strip()
        return _parse_relative_block(base_pitch, body)
    else:
        return _parse_absolute_block(snippet)


def _parse_relative_block(base_pitch: str, body: str) -> music21.stream.Part:
    """
    Resolve LilyPond relative notation to absolute pitches.
    """
    part = music21.stream.Part()

    ref_note = _parse_note_token(base_pitch)
    if not isinstance(ref_note, music21.note.Note):
        raise ValueError(f"Invalid base pitch for relative: {base_pitch}")

    last_pitch = ref_note.pitch
    tokens = body.split()

    for tok in tokens:
        if tok == "|":
            continue

        # --- chords ---
        if tok.startswith("<") and ">" in tok:
            m = re.fullmatch(r"<([^>]*)>(\d+\.?)?", tok)
            if not m:
                raise ValueError(f"Invalid chord token: {tok}")
            chord_body, dur_token = m.groups()
            notes = chord_body.split()
            ql = _parse_duration(dur_token)

            chord_notes = []
            for note_token in notes:
                n = _resolve_relative(note_token, last_pitch, ql)
                if n is not None and isinstance(n, music21.note.Note):
                    last_pitch = n.pitch
                    chord_notes.append(n.pitch)
            if chord_notes:
                chord_obj = music21.chord.Chord(chord_notes, quarterLength=ql)
                part.append(chord_obj)
            continue

        # --- single notes & rests ---
        n = _resolve_relative(tok, last_pitch)
        if n is not None:
            if isinstance(n, music21.note.Note):
                last_pitch = n.pitch
            part.append(n)

    return part


def _resolve_relative(tok: str, last_pitch: music21.pitch.Pitch, ql: float = None):
    """
    Compute absolute pitch from LilyPond relative mode.
    """
    n = _parse_note_token(tok, ql)
    if isinstance(n, music21.note.Note):
        candidate = n.pitch
        candidate.octave = last_pitch.octave  # start from same octave

        # Adjust octave if interval is too big
        while candidate.ps - last_pitch.ps > 6:
            candidate.octave -= 1
        while last_pitch.ps - candidate.ps > 6:
            candidate.octave += 1

        n.pitch = candidate
    return n


def _parse_absolute_block(snippet: str) -> music21.stream.Part:
    """
    Parse absolute LilyPond notation (no relative mode).
    """
    part = music21.stream.Part()
    tokens = snippet.split()
    for tok in tokens:
        if tok == "|":
            continue
        if tok.startswith("<") and ">" in tok:
            m = re.fullmatch(r"<([^>]*)>(\d+\.?)?", tok)
            if not m:
                raise ValueError(f"Invalid chord token: {tok}")
            chord_body, dur_token = m.groups()
            notes = chord_body.split()
            ql = _parse_duration(dur_token)
            chord_notes = []
            for note_token in notes:
                n = _parse_note_token(note_token, ql)
                if n is not None and isinstance(n, music21.note.Note):
                    chord_notes.append(n.pitch)
            if chord_notes:
                part.append(music21.chord.Chord(chord_notes, quarterLength=ql))
        else:
            n = _parse_note_token(tok)
            if n:
                part.append(n)
    return part


def _parse_duration(dur_token: str) -> float:
    if not dur_token:
        return 1.0
    base = int(re.sub(r"\D", "", dur_token))
    ql = 4 / base
    if "." in dur_token:
        ql *= 1.5
    return ql


def _parse_note_token(tok: str, ql: float = None):
    m = re.match(r"([a-gr][eis]*[,']*)(\d+\.?)?", tok)
    if not m:
        return None
    pitch_token, dur_token = m.groups()
    if not ql:
        ql = _parse_duration(dur_token)
    if pitch_token.startswith("r"):
        return music21.note.Rest(quarterLength=ql)

    # step + accidental
    step = pitch_token[0].upper()
    accidental = ""
    if "is" in pitch_token:
        accidental = "#"
    elif "es" in pitch_token:
        accidental = "-"

    # octaves (middle C = c')
    octave_shift = pitch_token.count("'") - pitch_token.count(",")
    octave = 4 + octave_shift

    return music21.note.Note(f"{step}{accidental}{octave}", quarterLength=ql)


# ================================================================
# Abjad Export
# ================================================================
def engrave_with_abjad(parts: dict, output_file: str):
    voices = {}
    for name, part in parts.items():
        notes = []
        for n in part.notesAndRests:
            if isinstance(n, music21.note.Note):
                dur = int(4 / n.quarterLength)
                notes.append(f"{n.pitch.name.lower()}{dur}")
            elif isinstance(n, music21.note.Rest):
                dur = int(4 / n.quarterLength)
                notes.append(f"r{dur}")
            elif isinstance(n, music21.chord.Chord):
                dur = int(4 / n.quarterLength)
                chord_pitches = " ".join(p.name.lower() for p in n.pitches)
                notes.append(f"<{chord_pitches}>{dur}")
        voices[name] = abjad.Voice(" ".join(notes), name=name)

    melody_staff = abjad.Staff([voices["Melody"]], name="Melody")
    harmony_staff = abjad.Staff([voices["Harmony"]], name="Harmony")

    abjad.attach(abjad.Clef("treble"), abjad.select.leaf(melody_staff, 0))
    abjad.attach(abjad.Clef("bass"), abjad.select.leaf(harmony_staff, 0))
    abjad.attach(abjad.TimeSignature((4, 4)), abjad.select.leaf(melody_staff, 0))
    abjad.attach(abjad.TimeSignature((4, 4)), abjad.select.leaf(harmony_staff, 0))

    staff_group = abjad.StaffGroup([melody_staff, harmony_staff], lilypond_type="PianoStaff")
    score = abjad.Score([staff_group])

    header_block = abjad.Block(name="header", items=[
        'title = "Relative LilyPond Parser"',
        'composer = "Python + music21 + Abjad"'
    ])
    lilypond_file = abjad.LilyPondFile(items=[header_block, score])

    ly_path = Path(output_file).with_suffix(".ly")
    abjad.persist.as_ly(lilypond_file, ly_path)

    print(f"Compiling {ly_path} with LilyPond...")
    subprocess.run(["lilypond", str(ly_path)])


# ================================================================
# MAIN EXECUTION
# ================================================================
if __name__ == "__main__":
    # Example input with relative and absolute
    melody_snippet = r"\relative c' { e4 f g a <c e g>1 }"
    harmony_snippet = "c,2 g,2 <c e g>1 r4"

    melody = parse_lilypond_snippet(melody_snippet)
    harmony = parse_lilypond_snippet(harmony_snippet)

    print("Melody:", [str(n) for n in melody.notesAndRests])
    print("Harmony:", [str(n) for n in harmony.notesAndRests])

    # Transform: transpose melody up a fifth
    melody_t = melody.transpose("P5")

    # Export
    engrave_with_abjad({"Melody": melody_t, "Harmony": harmony}, "relative_score")

    print("\n✅ Done.")
