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
        is_tuplet: True if this is a tuplet group
        is_grace: True if this is a grace note (prefix ~)
        pitch_letter: Note letter (c, d, e, f, g, a, b) or None for rests
        accidental: Normalized accidental (sharp, flat, double-sharp, double-flat, or '')
        octave_markers: String of octave markers (e.g., "''" or ",,")
        duration: Duration string (e.g., "4", "8.", "2")
        has_tie: True if this note has a tie indicator (~)
        articulations: List of articulation names from suffix container
        dynamics: Dynamic marking from suffix container (p, f, mp, etc.)
        tracker: Tracking identifier from suffix container
        unparsed_suffix: Unrecognized trailing characters (for graceful degradation)
        warnings: List of warning messages
        tuplet_ratio: Tuple (numerator, denominator) for tuplets, e.g., (3, 2)
        tuplet_notes: List of ParsedToken objects for notes inside tuplet
        is_chord: True if this is a chord token
        chord_base_note: ParsedToken of the first note in the chord (for relative octave)
        chord_other_notes: List of raw note strings for other notes in chord
    """
    original: str
    is_rest: bool
    is_tuplet: bool = False
    is_grace: bool = False
    pitch_letter: Optional[str] = None
    accidental: str = ''
    octave_markers: str = ''
    duration: str = ''
    has_tie: bool = False
    articulations: list = None  # List of articulation names
    dynamics: str = ''  # Dynamic symbol (p, f, mp, etc.)
    tracker: str = ''  # Tracking identifier
    unparsed_suffix: str = ''  # Unrecognized trailing characters
    warnings: list = None
    tuplet_ratio: Optional[Tuple[int, int]] = None
    tuplet_notes: Optional[list] = None
    is_chord: bool = False
    chord_base_note: Optional['ParsedToken'] = None
    chord_other_notes: list = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.articulations is None:
            self.articulations = []
        if self.chord_other_notes is None:
            self.chord_other_notes = []


def parse_suffix_container(content: str) -> dict:
    """
    Parse content from suffix container (modifiers) syntax into classified components.
    
    The suffix container has the syntax: note(modifier1, modifier2, ...)
    where modifiers can be:
    - Articulations: . (staccato), - (tenuto), > (accent)
    - Dynamics: p, pp, ppp, f, ff, fff, mf, mp, <, >
    - Tracking: any other identifier (e.g., themeA, motif1)
    
    Args:
        content: The content between parentheses, e.g., "., p, themeA"
    
    Returns:
        Dictionary with keys:
        - 'articulations': list of articulation names (e.g., ['staccato', 'accent'])
        - 'dynamics': dynamic marking string (e.g., 'p', 'ff', '<')
        - 'tracker': tracking identifier string (e.g., 'themeA')
    
    Examples:
        >>> parse_suffix_container(".")
        {'articulations': ['staccato'], 'dynamics': '', 'tracker': ''}
        
        >>> parse_suffix_container("p")
        {'articulations': [], 'dynamics': 'p', 'tracker': ''}
        
        >>> parse_suffix_container("themeA, ., p")
        {'articulations': ['staccato'], 'dynamics': 'p', 'tracker': 'themeA'}
    """
    # Initialize result
    result = {
        'articulations': [],
        'dynamics': '',
        'tracker': ''
    }
    
    # Empty container
    if not content or content.strip() == '':
        return result
    
    # Split by comma and process each modifier
    modifiers = [m.strip() for m in content.split(',')]
    
    # Define articulation mapping
    articulation_map = {
        '.': 'staccato',
        '-': 'tenuto',
        '>': 'accent'
    }
    
    # Define dynamic symbols
    dynamic_symbols = {'p', 'pp', 'ppp', 'f', 'ff', 'fff', 'mf', 'mp', '<', '>'}
    
    for modifier in modifiers:
        if modifier in articulation_map:
            # Articulation
            result['articulations'].append(articulation_map[modifier])
        elif modifier in dynamic_symbols:
            # Dynamic (only keep the first one if multiple)
            if not result['dynamics']:
                result['dynamics'] = modifier
        else:
            # Tracking identifier (only keep the first one if multiple)
            if not result['tracker']:
                result['tracker'] = modifier
    
    return result


def parse_token(token) -> ParsedToken:
    """
    Parse a single LilyPond token into its components.
    
    Args:
        token: A single token string (e.g., "c4", "bmol8", "r2", "fis'4", "<c e g>4")
               OR a tuplet dictionary from the tokenizer
    
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
    
    # Check if it's a tuplet dictionary (from tokenizer)
    if isinstance(token, dict) and token.get('type') == 'tuplet':
        # Parse tuplet: \tuplet 3/2 { c8 d8 e8 }
        numerator = int(token['numerator'])
        denominator = int(token['denominator'])
        content = token['content']
        
        # Tokenize the tuplet content (simple tokenization - no nested tuplets yet)
        from lily_tokenizer import tokenize_body
        tuplet_body = f"{{ {content} }}"  # Wrap in braces for tokenizer
        inner_tokens = tokenize_body(tuplet_body)
        
        # Parse each inner token recursively
        tuplet_notes = [parse_token(t) for t in inner_tokens]
        
        return ParsedToken(
            original=f"\\tuplet {numerator}/{denominator} {{ {content} }}",
            is_rest=False,
            is_tuplet=True,
            pitch_letter=None,
            accidental='',
            octave_markers='',
            duration='',
            unparsed_suffix='',
            warnings=warnings,
            tuplet_ratio=(numerator, denominator),
            tuplet_notes=tuplet_notes
        )
    
    # Check if it's a chord: <c e g>4
    if token.startswith('<'):
        # Parse chord: extract pitches between < > and duration after >
        chord_match = re.match(r'<([^>]+)>(.*)$', token)
        if chord_match:
            pitches_str = chord_match.group(1)  # e.g., "c e g" or "c' ees g'"
            duration_and_suffix = chord_match.group(2) or ''
            
            # Split notes
            note_tokens = pitches_str.strip().split()
            
            if not note_tokens:
                warnings.append(f"Empty chord: {token}")
                return ParsedToken(
                    original=token,
                    is_rest=False,
                    unparsed_suffix='',
                    warnings=warnings
                )
            
            # Parse the FIRST note fully (recursively call parse_token)
            first_note_parsed = parse_token(note_tokens[0])
            
            # Store the rest as raw strings
            other_note_strings = note_tokens[1:]
            
            # Extract duration from the suffix
            duration_match = re.match(r'^(\d*\.?)', duration_and_suffix)
            duration = duration_match.group(1) if duration_match else ''
            
            return ParsedToken(
                original=token,
                is_rest=False,
                is_chord=True,
                chord_base_note=first_note_parsed,
                chord_other_notes=other_note_strings,
                duration=duration,
                unparsed_suffix='',
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
                unparsed_suffix='',
                warnings=warnings
            )
    
    # Check if it's a rest
    if token.startswith('r'):
        # Parse rest: r4, r8., r2 (ties on rests don't make musical sense but parse anyway)
        duration_match = re.match(r'r(\d*\.?)(~?)', token)
        duration = duration_match.group(1) if duration_match else ''
        tie_marker = duration_match.group(2) if duration_match else ''
        has_tie = (tie_marker == '~')
        
        if has_tie:
            warnings.append("Tie on rest has no musical effect")
        
        return ParsedToken(
            original=token,
            is_rest=True,
            pitch_letter=None,
            accidental='',
            octave_markers='',
            duration=duration,
            has_tie=has_tie,
            unparsed_suffix='',
            warnings=warnings
        )
    
    # Special case: Complete note names (German notes + localized names like bmol)
    # These are complete pitch names, not pitch + accidental
    # IMPORTANT: Check these BEFORE the generic regex to avoid ambiguity
    complete_note_names = {
        # Localized names (must come first to avoid b+mol parsing)
        'bmol': ('b', 'flat'),
        # German note names
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
    
    # Try to match complete note names first (prioritize longest matches)
    # Sort by length descending to match 'bmol' before 'b'
    sorted_note_names = sorted(complete_note_names.items(), key=lambda x: len(x[0]), reverse=True)
    
    for note_name, (base_pitch, accidental) in sorted_note_names:
        if token.startswith(note_name):
            # Extract everything after the complete note name
            remainder = token[len(note_name):]
            # Parse octave markers, duration, suffix container, and tie from remainder
            octave_duration_match = re.match(r"^([',]*)(\d*\.?)(?:\(([^)]*)\))?(~?)$", remainder)
            if octave_duration_match:
                octave_markers = octave_duration_match.group(1) or ''
                duration = octave_duration_match.group(2) or ''
                container_content = octave_duration_match.group(3) or ''
                tie_marker = octave_duration_match.group(4) or ''
                has_tie = (tie_marker == '~')
                
                # Parse suffix container if present
                articulations = []
                dynamics = ''
                tracker = ''
                if container_content:
                    parsed_container = parse_suffix_container(container_content)
                    articulations = parsed_container['articulations']
                    dynamics = parsed_container['dynamics']
                    tracker = parsed_container['tracker']
                
                return ParsedToken(
                    original=token,
                    is_rest=False,
                    is_grace=False,
                    pitch_letter=base_pitch,
                    accidental=accidental,
                    octave_markers=octave_markers,
                    duration=duration,
                    has_tie=has_tie,
                    articulations=articulations,
                    dynamics=dynamics,
                    tracker=tracker,
                    unparsed_suffix='',
                    warnings=warnings
                )
        # Check for grace note version: ~bmol, ~es, etc.
        grace_note_name = f"~{note_name}"
        if token.startswith(grace_note_name):
            # Extract everything after the grace note name
            remainder = token[len(grace_note_name):]
            # Parse octave markers, duration, suffix container, and tie from remainder
            octave_duration_match = re.match(r"^([',]*)(\d*\.?)(?:\(([^)]*)\))?(~?)$", remainder)
            if octave_duration_match:
                octave_markers = octave_duration_match.group(1) or ''
                duration = octave_duration_match.group(2) or ''
                container_content = octave_duration_match.group(3) or ''
                tie_marker = octave_duration_match.group(4) or ''
                has_tie = (tie_marker == '~')
                
                # Parse suffix container if present
                articulations = []
                dynamics = ''
                tracker = ''
                if container_content:
                    parsed_container = parse_suffix_container(container_content)
                    articulations = parsed_container['articulations']
                    dynamics = parsed_container['dynamics']
                    tracker = parsed_container['tracker']
                
                return ParsedToken(
                    original=token,
                    is_rest=False,
                    is_grace=True,
                    pitch_letter=base_pitch,
                    accidental=accidental,
                    octave_markers=octave_markers,
                    duration=duration,
                    has_tie=has_tie,
                    articulations=articulations,
                    dynamics=dynamics,
                    tracker=tracker,
                    unparsed_suffix='',
                    warnings=warnings
                )
    
    # Parse regular notes with BOTH syntaxes:
    # 1. LilyShorthand: c4(., p) - suffix container with modifiers
    # 2. Standard LilyPond: c4-.\p~ - articulations, dynamics, ties after duration
    # Pattern captures both: ~?[a-g](accidentals)?[',]*\d*\.? + (suffix_container)? + (lilypond_expressions)? + (unparsed)?
    # Note: Put longer accidentals first (eses, isis before es, is)
    # GRACEFUL DEGRADATION: Capture ANY trailing characters in group 8 for warning (don't fail)
    
    match = re.match(
        r'^(~?)([a-g])(eses|isis|bmol|mol|is|\#|b)?([' + r"',]*" + r')(\d*\.?)(?:\(([^)]*)\))?((?:[-_.^+>()~]|\\[a-z]+)*)(.*?)$',
        #                                                                                                                  ^^^^^ 
        #                                                                                                             Group 8: unparsed_suffix
        token
    )
    
    if not match:
        # Couldn't parse even basic structure - return error token
        warnings.append(f"Could not parse token: {token}")
        return ParsedToken(
            original=token,
            is_rest=False,
            is_grace=False,
            pitch_letter=None,
            accidental='',
            octave_markers='',
            duration='',
            has_tie=False,
            unparsed_suffix='',
            warnings=warnings
        )
    
    grace_prefix = match.group(1) or ''
    pitch_letter = match.group(2)
    raw_accidental = match.group(3) or ''
    octave_markers = match.group(4) or ''
    duration = match.group(5) or ''
    container_content = match.group(6) or ''  # Content inside (...) - LilyShorthand
    lily_expressions = match.group(7) or ''   # Standard LilyPond expressions: -., \p, ~, (, etc.
    unparsed_suffix = match.group(8) or ''    # GRACEFUL DEGRADATION: Unrecognized trailing chars
    
    is_grace = (grace_prefix == '~')
    
    # Normalize accidental
    accidental = normalize_accidental(raw_accidental)
    
    # Check for localized accidentals
    if is_localized_accidental(raw_accidental):
        warnings.append(f"Localized accidental: {raw_accidental}")
    
    # GRACEFUL DEGRADATION: Warn if unparsed suffix detected (but continue)
    if unparsed_suffix:
        warnings.append(f"Unrecognized LilyPond syntax attached: '{unparsed_suffix}'")
        warnings.append(f"ℹ️  Core note/duration parsed successfully: {pitch_letter}{raw_accidental}{octave_markers}{duration}")
        warnings.append(f"⚠️  Unparsed expressions may be ignored during transformation")
    
    # Parse BOTH LilyShorthand suffix container AND standard LilyPond expressions
    articulations = []
    dynamics = ''
    tracker = ''
    has_tie = False
    
    # 1. Parse LilyShorthand suffix container if present: c4(., p)
    if container_content:
        parsed_container = parse_suffix_container(container_content)
        articulations = parsed_container['articulations']
        dynamics = parsed_container['dynamics']
        tracker = parsed_container['tracker']
    
    # 2. Parse standard LilyPond expressions if present: c4-.\p~
    if lily_expressions:
        # Check for tie
        if '~' in lily_expressions:
            has_tie = True
        
        # Extract articulations: -., ->, -^, etc.
        articulation_map = {
            '-.': 'staccato',
            '-^': 'marcato',
            '->': 'accent',
            '--': 'tenuto',
            '_': 'portato',
        }
        for pattern, name in articulation_map.items():
            if pattern in lily_expressions:
                if name not in articulations:  # Don't duplicate if already in suffix container
                    articulations.append(name)
        
        # Extract dynamics: \p, \f, \mp, \ff, etc.
        dynamic_matches = re.findall(r'\\(p{1,3}|f{1,3}|mp|mf|fp|sf|sff)', lily_expressions)
        if dynamic_matches and not dynamics:  # Use first dynamic found (don't override suffix container)
            dynamics = dynamic_matches[0]
    
    return ParsedToken(
        original=token,
        is_rest=False,
        is_grace=is_grace,
        pitch_letter=pitch_letter,
        accidental=accidental,
        octave_markers=octave_markers,
        duration=duration,
        has_tie=has_tie,
        articulations=articulations,
        dynamics=dynamics,
        tracker=tracker,
        unparsed_suffix=unparsed_suffix,
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
    
    # MIDI note number = base + accidental + ((octave + 1) * 12)
    # This formula compensates for the octave numbering system used elsewhere
    # Middle C (C4) = 60 = 0 + 0 + ((4+1) * 12) = 60 ✓
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
    # Handle tuplets - TinyNotation doesn't have native tuplet support
    # Return a placeholder or skip
    if hasattr(parsed, 'is_tuplet') and parsed.is_tuplet:
        # Tuplets are handled separately in the full pipeline
        # Return a marker for debugging purposes
        return f"[tuplet:{parsed.tuplet_ratio[0]}/{parsed.tuplet_ratio[1]}]"
    
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
