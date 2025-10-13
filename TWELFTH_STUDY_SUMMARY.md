# Twelfth Study: Complete Summary

## Overview

The **Twelfth Study** demonstrates the complete four-station workflow with all relevant music21 transformations applied to a single melodic snippet, arranged using **shorthand notation**.

## Four-Station Workflow

### Station 1: Original LilyPond Snippet
```lilypond
\relative e { 
  \time 6/4 
  \key c \major 
  \tempo 4=90 
  e2 b4 c2 r4 | 
  e2 f4 e2 r4 | 
  b2. f'2. | 
  e2. c2. | 
  e2 b2 c2 
}
```

### Station 2: TinyNotation Equivalent
```
tinynotation: 6/4 e2 b4 c'2 r4 e'2 f'4 e'2 r4 b'2. f''2. e''2. c''2. e''2 b''2 c'''2
```

### Station 3: Shorthand Structure
The piece is arranged using **declarative shorthand notation**:

```python
VOICE_ASSIGNMENTS = {
    'SingleLine': {
        'Original': 'SNIPPET',
        'Intermezzo_1': 'HARMONY',
        'Transposed_P5': 'SNIPPET_TRANSPOSED_P5',
        'Intermezzo_2': 'HARMONY',
        'Inverted_C4': 'SNIPPET_INVERTED_C4',
        'Intermezzo_3': 'HARMONY',
        'Retrograde': 'SNIPPET_RETROGRADE',
        'Intermezzo_4': 'HARMONY',
        'Augmented_x2': 'SNIPPET_AUGMENTED',
        'Intermezzo_5': 'HARMONY',
        'Diminished_x0.5': 'SNIPPET_DIMINISHED',
        'Intermezzo_6': 'HARMONY',
        'Octave_Up': 'SNIPPET_OCTAVE_UP',
        'Intermezzo_7': 'HARMONY',
        'Octave_Down': 'SNIPPET_OCTAVE_DOWN',
    }
}
```

### Station 4: Programmatic Transformations
All transformations are generated programmatically and **documented** as reusable snippets:

1. **SNIPPET** - Identity (original snippet)
2. **HARMONY** - Chordified harmony (recurring intermezzo)
3. **SNIPPET_TRANSPOSED_P5** - Transposed up a perfect fifth
4. **SNIPPET_INVERTED_C4** - Melodically inverted around C4
5. **SNIPPET_RETROGRADE** - Reversed (retrograde)
6. **SNIPPET_AUGMENTED** - Augmented (x2 duration)
7. **SNIPPET_DIMINISHED** - Diminished (x0.5 duration)
8. **SNIPPET_OCTAVE_UP** - Octave up (+P8)
9. **SNIPPET_OCTAVE_DOWN** - Octave down (-P8)

## Structure

The final piece follows this pattern:
```
[Original] → [Harmony] → [Transform 1] → [Harmony] → [Transform 2] → ... → [Transform 7]
```

- **15 total sections** on a single staff
- **Harmony intermezzo** recurs 7 times (between each transformation)
- **7 transformations** showcase all major music21 operations

## Key Features

1. ✅ **Complete four-station workflow** documented
2. ✅ **Shorthand notation** used for arrangement
3. ✅ **All transformations documented** as reusable snippets
4. ✅ **Both LilyPond and TinyNotation** formats shown
5. ✅ **Recurring intermezzo** separates each transformation
6. ✅ **Everything on a single line** for easy comparison
7. ✅ **MusicXML export** for MuseScore compatibility

## Output Files

Generated in `outputs/`:
- `twelfth.ly` - LilyPond source with complete documentation
- `twelfth.pdf` - Musical score
- `twelfth.midi` - Audio playback
- `twelfth.musicxml` - MuseScore import file

## How to Use

1. **Run**: `python twelfth.py`
2. **View**: `outputs/twelfth.pdf`
3. **Edit**: Copy any snippet from `outputs/twelfth.ly`
4. **Import**: Open `outputs/twelfth.musicxml` in MuseScore
5. **Customize**: Modify `VOICE_ASSIGNMENTS` to create your own arrangement

## Promotion Toggles

- `PROMOTE_TO_TINYNOTATION = False` - Use LilyPond as primary format
- `PROMOTE_TO_PROGRAMMATIC = False` - Use shorthand notation (set `True` for manual assembly)
