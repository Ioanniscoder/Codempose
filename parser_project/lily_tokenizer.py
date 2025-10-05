"""
LilyPond Tokenizer (Phase 2)
=============================

Breaks down a LilyPond snippet into tokens for parsing.

Responsibilities:
1. Extract directives (\time, \key, \clef, etc.)
2. Extract \relative base pitch
3. Tokenize the musical body into individual elements

This module produces raw tokens; it does NOT interpret them.
"""

import re
from typing import Dict, Optional, List, Tuple


def extract_directives(snippet: str) -> Dict[str, str]:
    """
    Extract LilyPond directives from the snippet.
    
    Args:
        snippet: Raw LilyPond string
    
    Returns:
        Dictionary of directives found (e.g., {'time': '4/4', 'key': 'c \\major'})
    
    Examples:
        >>> extract_directives(r"\\time 3/4 \\key d \\major c4 d e")
        {'time': '3/4', 'key': 'd \\\\major'}
    """
    directives = {}
    
    # Extract time signature: \time 4/4
    time_match = re.search(r'\\time\s+(\d+/\d+)', snippet)
    if time_match:
        directives['time'] = time_match.group(1)
    
    # Extract key signature: \key c \major
    key_match = re.search(r'\\key\s+([a-g](?:es|is)?)\s+\\(major|minor)', snippet)
    if key_match:
        directives['key'] = f"{key_match.group(1)} \\{key_match.group(2)}"
    
    # Extract clef: \clef "treble" or \clef treble
    clef_match = re.search(r'\\clef\s+"?([a-z]+)"?', snippet)
    if clef_match:
        directives['clef'] = clef_match.group(1)
    
    # Extract tempo: \tempo 4 = 120
    tempo_match = re.search(r'\\tempo\s+(\d+)\s*=\s*(\d+)', snippet)
    if tempo_match:
        directives['tempo'] = f"{tempo_match.group(1)} = {tempo_match.group(2)}"
    
    return directives


def extract_relative_base(snippet: str) -> Optional[str]:
    """
    Extract the base pitch from a \\relative directive.
    
    Args:
        snippet: Raw LilyPond string
    
    Returns:
        Base pitch string (e.g., "c'") or None if not in relative mode
    
    Examples:
        >>> extract_relative_base(r"\\relative c' { c4 d e }")
        "c'"
        >>> extract_relative_base(r"{ c4 d e }")
        None
    """
    # Match: \relative c' { ... } or \relative c'' { ... }
    match = re.search(r'\\relative\s+([a-g][\'|,]*)', snippet)
    if match:
        return match.group(1)
    return None


def tokenize_body(snippet: str) -> List[str]:
    """
    Break the musical body into individual tokens.
    
    Args:
        snippet: Raw LilyPond string (directives can be present but will be filtered)
    
    Returns:
        List of token strings (notes, rests, chords, etc.)
    
    Examples:
        >>> tokenize_body(r"\\relative c' { c4 d e f }")
        ['c4', 'd', 'e', 'f']
        >>> tokenize_body(r"e2 bmol4 c2 r4")
        ['e2', 'bmol4', 'c2', 'r4']
    
    Notes:
        - Strips directives (\time, \key, etc.)
        - Removes braces, \relative, and structural markers
        - Preserves accidentals (fis, bes, bmol, f#, etc.)
        - Preserves durations (4, 8, 16, 2., etc.)
        - Preserves octave markers (', ,)
    """
    # Step 1: Remove directives
    body = snippet
    
    # Remove \relative c' { and closing }
    body = re.sub(r'\\relative\s+[a-g][\'|,]*\s*\{', '', body)
    
    # Remove other directives
    body = re.sub(r'\\time\s+\d+/\d+', '', body)
    body = re.sub(r'\\key\s+[a-g](?:es|is)?\s+\\(?:major|minor)', '', body)
    body = re.sub(r'\\clef\s+"?[a-z]+"?', '', body)
    body = re.sub(r'\\tempo\s+\d+\s*=\s*\d+', '', body)
    
    # Remove bare braces (but preserve chord delimiters like <c e g>)
    body = re.sub(r'(?<![<>])\{|\}(?![<>])', '', body)
    
    # Step 2: Tokenize
    # Pattern matches:
    # - Rests: r4, r8., r2
    # - Notes: c4, fis8, bmol2, c'4, d,,2
    # - Dotted durations: c4., r8.
    # - Chords: <c e g>4
    
    # Token pattern: 
    # - Note/rest letter: [a-gr]
    # - Optional accidental: (is|es|eses|isis|bmol|mol|#|b)?
    # - Optional octave markers: [',]*
    # - Optional duration: \d+\.?
    # OR
    # - Chord: <...>duration
    
    # Pattern explanation:
    # German notes need special handling:
    # - Standalone "es" (E-flat) and "as" (A-flat) are complete pitch names
    # - But "bes" (B-flat), "des" (D-flat) use -es as a suffix  
    # Strategy: Use word boundaries to detect standalone es/as vs. suffix es/as
    
    token_pattern = r'''
        <[^>]+>\d*\.?                    # Chords: <c e g>4
        |
        (?:heses|ces|eses|ases|des|fes)  # D/F/other + es (always combined)
        [',]*\d*\.?                      # Octave markers and duration
        |
        (?:es|as)                        # Standalone E-flat or A-flat
        (?![a-z])                        # NOT followed by another letter (negative lookahead)
        [',]*\d*\.?                      # Octave markers and duration
        |
        [a-gr]                           # Note/rest letter
        (?:isis|ises|eses|is|es|bmol|mol|\#|b)?   # Accidental suffix (including localized bmol/mol)
        [',]*\d*\.?                      # Octave markers and duration
    '''
    
    tokens = re.findall(token_pattern, body, re.VERBOSE)
    
    # Filter out empty strings and whitespace
    tokens = [t.strip() for t in tokens if t.strip()]
    
    return tokens


def preprocess_snippet(snippet: str) -> Tuple[Dict[str, str], Optional[str], List[str]]:
    """
    Complete preprocessing pipeline for a LilyPond snippet.
    
    Args:
        snippet: Raw LilyPond string
    
    Returns:
        Tuple of (directives, relative_base, tokens)
    
    Examples:
        >>> preprocess_snippet(r"\\relative c' { \\time 4/4 c4 d e f }")
        ({'time': '4/4'}, "c'", ['c4', 'd', 'e', 'f'])
    """
    directives = extract_directives(snippet)
    relative_base = extract_relative_base(snippet)
    tokens = tokenize_body(snippet)
    
    return directives, relative_base, tokens


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

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


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    # Test cases
    test_snippets = [
        r"\relative c' { \time 4/4 c4 d e f }",
        r"\relative c' { e2 bmol4 c2 r4 }",
        r"\time 3/4 \key d \major d4 fis a",
        r"{ c4 d e f }",  # No relative
        r"\relative c'' { c8 d e f g a b c }",
    ]
    
    print("=== LilyPond Tokenizer Test ===\n")
    
    for i, snippet in enumerate(test_snippets, 1):
        print(f"Test {i}: {snippet}")
        directives, relative_base, tokens = preprocess_snippet(snippet)
        print(f"  Directives: {directives}")
        print(f"  Relative Base: {relative_base}")
        print(f"  Tokens: {tokens}")
        print()
