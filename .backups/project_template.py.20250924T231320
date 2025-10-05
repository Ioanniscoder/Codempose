"""
LilyPond ↔ music21 Hybrid (chords preserved & dotted durations)
===============================================================
- This version contains a robust parser that correctly handles chords and \relative mode.
"""
import re
import music21
import abjad
from pathlib import Path
import subprocess
from fractions import Fraction
from typing import List

# Configuration toggles (adjustable by study files)
RELATIVE_OCTAVE_POLICY = 'nearest'  # 'nearest' or 'fixed'
EXPLICIT_OCTAVE_AFFECTS_CONTEXT = True


def set_relative_octave_policy(policy: str):
    """Set relative octave resolution policy used by the parser.

    Accepts 'nearest' (default) or 'fixed'.
    """
    global RELATIVE_OCTAVE_POLICY
    if policy not in ('nearest', 'fixed'):
        raise ValueError("policy must be 'nearest' or 'fixed'")
    RELATIVE_OCTAVE_POLICY = policy


def set_explicit_octave_affects_context(value: bool):
    """Set whether explicit octave markers (,' ) affect subsequent relative context."""
    global EXPLICIT_OCTAVE_AFFECTS_CONTEXT
    EXPLICIT_OCTAVE_AFFECTS_CONTEXT = bool(value)


def _get_tokens(body: str) -> List[str]:
    """Tokenize a LilyPond body into note/chord/rest/| tokens.

    This is a conservative tokenizer used by the relative/absolute
    parsers elsewhere in the module.
    """
    token_regex = r"<[^>]+>\d*\.?|[a-gr][eis]*[,']*\d*\.?|\\[a-zA-Z]+|\|"
    return re.findall(token_regex, body)


def parse_lilypond_snippet(snippet: str) -> music21.stream.Part:
    """Parse a LilyPond snippet string into a music21.stream.Part.

    Supports absolute tokens and a simple form of \relative blocks
    (single-line or multi-line content inside braces).
    """
    # Detect relative mode: \relative <base> { <body> }
    m = re.match(r"\\relative\s+([a-g][eis]*[,']*)\s*\{(.+)\}", snippet, re.DOTALL)
    if m:
        base_pitch = m.group(1).strip()
        body = m.group(2).strip()
        part = _parse_relative_block(base_pitch, body)
        try:
            part._original_snippet = snippet
        except Exception:
            pass
        return part
    else:
        return _parse_absolute_block(snippet)


def _parse_relative_block(base_pitch: str, body: str) -> music21.stream.Part:
    part = music21.stream.Part()
    ref_note = _parse_note_token(base_pitch)
    if not isinstance(ref_note, music21.note.Note):
        raise ValueError(f"Invalid base pitch for relative: {base_pitch}")

    last_pitch = ref_note.pitch
    tokens = _get_tokens(body) # Use the new, robust tokenizer
    # Normalize tokens: if a note/rest/chord token lacks an explicit
    # duration, append a default quarter-note duration '4'. This makes
    # snippet format deterministic and avoids surprises from implicit
    # durations in relative mode.
    norm_tokens = []
    for tok in tokens:
        if tok == '|' or tok.startswith('\\'):
            norm_tokens.append(tok)
            continue
        if tok.startswith('<'):
            # chord token; add duration if missing
            if not re.search(r">\d", tok):
                tok = tok.rstrip() + '4'
            norm_tokens.append(tok)
            continue
        # rest or single note without explicit digits
        m_no_dur = re.fullmatch(r"([a-gr][eis]*[,']*)", tok)
        m_rest = re.fullmatch(r"(r)", tok)
        if m_no_dur:
            norm_tokens.append(tok + '4')
            continue
        if m_rest:
            norm_tokens.append(tok + '4')
            continue
        norm_tokens.append(tok)
    tokens = norm_tokens

    for tok in tokens:
        if tok.startswith("<"):
            element = _parse_chord_token(tok, last_pitch)
            if element:
                # Update last_pitch to the top note of the chord for correct relative context
                # (chords are treated as explicit context changes)
                last_pitch = element.pitches[-1]
                part.append(element)
        else:
            element = _resolve_relative(tok, last_pitch)
            if element:
                # If the token contains explicit octave marks and the project
                # policy says explicit marks should not affect subsequent
                # relative context, do not update last_pitch here.
                has_mark = bool(re.search(r"[,']", tok))
                if isinstance(element, music21.note.Note):
                    if not (has_mark and not EXPLICIT_OCTAVE_AFFECTS_CONTEXT):
                        last_pitch = element.pitch
                part.append(element)
    return part

def _parse_absolute_block(snippet: str) -> music21.stream.Part:
    part = music21.stream.Part()
    tokens = _get_tokens(snippet) # Use the new, robust tokenizer
    # Normalize tokens to ensure a clear format: attach default '4' where
    # a duration is missing on a note/rest/chord.
    norm_tokens = []
    for tok in tokens:
        if tok == '|' or tok.startswith('\\'):
            norm_tokens.append(tok)
            continue
        if tok.startswith('<'):
            if not re.search(r">\d", tok):
                tok = tok.rstrip() + '4'
            norm_tokens.append(tok)
            continue
        m_no_dur = re.fullmatch(r"([a-gr][eis]*[,']*)", tok)
        m_rest = re.fullmatch(r"(r)", tok)
        if m_no_dur:
            norm_tokens.append(tok + '4')
            continue
        if m_rest:
            norm_tokens.append(tok + '4')
            continue
        norm_tokens.append(tok)
    tokens = norm_tokens
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
        # If the token contains explicit octave markers (apostrophes or commas)
        # then _parse_note_token already applied them. Respect explicit marks.
        has_mark = bool(re.search(r"[,']", tok))
        if has_mark:
            # honor explicit octave markers exactly
            n.pitch = cand
            return n

        if RELATIVE_OCTAVE_POLICY == 'fixed':
            # keep the octave equal to reference to avoid nearest-octave jumps
            cand.octave = last_pitch.octave
        else:
            # default/nearest behavior: start from the candidate's parsed
            # octave (as returned by _parse_note_token) and shift by octaves
            # until the interval to last_pitch is within +/-6 semitones.
            # This mimics LilyPond's "nearest" relative octave choice.
            while cand.ps - last_pitch.ps > 6:
                cand.octave -= 1
            while last_pitch.ps - cand.ps > 6:
                cand.octave += 1
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
    n = music21.note.Note(f"{step}{acc}{octave}", quarterLength=ql)
    # Preserve the original pitch token (e.g. "f'" or "c,") so we can
    # prefer this textual form when emitting LilyPond tokens later. This
    # helps keep explicit octave marks exactly as the user wrote them.
    try:
        n._orig_pitch_token = pitch_token
    except Exception:
        pass
    try:
        # store the full normalized token (including duration) so emission
        # can reproduce the exact user-supplied text when available
        n._orig_token = tok
    except Exception:
        pass
    return n

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
        ch = music21.chord.Chord(chord_pitches, quarterLength=ql)
        try:
            ch._orig_chord_body = chord_body
        except Exception:
            pass
        try:
            # store the full token (e.g. "<c e g>4") for verbatim emission when
            # engraving the Lily tokens later
            ch._orig_token = tok
        except Exception:
            pass
        return ch
    return None


# -----------------------------------------------------------------
# High-level input helpers
# -----------------------------------------------------------------
def _convert_duration_input(d):
    """Convert common duration representations to quarterLength.

    Accepts int/float (treated as ql), or strings like '4', '8.', or '0.5'.
    """
    if d is None:
        return 1.0
    if isinstance(d, (int, float)):
        return float(d)
    if isinstance(d, str):
        s = d.strip()
        # dotted forms
        dotted = s.endswith('.')
        if dotted:
            s_base = s[:-1]
        else:
            s_base = s
        # try integer denominator like '4' -> quarter
        try:
            den = int(s_base)
            ql = 4.0 / float(den)
            if dotted:
                ql *= 1.5
            return ql
        except Exception:
            try:
                return float(s)
            except Exception:
                raise ValueError(f"Unsupported duration input: {d}")
    raise ValueError(f"Unsupported duration input type: {type(d)}")


def part_from_input(inp):
    """Create a music21 Part from a supported input form.

    Supported input types:
    - music21.stream.Part: returned unchanged
    - LilyPond snippet (string containing backslashes or starting with '\relative'): parsed with parse_lilypond_snippet
    - tinyNotation string (prefix 'tiny:' or 'tinynotation:') or bare tiny tokens: parsed with music21.converter.parse('tinynotation: ...')

    Note: Python-level pitch-lists (lists/tuples of pitch strings) are intentionally
    unsupported. Please provide LilyPond shorthand or tinyNotation so the same
    human-editable format is used across study files. If you need programmatic
    generation, return a music21.stream.Part from your generator and pass that
    Part directly to this function.
    """
    from music21 import stream, note, converter

    # already a Part
    if isinstance(inp, music21.stream.Part):
        return inp

    # strings: detect tinynotation vs lilypond
    if isinstance(inp, str):
        s = inp.strip()
        low = s.lower()
        # explicit tinyNotation prefix
        if low.startswith('tinynotation:') or low.startswith('tiny:'):
            try:
                # ensure converter sees the right format
                if low.startswith('tinynotation:'):
                    return converter.parse(s)
                else:
                    body = s.split(':', 1)[1].strip()
                    return converter.parse('tinynotation: ' + body)
            except Exception:
                # fallback to lily parser
                return parse_lilypond_snippet(s)

        # Heuristic: if it contains backslash tokens or Lily-like markers, assume Lily
        if '\\' in s or s.startswith('\\relative') or '<' in s or '|' in s:
            return parse_lilypond_snippet(s)

        # Otherwise try tinyNotation and fall back to lilypond
        try:
            return converter.parse('tinynotation: ' + s)
        except Exception:
            return parse_lilypond_snippet(s)

    # Explicit pitch-lists are not accepted. This keeps repository inputs
    # consistent (LilyPond or tinyNotation) and avoids a second, divergent
    # input format. If a caller passes a list/tuple, raise with a helpful
    # message explaining the preferred alternatives.
    if isinstance(inp, (list, tuple)):
        raise TypeError(
            "Pitch-list inputs (list/tuple of pitches) are deprecated and not supported. "
            "Please supply LilyPond shorthand or tinyNotation strings, or return a "
            "music21.stream.Part from your programmatic generator and pass that Part."
        )

    raise TypeError(f"Unsupported input type for part_from_input: {type(inp)}")


def part_to_tinynotation(part: music21.stream.Part) -> str:
    """Produce a conservative tinyNotation string from a music21 Part.

    This mirrors the earlier helper but lives in the template so study
    files can request a tinyNotation representation consistently.
    """
    from music21 import meter

    # find time signature if present
    ts = None
    for el in part.recurse():
        if isinstance(el, meter.TimeSignature):
            ts = el
            break
    ts_text = ts.ratioString if ts is not None else '4/4'

    # find key if present
    key_text = None
    try:
        from music21 import key as m21key, tempo as m21tempo
        klist = list(part.recurse().getElementsByClass(m21key.Key))
        if klist:
            k = klist[0]
            key_text = f"key {k.tonic.name.lower()} {('major' if k.mode=='major' else 'minor')}"
    except Exception:
        key_text = None

    # find tempo if present
    tempo_text = None
    try:
        tlist = list(part.recurse().getElementsByClass(m21tempo.MetronomeMark))
        if tlist:
            tm = tlist[0]
            if tm.number:
                # numeric bpm
                tempo_text = f"tempo {int(tm.number)}"
            elif tm.getText():
                tempo_text = f"tempo {tm.getText()}"
    except Exception:
        tempo_text = None

    def ql_to_den_token(ql):
        dens = [1, 2, 4, 8, 16, 32]
        for den in dens:
            base = 4.0 / den
            if abs(ql - base) < 1e-6:
                return str(den)
            if abs(ql - base * 1.5) < 1e-6:
                return f"{den}."
        best = min(dens, key=lambda d: abs(ql - (4.0 / d)))
        base = 4.0 / best
        if abs(ql - base * 1.5) < abs(ql - base):
            return f"{best}."
        return str(best)

    tokens = []
    for el in part.flatten().notesAndRests:
        ql = el.quarterLength
        dur_token = ql_to_den_token(ql)
        if el.isRest:
            tokens.append(f"r{dur_token}")
        else:
            try:
                pname = el.pitch.nameWithOctave
            except Exception:
                pname = str(el)
            tokens.append(f"{pname.lower()}{dur_token}")

    header_parts = [ts_text]
    if key_text:
        header_parts.append(key_text)
    if tempo_text:
        header_parts.append(tempo_text)
    header = ' '.join(header_parts)
    return f"tinynotation: {header} {' '.join(tokens)}"


def chordify_harmony(melody: music21.stream.Part) -> music21.stream.Part:
    """Create a chordified harmony part from a melody.

    This groups simultaneous events into harmonic moments (chords) and
    returns a music21 Part where gaps are filled with rests so durations
    align with the source melody. This is useful for engraving chordified
    harmony alongside a melody and ensures measure alignment.
    """
    from music21 import stream, chord as m21chord, note

    harmony = stream.Part()
    chordified = melody.chordify()

    # compute total length of the source melody so we can pad at the end
    total_len = 0.0
    for el in melody.flatten().notesAndRests:
        total_len = max(total_len, getattr(el, 'offset', 0) + getattr(el, 'quarterLength', 0))

    # collect chord events and sort by offset
    events = sorted(chordified.recurse().getElementsByClass(m21chord.Chord), key=lambda e: e.offset)

    cur = 0.0
    for el in events:
        # if there's a gap before this chord, insert a rest to fill it
        if el.offset > cur + 1e-8:
            gap = el.offset - cur
            harmony.append(note.Rest(quarterLength=gap))
            cur += gap

        # determine a sensible root; prefer explicit root() if available
        try:
            root_pitch = el.root()
        except Exception:
            # fallback: use the bass pitch
            root_pitch = el.bass()
        # build triad (root, +3, +7)
        tri = m21chord.Chord([root_pitch, root_pitch.transpose(3), root_pitch.transpose(7)])
        # preserve the duration of the chordified event
        tri.quarterLength = el.quarterLength
        harmony.insert(el.offset, tri)
        cur = max(cur, el.offset + el.quarterLength)

    # pad final gap to match melody total length
    if cur < total_len - 1e-8:
        harmony.append(note.Rest(quarterLength=(total_len - cur)))

    return harmony

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


def _normalize_lily_for_abjad(s: str) -> str:
    """Normalize a LilyPond token string so Abjad's parser accepts
    localized accidentals and common ASCII forms.

    Examples:
    - 'bmol' or 'bemol' -> 'bes' (B-flat)
    - 'f#' -> 'fis' (F-sharp)
    - Unicode ♯/♭ -> 'is'/'es'
    This normalization is only applied to strings being fed to Abjad's
    parser; the original snippet text written to the .ly file is left
    unchanged for fidelity.
    """
    import re

    if not s:
        return s

    # Replace only occurrences that look like note names (avoid matching
    # backslash commands like \time, \key). Use negative lookbehind to
    # ensure we don't replace letters immediately preceded by a backslash.
    def repl_acc(m):
        note = m.group('note')
        acc = m.group('acc') or ''
        octave = m.group('oct') or ''
        dur = m.group('dur') or ''
        # normalize accidentals
        if not acc:
            acc_norm = ''
        else:
            a = acc.lower()
            if a in ('mol', 'bemol', '\u266d'):
                acc_norm = 'es'
            elif a in ('#', '\u266f'):
                acc_norm = 'is'
            else:
                acc_norm = a
        return note + acc_norm + octave + dur

    # Match note tokens like: a, a#, amus, bmol, a'4, <a c e>2 (we handle inner notes)
    note_re = re.compile(r"(?<!\\)(?P<note>[a-gA-G])(?P<acc>mol|bemol|#|\u266f|\u266d|is|es)?(?P<oct>[,']*)(?P<dur>\d*\.?\d*)", re.IGNORECASE)

    # First handle chords: replace inside < ... > bodies separately
    def norm_chord(match):
        body = match.group(1)
        new_body = note_re.sub(repl_acc, body)
        return '<' + new_body + '>'

    s = re.sub(r"<([^>]+)>", norm_chord, s)

    # Then replace standalone notes
    s = note_re.sub(repl_acc, s)

    return s

def m21_pitch_to_lily(p: music21.pitch.Pitch) -> str:
    # Default conversion via music21 pitch nameWithOctave
    return abjad.lilypond(abjad.NamedPitch(p.nameWithOctave))

def engrave_with_abjad(parts: dict, output_file: str, prune_other: bool = False, force: bool = False):
    # If one part provides global directives (time signature, key, tempo),
    # propagate them to any part that lacks them. This ensures consistent
    # engraving (same barlines and tempo) even when some parts were created
    # without those directives.
    def _propagate_global_directives(source_part, target_part):
        try:
            from music21 import meter, tempo, key as m21key
            ts_list = list(source_part.recurse().getElementsByClass(meter.TimeSignature))
            if ts_list:
                ts = ts_list[0]
                existing_ts = list(target_part.recurse().getElementsByClass(meter.TimeSignature))
                if not existing_ts:
                    target_part.insert(0, ts)
            key_list = list(source_part.recurse().getElementsByClass(m21key.Key))
            if key_list:
                k = key_list[0]
                existing_k = list(target_part.recurse().getElementsByClass(m21key.Key))
                if not existing_k:
                    target_part.insert(0, k)
            tempo_list = list(source_part.recurse().getElementsByClass(tempo.MetronomeMark))
            if tempo_list:
                tm = tempo_list[0]
                existing_tm = list(target_part.recurse().getElementsByClass(tempo.MetronomeMark))
                if not existing_tm:
                    target_part.insert(0, tm)
        except Exception:
            pass

    # Choose a source for global directives: prefer the first part that contains
    # a TimeSignature, otherwise fall back to the first part in the dict.
    source_for_directives = None
    try:
        from music21 import meter
        for p in parts.values():
            if list(p.recurse().getElementsByClass(meter.TimeSignature)):
                source_for_directives = p
                break
        if source_for_directives is None:
            # fallback to first part
            if len(parts) > 0:
                source_for_directives = next(iter(parts.values()))
    except Exception:
        source_for_directives = next(iter(parts.values())) if parts else None

    if source_for_directives is not None:
        for name, part in parts.items():
            if part is None:
                continue
            if part is not source_for_directives:
                # Warning: inform the user when propagation is applied so it's
                # obvious which parts are inheriting time/key/tempo.
                try:
                    from music21 import meter
                    if not list(part.recurse().getElementsByClass(meter.TimeSignature)):
                        print(f"[warning] propagating TimeSignature/Key/Tempo from '{list(parts.keys())[0]}' to part '{name}'")
                except Exception:
                    pass
                _propagate_global_directives(source_for_directives, part)

    # Prepare a minimal comment header early so fallback emission can use it
    # even if the detailed comment block is constructed later. This prevents
    # UnboundLocalError when a manual multi-staff fallback path is taken
    # before the full comment block is assembled.
    comment_lines = [
        "% ======= Generated comparison (Lily tokens vs tinyNotation) =======",
        "% (This block is informational — LilyPond ignores lines starting with %)",
        "%",
    ]

    # Convert each provided music21 Part into an Abjad Voice (if it contains tokens)
    voices = {}
    voice_token_texts = {}
    for name, part in parts.items():
        if part is None:
            continue
        tokens = []
        # Heuristic: warn if many tokens lack explicit durations (these are
        # commonly the source of surprising relative-octave or measure issues).
        try:
            # inspect the original part's leaves for duration metadata
            nodur_count = 0
            total = 0
            for el in part.flatten().notesAndRests:
                total += 1
                if getattr(el, 'quarterLength', None) is None:
                    nodur_count += 1
            if total and nodur_count/total > 0.0:
                # if any element has missing duration, warn (0.0 threshold to show any)
                print(f"[info] part '{name}' has {nodur_count}/{total} elements with missing duration metadata")
        except Exception:
            pass
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
                # Prefer original textual tokens only when they include explicit
                # octave marks (apostrophes or commas). Otherwise fall back to
                # pitch-derived strings which include the octave number so the
                # emitted pitches remain correct.
                if isinstance(el, music21.chord.Chord):
                    # Prefer a verbatim original token (including duration) if available
                    full = getattr(el, '_orig_token', None)
                    if full:
                        tokens.append(full)
                    else:
                        orig = getattr(el, '_orig_chord_body', None)
                        if orig and ("'" in orig or "," in orig):
                            chord_pitches = orig
                        else:
                            chord_pitches = " ".join(m21_pitch_to_lily(p) for p in el.pitches)
                        tokens.append(f"<{chord_pitches}>{dur_str}")
                elif isinstance(el, music21.note.Note):
                    full = getattr(el, '_orig_token', None)
                    if full:
                        tokens.append(full)
                    else:
                        orig = getattr(el, '_orig_pitch_token', None)
                        if orig and ("'" in orig or "," in orig):
                            pitch_text = orig
                        else:
                            pitch_text = m21_pitch_to_lily(el.pitch)
                        tokens.append(f"{pitch_text}{dur_str}")
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
                            full = getattr(el, '_orig_token', None)
                            if full:
                                inner = full
                            else:
                                orig = getattr(el, '_orig_chord_body', None)
                                if orig and ("'" in orig or "," in orig):
                                    chord_pitches = orig
                                else:
                                    chord_pitches = " ".join(m21_pitch_to_lily(p) for p in el.pitches)
                                inner = f"<{chord_pitches}>{inner_dur}"
                        elif isinstance(el, music21.note.Note):
                            full = getattr(el, '_orig_token', None)
                            if full:
                                inner = full
                            else:
                                orig = getattr(el, '_orig_pitch_token', None)
                                if orig and ("'" in orig or "," in orig):
                                    pitch_text = orig
                                else:
                                    pitch_text = m21_pitch_to_lily(el.pitch)
                                inner = f"{pitch_text}{inner_dur}"
                        else:
                            inner = f"r{inner_dur}"
                        tokens.append(f"\\tuplet {r.numerator}/{r.denominator} {{ {inner} }}")
                        tuplet_emitted = True
                        break
                if not tuplet_emitted:
                    # Fallback to approximate lily duration string (existing behavior)
                    dur_str = ql_to_lily_duration_string(el.quarterLength)
                    if isinstance(el, music21.chord.Chord):
                        full = getattr(el, '_orig_token', None)
                        if full:
                            tokens.append(full)
                        else:
                            orig = getattr(el, '_orig_chord_body', None)
                            if orig and ("'" in orig or "," in orig):
                                chord_pitches = orig
                            else:
                                chord_pitches = " ".join(m21_pitch_to_lily(p) for p in el.pitches)
                            tokens.append(f"<{chord_pitches}>{dur_str}")
                    elif isinstance(el, music21.note.Note):
                        full = getattr(el, '_orig_token', None)
                        if full:
                            tokens.append(full)
                        else:
                            orig = getattr(el, '_orig_pitch_token', None)
                            if orig and ("'" in orig or "," in orig):
                                pitch_text = orig
                            else:
                                pitch_text = m21_pitch_to_lily(el.pitch)
                            tokens.append(f"{pitch_text}{dur_str}")
                    elif isinstance(el, music21.note.Rest):
                        tokens.append(f"r{dur_str}")

        # If the original part stored the user's Lily snippet and it used
        # \relative, prefer emitting that snippet verbatim so LilyPond's
        # relative octave context is preserved. Otherwise use the generated
        # token stream.
        orig_snip = getattr(part, '_original_snippet', None)
        if orig_snip and '\\relative' in orig_snip:
            token_text = orig_snip
        else:
            token_text = " ".join(tokens).strip()
        if token_text:
            # Keep user-visible token_text in the comment index
            voice_token_texts[name] = token_text
            try:
                token_for_abjad = _normalize_lily_for_abjad(token_text)
                voices[name] = abjad.Voice(token_for_abjad, name=name)
            except Exception:
                # If Abjad can't parse this token text, fall back to a
                # manual multi-staff emission below (so LilyPond itself will
                # parse the original snippets). Mark a flag and stop building
                # Abjad voices.
                manual_multi_fallback = True
                # keep the original token_texts for manual emission
                break

    if 'manual_multi_fallback' in locals() and manual_multi_fallback:
        # Build a manual multi-staff Lily file using the available
        # original snippets or token_texts so LilyPond parses them
        # directly. This preserves localized notation and avoids
        # Abjad parsing errors.
        # Ensure we have an output path available here (the usual out_path
        # is computed later). Compute a local out_dir/ly_path so we can
        # immediately write the manual .ly and call LilyPond.
        out_path = Path(output_file)
        if out_path.parent == Path('.') or str(out_path.parent) == '':
            out_dir = Path('outputs')
        else:
            out_dir = out_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        ly_filename = out_path.with_suffix('.ly').name
        ly_path = out_dir / ly_filename

        manual_lines = []
        manual_lines.extend(comment_lines)
        # Build a safe Lily body from a music21 Part by emitting explicit
        # pitches (nameWithOctave) so LilyPond receives unambiguous tokens.
        def _lily_from_m21_pitch(p: music21.pitch.Pitch, octave_nudge: int = 0) -> str:
            # Build a LilyPond pitch token with explicit octave marks so
            # LilyPond rendering won't rely on a surrounding relative
            # context. This avoids octave-shifts when emitting raw tokens
            # inside Staff blocks.
            try:
                name = p.name  # e.g. 'C#' or 'B-'
                octave = int(p.octave) + octave_nudge
            except Exception:
                # fallback: try to parse nameWithOctave
                s = getattr(p, 'nameWithOctave', str(p))
                m = re.match(r"([A-Ga-g])([#b-]?)(\d+)", s)
                if not m:
                    return s.lower()
                base_letter = m.group(1).lower()
                acc = m.group(2)
                octave = int(m.group(3))
                name = base_letter + (acc or '')

            base = name[0].lower()
            acc = name[1:] if len(name) > 1 else ''
            if acc in ('#', '♯'):
                acc_text = 'is'
            elif acc in ('b', '-', '♭'):
                acc_text = 'es'
            else:
                acc_text = ''

            # LilyPond convention: c  -> C3, c' -> C4, c'' -> C5
            # so the number of apostrophes = octave - 3 (negative -> commas)
            n = octave - 3
            if n > 0:
                oct_marks = "'" * n
            elif n < 0:
                oct_marks = "," * (-n)
            else:
                oct_marks = ''

            return f"{base}{acc_text}{oct_marks}"

        def _safe_body_from_part(part):
            toks = []
            try:
                for el in part.flatten().notesAndRests:
                    ql = getattr(el, 'quarterLength', 1.0) or 1.0
                    dur_str = ql_to_lily_duration_string(ql)
                    if getattr(el, 'isRest', False):
                        toks.append(f"r{dur_str}")
                        continue
                    if isinstance(el, music21.chord.Chord):
                        chord_pitches = " ".join(_lily_from_m21_pitch(p) for p in el.pitches)
                        toks.append(f"<{chord_pitches}>{dur_str}")
                        continue
                    if isinstance(el, music21.note.Note):
                        pitch_text = _lily_from_m21_pitch(el.pitch)
                        toks.append(f"{pitch_text}{dur_str}")
                        continue
            except Exception:
                return ""
            return " ".join(toks)
        # Simplified: always include a \version line, force English,
        # prefer original snippets verbatim, and wrap multiple Staffs
        # in a simultaneous block.
        manual_lines.append('\\version "2.24.1"')
        manual_lines.append('\\language "english"')
        manual_lines.append('\\header {')
        manual_lines.append(f'    title = "{out_path.stem} (generated)"')
        manual_lines.append('    composer = "Python + music21 + Abjad"')
        manual_lines.append('}')
        manual_lines.append('')
        manual_lines.append('\\score {')
        if len(parts) > 1:
            manual_lines.append('  <<')

        for pname in parts.keys():
            ppart = parts.get(pname)
            p_snip = getattr(ppart, '_original_snippet', None)

            # Build directive prefix (time/key/tempo) from part if available
            dir_prefix = ''
            try:
                if ppart is not None:
                    from music21 import meter, key as m21key, tempo as m21tempo
                    ts_list = list(ppart.recurse().getElementsByClass(meter.TimeSignature))
                    if ts_list:
                        ts = ts_list[0]
                        dir_prefix += f"\\time {ts.numerator}/{ts.denominator} "
                    k_list = list(ppart.recurse().getElementsByClass(m21key.Key))
                    if k_list:
                        k = k_list[0]
                        k_mode = getattr(k, 'mode', '') or ''
                        mode = 'minor' if 'minor' in k_mode.lower() else 'major'
                        dir_prefix += f"\\key {k.tonic.name.lower()} \\\{mode} "
                    tm_list = list(ppart.recurse().getElementsByClass(m21tempo.MetronomeMark))
                    if tm_list and getattr(tm_list[0], 'number', None):
                        tm = tm_list[0]
                        dir_prefix += f"\\tempo 4={int(getattr(tm, 'number', 120))} "
            except Exception:
                dir_prefix = ''

            # Prefer user-supplied snippet when available; otherwise synthesize
            if isinstance(p_snip, str) and p_snip.strip():
                # Normalize localized accidentals and ASCII sharps to
                # canonical LilyPond tokens so LilyPond will accept them
                # in the manual-emitted file. This preserves the user's
                # structure but avoids unrecognized tokens like 'bmol'.
                try:
                    body = _normalize_lily_for_abjad(p_snip)
                except Exception:
                    body = p_snip
            else:
                body = _safe_body_from_part(ppart) or voice_token_texts.get(pname, '')

            manual_lines.append('  \\new Staff')
            manual_lines.append('  {')
            try:
                if p_snip:
                    manual_lines.append(f'    % original snippet: {p_snip}')
            except Exception:
                pass

            # Attach clef if this part looks like harmony/bass
            try:
                clef_tok = ''
                if 'harmony' in pname.lower() or 'bass' in pname.lower():
                    clef_tok = '\\clef bass '
                else:
                    clef_tok = '\\clef treble '
            except Exception:
                clef_tok = ''

            manual_lines.append(f'    {clef_tok}{dir_prefix}{body}')
            manual_lines.append('  }')

        if len(parts) > 1:
            manual_lines.append('  >>')

        manual_lines.append('  \\layout { }')
        manual_lines.append('  \\midi { }')
        manual_lines.append('}')
        # Sanitize lines to remove control characters that may have been
        # introduced accidentally (e.g. vertical tab 0x0B). LilyPond is
        # sensitive to such bytes and will fail parsing the \version line.
        import re as _re
        cleaned = []
        for _l in manual_lines:
            if not isinstance(_l, str):
                _l = str(_l)
            # Detect control characters; rather than silently deleting them
            # (which can truncate sequences like "\version" if a control
            # byte is present), replace them with visible escape markers
            # (e.g. '\\x0b') and warn so the user can inspect the source.
            if _re.search(r"[\x00-\x1f]", _l):
                def _esc_ctrl(m):
                    return '\\x%02x' % ord(m.group(0))
                _l = _re.sub(r"[\x00-\x1f]", _esc_ctrl, _l)
                print(f"[warning] control characters replaced with escape sequences in Lily line: {repr(_l)[:200]}")
            cleaned.append(_l)
        ly_text = "\n".join(cleaned) + "\n"
        ly_path.write_text(ly_text)
        print(f"Wrote manual multi-staff Lily file: {ly_path}")
        subprocess.run(["lilypond", str(ly_path.name)], cwd=str(out_dir))
        return

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

    # If there is exactly one part and it stored the original Lily snippet
    # using \relative, prefer emitting that original snippet verbatim inside
    # a Staff so LilyPond's relative octave semantics are preserved.
    try:
        if len(parts) == 1:
            name_only = next(iter(parts.keys()))
            orig_part = parts.get(name_only)
            orig_snip = getattr(orig_part, '_original_snippet', None)
            if orig_snip and "\\relative" in orig_snip:
                # Emit a minimal Lily file that wraps the original \relative
                # snippet verbatim inside a single Staff. This guarantees
                # LilyPond will interpret relative octaves exactly as the
                # user wrote them and avoids mixing in Abjad-generated tokens.
                manual = []
                manual.append('\\version "2.24.1"')
                manual.append('\\language "english"')
                manual.append('\\header {')
                manual.append(f'    title = "{out_path.stem} (generated)"')
                manual.append('    composer = "Python + music21 + Abjad"')
                manual.append('}')
                # Place the original snippet directly inside a Staff so the
                # \relative block is preserved verbatim.
                manual.append('\\score {')
                manual.append('  \\new Staff')
                manual.append('  {')
                manual.append(f'    {orig_snip}')
                manual.append('  }')
                manual.append('  \\layout { }')
                manual.append('  \\midi { }')
                manual.append('}')
                wrapped = "\n".join(manual) + "\n"
    except Exception:
        pass

    # Determine output directory. If output_file includes a path, use that
    # parent, otherwise default to outputs/ so generated artifacts are grouped.
    out_path = Path(output_file)
    if out_path.parent == Path('.') or str(out_path.parent) == '':
        out_dir = Path('outputs')
    else:
        out_dir = out_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # If a PDF already exists and force is False, don't overwrite — let the
    # template decide whether to regenerate. This moves overwrite control out
    # of study files and into the template so callers don't need to duplicate
    # the same existence checks.
    try:
        pdf_path = out_dir / f"{out_path.stem}.pdf"
        if pdf_path.exists() and not force:
            print(f"Output exists ({pdf_path}). Use --force to overwrite. Leaving file unchanged.")
            return
    except Exception:
        pass

    # Optionally prune other generated basenames in out_dir so only files
    # matching this output basename remain (e.g. keep first_score.* only).
    if prune_other:
        try:
            basename = out_path.stem
            for p in out_dir.iterdir():
                if not p.is_file():
                    continue
                if p.suffix.lower() in {'.ly', '.pdf', '.midi'} and p.stem != basename:
                    try:
                        p.unlink()
                    except Exception:
                        pass
        except Exception:
            pass

    ly_filename = out_path.with_suffix('.ly').name
    ly_path = out_dir / ly_filename
    # Prepend a concise commented comparison block to the LilyPond file so
    # users can inspect the emitted Lily tokens and the derived tinyNotation
    # directly inside the .ly file. This mirrors outputs/<basename>.txt but
    # keeps everything in a single concise artifact.
    try:
        comment_lines = [
            "% ======= Generated comparison (Lily tokens vs tinyNotation) =======",
            "% (This block is informational — LilyPond ignores lines starting with %)",
            "%"
        ]
        for name, part in parts.items():
            if part is None:
                continue
            comment_lines.append(f"% === Part: {name} ===")
            # include original snippet if the part stores it
            try:
                orig = getattr(part, '_original_snippet', None)
                if orig:
                    comment_lines.append(f"% original snippet: {orig}")
            except Exception:
                pass
            try:
                tn = part_to_tinynotation(part)
                comment_lines.append(f"% tinyNotation: {tn}")
            except Exception:
                comment_lines.append("% tinyNotation: (failed to derive)")
            lp = voice_token_texts.get(name, "")
            # Wrap long token strings to reasonable line lengths
            maxw = 120
            if lp:
                for i in range(0, len(lp), maxw):
                    comment_lines.append(f"% lilyTokens: {lp[i:i+maxw]}")
            else:
                comment_lines.append("% lilyTokens: (none)")
            comment_lines.append("%")
        comment_block = "\n".join(comment_lines) + "\n\n"
        # If a single part provided an original \relative snippet, write a
        # minimal LilyPond file that uses that snippet verbatim. This avoids
        # any Abjad-driven reformatting that can alter relative octave
        # interpretation.
        try:
            if len(parts) == 1:
                only_name = next(iter(parts.keys()))
                only_part = parts.get(only_name)
                only_snip = getattr(only_part, '_original_snippet', None)
                if only_snip and '\\relative' in only_snip:
                    manual_lines = [
                        '% ======= Generated comparison (Lily tokens vs tinyNotation) =======',
                        '% (This block is informational — LilyPond ignores lines starting with %)',
                        '%',
                    ]
                    manual_lines.extend(comment_lines[3:])
                    manual_lines.append('')
                    manual_lines.append('\\version "2.24.1"')
                    manual_lines.append('\\language "english"')
                    manual_lines.append('\\header {')
                    manual_lines.append(f'    title = "{out_path.stem} (generated)"')
                    manual_lines.append('    composer = "Python + music21 + Abjad"')
                    manual_lines.append('}')
                    manual_lines.append('')
                    # If the \relative base lacks explicit octave marks, add a
                    # single apostrophe so the reference pitch is unambiguous
                    # (this nudges the reference into the expected octave).
                    adj = only_snip
                    try:
                        mbase = re.match(r"(\\relative\s+)([a-g][eis]*)(\s*\{)", only_snip)
                        if mbase:
                            prefix, base_tok, brace = mbase.groups()
                            if "'" not in base_tok and "," not in base_tok:
                                base_tok = base_tok + "'"
                                adj = prefix + base_tok + brace + only_snip[mbase.end():]
                    except Exception:
                        adj = only_snip
                    # Place the (possibly adjusted) snippet in the file
                    # Build a full LilyPond score that wraps the (possibly
                    # adjusted) original snippet in a Staff and includes
                    # layout and midi blocks. Writing a complete \score
                    # ensures LilyPond interprets the \relative base the
                    # same way it would in a normal score file.
                    full = []
                    full.extend([
                        '% ======= Generated comparison (Lily tokens vs tinyNotation) =======',
                        '% (This block is informational — LilyPond ignores lines starting with %)',
                        '%',
                    ])
                    full.extend(comment_lines[3:])
                    full.append('')
                    full.append('\\version "2.24.1"')
                    full.append('\\language "english"')
                    full.append('\\header {')
                    full.append(f'    title = "{out_path.stem} (generated)"')
                    full.append('    composer = "Python + music21 + Abjad"')
                    full.append('}')
                    full.append('')
                    # Place the adjusted original snippet inside a Staff within
                    # an explicit \score so LilyPond's relative rules apply
                    full.append('\\score {')
                    full.append('  \\new Staff {')
                    full.append(f'    {adj}')
                    full.append('  }')
                    full.append('  \\layout { }')
                    full.append('  \\midi { }')
                    full.append('}')
                    full_text = "\n".join(full) + "\n"
                    # indicate that we emitted a manual full-score (use MIDI to
                    # derive JSON events later so the event list matches the
                    # engraved output)
                    manual_emitted = True
                    ly_path.write_text(full_text)
                    # Re-parse the adjusted snippet so JSON/events reflect
                    # the same pitch interpretation LilyPond will use.
                    try:
                        parsed_adj = parse_lilypond_snippet(adj)
                        parsed_adj._original_snippet = adj
                        parts[only_name] = parsed_adj
                    except Exception:
                        pass
                    # We've written the proper manual score; skip the hybrid write
                    raise StopIteration()
        except StopIteration:
            pass
        except Exception:
            # fallback to writing the hybrid content if anything goes wrong
            ly_path.write_text(comment_block + wrapped)
        else:
            # normal case: write the hybrid content
            ly_path.write_text(comment_block + wrapped)
    except Exception:
        ly_path.write_text(wrapped)
    # The .ly file already contains a commented comparison block (tinyNotation
    # + lily tokens). We will produce a small JSON events file that browser
    # players can use as a lightweight fallback. If we emitted a manual
    # full-score from the original \relative snippet (manual_emitted), then
    # build the JSON from the generated MIDI so it matches LilyPond's
    # interpretation exactly. Otherwise build events from the music21 Parts.
    manual_emitted = locals().get('manual_emitted', False)

    print(f"Compiling {ly_path} with LilyPond...")
    # Run lilypond in the output directory so auxiliary files land there
    subprocess.run(["lilypond", str(ly_path.name)], cwd=str(out_dir))

    # Now produce JSON events. If we emitted a manual full-score, parse the
    # generated MIDI and derive events from it to guarantee consistency with
    # the engraved PDF/MIDI; otherwise derive events from the music21 Parts.
    try:
        import json
        from music21 import converter as m21converter
        # Determine BPM first (prefer a MetronomeMark from source_for_directives)
        bpm = None
        try:
            from music21 import tempo as m21tempo
            if source_for_directives is not None:
                tlist = list(source_for_directives.recurse().getElementsByClass(m21tempo.MetronomeMark))
                if tlist and getattr(tlist[0], 'number', None):
                    bpm = float(tlist[0].number)
            if bpm is None:
                for p in parts.values():
                    if p is None: continue
                    tlist = list(p.recurse().getElementsByClass(m21tempo.MetronomeMark))
                    if tlist and getattr(tlist[0], 'number', None):
                        bpm = float(tlist[0].number)
                        break
        except Exception:
            bpm = None
        if bpm is None:
            bpm = 120.0

        seconds_per_quarter = 60.0 / float(bpm)

        json_out = {'bpm': bpm, 'parts': {}}

        if manual_emitted:
            # parse the output MIDI to extract events
            midi_path = out_dir / f"{out_path.stem}.midi"
            try:
                s = m21converter.parse(str(midi_path))
                events = []
                for n in s.flat.notes:
                    events.append({'time': float(n.offset) * seconds_per_quarter, 'name': n.nameWithOctave, 'duration': float(n.quarterLength) * seconds_per_quarter, 'velocity': 0.9})
                json_out['parts'][next(iter(parts.keys()))] = events
            except Exception:
                # fallback to deriving from music21 parts
                manual_emitted = False

        if not manual_emitted:
            for name, part in parts.items():
                if part is None:
                    continue
                events = []
                try:
                    for el in part.flatten().notesAndRests:
                        if getattr(el, 'isRest', False):
                            continue
                        offset_q = getattr(el, 'offset', None)
                        ql = getattr(el, 'quarterLength', None) or 0.0
                        if offset_q is None:
                            continue
                        start_s = float(offset_q) * seconds_per_quarter
                        dur_s = float(ql) * seconds_per_quarter
                        if isinstance(el, music21.chord.Chord):
                            for p in el.pitches:
                                events.append({'time': start_s, 'name': p.nameWithOctave, 'duration': dur_s, 'velocity': 0.9})
                        elif isinstance(el, music21.note.Note):
                            events.append({'time': start_s, 'name': el.pitch.nameWithOctave, 'duration': dur_s, 'velocity': 0.9})
                except Exception:
                    pass
                json_out['parts'][name] = events

        json_path = out_dir / f"{out_path.stem}.json"
        try:
            with json_path.open('w', encoding='utf8') as fh:
                json.dump(json_out, fh, indent=2)
            print(f"Wrote JSON events file: {json_path}")
        except Exception:
            pass
    except Exception:
        pass

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