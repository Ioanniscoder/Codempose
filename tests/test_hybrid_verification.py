from project_template import engrave_with_abjad


def test_hybrid_verification_accepts_respelling():
    # Build a tiny score_data with a flat that Abjad might respell
    sd = {
        'metadata': {'title': 'respell-test'},
        'parts': {
            'Mel': [
                {'type': 'note', 'step': 'b', 'alter': -1, 'octave': 4, 'ql': 1.0},
                {'type': 'note', 'step': 'e', 'alter': 0, 'octave': 4, 'ql': 1.0}
            ]
        }
    }
    # Should not raise
    engrave_with_abjad(sd, 'test_respell')
