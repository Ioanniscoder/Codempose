"""
Eerste compositie: basisstructuur voor een nieuwe melodie
Gebaseerd op project_template.py, maar minimalistisch en klaar voor eigen invulling.
"""

import argparse
from pathlib import Path

import music21
import abjad


# Variant 1: LilyPond-snippet van E4 naar B3
# Shorthand: plaats metrum, toonsoort en tempo in de snippet header zodat
# zowel de parser als de gebruiker de basisinstellingen op één plek hebben.
# Voorbeeld: \time 6/4, \key c \major, \tempo 4=90
MELODY_SNIPPET = r"\relative e' { \time 6/4 \key c \major \tempo 4=90 e2 b c2 r | e2 f e2 r | b3 f3 | e3 c3 | e2 b c2 }"
HARMONY_SNIPPET = "e2 b2 |<e g b>1"
OUTPUT_BASENAME = "first_score"

# Variant 2: Python-lijst van noten
MELODY_LIST = ["e4", "d4", "c4", "b3"]

# Variant 3: Algoritmisch (stap omlaag per noot)
def generate_stepwise_melody(start_note="e4", steps=4):
    from music21 import note, stream
    pitches = ["e4", "d4", "c4", "b3"]
    part = stream.Part()
    for p in pitches:
        part.append(note.Note(p, quarterLength=1.0))
    return part

# Variant 4: Motief-variatie (herhaal motief, transpose)
def generate_motif_variation(motif=["e4", "d4"], transpositions=[0, -2]):
    from music21 import note, interval, stream
    part = stream.Part()
    for t in transpositions:
        for p in motif:
            n = note.Note(p, quarterLength=1.0)
            if t != 0:
                n = n.transpose(t)
            part.append(n)
    return part


def generate_harmony_from_melody(melody):
    """Generate a simple triadic harmony under a melody.

    For each note in the melody we create a triad whose root is a third
    below the melody note. The chord keeps the same duration as the melody
    note so the parts align when engraved side-by-side.
    """
    from music21 import stream, note, chord, interval

    harmony = stream.Part()
    down_third = interval.Interval(-3)   # a third below the melody
    tri_third = interval.Interval(3)
    tri_fifth = interval.Interval(7)

    for el in melody.flatten().notesAndRests:
        if isinstance(el, note.Rest):
            harmony.append(note.Rest(quarterLength=el.quarterLength))
            continue

        # choose reference pitch (for chords, take the highest pitch)
        if isinstance(el, chord.Chord):
            ref = el.pitches[-1]
        else:
            ref = el.pitch

        root = ref.transpose(down_third)
        third = root.transpose(tri_third)
        fifth = root.transpose(tri_fifth)
        ch = chord.Chord([root, third, fifth], quarterLength=el.quarterLength)
        harmony.append(ch)

    return harmony


def chordify_harmony(melody):
    """Create harmony by chordifying the melody and producing triads per chord.

    This groups simultaneous events into harmonic moments rather than
    creating a triad for every single melodic note.
    """
    from music21 import stream, chord as m21chord

    harmony = stream.Part()
    chordified = melody.chordify()
    # iterate chord events and create a triad for each
    for el in chordified.recurse().getElementsByClass(m21chord.Chord):
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
    return harmony

# Functies uit project_template.py hergebruiken
import project_template as pt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run first.py studies")
    parser.add_argument("--mode", choices=["manual", "auto", "chordify", "both"], default="both",
                        help="Which harmony mode to engrave: manual=use HARMONY_SNIPPET, auto=generate per-note harmony, chordify=grouped harmony, both=run both and overwrite outputs")
    args = parser.parse_args()

    # Minimal run: parse Melody1 and keep other example blocks present but commented
    print("--- Build: parse Melody1 and engrave single staff ---")
    melody1 = pt.parse_lilypond_snippet(MELODY_SNIPPET)
    harmony1 = pt.parse_lilypond_snippet(HARMONY_SNIPPET)
    # from music21 import stream, note
    # melody2 = stream.Part([note.Note(p, quarterLength=1.0) for p in MELODY_LIST])
    # melody3 = generate_stepwise_melody()
    # melody4 = generate_motif_variation()

    # Show parsed text for quick inspection
    print("Melody1:")
    try:
        melody1.show('text')
    except Exception:
        pass

    # ----------------------------------------
    # Programmatic insertion (commented):
    # Je kunt dezelfde instellingen ook via music21-inserties toevoegen.
    # Dit geeft je de mogelijkheid om muziekprogramma's (algoritmen) te
    # bouwen bovenop dezelfde basisinstelling die de snippet gebruikt.
    # Voorbeeld (uncomment om te gebruiken):
    # melody1 = pt.parse_lilypond_snippet(MELODY_SNIPPET)
    # from music21 import meter, tempo, key
    # # voeg maatsoort, tempo en key programmatic toe
    # melody1.insert(0, meter.TimeSignature('6/4'))
    # melody1.insert(0, tempo.MetronomeMark(number=90))
    # melody1.insert(0, key.Key('C'))
    # ----------------------------------------

    # print("Melody2:")
    # try:
    #     melody2.show('text')
    # except Exception:
    #     pass

    # Combine parts dictionary (only Melody1 active; other parts kept commented)
    parts = {
        "Melody1": melody1,
         "Harmony": harmony1,
        # "Melody2": melody2,
        # "Melody3": melody3,
        # "Melody4": melody4,
    }
    # Choose behavior based on CLI mode
    if args.mode == "manual":
        parts = {"Melody1": melody1, "Harmony": harmony1}
        pt.engrave_with_abjad(parts, OUTPUT_BASENAME)
        print(f"✅ PDF generated: {OUTPUT_BASENAME}.pdf")
    elif args.mode == "auto":
        auto_harmony = generate_harmony_from_melody(melody1)
        parts = {"Melody1": melody1, "AutoHarmony": auto_harmony}
        pt.engrave_with_abjad(parts, OUTPUT_BASENAME)
        print(f"✅ PDF generated: {OUTPUT_BASENAME}.pdf")
    elif args.mode == "chordify":
        chord_harmony = chordify_harmony(melody1)
        parts = {"Melody1": melody1, "ChordHarmony": chord_harmony}
        pt.engrave_with_abjad(parts, OUTPUT_BASENAME)
        print(f"✅ PDF generated: {OUTPUT_BASENAME}.pdf")
    else:  # both
        # Run manual first, then overwrite with auto (keeps behavior simple)
        parts = {"Melody1": melody1, "Harmony": harmony1}
        pt.engrave_with_abjad(parts, OUTPUT_BASENAME)
        print(f"✅ PDF generated: {OUTPUT_BASENAME}.pdf")
        auto_harmony = generate_harmony_from_melody(melody1)
        parts2 = {"Melody1": melody1, "AutoHarmony": auto_harmony}
        pt.engrave_with_abjad(parts2, OUTPUT_BASENAME)
        print(f"✅ PDF generated: {OUTPUT_BASENAME}.pdf")
