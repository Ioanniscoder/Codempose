"""
Eerste compositie: basisstructuur voor een nieuwe melodie
Gebaseerd op project_template.py, maar minimalistisch en klaar voor eigen invulling.
"""

import music21
import abjad
from pathlib import Path


# Variant 1: LilyPond-snippet van E4 naar B3
MELODY_SNIPPET = r"\relative e' { e4 d c b }"  # E4 D4 C4 B3
HARMONY_SNIPPET = "e2 b2 <e g b>1"
OUTPUT_BASENAME = "first_score"

# Variant 2: Python-lijst van noten
MELODY_LIST = ["e4", "d4", "c4", "b3"]

# Variant 3: Algoritmisch (stap omlaag per noot)
def generate_stepwise_melody(start_note="e4", steps=4):
    from music21 import note
    pitches = ["e4", "d4", "c4", "b3"]
    part = pt.music21.stream.Part()
    for p in pitches:
        part.append(note.Note(p, quarterLength=1.0))
    return part

# Variant 4: Motief-variatie (herhaal motief, transpose)
def generate_motif_variation(motif=["e4", "d4"], transpositions=[0, -2]):
    from music21 import note, interval
    part = pt.music21.stream.Part()
    for t in transpositions:
        for p in motif:
            n = note.Note(p, quarterLength=1.0)
            if t != 0:
                n = n.transpose(t)
            part.append(n)
    return part

# Functies uit project_template.py hergebruiken
import project_template as pt


if __name__ == "__main__":
    print("--- Bouw alle varianten als afzonderlijke parts en combineer tot één score ---")
    # Maak de vier melodie parts
    melody1 = pt.parse_lilypond_snippet(MELODY_SNIPPET)
    harmony1 = pt.parse_lilypond_snippet(HARMONY_SNIPPET)
    from music21 import stream, note
    melody2 = stream.Part([note.Note(p, quarterLength=1.0) for p in MELODY_LIST])
    melody3 = generate_stepwise_melody()
    melody4 = generate_motif_variation()

    # Demonstreer inhoud
    print("Melody1:")
    melody1.show('text')
    print("Melody2:")
    melody2.show('text')

    # Combineer in één dictionary met expliciete staff-namen
    parts = {
        "Melody1": melody1,
        "Melody2": melody2,
        "Melody3": melody3,
        "Melody4": melody4,
    }

    # Roep engraving aan voor één enkel outputbestand met meerdere staves
    pt.engrave_with_abjad(parts, "first_score_all")
    print("✅ PDF gegenereerd: first_score_all.pdf")
