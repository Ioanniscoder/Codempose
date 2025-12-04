#!/usr/bin/env python3
"""
Test suite for unified suffix container syntax: note(modifiers)

This test file validates the implementation of the suffix container feature,
which allows comma-separated modifiers inside parentheses after notes:
- Articulations: . (staccato), - (tenuto), > (accent)
- Dynamics: p, pp, f, ff, mf, mp, <, >
- Tracking: any identifier (e.g., themeA, motif1)

Examples:
    c4(.)              # Note with staccato
    c4(p)              # Note with piano dynamic
    c4(themeA)         # Note with tracking identifier
    c4(themeA, ., p)   # Note with all three modifier types
"""

import pytest
from lily_token_parser import parse_suffix_container, parse_token
from lilypond_parser import parse_lilypond_to_data


class TestSuffixContainerParser:
    """Test the parse_suffix_container() helper function."""
    
    def test_empty_container(self):
        """Empty container returns empty fields."""
        result = parse_suffix_container("")
        assert result == {'articulations': [], 'dynamics': '', 'tracker': ''}
    
    def test_single_articulation(self):
        """Single articulation is correctly classified."""
        result = parse_suffix_container(".")
        assert result['articulations'] == ['staccato']
        assert result['dynamics'] == ''
        assert result['tracker'] == ''
        
        result = parse_suffix_container("-")
        assert result['articulations'] == ['tenuto']
        
        result = parse_suffix_container(">")
        assert result['articulations'] == ['accent']
    
    def test_single_dynamic(self):
        """Single dynamic is correctly classified."""
        result = parse_suffix_container("p")
        assert result['articulations'] == []
        assert result['dynamics'] == 'p'
        assert result['tracker'] == ''
        
        result = parse_suffix_container("ff")
        assert result['dynamics'] == 'ff'
        
        result = parse_suffix_container("<")
        assert result['dynamics'] == '<'
    
    def test_single_tracker(self):
        """Single tracking identifier is correctly classified."""
        result = parse_suffix_container("themeA")
        assert result['articulations'] == []
        assert result['dynamics'] == ''
        assert result['tracker'] == 'themeA'
    
    def test_multiple_articulations(self):
        """Multiple articulations are collected."""
        result = parse_suffix_container("., -")
        assert len(result['articulations']) == 2
        assert 'staccato' in result['articulations']
        assert 'tenuto' in result['articulations']
    
    def test_combined_modifiers(self):
        """Comma-separated modifiers are correctly classified."""
        result = parse_suffix_container("themeA, ., p")
        assert result['articulations'] == ['staccato']
        assert result['dynamics'] == 'p'
        assert result['tracker'] == 'themeA'
        
        # Order doesn't matter
        result = parse_suffix_container("., p, themeA")
        assert result['articulations'] == ['staccato']
        assert result['dynamics'] == 'p'
        assert result['tracker'] == 'themeA'
    
    def test_whitespace_handling(self):
        """Whitespace around modifiers is stripped."""
        result = parse_suffix_container("  .  ,  p  ,  themeA  ")
        assert result['articulations'] == ['staccato']
        assert result['dynamics'] == 'p'
        assert result['tracker'] == 'themeA'


class TestTokenParserWithContainer:
    """Test that lily_token_parser correctly extracts container content."""
    
    def test_note_with_staccato(self):
        """Note with staccato articulation."""
        parsed = parse_token("c4(.)")
        assert parsed.pitch_letter == 'c'
        assert parsed.duration == '4'
        assert parsed.articulations == ['staccato']
        assert parsed.dynamics == ''
        assert parsed.tracker == ''
    
    def test_note_with_dynamic(self):
        """Note with dynamic marking."""
        parsed = parse_token("d4(p)")
        assert parsed.pitch_letter == 'd'
        assert parsed.dynamics == 'p'
        assert parsed.articulations == []
    
    def test_note_with_tracker(self):
        """Note with tracking identifier."""
        parsed = parse_token("e4(motif1)")
        assert parsed.pitch_letter == 'e'
        assert parsed.tracker == 'motif1'
    
    def test_note_with_combined_modifiers(self):
        """Note with multiple modifier types."""
        parsed = parse_token("f4(themeA, ., p)")
        assert parsed.pitch_letter == 'f'
        assert parsed.articulations == ['staccato']
        assert parsed.dynamics == 'p'
        assert parsed.tracker == 'themeA'
    
    def test_note_with_container_and_tie(self):
        """Container can coexist with tie marker."""
        parsed = parse_token("g4(.)~")
        assert parsed.pitch_letter == 'g'
        assert parsed.articulations == ['staccato']
        assert parsed.has_tie is True
    
    def test_grace_note_with_container(self):
        """Grace notes can have suffix containers."""
        parsed = parse_token("~a16(f)")
        assert parsed.is_grace is True
        assert parsed.pitch_letter == 'a'
        assert parsed.duration == '16'
        assert parsed.dynamics == 'f'
    
    def test_note_with_octave_and_container(self):
        """Octave markers work with containers."""
        parsed = parse_token("c'4(.)")
        assert parsed.pitch_letter == 'c'
        assert parsed.octave_markers == "'"
        assert parsed.articulations == ['staccato']
    
    def test_note_with_accidental_and_container(self):
        """Accidentals work with containers."""
        parsed = parse_token("cis4(p)")
        assert parsed.pitch_letter == 'c'
        assert parsed.accidental == 'sharp'
        assert parsed.dynamics == 'p'


class TestFullParserIntegration:
    """Test complete parsing flow from LilyPond syntax to events."""
    
    def test_simple_note_with_articulation(self):
        """Parse note with staccato."""
        result = parse_lilypond_to_data(r"\relative c' { c4(.) }")
        events = result['parts']['Part 1']
        assert len(events) == 1
        assert events[0]['type'] == 'note'
        assert events[0]['step'] == 'C'
        assert 'articulations' in events[0]
        assert 'staccato' in events[0]['articulations']
    
    def test_note_with_dynamic(self):
        """Parse note with dynamic marking."""
        result = parse_lilypond_to_data(r"\relative c' { d4(p) }")
        events = result['parts']['Part 1']
        assert len(events) == 1
        assert events[0]['type'] == 'note'
        assert events[0]['step'] == 'D'
        assert 'dynamics' in events[0]
        assert events[0]['dynamics'] == 'p'
    
    def test_note_with_tracker(self):
        """Parse note with tracking identifier."""
        result = parse_lilypond_to_data(r"\relative c' { e4(motif1) }")
        events = result['parts']['Part 1']
        assert len(events) == 1
        assert events[0]['type'] == 'note'
        assert events[0]['step'] == 'E'
        assert 'tracker' in events[0]
        assert events[0]['tracker'] == 'motif1'
    
    def test_note_with_combined_modifiers(self):
        """Parse note with all modifier types."""
        result = parse_lilypond_to_data(r"\relative c' { f4(themeA, ., p) }")
        events = result['parts']['Part 1']
        assert len(events) == 1
        event = events[0]
        assert event['type'] == 'note'
        assert event['step'] == 'F'
        assert 'articulations' in event
        assert 'staccato' in event['articulations']
        assert event['dynamics'] == 'p'
        assert event['tracker'] == 'themeA'
    
    def test_tied_notes_with_modifiers(self):
        """Parse tied notes where first has modifiers."""
        result = parse_lilypond_to_data(r"\relative c' { a2(p, >)~ a2 }")
        events = result['parts']['Part 1']
        assert len(events) == 1  # Tied notes merge into one event
        event = events[0]
        assert event['type'] == 'note'
        assert event['step'] == 'A'
        assert event['ql'] == 4.0  # 2.0 + 2.0 from tie merge
        assert 'articulations' in event
        assert 'accent' in event['articulations']
        assert event['dynamics'] == 'p'
    
    def test_grace_note_with_dynamic(self):
        """Parse grace note with dynamic marking."""
        result = parse_lilypond_to_data(r"\relative c' { ~g16 a2(f) }")
        events = result['parts']['Part 1']
        assert len(events) == 2
        # First event: grace note
        assert events[0]['is_grace'] is True
        assert events[0]['ql'] == 0.0
        # Second event: regular note with dynamic
        assert events[1]['type'] == 'note'
        assert events[1]['step'] == 'A'
        assert 'dynamics' in events[1]
        assert events[1]['dynamics'] == 'f'
    
    def test_comprehensive_example(self):
        """Parse the complete test case from specification.
        
        Input: r"\relative c' { ~g16 a2(p, themeA, >) a2~ a2(f) r4 }"
        Expected events:
        1. Grace G (ql=0.0)
        2. A with dynamics=p, tracker=themeA, articulations=[accent] (no tie)
        3. A tied (a2~ merged with a2(f)) - duration = 4.0, dynamics=f from second note lost in merge
        4. Rest
        
        Note: In a tie, only the first note's attributes are kept. The second note's modifiers
        are discarded during merge, which is musically correct (tied notes are one continuous sound).
        """
        result = parse_lilypond_to_data(r"\relative c' { ~g16 a2(p, themeA, >) a2~ a2(f) r4 }")
        events = result['parts']['Part 1']
        
        # Event 0: Grace note G
        assert events[0]['type'] == 'note'
        assert events[0]['step'] == 'G'
        assert events[0]['is_grace'] is True
        assert events[0]['ql'] == 0.0
        
        # Event 1: First A with modifiers (not tied)
        assert events[1]['type'] == 'note'
        assert events[1]['step'] == 'A'
        assert events[1]['ql'] == 2.0
        assert 'articulations' in events[1]
        assert 'accent' in events[1]['articulations']
        assert events[1]['dynamics'] == 'p'
        assert events[1]['tracker'] == 'themeA'
        
        # Event 2: Second and third A merged by tie (a2~ a2(f))
        assert events[2]['type'] == 'note'
        assert events[2]['step'] == 'A'
        assert events[2]['ql'] == 4.0  # 2.0 + 2.0 from tie merge
        # Note: dynamics='f' from a2(f) is lost in tie merge (correct behavior)
        
        # Event 3: Rest
        assert events[3]['type'] == 'rest'
        assert events[3]['ql'] == 1.0


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_dotted_rhythm_without_container(self):
        """Dotted rhythms still work without container."""
        parsed = parse_token("c4.")
        assert parsed.duration == '4.'
        assert parsed.articulations == []
    
    def test_dotted_rhythm_with_staccato_in_container(self):
        """Dotted rhythm with staccato in container (no conflict)."""
        parsed = parse_token("c4.(.)")
        assert parsed.duration == '4.'
        assert parsed.articulations == ['staccato']
    
    def test_note_without_container(self):
        """Notes without containers have empty modifier fields."""
        parsed = parse_token("c4")
        assert parsed.articulations == []
        assert parsed.dynamics == ''
        assert parsed.tracker == ''
    
    def test_multiple_notes_with_varying_modifiers(self):
        """Parse sequence with different modifier combinations."""
        result = parse_lilypond_to_data(r"\relative c' { c4(.) d4(p) e4(motif1) f4 }")
        events = result['parts']['Part 1']
        assert len(events) == 4
        
        # First note: staccato only
        assert 'articulations' in events[0]
        assert 'staccato' in events[0]['articulations']
        assert 'dynamics' not in events[0]
        
        # Second note: dynamic only
        assert 'dynamics' in events[1]
        assert events[1]['dynamics'] == 'p'
        assert 'articulations' not in events[1]
        
        # Third note: tracker only
        assert 'tracker' in events[2]
        assert events[2]['tracker'] == 'motif1'
        
        # Fourth note: no modifiers
        assert 'articulations' not in events[3]
        assert 'dynamics' not in events[3]
        assert 'tracker' not in events[3]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
