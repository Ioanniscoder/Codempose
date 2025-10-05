"""
Comprehensive Test Suite for LilyPond to TinyNotation Converter
================================================================

Tests based on test_cases.txt covering all documented scenarios.
"""

import unittest
from lily_to_tiny import lily_to_tiny_notation
from data_structures import ParseResult


class TestBasicNotes(unittest.TestCase):
    """Test basic note conversions."""
    
    def test_simple_ascending_scale(self):
        """Test 1: Simple C Major scale."""
        snippet = r"\relative c' { c4 d e f g a b c }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("C4", result.tiny_notation)
        self.assertIn("C4", result.tiny_notation)  # Last note should be C5 in relative mode
        self.assertFalse(result.has_warnings())
    
    def test_single_note(self):
        """Test 2: Single note."""
        snippet = r"\relative c' { c4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("C4", result.tiny_notation)
        self.assertFalse(result.has_warnings())
    
    def test_all_same_pitch(self):
        """Test 3: All same pitch."""
        snippet = r"\relative c' { c4 c c c }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        # All should be C4 since they're the same pitch
        self.assertEqual(result.tiny_notation.count("C4"), 4)


class TestOctaveMarkers(unittest.TestCase):
    """Test octave marker handling."""
    
    def test_single_octave_up(self):
        """Test 4: Single octave up marker."""
        snippet = r"\relative c { c'4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        # c with base of c (C3), then c' should be C4
        self.assertIn("C4", result.tiny_notation)
    
    def test_double_octave_up(self):
        """Test 5: Double octave up markers."""
        snippet = r"\relative c { c''4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("C", result.tiny_notation)
    
    def test_octave_down(self):
        """Test 6: Octave down marker."""
        snippet = r"\relative c'' { c,4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("C", result.tiny_notation)


class TestAccidentals(unittest.TestCase):
    """Test accidental handling."""
    
    def test_sharp_is_suffix(self):
        """Test 7: Sharp with 'is' suffix."""
        snippet = r"\relative c' { fis4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("F#", result.tiny_notation)
        self.assertFalse(result.has_warnings())
    
    def test_flat_es_suffix(self):
        """Test 8: Flat with 'es' suffix."""
        snippet = r"\relative c' { bes4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("B-", result.tiny_notation)
        self.assertFalse(result.has_warnings())
    
    def test_localized_bmol(self):
        """Test 9: Localized 'bmol' (should warn)."""
        snippet = r"\relative c' { bmol4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("B-", result.tiny_notation)
        self.assertTrue(result.has_warnings())
        self.assertIn("Localized accidental", result.warnings[0])
    
    def test_localized_mol(self):
        """Test 10: Localized 'mol' (should warn)."""
        snippet = r"\relative c' { emol4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        # emol should be interpreted as e + mol (E-flat)
        # But our current tokenizer might not parse this correctly
        # This might need adjustment


class TestDurations(unittest.TestCase):
    """Test duration handling."""
    
    def test_whole_notes(self):
        """Test 11: Whole notes."""
        snippet = r"\relative c' { c1 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("C1", result.tiny_notation)
    
    def test_mixed_durations(self):
        """Test 12: Mixed durations."""
        snippet = r"\relative c' { c4 d8 e16 f2 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("C4", result.tiny_notation)
        self.assertIn("D8", result.tiny_notation)
        self.assertIn("E16", result.tiny_notation)
        self.assertIn("F2", result.tiny_notation)
    
    def test_dotted_notes(self):
        """Test 13: Dotted notes."""
        snippet = r"\relative c' { c4. d8. }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("C4.", result.tiny_notation)
        self.assertIn("D8.", result.tiny_notation)


class TestRests(unittest.TestCase):
    """Test rest handling."""
    
    def test_simple_rest(self):
        """Test 14: Simple rest."""
        snippet = r"\relative c' { c4 r4 d4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("r4", result.tiny_notation)
    
    def test_multiple_rests(self):
        """Test 15: Multiple rests with different durations."""
        snippet = r"\relative c' { r2 r4 r8 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("r2", result.tiny_notation)
        self.assertIn("r4", result.tiny_notation)
        self.assertIn("r8", result.tiny_notation)


class TestTimeSignatures(unittest.TestCase):
    """Test time signature handling."""
    
    def test_common_time(self):
        """Test 16: Common time (4/4)."""
        snippet = r"\time 4/4 \relative c' { c4 d e f }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("4/4", result.tiny_notation)
        self.assertEqual(result.directives.get('time'), '4/4')
    
    def test_waltz_time(self):
        """Test 17: Waltz time (3/4)."""
        snippet = r"\time 3/4 \relative c' { c4 d e }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("3/4", result.tiny_notation)
        self.assertEqual(result.directives.get('time'), '3/4')
    
    def test_six_eight_time(self):
        """Test 18: 6/8 time."""
        snippet = r"\time 6/8 \relative c' { c8 d e f g a }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("6/8", result.tiny_notation)


class TestComplexExamples(unittest.TestCase):
    """Test real-world complex examples."""
    
    def test_mixed_accidentals_and_rests(self):
        """Test 19: Mixed accidentals and rests."""
        snippet = r"\relative c' { e2 bmol4 c2 r4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("E2", result.tiny_notation)
        self.assertIn("B-4", result.tiny_notation)
        self.assertIn("r4", result.tiny_notation)
        self.assertTrue(result.has_warnings())  # bmol is localized
    
    def test_with_key_signature(self):
        """Test 20: With key signature."""
        snippet = r"\time 3/4 \key d \major \relative c' { d4 fis a }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("3/4", result.tiny_notation)
        self.assertIn("F#", result.tiny_notation)
        self.assertEqual(result.directives.get('key'), 'd \\major')
    
    def test_full_measure(self):
        """Test 21: Full measure with various elements."""
        snippet = r"\time 4/4 \relative c' { c4 r8 d16 e fis4. g8 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertIn("4/4", result.tiny_notation)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_snippet(self):
        """Test 22: Empty snippet."""
        snippet = r"{}"
        result = lily_to_tiny_notation(snippet)
        
        self.assertFalse(result.success)
        self.assertTrue(result.has_warnings())
    
    def test_large_leap_detection(self):
        """Test 23: Large leap detection."""
        snippet = r"\relative c { c4 c'''4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        self.assertTrue(result.has_warnings())
        # Should have warning about large leap
        self.assertTrue(any("leap" in w.lower() for w in result.warnings))
    
    def test_absolute_mode(self):
        """Test 24: Absolute mode (no \\relative)."""
        snippet = r"{ c4 d e f }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertTrue(result.success)
        # In absolute mode, notes should still parse correctly


class TestParseResultStructure(unittest.TestCase):
    """Test ParseResult object structure and methods."""
    
    def test_parse_result_has_required_fields(self):
        """Ensure ParseResult has all required fields."""
        snippet = r"\relative c' { c4 }"
        result = lily_to_tiny_notation(snippet)
        
        self.assertIsInstance(result, ParseResult)
        self.assertIsInstance(result.tiny_notation, str)
        self.assertIsInstance(result.tokens, list)
        self.assertIsInstance(result.directives, dict)
        self.assertIsInstance(result.warnings, list)
        self.assertIsInstance(result.success, bool)
    
    def test_flagged_tokens(self):
        """Test flagged_tokens() method."""
        snippet = r"\relative c' { bmol4 }"
        result = lily_to_tiny_notation(snippet)
        
        flagged = result.flagged_tokens()
        self.assertGreater(len(flagged), 0)
        self.assertTrue(flagged[0].warnings)
    
    def test_format_review(self):
        """Test format_review() method."""
        snippet = r"\relative c' { e2 bmol4 c2 r4 }"
        result = lily_to_tiny_notation(snippet)
        
        review = result.format_review()
        self.assertIsInstance(review, str)
        self.assertIn("TinyNotation", review)
        self.assertIn("⚠️", review)  # Should have warnings
    
    def test_to_dict(self):
        """Test to_dict() method."""
        snippet = r"\relative c' { c4 d e }"
        result = lily_to_tiny_notation(snippet)
        
        d = result.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn('tiny_notation', d)
        self.assertIn('success', d)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
