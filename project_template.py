"""
LilyPond ↔ music21 Hybrid (chords preserved & dotted durations)
===============================================================
- This version contains a robust parser that correctly handles chords and \relative mode.
"""

import re
from fractions import Fraction
from pathlib import Path
import subprocess

import music21
import abjad

# ==============================
# LilyPond → music21 parser
# ==============================
def parse_lilypond_snippet(snippet: str) -> music21.stream.Part:
    """
    Parses a LilyPond snippet, including \relative mode and chords.
    """
    snippet = snippet.strip()
    m = re.match(r"\\relative\s+([a-g][eis]*[,']*)\s*\{(.+)\}", snippet, re.DOTALL)
    if m:
        base = m.group(1).strip()
        body = m.group(2).strip()
        return _parse_relative_block(base, body)
    return _parse_absolute_block(snippet)

def _get_tokens(body: str):
    """THE FIX: Use a robust regex to find all musical tokens."""
    token_regex = r"<[^>]+>\d*\.?|[a-gr][eis]*[,']*\d*\.?|\|"
    return re.findall(token_regex, body)

def _parse_relative_block(base_pitch: str, body: str) -> music21.stream.Part:
    part = music21.stream.Part()
    ref_note = _parse_note_token(base_pitch)
    if not isinstance(ref_note, music21.note.Note):
        raise ValueError(f"Invalid base pitch for relative: {base_pitch}")
    
    last_pitch = ref_note.pitch
    tokens = _get_tokens(body) # Use the new, robust tokenizer

    for tok in tokens:
        if tok.startswith("<"):
            element = _parse_chord_token(tok, last_pitch)
            if element:
                # Update last_pitch to the top note of the chord for correct relative context
                last_pitch = element.pitches[-1]
                part.append(element)
        else:
            element = _resolve_relative(tok, last_pitch)
            if element:
                if isinstance(element, music21.note.Note):
                    last_pitch = element.pitch
                part.append(element)
    return part

def _parse_absolute_block(snippet: str) -> music21.stream.Part:
    part = music21.stream.Part()
    tokens = _get_tokens(snippet) # Use the new, robust tokenizer
    for tok in tokens:
        if tok.startswith("<"):
            element = _parse_chord_token(tok)
            if element:
                part.append(element)
        else:
            element = _parse_note_token(tok)
            if element:
                part.append(element)
    return part

def _resolve_relative(tok: str, last_pitch: music21.pitch.Pitch, ql: float = None):
    n = _parse_note_token(tok, ql)
    if isinstance(n, music21.note.Note):
        cand = n.pitch
        cand.octave = last_pitch.octave
        while cand.ps - last_pitch.ps > 6: cand.octave -= 1
        while last_pitch.ps - cand.ps > 6: cand.octave += 1
        n.pitch = cand
    return n

def _parse_duration(dur_token: str) -> float:
    if not dur_token: return 1.0
    base = int(re.sub(r"\D", "", dur_token))
    ql = 4 / base
    if "." in dur_token: ql *= 1.5
    return ql

def _parse_note_token(tok: str, ql: float = None):
    m = re.match(r"([a-gr][eis]*[,']*)(\d+\.?)?", tok)
    if not m: return None
    pitch_token, dur_token = m.groups()
    if ql is None: ql = _parse_duration(dur_token)
    if pitch_token.startswith("r"): return music21.note.Rest(quarterLength=ql)
    step = pitch_token[0].upper()
    acc = ""
    if "is" in pitch_token: acc = "#"
    elif "es" in pitch_token: acc = "-"
    octave_shift = pitch_token.count("'") - pitch_token.count(",")
    octave = 4 + octave_shift
    return music21.note.Note(f"{step}{acc}{octave}", quarterLength=ql)

def _parse_chord_token(tok: str, last_pitch: music21.pitch.Pitch = None):
    m = re.fullmatch(r"<([^>]*)>(\d+\.?)?", tok)
    if not m: return None
    chord_body, dur_token = m.groups()
    ql = _parse_duration(dur_token)
    chord_pitches = []
    
    # Use a temporary last_pitch for resolving notes inside the chord
    temp_last_pitch = last_pitch
    for t in chord_body.split():
        if last_pitch: # Relative mode
            n = _resolve_relative(t, temp_last_pitch, ql)
            if isinstance(n, music21.note.Note):
                temp_last_pitch = n.pitch
                chord_pitches.append(n.pitch)
        else: # Absolute mode
            n = _parse_note_token(t, ql)
            if isinstance(n, music21.note.Note):
                chord_pitches.append(n.pitch)
    if chord_pitches:
        return music21.chord.Chord(chord_pitches, quarterLength=ql)
    return None

# ==============================
# music21 → Abjad/LilyPond export
# ==============================
def ql_to_lily_duration_string(ql: float) -> str:
    dur = abjad.Duration(Fraction(ql / 4))
    return dur.lilypond_duration_string()

def m21_pitch_to_lily(p: music21.pitch.Pitch) -> str:
    return abjad.lilypond(abjad.NamedPitch(p.nameWithOctave))

def engrave_with_abjad(parts: dict, output_file: str):
    # Convert each provided music21 Part into an Abjad Voice (if it contains tokens)
    voices = {}
    for name, part in parts.items():
        if part is None:
            continue
        tokens = []
        for el in part.flatten().notesAndRests:
            if isinstance(el, music21.chord.Chord):
                dur_str = ql_to_lily_duration_string(el.quarterLength)
                chord_pitches = " ".join(m21_pitch_to_lily(p) for p in el.pitches)
                tokens.append(f"<{chord_pitches}>{dur_str}")
            elif isinstance(el, music21.note.Note):
                dur_str = ql_to_lily_duration_string(el.quarterLength)
                tokens.append(f"{m21_pitch_to_lily(el.pitch)}{dur_str}")
            elif isinstance(el, music21.note.Rest):
                dur_str = ql_to_lily_duration_string(el.quarterLength)
                tokens.append(f"r{dur_str}")

        token_text = " ".join(tokens).strip()
        print(f"Generated {name} tokens: {token_text}")
        if token_text:
            # voices[name] = abjad.Voice(token_text, name=name)
            voices[name] = token_text  # Store as string instead of abjad.Voice

    if not voices:
        raise RuntimeError("No musical parts provided to engrave_with_abjad")

    print(f"Successfully generated LilyPond tokens for parts: {list(voices.keys())}")
    print("Abjad engraving has been commented out - tokens generated successfully")
    
    # # Create Abjad Staffs for each voice and attach basic directives
    # staffs = []
    # for idx, (name, voice) in enumerate(voices.items()):
    #     staff = abjad.Staff([voice], name=name)
    #     staffs.append(staff)
    #     try:
    #         if abjad.select.leaf(staff, 0):
    #             leaf0 = abjad.select.leaf(staff, 0)
    #             # first staff: add treble clef, key/time/metronome
    #             if idx == 0:
    #                 abjad.attach(abjad.Clef("treble"), leaf0)
    #                 abjad.attach(abjad.TimeSignature((4, 4)), leaf0)
    #                 abjad.attach(abjad.KeySignature(abjad.NamedPitchClass("c"), abjad.Mode("major")), leaf0)
    #                 abjad.attach(abjad.MetronomeMark(abjad.Duration(1, 4), 100), leaf0)
    #             # if name suggests harmony, use bass clef
    #             elif "harmony" in name.lower() or "bass" in name.lower():
    #                 abjad.attach(abjad.Clef("bass"), leaf0)
    #                 abjad.attach(abjad.TimeSignature((4, 4)), leaf0)
    #     except Exception:
    #         # keep going even if attachments fail
    #         pass

    # # Build score: single staff => Score(staff), multiple => StaffGroup
    # if len(staffs) == 1:
    #     score = abjad.Score(staffs)
    # else:
    #     score = abjad.Score([abjad.StaffGroup(staffs, lilypond_type="PianoStaff")])

    # header = abjad.Block(name="header", items=[
    #     f'title = "{output_file} (generated)"',
    #     'composer = "Python + music21 + Abjad"',
    # ])
    # lyfile = abjad.LilyPondFile(items=[header, score])

    # ly_path = Path(output_file).with_suffix(".ly")
    # abjad.persist.as_ly(lyfile, ly_path)
    # print(f"LilyPond file written to: {ly_path}")
    # # print(f"Compiling {ly_path} with LilyPond...")
    # # subprocess.run(["lilypond", str(ly_path)])

# ==============================
# Demo / main
# ==============================
if __name__ == "__main__":
    melody_snippet = r"\relative c' { e4 f g a <c e g>2. r4 }"
    harmony_snippet = "c,2 g,2 <c e g>1"
    
    print("--- Parsing music from LilyPond strings ---")
    melody = parse_lilypond_snippet(melody_snippet)
    harmony = parse_lilypond_snippet(harmony_snippet)

    print("\n--- Transforming with music21 ---")
    melody_t = melody.transpose("P5")
    print(f"Original melody start: {melody.notes[0].pitch.nameWithOctave}")
    print(f"Transposed melody start: {melody_t.notes[0].pitch.nameWithOctave}")
    print("\nOriginal melody contents:")
    melody.show('text')
    print("\nTransposed melody contents:")
    melody_t.show('text')

    print("\n--- Engraving with Abjad ---")
    engrave_with_abjad({"Melody": melody_t, "Harmony": harmony}, "relative_score")
    print("\n✅ Done.")