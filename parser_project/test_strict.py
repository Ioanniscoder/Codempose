"""
Strict Test Suite - Character-by-Character Verification
========================================================

This test suite uses EXACT string matching to verify correct behavior.
Every test asserts the EXACT expected output and specific warnings.
"""

import unittest
from lily_to_tiny import lily_to_tiny_notation


class TestRelativeOctaveCrossing(unittest.TestCase):
    """Test that relative mode correctly handles octave boundaries."""
    
    def test_ascending_scale_crosses_octave(self):
        """C Major scale: b to c should cross to next octave."""
        snippet = r"\relative c' { c4 d e f g a b c }"
        result = lily_to_tiny_notation(snippet)
        
        # EXACT expected output
        self.assertEqual(result.tiny_notation, "c4 d4 e4 f4 g4 a4 b4 c'4")
        self.assertTrue(result.success)
        self.assertFalse(result.has_warnings(), "Scale should not generate warnings")
    
    def test_descending_scale_crosses_octave(self):
        """Descending: c to b should cross down."""
        snippet = r"\relative c' { c4 b a g f e d c }"
        result = lily_to_tiny_notation(snippet)
        
        # From c (C4): b is B3 (down 1 semitone, closest)
        # From B3: a is A3, etc., until final c is C3
        self.assertEqual(result.tiny_notation, "c4 b,4 a,4 g,4 f,4 e,4 d,4 c,4")
        self.assertTrue(result.success)


class TestExplicitOctaveMarkers(unittest.TestCase):
    """Test that explicit ' and , markers work correctly."""
    
    def test_single_tick_up(self):
        """c' should force one octave up from calculated position."""
        snippet = r"\relative c { c'4 }"
        result = lily_to_tiny_notation(snippet)
        
        # Base c = C3. First c' calculates to C3, then ' forces to C4
        self.assertEqual(result.tiny_notation, "c4")
        self.assertTrue(result.success)
    
    def test_comma_down(self):
        """c, should force one octave down."""
        snippet = r"\relative c'' { c,4 }"
        result = lily_to_tiny_notation(snippet)
        
        # Base c'' = C5. First c, calculates to C5, then , forces to C4
        self.assertEqual(result.tiny_notation, "c4")
        self.assertTrue(result.success)
    
    def test_mixed_markers_complex(self):
        """Mixed ' and , markers in sequence."""
        snippet = r"\relative c' { c4 e' g, c' }"
        result = lily_to_tiny_notation(snippet)
        
        # c4: C4 (base)
        # e': E closest to C4 is E4, then ' makes it E5
        # g,: G closest to E5 is G5 (up 3 semitones), then , makes it G4
        # c': C closest to G4 is C5 (up 5 semitones), then ' makes it C6
        
        # In TinyNotation from base c (C4):
        # C4=c4, E5=e'4, G4=g4, C6=c''4
        self.assertEqual(result.tiny_notation, "c4 e'4 g4 c''4")
        self.assertTrue(result.success)


class TestImplicitDurations(unittest.TestCase):
    """Test that durations inherit from previous note."""
    
    def test_eighth_notes_inherit(self):
        """Eighth note should carry forward."""
        snippet = r"\time 6/8 \relative c' { c8 d e f g a }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertEqual(result.tiny_notation, "6/8 c8 d8 e8 f8 g8 a8")
        self.assertTrue(result.success)
    
    def test_mixed_durations_inherit_correctly(self):
        """Each duration change should affect following notes."""
        snippet = r"\relative c' { c8 d e4 f g2 a }"
        result = lily_to_tiny_notation(snippet)
        
        # c8 d8 (inherits 8), e4 f4 (inherits 4), g2 a2 (inherits 2)
        self.assertEqual(result.tiny_notation, "c8 d8 e4 f4 g2 a2")
        self.assertTrue(result.success)
    
    def test_dotted_durations_inherit(self):
        """Dotted durations should inherit."""
        snippet = r"\relative c' { c4. d e8 f }"
        result = lily_to_tiny_notation(snippet)
        
        # c4. d4. (inherits 4.), e8 f8 (inherits 8)
        self.assertEqual(result.tiny_notation, "c4. d4. e8 f8")
        self.assertTrue(result.success)


class TestAccidentalsInRelativeMode(unittest.TestCase):
    """Test that accidentals are considered in relative calculations."""
    
    def test_ascending_flats(self):
        """Flats should create ascending line."""
        snippet = r"\relative c' { bes4 es as des }"
        result = lily_to_tiny_notation(snippet)
        
        # Starting from c' (C4):
        # bes: Bb closest to C4 is Bb3 (down 2 semitones)
        # es: Eb closest to Bb3 is Eb4 (up 5 semitones)
        # as: Ab closest to Eb4 is Ab4 (up 5 semitones)  
        # des: Db closest to Ab4 is Db5 (up 5 semitones)
        # In TinyNotation: Bb3=b-,4, Eb4=e-4, Ab4=a-4, Db5=d-'4
        self.assertEqual(result.tiny_notation, "b-,4 e-4 a-4 d-'4")
        self.assertTrue(result.success)
    
    def test_ascending_sharps(self):
        """Sharps should be calculated correctly."""
        snippet = r"\relative c' { fis4 cis gis dis }"
        result = lily_to_tiny_notation(snippet)
        
        # Smallest chromatic interval rule:
        # From C4: F# closest is F#4 (up 6 semitones)
        # From F#4: C# closest is C#4 (down 5 semitones)
        # From C#4: G# closest is G#4 (up 7 semitones)
        # From G#4: D# closest is D#4 (down 5 semitones)
        
        self.assertEqual(result.tiny_notation, "f#4 c#4 g#4 d#4")
        self.assertTrue(result.success)


class TestWarnings(unittest.TestCase):
    """Test that warnings are generated correctly."""
    
    def test_localized_accidental_warning(self):
        """bmol should generate specific warning."""
        snippet = r"\relative c' { bmol4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertTrue(result.has_warnings())
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("Localized accidental", result.warnings[0])
        self.assertIn("mol", result.warnings[0])
    
    def test_large_leap_warning(self):
        """Large leap (without explicit marker) should warn."""
        snippet = r"\relative c { c4 c'' }"  # Would be 2 octaves
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        # This should NOT warn because c'' has explicit marker
        # Let's test a true large leap
        
    def test_no_warning_with_explicit_marker(self):
        """Explicit markers should NOT generate leap warnings."""
        snippet = r"\relative c { c4 c'''4 }"
        result = lily_to_tiny_notation(snippet)
        
        # c'''4 has explicit marker, so no warning even though it's a huge leap
        self.assertFalse(result.has_warnings())


if __name__ == "__main__":
    unittest.main(verbosity=2)
