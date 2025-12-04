import re
from project_template import parse_lilypond_snippet, _get_tokens
import copy
import first
import music21


def extract_relative_body(snippet: str):
    m = re.match(r"\\relative\s+([a-g][eis]*[,']*)\s*\{(.+)\}", snippet, re.DOTALL)
    if m:
        return m.group(2).strip()
    return snippet


def inspect_tokens(snippet: str, name: str):
    body = extract_relative_body(snippet)
    tokens = _get_tokens(body)
    print(f"--- Tokens for {name} ---")
    print(tokens)
    print()


def inspect_part(part, name, ts_override=None):
    ts = list(part.recurse().getElementsByClass(music21.meter.TimeSignature))
    if ts_override is not None:
        ts_use = ts_override
    else:
        ts_use = ts[0] if ts else None
    if ts_use:
        measure_ql = ts_use.numerator * (4/ts_use.denominator)
    else:
        measure_ql = 4.0
    print(f"--- Part: {name}  Has TS: {bool(ts)}  Using TS: {ts_use}  measure_q_length={measure_ql} ---")
    running = 0.0
    for i, el in enumerate(part.flatten().notesAndRests, start=1):
        # element repr
        typ = type(el).__name__
        pitch = getattr(el, 'pitch', None)
        pitches = getattr(el, 'pitches', None)
        if pitches is not None:
            pstr = ",".join(p.nameWithOctave for p in pitches)
        elif pitch is not None:
            pstr = pitch.nameWithOctave
        else:
            pstr = 'Rest'
        print(f"{i:02d}: offset~{running:.4f} ql={el.quarterLength:.4f} -> measure {int(running//measure_ql)+1}   {typ}({pstr})")
        running += el.quarterLength
    print(f" total ql= {running}\n")


if __name__ == '__main__':
    print('\n=== Current MELODY_SNIPPET ===')
    print(first.MELODY_SNIPPET)
    print('\n=== Current HARMONY_SNIPPET ===')
    print(first.HARMONY_SNIPPET)

    inspect_tokens(first.MELODY_SNIPPET, 'Melody')
    inspect_tokens(first.HARMONY_SNIPPET, 'Harmony')

    mel = parse_lilypond_snippet(first.MELODY_SNIPPET)
    har = parse_lilypond_snippet(first.HARMONY_SNIPPET)

    inspect_part(mel, 'Melody')
    inspect_part(har, 'Harmony')

    # simulate propagation
    ts = list(mel.recurse().getElementsByClass(music21.meter.TimeSignature))
    if ts:
        print('--- Simulate propagation: inserting Melody TS into Harmony and re-inspecting')
        har2 = copy.deepcopy(har)
        har2.insert(0, ts[0])
        inspect_part(har2, 'Harmony (propagated)')

    print('--- Example: dotted halves in 6/4 (b2. f2.) ---')
    ex = parse_lilypond_snippet("\\relative c' { \\time 6/4 b2. f2. }")
    inspect_part(ex, 'example dotted halves')

    print('--- Example: malformed token (32 f e2 r) ---')
    ex2 = parse_lilypond_snippet("\\relative c' { 32 f e2 r }")
    inspect_tokens("\\relative c' { 32 f e2 r }", 'malformed')
    inspect_part(ex2, 'example malformed')
