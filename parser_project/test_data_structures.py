"""
Test suite for ParseResult and TokenInfo data structures.

These tests verify the metadata tracking and formatting capabilities.
"""

import unittest
from data_structures import ParseResult, TokenInfo


class TestTokenInfo(unittest.TestCase):
    """Tests for the TokenInfo dataclass."""
    
    def test_basic_token_creation(self):
        """Test creating a simple token without warnings."""
        token = TokenInfo(
            original="c4",
            converted="C4",
            position=0
        )
        self.assertEqual(token.original, "c4")
        self.assertEqual(token.converted, "C4")
        self.assertEqual(token.position, 0)
        self.assertFalse(token.has_warning())
        self.assertFalse(token.is_flagged())
    
    def test_token_with_warning(self):
        """Test token flagged with a warning."""
        token = TokenInfo(
            original="bmol4",
            converted="Bb4",
            position=1,
            warnings=["Localized accidental 'bmol' converted to 'Bb'"]
        )
        self.assertTrue(token.has_warning())
        self.assertTrue(token.is_flagged())
        self.assertEqual(len(token.warnings), 1)
    
    def test_token_with_large_leap(self):
        """Test token flagged due to large pitch leap."""
        token = TokenInfo(
            original="c'4",
            converted="C5",
            position=2,
            pitch_leap=13
        )
        self.assertFalse(token.has_warning())
        self.assertTrue(token.is_flagged())  # Large leap
        self.assertEqual(token.pitch_leap, 13)
    
    def test_token_with_small_leap(self):
        """Test token with small leap is not flagged."""
        token = TokenInfo(
            original="d4",
            converted="D4",
            position=1,
            pitch_leap=2
        )
        self.assertFalse(token.has_warning())
        self.assertFalse(token.is_flagged())  # Small leap


class TestParseResult(unittest.TestCase):
    """Tests for the ParseResult dataclass."""
    
    def test_empty_result(self):
        """Test creating an empty ParseResult."""
        result = ParseResult()
        self.assertEqual(result.tiny_notation, "")
        self.assertEqual(len(result.tokens), 0)
        self.assertTrue(result.success)
        self.assertFalse(result.has_warnings())
    
    def test_simple_successful_parse(self):
        """Test a successful parse with no warnings."""
        result = ParseResult(
            tiny_notation="4/4 C4 D4 E4 F4",
            tokens=[
                TokenInfo("c4", "C4", 0),
                TokenInfo("d4", "D4", 1, pitch_leap=2),
                TokenInfo("e4", "E4", 2, pitch_leap=2),
                TokenInfo("f4", "F4", 3, pitch_leap=1),
            ],
            directives={"time": "4/4"}
        )
        self.assertTrue(result.success)
        self.assertEqual(len(result.tokens), 4)
        self.assertFalse(result.has_warnings())
        self.assertEqual(len(result.flagged_tokens()), 0)
    
    def test_parse_with_token_warnings(self):
        """Test parse that generated token-level warnings."""
        result = ParseResult(
            tiny_notation="4/4 C4 Bb4",
            tokens=[
                TokenInfo("c4", "C4", 0),
                TokenInfo("bmol4", "Bb4", 1, warnings=["Localized accidental"]),
            ]
        )
        self.assertTrue(result.has_warnings())
        self.assertEqual(len(result.flagged_tokens()), 1)
        self.assertEqual(result.flagged_tokens()[0].original, "bmol4")
    
    def test_parse_with_global_warnings(self):
        """Test parse with global warnings."""
        result = ParseResult(
            tiny_notation="4/4 C4",
            warnings=["Time signature not specified, defaulting to 4/4"]
        )
        self.assertTrue(result.has_warnings())
    
    def test_format_review(self):
        """Test generating a review report."""
        result = ParseResult(
            tiny_notation="6/4 E2 Bb4 C2",
            tokens=[
                TokenInfo("e2", "E2", 0),
                TokenInfo("bmol4", "Bb4", 1, 
                         warnings=["Localized accidental 'bmol'"],
                         pitch_leap=-2),
                TokenInfo("c2", "C2", 2, pitch_leap=13),
            ],
            directives={"time": "6/4"}
        )
        
        review = result.format_review()
        self.assertIn("CONVERSION REVIEW", review)
        self.assertIn("6/4 E2 Bb4 C2", review)
        self.assertIn("bmol4", review)
        self.assertIn("Localized accidental", review)
        self.assertIn("13 semitones", review)
    
    def test_format_inline_annotated(self):
        """Test inline annotation format."""
        result = ParseResult(
            tiny_notation="4/4 C4 Bb4 C5",
            tokens=[
                TokenInfo("c4", "C4", 0),
                TokenInfo("bmol4", "Bb4", 1, warnings=["Warning"]),
                TokenInfo("c'4", "C5", 2, pitch_leap=13),
            ],
            directives={"time": "4/4"}
        )
        
        annotated = result.format_inline_annotated()
        self.assertEqual(annotated, "4/4 C4 Bb4[⚠️] C5[↗️]")
    
    def test_to_dict(self):
        """Test JSON serialization."""
        result = ParseResult(
            tiny_notation="4/4 C4 D4",
            tokens=[
                TokenInfo("c4", "C4", 0),
                TokenInfo("d4", "D4", 1, pitch_leap=2),
            ],
            directives={"time": "4/4"},
            success=True
        )
        
        data = result.to_dict()
        self.assertEqual(data["tiny_notation"], "4/4 C4 D4")
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["tokens"]), 2)
        self.assertEqual(data["tokens"][1]["pitch_leap"], 2)
        self.assertEqual(data["flagged_count"], 0)


if __name__ == '__main__':
    unittest.main()
