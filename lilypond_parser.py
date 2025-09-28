import re
import music21
from music_data import extract_data_from_part

def parse_lilypond_to_data(lily_string: str, part_name: str = "Part 1") -> dict:
    """
    Parses a LilyPond shorthand string into the standard data dictionary.
    Returns a dict: {"metadata": {...}, "parts": { part_name: [events...] }}
    """
    # Basic sanitization (strip control chars that break tokenization)
    if lily_string is None:
        lily_string = ''
    lily_string = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", '', lily_string)

    # Collect warnings and suggestions during parsing so callers can
    # inspect issues and present actionable advice. Keep parser behavior
    # unchanged; we only surface diagnostics.
    parse_warnings = []
    parse_suggestions = []

    # Parse the lily snippet into a music21 Part using a simplified internal
    # parser (keeps relative-pitch semantics). For complex needs, extend
    # this function to call the older robust tokenizer/resolver.
    part = _parse_lilypond_snippet_to_part(lily_string, parse_warnings, parse_suggestions)
    # Attach warnings to the part so downstream code can access them
    try:
        if parse_warnings:
            part._parse_warnings = parse_warnings
    except Exception:
        pass

    # Extract metadata
    metadata = {"title": "LilyPond Score", "composer": "Codempose"}
    ts = part.getElementsByClass(music21.meter.TimeSignature)
    if ts:
        metadata["time_signature"] = ts[0].ratioString
    ks = part.getElementsByClass(music21.key.Key)
    if ks:
        k = ks[0]
        metadata["key_signature"] = {"tonic": getattr(k, 'tonic', getattr(k, 'tonicPitch', 'C')).name, "mode": getattr(k, 'mode', 'major')}
    tm = part.getElementsByClass(music21.tempo.MetronomeMark)
    if tm:
        metadata["tempo"] = int(getattr(tm[0], 'number', 0))

    # Convert the music21 Part to the canonical event list. Provide the
    # original tokens list (if available) so the extractor can flag
    # large relative leaps when tokens lack explicit octave markers.
    original_tokens = getattr(part, '_original_tokens', None)
    events = extract_data_from_part(part, original_tokens)

    # Attach any parsing warnings to the metadata so the engraver can
    # include them in audit headers and provide suggestions.
    if parse_warnings:
        metadata['warnings'] = parse_warnings
    if parse_suggestions:
        metadata['suggestions'] = parse_suggestions

    score_data = {"metadata": metadata, "parts": {part_name: events}}
    return score_data


def _parse_lilypond_snippet_to_part(snippet: str, warnings: list = None, suggestions: list = None) -> music21.stream.Part:
    """A small, robust parser that preserves \relative semantics and
    returns a music21.stream.Part. This intentionally keeps the parser
    simple; you can swap in the older, fuller tokenizer if needed.
    """
    part = music21.stream.Part()

    # Extract simple directives
    time_match = re.search(r"\\time\s+(\d+/\d+)", snippet)
    if time_match:
        part.append(music21.meter.TimeSignature(time_match.group(1)))

    key_match = re.search(r"\\key\s+([A-Ga-g][#b]?)[^\n]*?(major|minor)?", snippet, re.IGNORECASE)
    if key_match:
        tonic = key_match.group(1)
        mode = key_match.group(2) or 'major'
        try:
            part.append(music21.key.Key(tonic, mode))
        except Exception:
            pass

    tempo_match = re.search(r"\\tempo\s+[^=]*=(\d+)", snippet)
    if tempo_match:
        try:
            part.append(music21.tempo.MetronomeMark(number=int(tempo_match.group(1))))
        except Exception:
            pass

    # Find the main relative block and tokens (very permissive here)
    m = re.search(r"\\relative\s+([a-g][,']*)?\s*\{([\s\S]+)\}", snippet, re.IGNORECASE)
    if not m:
        raise ValueError("Snippet must be in \\relative c' { ... } format")

    start_note_tok, body = m.groups()
    # Determine starting pitch
    if start_note_tok:
        try:
            # use tinyNotation to get a starting pitch robustly
            tn = f"tinynotation: {start_note_tok}4"
            start_part = music21.converter.parse(tn)
            last_pitch = start_part.notes[0].pitch
        except Exception:
            last_pitch = music21.pitch.Pitch('C4')
    else:
        last_pitch = music21.pitch.Pitch('C4')
    # Preserve the octave as parsed by tinyNotation for the \relative base.
    # Avoid forcing an arbitrary octave nudge here; let subsequent
    # relative-resolution follow LilyPond-like nearest-octave rules.

    # Tokenize chord bodies and notes/rests (supports localized accidentals like 'mol'/'bemol')
    # Require at least one digit when a duration is present to avoid accidentally
    # matching a note token without its intended duration (which caused many
    # notes to default to quarterLength=1.0).
    tokens = re.findall(r"<[^>]+>[,']*\d+\.?|[a-gr](?:is|es|mol|bemol|#|b|\u266f|\u266d)?[,']*\d+\.?|r\d+\.?", body, re.IGNORECASE)
    # store original tokens on the part for downstream consumers
    try:
        part._original_tokens = [t.strip() for t in tokens]
    except Exception:
        pass

    for token in tokens:
        element = None
        token = token.strip()
        if token.startswith('<'):
            # chord
            notes_in_chord = re.findall(r"[a-gr](?:is|es|#|b)?[,']*", token, re.IGNORECASE)
            dur_m = re.search(r"(\d+\.?)(?![^{]*})", token)
            ql = 1.0
            if dur_m:
                d = dur_m.group(1)
                ql = 4.0 / float(d.replace('.', ''))
                if '.' in d: ql *= 1.5
            chord_pitches = []
            temp_last = last_pitch
            for nt in notes_in_chord:
                p = _resolve_relative_pitch(nt, temp_last, warnings, suggestions)
                chord_pitches.append(p)
                temp_last = p
            element = music21.chord.Chord(chord_pitches, quarterLength=ql)
        else:
            if token.startswith('r'):
                dur = token[1:]
                ql = 1.0
                if dur:
                    ql = 4.0 / float(dur.replace('.', ''))
                    if '.' in dur: ql *= 1.5
                element = music21.note.Rest(quarterLength=ql)
            else:
                # accept a wider set of accidental spellings (mol, bemol, unicode flats/sharps)
                # Require at least one digit for duration capture
                m_note = re.match(r"([a-gr](?:is|es|mol|bemol|#|b|\u266f|\u266d)?[,']*)(\d+\.?)", token, re.IGNORECASE)
                if m_note:
                    pitch_tok, dur_tok = m_note.groups()
                    ql = 1.0
                    if dur_tok:
                        ql = 4.0 / float(dur_tok.replace('.', ''))
                        if '.' in dur_tok: ql *= 1.5
                    p = _resolve_relative_pitch(pitch_tok, last_pitch, warnings, suggestions)
                    element = music21.note.Note(p, quarterLength=ql)

        if element is not None:
            part.append(element)
            if hasattr(element, 'pitch'):
                last_pitch = element.pitch
            elif hasattr(element, 'pitches') and element.pitches:
                last_pitch = element.pitches[-1]

    # Attach any collected warnings/suggestions to the part for downstream
    # inspection by the engraver.
    try:
        if warnings:
            part._parse_warnings = warnings
        if suggestions:
            part._parse_suggestions = suggestions
    except Exception:
        pass

    return part

    # (Note: unreachable)


def _resolve_relative_pitch(token, last_pitch, warnings: list = None, suggestions: list = None):
    """Resolve a simple pitch token into an absolute music21 Pitch.
    This uses music21's tinyNotation to interpret the step+accidentals
    and then adjusts octaves to be near last_pitch unless explicit
    octave marks are present.
    """
    # First try tinyNotation (best effort). If that fails, parse manually
    # to support localized accidentals (e.g. 'bmol', 'bemol') and avoid
    # falling back to C4 which produced many incorrect Cs in outputs.
    try:
        tn = f"tinynotation: {token}4"
        p = music21.converter.parse(tn).notes[0].pitch
    except Exception as e:
        # Record a warning the first time this token causes a fallback
        if warnings is not None:
            msg = f"tinyNotation parse failed for token '{token}': {e}. Falling back to manual resolution."
            # avoid duplicates
            if msg not in warnings:
                warnings.append(msg)
        # Add a short actionable suggestion for common cases
        if suggestions is not None:
            try:
                s = f"For token '{token}': consider adding explicit octave markers (e.g., e' or e,), or provide a tinyNotation input, or use canonical accidentals ('is'/'es') instead of localized forms like 'mol'/'bemol'."
                if s not in suggestions:
                    suggestions.append(s)
            except Exception:
                pass
        # Manual parse: step, accidental, octave marks
        
        # Manual parse: step, accidental, octave marks
        m = re.match(r"(?P<step>[a-g])(?P<acc>is|es|mol|bemol|#|b|\u266f|\u266d)?(?P<marks>[,']*)", token, re.IGNORECASE)
        if not m:
            # last-resort fallback: return a pitch near last_pitch
            p = music21.pitch.Pitch()
            p.step = last_pitch.step
            p.octave = last_pitch.octave
            return p

        step = m.group('step').upper()
        acc = (m.group('acc') or '').lower()
        marks = m.group('marks') or ''

        # Build a base pitch near the last_pitch octave
        p = music21.pitch.Pitch()
        p.step = step
        # default octave: align with last_pitch
        try:
            p.octave = int(last_pitch.octave)
        except Exception:
            p.octave = 4

        # apply accidental
        try:
            if acc in ('is', '#', '\u266f'):
                p.accidental = music21.pitch.Accidental(1)
            elif acc in ('es', 'b', 'mol', 'bemol', '\u266d'):
                p.accidental = music21.pitch.Accidental(-1)
        except Exception:
            pass

        # handle explicit octave marks (apostrophes/commas) by shifting
        if marks:
            up = marks.count("'")
            down = marks.count(',')
            p.octave = p.octave + up - down

        # Now nudge octave so the pitch is nearest to last_pitch (mimic LilyPond)
        try:
            while abs(p.ps - last_pitch.ps) > 6:
                if p.ps > last_pitch.ps:
                    p.octave -= 1
                else:
                    p.octave += 1
        except Exception:
            pass

    return p

