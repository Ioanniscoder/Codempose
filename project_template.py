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
    If a \time X/Y token is present, attach a music21 TimeSignature to the
    returned Part so the engraver can pick it up.
    """
    snippet = snippet.strip()
    m = re.match(r"\\relative\s+([a-g][eis]*[,']*)\s*\{(.+)\}", snippet, re.DOTALL)
    if m:
        base = m.group(1).strip()
        body = m.group(2).strip()
        part = _parse_relative_block(base, body)
        # detect and attach \time if present
        tm = re.search(r"\\time\s+(\d+)\/(\d+)", snippet)
        if tm:
            try:
                num, den = int(tm.group(1)), int(tm.group(2))
                ts = music21.meter.TimeSignature(f"{num}/{den}")
                part.insert(0, ts)
            except Exception:
                pass
        return part

    # absolute-mode
    part = _parse_absolute_block(snippet)
    tm = re.search(r"\\time\s+(\d+)\/(\d+)", snippet)
    if tm:
        try:
            num, den = int(tm.group(1)), int(tm.group(2))
            ts = music21.meter.TimeSignature(f"{num}/{den}")
            part.insert(0, ts)
        except Exception:
            pass
    return part

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
    # Try the exact representation first (fraction of whole note)
    frac = Fraction(ql).limit_denominator(1024)
    try:
        dur = abjad.Duration(Fraction(frac, 4))
        return dur.lilypond_duration_string
    except Exception:
        # Fall back: approximate with power-of-two base durations and dots
        candidates = []
        # LilyPond duration numbers (1,2,4,8,16...) correspond to whole-note denominators
        bases = [1, 2, 4, 8, 16, 32, 64]
        for base in bases:
            for dots in range(0, 4):
                factor = 2 - 1 / (2 ** dots) if dots > 0 else 1
                ql_candidate = 4 / base * factor
                diff = abs(ql_candidate - float(ql))
                candidates.append((diff, base, dots, ql_candidate))
        candidates.sort(key=lambda x: x[0])
        best = candidates[0]
        diff, base, dots, ql_candidate = best
        # Build lilypond duration string (e.g. 4., 8..)
        dur_str = str(base) + ('.' * dots)
        if diff > 1e-2:
            print(f"[warning] approximate duration: requested ql={ql} approximated as {ql_candidate} (LilyPond: {dur_str}); diff={diff}")
        return dur_str

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
            # Try to create an exact LilyPond duration via Abjad; if Abjad
            # cannot assign the duration (e.g. 1/3 whole), fall back to
            # emitting a LilyPond tuplet that represents the intended
            # duration exactly.
            try:
                frac = Fraction(el.quarterLength).limit_denominator(1024)
            except Exception:
                frac = Fraction(str(el.quarterLength)).limit_denominator(1024)

            try:
                # abjad expects a fraction of a whole note
                dur = abjad.Duration(Fraction(frac, 4))
                dur_str = dur.lilypond_duration_string
                if isinstance(el, music21.chord.Chord):
                    chord_pitches = " ".join(m21_pitch_to_lily(p) for p in el.pitches)
                    tokens.append(f"<{chord_pitches}>{dur_str}")
                elif isinstance(el, music21.note.Note):
                    tokens.append(f"{m21_pitch_to_lily(el.pitch)}{dur_str}")
                elif isinstance(el, music21.note.Rest):
                    tokens.append(f"r{dur_str}")
            except Exception:
                # Couldn't assign a simple duration; try to encode as a tuplet
                tuplet_emitted = False
                for base in [1, 2, 4, 8, 16, 32]:
                    # ratio r = (desired ql) / (4/base)
                    r = Fraction(frac * base, 4).limit_denominator(32)
                    # Limit numerator/denominator to reasonable values
                    if r.numerator <= 32 and r.denominator <= 32:
                        inner_dur = str(base)
                        if isinstance(el, music21.chord.Chord):
                            chord_pitches = " ".join(m21_pitch_to_lily(p) for p in el.pitches)
                            inner = f"<{chord_pitches}>{inner_dur}"
                        elif isinstance(el, music21.note.Note):
                            inner = f"{m21_pitch_to_lily(el.pitch)}{inner_dur}"
                        else:
                            inner = f"r{inner_dur}"
                        tokens.append(f"\\tuplet {r.numerator}/{r.denominator} {{ {inner} }}")
                        tuplet_emitted = True
                        break
                if not tuplet_emitted:
                    # Fallback to approximate lily duration string (existing behavior)
                    dur_str = ql_to_lily_duration_string(el.quarterLength)
                    if isinstance(el, music21.chord.Chord):
                        chord_pitches = " ".join(m21_pitch_to_lily(p) for p in el.pitches)
                        tokens.append(f"<{chord_pitches}>{dur_str}")
                    elif isinstance(el, music21.note.Note):
                        tokens.append(f"{m21_pitch_to_lily(el.pitch)}{dur_str}")
                    elif isinstance(el, music21.note.Rest):
                        tokens.append(f"r{dur_str}")

        token_text = " ".join(tokens).strip()
        if token_text:
            voices[name] = abjad.Voice(token_text, name=name)

    if not voices:
        raise RuntimeError("No musical parts provided to engrave_with_abjad")

    # Create Abjad Staffs for each voice and attach basic directives
    staffs = []
    for idx, (name, voice) in enumerate(voices.items()):
        staff = abjad.Staff([voice], name=name)
        staffs.append(staff)
        try:
            if abjad.select.leaf(staff, 0):
                leaf0 = abjad.select.leaf(staff, 0)
                # first staff: add treble clef, key/time/metronome
                if idx == 0:
                    abjad.attach(abjad.Clef("treble"), leaf0)
                    # prefer a TimeSignature found in the original music21 Part
                    ts_attached = False
                    try:
                        orig_part = parts.get(name)
                        if orig_part is not None:
                            ts_list = list(orig_part.recurse().getElementsByClass(music21.meter.TimeSignature))
                            if ts_list:
                                ts = ts_list[0]
                                abjad.attach(abjad.TimeSignature((ts.numerator, ts.denominator)), leaf0)
                                ts_attached = True
                    except Exception:
                        ts_attached = False
                    if not ts_attached:
                        abjad.attach(abjad.TimeSignature((4, 4)), leaf0)
                    abjad.attach(abjad.KeySignature(abjad.NamedPitchClass("c"), abjad.Mode("major")), leaf0)
                    abjad.attach(abjad.MetronomeMark(abjad.Duration(1, 4), 100), leaf0)
                # if name suggests harmony, use bass clef
                elif "harmony" in name.lower() or "bass" in name.lower():
                    abjad.attach(abjad.Clef("bass"), leaf0)
                    # try to attach the same time signature if present
                    try:
                        orig_part = parts.get(name)
                        if orig_part is not None:
                            ts_list = list(orig_part.recurse().getElementsByClass(music21.meter.TimeSignature))
                            if ts_list:
                                ts = ts_list[0]
                                abjad.attach(abjad.TimeSignature((ts.numerator, ts.denominator)), leaf0)
                            else:
                                abjad.attach(abjad.TimeSignature((4, 4)), leaf0)
                    except Exception:
                        abjad.attach(abjad.TimeSignature((4, 4)), leaf0)
        except Exception:
            # keep going even if attachments fail
            pass

    # Build score: single staff => Score(staff), multiple => StaffGroup
    if len(staffs) == 1:
        score = abjad.Score(staffs)
    else:
        score = abjad.Score([abjad.StaffGroup(staffs, lilypond_type="PianoStaff")])

    header = abjad.Block(name="header", items=[
        f'title = "{output_file} (generated)"',
        'composer = "Python + music21 + Abjad"',
    ])
    lyfile = abjad.LilyPondFile(items=[header, score])

    # Render the LilyPond text and ensure it's wrapped in a \score block
    # that contains a \layout and \midi block so LilyPond will produce MIDI.
    ly_text = abjad.lilypond(lyfile)
    # Find the score start (\new Score ...) and wrap it in a full \score { ... }
    idx = ly_text.find("\\new Score")
    if idx != -1:
        wrapped = ly_text[:idx] + "\\score {\n" + ly_text[idx:]
        wrapped += "\n\\layout { }\n\\midi { }\n}\n"
    else:
        # fallback: append layout/midi blocks
        wrapped = ly_text + "\n\\layout { }\n\\midi { }\n"

    # Determine output directory. If output_file includes a path, use that
    # parent, otherwise default to outputs/ so generated artifacts are grouped.
    out_path = Path(output_file)
    if out_path.parent == Path('.') or str(out_path.parent) == '':
        out_dir = Path('outputs')
    else:
        out_dir = out_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    ly_filename = out_path.with_suffix('.ly').name
    ly_path = out_dir / ly_filename
    ly_path.write_text(wrapped)
    print(f"Compiling {ly_path} with LilyPond...")
    # Run lilypond in the output directory so auxiliary files land there
    subprocess.run(["lilypond", str(ly_path.name)], cwd=str(out_dir))

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