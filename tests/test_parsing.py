import unittest
import project_template as pt

class TestParsing(unittest.TestCase):
    def test_relative_snippet_durations_and_accidentals(self):
        s = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 }"
        # ensure tokenizer handles localized accidental and ASCII '#'
        tokens = pt._get_tokens(pt._normalize_lily_for_abjad(s))
        self.assertIn('bes4', tokens)
        self.assertIn('fis4', tokens)
        # parse snippet
        part = pt.parse_lilypond_snippet(s)
        elems = [el for el in part.flatten().notesAndRests]
        # first four elements should be e2, bmol4, c2, r4
        self.assertGreaterEqual(len(elems), 4)
        first, second, third, fourth = elems[0:4]
        # durations: 2 -> quarterLength 2.0, 4 -> 1.0
        self.assertAlmostEqual(first.quarterLength, 2.0)
        self.assertAlmostEqual(second.quarterLength, 1.0)
        self.assertAlmostEqual(third.quarterLength, 2.0)
        self.assertAlmostEqual(fourth.quarterLength, 1.0)
        # accidentals: second should be B-flat
        self.assertTrue(hasattr(second, 'pitch'))
        self.assertEqual(second.pitch.step.upper(), 'B')
        # pitch alteration: ensure it's flat (alter == -1.0) if accidental metadata exists
        if getattr(second.pitch, 'accidental', None) is not None:
            self.assertAlmostEqual(second.pitch.accidental.alter, -1.0)

    def test_emitter_preserves_accidentals(self):
        s = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 }"
        part = pt.parse_lilypond_snippet(s)
        emitted = pt.emit_lily_tokens_from_part(part)
        # Tokenize the emitted string and remove octave marks (apostrophes/commas)
        import re
        toks = pt._get_tokens(emitted)
        norm = [re.sub(r"[,']", "", t) for t in toks]
        # After normalization, we expect to see B-flat (bes4) and F-sharp (fis4)
        self.assertIn('bes4', norm)
        self.assertIn('fis4', norm)

if __name__ == '__main__':
    unittest.main()
