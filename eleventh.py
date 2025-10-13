"""
ELEVENTH STUDY: All-in-One Transformation Template
====================================================

This template demonstrates a comprehensive approach: combining all relevant music21 transformations on a single melody line, with a structure suitable for both single and double staves.

- SOURCE_MELODY_LILY is the single source-of-truth (LilyPond \relative snippet, no accidentals).
- All transformations are applied to this melody.
- The structure is fully documented and ready for further experimentation.

"""

from typing import Dict, List
import copy
import music21

from lilypond_parser import parse_lilypond_to_data
from music_data import extract_data_from_part, data_to_part

# ---------------------------------------------------------------------------
# 1) Source Melody (no accidentals)
# ---------------------------------------------------------------------------
SOURCE_MELODY_LILY = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 b4 c2 r4 | e2 f4 e2 r4 | b2. f'2. | e2. c2. | e2 b2 c2 }"

# ---------------------------------------------------------------------------
# 2) Transformation helpers (all relevant music21 transforms)
# ---------------------------------------------------------------------------
def identity(part: music21.stream.Part) -> music21.stream.Part:
    return copy.deepcopy(part)

def transpose_part(part: music21.stream.Part, interval: str) -> music21.stream.Part:
    return part.transpose(interval)

def invert_part(part: music21.stream.Part, center_pitch: str) -> music21.stream.Part:
    p = copy.deepcopy(part)
    from music21 import pitch, interval
    center = pitch.Pitch(center_pitch)
    notes = list(p.recurse().getElementsByClass(music21.note.Note))
    for n in notes:
        try:
            iv = interval.Interval(noteStart=center, noteEnd=n.pitch)
            inv = iv.complement
            n.pitch = center.transpose(inv)
        except Exception:
            continue
    return p

def retrograde_part(part: music21.stream.Part) -> music21.stream.Part:
    p = copy.deepcopy(part)
    elems = [e for e in p.recurse().notesAndRests]
    newp = music21.stream.Part()
    for e in reversed(elems):
        try:
            newp.append(e.clone())
        except Exception:
            newp.append(copy.deepcopy(e))
    return newp

def augment_part(part: music21.stream.Part, factor: float) -> music21.stream.Part:
    p = copy.deepcopy(part)
    for n in p.flat.notesAndRests:
        n.quarterLength *= factor
    return p

def diminish_part(part: music21.stream.Part, factor: float) -> music21.stream.Part:
    p = copy.deepcopy(part)
    for n in p.flat.notesAndRests:
        n.quarterLength /= factor
    return p

def chordify_part(part: music21.stream.Part) -> music21.stream.Part:
    return part.chordify()

# ---------------------------------------------------------------------------
# 3) Build all transformations
# ---------------------------------------------------------------------------
def build_score_data() -> Dict[str, Dict]:
    """Apply all relevant transformations to the source melody."""
    parsed = parse_lilypond_to_data(SOURCE_MELODY_LILY, part_name='Melody')
    metadata = parsed.get('metadata', {})
    melody_events = parsed.get('parts', {}).get('Melody', [])
    melody_part = data_to_part(melody_events, metadata)
    melody_part.id = 'Melody'

    # Apply transformations
    transformations = {
        'Original': identity(melody_part),
        'Transposed_P5': transpose_part(melody_part, 'P5'),
        'Inverted_C4': invert_part(melody_part, 'C4'),
        'Retrograde': retrograde_part(melody_part),
        'Augmented_x2': augment_part(melody_part, 2.0),
        'Diminished_x0.5': diminish_part(melody_part, 2.0),
        'Chordified': chordify_part(melody_part),
    }

    # Convert each transformation to canonical event lists
    parts = {name: extract_data_from_part(part) for name, part in transformations.items()}

    out_meta = dict(metadata) if metadata else {}
    out_meta.setdefault('title', 'Eleventh Study: All-in-One Transformations')

    score_data = {
        'metadata': out_meta,
        'parts': parts,
    }
    return score_data

__all__ = ['SOURCE_MELODY_LILY', 'build_score_data', 'transpose_part', 'invert_part', 'retrograde_part', 'augment_part', 'diminish_part', 'chordify_part']

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
