"""
LilyPond Token Parser (Phase 3)
================================

Parses individual LilyPond tokens into structured data.

Responsibilities:
1. Parse pitch (note letter)
2. Parse accidentals (is, es, bmol, #, b, etc.)
3. Parse octave markers (' and ,)
4. Parse durations (4, 8., 16, etc.)
5. Detect warnings (localized accidentals)

This module interprets tokens; it does NOT handle relative octave logic.
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedToken:
    """
    Structured representation of a parsed LilyPond token.
    
    Attributes:
        original: The original token string
        is_rest: True if this is a rest
        pitch_letter: Note letter (c, d, e, f, g, a, b) or None for rests
        accidental: Normalized accidental (sharp, flat, double-sharp, double-flat, or '')
        octave_markers: String of octave markers (e.g., "''" or ",,")
        duration: Duration string (e.g., "4", "8.", "2")
        warnings: List of warning messages
    """
    original: str
    is_rest: bool
    pitch_letter: Optional[str]
    accidental: str
    octave_markers: str
    duration: str
    warnings: list


def parse_token(token: str) -> ParsedToken:
    """
    Parse a single LilyPond token into its components.
    
    Args:
        token: A single token string (e.g., "c4", "bmol8", "r2", "fis'4", "<c e g>4")
    
    Returns:
        ParsedToken object with structured data
    
    Examples:
        >>> parse_token("c4")
        ParsedToken(original='c4', is_rest=False, pitch_letter='c', 
                    accidental='', octave_markers='', duration='4', warnings=[])
        
        >>> parse_token("bmol8")
        ParsedToken(original='bmol8', is_rest=False, pitch_letter='b', 
                    accidental='flat', octave_markers='', duration='8', 
                    warnings=['Localized accidental: bmol'])
        
        >>> parse_token("r2")
        ParsedToken(original='r2', is_rest=True, pitch_letter=None, 
                    accidental='', octave_markers='', duration='2', warnings=[])
        
        >>> parse_token("<c e g>4")
        ParsedToken(original='<c e g>4', is_rest=False, pitch_letter='<c e g>', 
                    accidental='', octave_markers='', duration='4', warnings=[])
    """
    warnings = []
    
    # Check if it's a chord: <c e g>4
    if token.startswith('<'):
        # Parse chord: extract pitches between < > and duration after >
        chord_match = re.match(r'<([^>]+)>(\d*\.?)', token)
        if chord_match:
            pitches_str = chord_match.group(1)  # e.g., "c e g" or "c' ees g'"
            duration = chord_match.group(2) or ''
            
            # Store the full chord specification as "pitch_letter"
            # This is a special case - the consumer will need to handle it
            return ParsedToken(
                original=token,
                is_rest=False,
                pitch_letter=f"<{pitches_str}>",  # Mark as chord
                accidental='',  # Chords don't have a single accidental
                octave_markers='',  # Chords don't have single octave markers
                duration=duration,
                warnings=warnings
            )
        else:
            warnings.append(f"Malformed chord token: {token}")
            return ParsedToken(
                original=token,
                is_rest=False,
                pitch_letter=None,
                accidental='',
                octave_markers='',
                duration='',
                warnings=warnings
            )
    
    # Check if it's a rest
    if token.startswith('r'):
        # Parse rest: r4, r8., r2
        duration_match = re.match(r'r(\d*\.?)', token)
        duration = duration_match.group(1) if duration_match else ''
        
        return ParsedToken(
            original=token,
            is_rest=True,
            pitch_letter=None,
            accidental='',
            octave_markers='',
            duration=duration,
            warnings=warnings
        )
    
    # Special case: German note names (es, as, ases, eses, etc.)
    # These are complete pitch names, not pitch + accidental
    german_notes = {
        'eses': ('e', 'double-flat'),
        'es': ('e', 'flat'),
        'ases': ('a', 'double-flat'),
        'as': ('a', 'flat'),
        'bes': ('b', 'flat'),
        'ces': ('c', 'flat'),
        'des': ('d', 'flat'),
        'fes': ('f', 'flat'),
        'ges': ('g', 'flat'),
    }
    
    # Try to match German note names first
    for german_name, (base_pitch, accidental) in german_notes.items():
        if token.startswith(german_name):
            # Extract everything after the German note name
            remainder = token[len(german_name):]
            # Parse octave markers and duration from remainder
            octave_duration_match = re.match(r"^([',]*)(\d*\.?)$", remainder)
            if octave_duration_match:
                octave_markers = octave_duration_match.group(1) or ''
                duration = octave_duration_match.group(2) or ''
                
                return ParsedToken(
                    original=token,
                    is_rest=False,
                    pitch_letter=base_pitch,
                    accidental=accidental,
                    octave_markers=octave_markers,
                    duration=duration,
                    warnings=warnings
                )
    
    # Parse regular notes: letter + optional accidental + optional octave + optional duration
    # Pattern: [a-gcdf](accidentals)?[',]*\d*\.?
    # Note: Put longer accidentals first (eses, isis before es, is)
    
    match = re.match(
        r'^([a-g])(eses|isis|bmol|mol|is|\#|b)?([' + r"',]*" + r')(\d*\.?)$',
        token
    )
    
    if not match:
        # Couldn't parse - return error token
        warnings.append(f"Could not parse token: {token}")
        return ParsedToken(
            original=token,
            is_rest=False,
            pitch_letter=None,
            accidental='',
            octave_markers='',
            duration='',
            warnings=warnings
        )
    
    pitch_letter = match.group(1)
    raw_accidental = match.group(2) or ''
    octave_markers = match.group(3) or ''
    duration = match.group(4) or ''
    
    # Normalize accidental
    accidental = normalize_accidental(raw_accidental)
    
    # Check for localized accidentals
    if is_localized_accidental(raw_accidental):
        warnings.append(f"Localized accidental: {raw_accidental}")
    
    return ParsedToken(
        original=token,
        is_rest=False,
        pitch_letter=pitch_letter,
        accidental=accidental,
        octave_markers=octave_markers,
        duration=duration,
        warnings=warnings
    )


def normalize_accidental(accidental: str) -> str:
    """
    Normalize various accidental spellings to canonical form.
    
    Args:
        accidental: Raw accidental string (is, #, bmol, b, etc.)
    
    Returns:
        Normalized form: 'sharp', 'flat', 'double-sharp', 'double-flat', or ''
    
    Examples:
        >>> normalize_accidental('is')
        'sharp'
        >>> normalize_accidental('bmol')
        'flat'
        >>> normalize_accidental('#')
        'sharp'
    """
    accidental_map = {
        'is': 'sharp',
        '#': 'sharp',
        'es': 'flat',
        'b': 'flat',
        'bmol': 'flat',
        'mol': 'flat',
        'isis': 'double-sharp',
        'eses': 'double-flat',
    }
    
    return accidental_map.get(accidental, '')


def is_localized_accidental(accidental: str) -> bool:
    """
    Check if an accidental uses localized (non-standard) syntax.
    
    Args:
        accidental: Raw accidental string
    
    Returns:
        True if localized (bmol, mol), False otherwise
    
    Examples:
        >>> is_localized_accidental('bmol')
        True
        >>> is_localized_accidental('is')
        False
    """
    localized = {'bmol', 'mol'}
    return accidental in localized


def pitch_to_midi(pitch_letter: str, accidental: str, octave: int) -> int:
    """
    Convert pitch information to MIDI note number.
    
    Args:
        pitch_letter: Note letter (c, d, e, f, g, a, b)
        accidental: Normalized accidental ('sharp', 'flat', etc.)
        octave: Octave number (4 = middle C octave)
    
    Returns:
        MIDI note number (0-127)
    
    Examples:
        >>> pitch_to_midi('c', '', 4)
        60  # Middle C
        >>> pitch_to_midi('a', '', 4)
        69  # A440
        >>> pitch_to_midi('c', 'sharp', 4)
        61  # C#4
    """
    # Base MIDI numbers for each pitch in octave 0
    pitch_base = {
        'c': 0, 'd': 2, 'e': 4, 'f': 5,
        'g': 7, 'a': 9, 'b': 11
    }
    
    # Accidental offsets
    accidental_offset = {
        '': 0,
        'sharp': 1,
        'flat': -1,
        'double-sharp': 2,
        'double-flat': -2,
    }
    
    base = pitch_base.get(pitch_letter, 0)
    acc_offset = accidental_offset.get(accidental, 0)
    
    # MIDI note number = base + accidental + (octave * 12)
    # Middle C (C4) = 60
    midi = base + acc_offset + ((octave + 1) * 12)
    
    return midi


def tiny_notation_accidental(accidental: str) -> str:
    """
    Convert normalized accidental to TinyNotation format.
    
    Args:
        accidental: Normalized accidental ('sharp', 'flat', etc.)
    
    Returns:
        TinyNotation accidental string ('#', '-', '##', '--', '')
    
    Examples:
        >>> tiny_notation_accidental('sharp')
        '#'
        >>> tiny_notation_accidental('flat')
        '-'
        >>> tiny_notation_accidental('')
        ''
    """
    tiny_map = {
        'sharp': '#',
        'flat': '-',
        'double-sharp': '##',
        'double-flat': '--',
        '': ''
    }
    
    return tiny_map.get(accidental, '')


def format_as_tiny_notation(parsed: ParsedToken, octave: int, default_duration: str = '4') -> str:
    """
    Format a ParsedToken as TinyNotation string.
    
    Args:
        parsed: ParsedToken object
        octave: Absolute octave number for this note
        default_duration: Duration to use if none specified
    
    Returns:
        TinyNotation string (e.g., "C4", "B-4", "r2")
        Format is: <PITCH><ACCIDENTAL><OCTAVE> for notes, r<DURATION> for rests
        Note: In TinyNotation, the octave and duration are separate concepts
    
    Examples:
        >>> token = parse_token("c4")
        >>> format_as_tiny_notation(token, 4, '4')
        'C4 4'  # C in octave 4, quarter note duration
        
        >>> token = parse_token("bmol8")
        >>> format_as_tiny_notation(token, 4, '4')
        'B-4 8'  # B-flat in octave 4, eighth note duration
    """
    if parsed.is_rest:
        duration = parsed.duration or default_duration
        return f"r{duration}"
    
    # Build TinyNotation note: <PITCH><ACCIDENTAL><OCTAVE> <DURATION>
    # Example: "C4 4" means C in octave 4, quarter note duration
    pitch_upper = parsed.pitch_letter.upper()
    accidental_str = tiny_notation_accidental(parsed.accidental)
    duration = parsed.duration or default_duration
    
    # Return pitch with octave, followed by space and duration
    return f"{pitch_upper}{accidental_str}{octave} {duration}"


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    # Test cases
    test_tokens = [
        "c4",
        "d",
        "fis8",
        "bmol4",
        "r2",
        "e'4",
        "g,,8.",
        "c#4",
        "bes2",
    ]
    
    print("=== LilyPond Token Parser Test ===\n")
    
    for token in test_tokens:
        parsed = parse_token(token)
        print(f"Token: {token}")
        print(f"  Parsed: {parsed}")
        
        if not parsed.is_rest:
            # Test formatting (using octave 4 as example)
            tiny = format_as_tiny_notation(parsed, octave=4)
            print(f"  TinyNotation (octave 4): {tiny}")
            
            # Test MIDI conversion
            midi = pitch_to_midi(parsed.pitch_letter, parsed.accidental, 4)
            print(f"  MIDI: {midi}")
        else:
            tiny = format_as_tiny_notation(parsed, octave=4)
            print(f"  TinyNotation: {tiny}")
        
        if parsed.warnings:
            print(f"  ⚠️  Warnings: {parsed.warnings}")
        
        print()
