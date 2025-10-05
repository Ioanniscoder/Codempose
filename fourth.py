# fourth.py
"""
Fourth study file for testing two-stave output with chords in a minor key.

This file follows the new architecture:
- It is self-executing (run with `python fourth.py`).
- It uses the validated parser via `lilypond_parser.py`.
- It performs programmatic composition (transformations).
- It uses music21's `.chordify()` to create a harmony part.
- It returns a two-part `score_data` dictionary for engraving.

This demonstrates:
- Two-stave output (Melody + Harmony)
- Chord handling throughout the pipeline
- Musical transformations (transpose, invert)
- A minor key (key-independent system)
"""
import music21
from copy import deepcopy
from lilypond_parser import parse_lilypond_to_data
from music_data import data_to_part, extract_data_from_part
from second import transpose_part, invert_part  # Reusing transformations

# 1. The musical theme, now in A minor
SOURCE_THEME_LILY = r"\relative c' { \time 4/4 \key a \minor a4 e' b c }"

# 2. The main builder function, called by the pipeline
def build_score_data():
    """Builds a two-part score (Melody + Harmony) from the theme.
    
    This function demonstrates:
    - Parsing LilyPond input
    - Converting to music21.Part
    - Applying transformations (transpose, invert)
    - Creating harmony via chordify()
    - Converting both parts to canonical event format
    - Returning complete score_data for engraving
    """
    
    # Parse the theme into events, then convert to a music21.Part
    parsed_theme = parse_lilypond_to_data(SOURCE_THEME_LILY, part_name='Theme')
    theme_part = data_to_part(
        parsed_theme.get('parts', {}).get('Theme', []),
        parsed_theme.get('metadata', {})
    )

    # Create a longer melody by transforming the theme
    phrase1 = theme_part
    phrase2 = transpose_part(theme_part, 'P4')  # Transpose up a 4th
    phrase3 = invert_part(theme_part, 'E4')     # Invert around E4
    
    # Combine phrases into a full melody Part
    full_melody_part = music21.stream.Part()
    for part in [phrase1, phrase2, phrase3]:
        for element in part.flatten().notesAndRests:
            full_melody_part.append(deepcopy(element))
            
    # CRITICAL TEST: Create the harmony part using .chordify()
    # This will create Chord objects that test our chord handling
    harmony_part = full_melody_part.chordify()

    # Convert both parts to the event dictionary format using our fixed function
    melody_events = extract_data_from_part(full_melody_part)
    harmony_events = extract_data_from_part(harmony_part)

    # Assemble the final score_data object for the engraver
    metadata = parsed_theme.get('metadata', {})
    metadata['title'] = 'Fourth Study - Two Staves in A Minor'

    score_data = {
        'metadata': metadata,
        'parts': {
            'Melody': melody_events,
            'Harmony': harmony_events,
        },
    }
    return score_data


# 3. Expose a small public API for tooling and tests
__all__ = ['SOURCE_THEME_LILY', 'build_score_data']


# 4. Make the script self-executing
if __name__ == '__main__':
    # This block makes `python fourth.py` work directly
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
