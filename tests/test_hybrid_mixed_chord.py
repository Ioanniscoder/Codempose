from project_template import engrave_with_abjad


def test_mixed_octave_chord_does_not_crash():
    sd = {
        'metadata': {'title': 'mixed-chord'},
        'parts': {
            'P': [
                {'type': 'chord', 'pitches': [ {'step':'c','alter':0,'octave':4}, {'step':'e','alter':0,'octave':5} ], 'ql': 1.0}
            ]
        }
    }
    engrave_with_abjad(sd, 'test_mixed_chord')
