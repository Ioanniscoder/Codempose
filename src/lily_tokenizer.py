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
    # Step 1: SEQUENCE-BASED SPLITTING to separate preamble from note body
    # This prevents extracting letters from quoted strings like \tempo "Andante"
    body = snippet
    
    # Remove \relative c' { and closing }
    # Note: Need to match backslash-quote (\') and comma (,) after the note
    body = re.sub(r'\\relative\s+[a-g][\\\',]*\s*\{', '', body)
    body = re.sub(r'\}$', '', body)  # Remove trailing brace
    
    # Find where the NOTE SEQUENCE begins (not isolated letters in directives)
    # Look for the FIRST complete note word with a duration number
    # CRITICAL: Must match COMPLETE note words (longest first!) to avoid partial matches
    note_sequence_start = re.search(
        r'(?:heses|ceses|deses|feses|geses|beses|aisis|bisis|cisis|disis|eisis|fisis|gisis|hisis|eses|ases|isis|bmol|ees|fes|ges|ces|des|ais|bis|cis|dis|eis|fis|gis|his|as|bes|[a-g]|r)[\'`,]*\d+',
        body
    )
    
    if note_sequence_start:
        # Split: everything before this note is preamble (directives), from this note onwards is music
        split_pos = note_sequence_start.start()
        preamble = body[:split_pos]
        note_body = body[split_pos:]
    else:
        # Fallback: couldn't find note start, use whole body
        preamble = ""
        note_body = body
    
    # Step 2: Remove directives from preamble only (don't touch note_body)
    # This prevents false matches in the actual note content
    preamble = re.sub(r'\\time\s+\d+/\d+', '', preamble)
    preamble = re.sub(r'\\key\s+[a-g](?:es|is)?\s+\\(?:major|minor)', '', preamble)
    preamble = re.sub(r'\\clef\s+"?[a-z]+"?', '', preamble)
    preamble = re.sub(r'\\tempo\s+"[^"]+"\s+\d+\s*=\s*\d+', '', preamble)  # Quoted tempo
    preamble = re.sub(r'\\tempo\s+\d+\s*=\s*\d+', '', preamble)  # Numeric tempo
    preamble = re.sub(r'\\mark\s+\\markup\s*\{[^}]+\}', '', preamble)  # Markup
    
    # CRITICAL: Strip comments from note_body BEFORE tokenizing!
    # Comments start with % and continue to end of line
    note_body = re.sub(r'%.*$', '', note_body, flags=re.MULTILINE)
    
    # DON'T recombine - tokenize ONLY the note_body using an ALLOW-LIST approach
    # This ensures we ONLY extract actual musical tokens, not dynamics/articulations
    
    # Step 3: Tokenize the NOTE BODY using WORD-BASED INCLUSION-LIST
    #
    # STRATEGY: Note names are COMPLETE WORDS followed by SUFFIX
    # - WORD: Complete note name like "ceses", "ases", "cis", "d", "r"
    # - SUFFIX: Octaves + Duration + Modifiers + Expressions
    #
    # TOKEN STRUCTURE: [~]?[NOTE_WORD][OCTAVES][DURATION][MODIFIERS][EXPRESSIONS]
    # Example: ~ceses''4(., p)-.\p~
    #   - Note word: "ceses" 
    #   - Suffix: "''4(., p)-.\p~"
    #
    # CRITICAL: Longest note words FIRST to prevent partial matches!
    
    token_pattern = r'''
        # ===== CHORDS =====
        <[^>]+>                          # Chord notes: <c e g>
        \d*\.?                           # Duration
        (?:\([^)]*\))?                   # Optional modifier container
        (?:[-_.^+>()~]|\\[a-z]+)*        # Expressions
        |
        # ===== BAR LINES =====
        \|                               # Bar line
        |
        # ===== NOTES: [~]?[NOTE_WORD][SUFFIX] =====
        ~?                               # Optional grace prefix
        (?:
            # 5-character note WORDS (longest first!)
            heses|ceses|deses|feses|geses|beses|
            aisis|bisis|cisis|disis|eisis|fisis|gisis|hisis|
            
            # 4-character note WORDS
            eses|ases|isis|bmol|
            
            # 3-character note WORDS
            ees|fes|ges|ces|des|
            ais|bis|cis|dis|eis|fis|gis|his|
            
            # 2-character note WORDS  
            as|bes|
            
            # 1-character note WORDS (must NOT be followed by more letters!)
            [a-g](?![a-z])|r(?![a-z])    # Use negative lookahead to ensure complete word
        )
        # SUFFIX (everything after the note word):
        [',]*                            # Octave markers
        \d*\.?                           # Duration
        (?:\([^)]*\))?                   # Modifier container: (., p, themeA)
        (?:[-_.^+>()~]|\\[a-z]+)*        # LilyPond expressions: -., \p, ~, etc.
    '''
    
    tokens = re.findall(token_pattern, note_body, re.VERBOSE)
    
    # Filter out empty strings and whitespace
    tokens = [t.strip() for t in tokens if t.strip()]
    
    return tokens


# OLD TOKENIZATION CODE BELOW (keeping for tuplet support if needed)
def tokenize_body_OLD(snippet: str) -> List[str]:
    """
    OLD VERSION - kept for reference
    Break the musical body into individual tokens.
    
    This version tries to parse everything including dynamics/articulations,
    which causes problems with complex markup.
    """
    # Step 1: Remove directives
    body = snippet
    
    # Remove \relative c' { and closing }
    body = re.sub(r'\\relative\s+[a-g][\\\',]*\s*\{', '', body)
    
    # Remove other directives
    body = re.sub(r'\\time\s+\d+/\d+', '', body)
    body = re.sub(r'\\key\s+[a-g](?:es|is)?\s+\\(?:major|minor)', '', body)
    body = re.sub(r'\\clef\s+"?[a-z]+"?', '', body)
    body = re.sub(r'\\tempo\s+\d+\s*=\s*\d+', '', body)
    
    # Remove bare braces (but preserve chord delimiters like <c e g>)
    body = re.sub(r'(?<![<>])\{|\}(?![<>])', '', body)
    
    # Step 2: Tokenize
    # Pattern matches:
    # - Tuplets: \tuplet 3/2 { ... }
    # - Rests: r4, r8., r2
    # - Notes: c4, fis8, bmol2, c'4, d,,2
    # - Dotted durations: c4., r8.
    # - Chords: <c e g>4
    
    # FIRST: Extract tuplets as special tokens (they contain sub-tokens)
    # We'll mark them with a special prefix and extract them separately
    tuplet_tokens = []
    
    # Pattern 1: Standard LilyPond tuplets: \tuplet 3/2 { c8 d8 e8 }
    tuplet_pattern_standard = r'\\tuplet\s+(\d+)/(\d+)\s*\{([^}]+)\}'
    
    # Pattern 2: Custom shorthand tuplets: [c d e]8
    tuplet_pattern_shorthand = r'\[([^\]]+)\](\d+\.?)'
    
    def replace_tuplet_standard(match):
        """Replace standard LilyPond tuplet with placeholder and store it."""
        numerator = match.group(1)
        denominator = match.group(2)
        content = match.group(3).strip()
        # Store the tuplet with a unique ID
        idx = len(tuplet_tokens)
        tuplet_tokens.append({
            'type': 'tuplet',
            'numerator': numerator,
            'denominator': denominator,
            'content': content,
            'id': idx
        })
        # Return a placeholder token that won't interfere with normal tokenization
        return f' __TUPLET_{idx}__ '
    
    def replace_tuplet_shorthand(match):
        """Replace shorthand tuplet [a b c]8 with placeholder and store it."""
        content = match.group(1).strip()
        duration = match.group(2)
        
        # Count notes in the tuplet by splitting on whitespace
        note_tokens = content.split()
        num_notes = len(note_tokens)
        
        # Auto-calculate tuplet ratio based on note count
        # 3 notes → 3/2 (triplet), 4 notes → 4/3 (quadruplet), etc.
        if num_notes == 3:
            numerator, denominator = '3', '2'
        elif num_notes == 5:
            numerator, denominator = '5', '4'
        elif num_notes == 6:
            numerator, denominator = '6', '4'
        elif num_notes == 7:
            numerator, denominator = '7', '4'
        else:
            # Default: n notes in time of (n-1)
            numerator, denominator = str(num_notes), str(num_notes - 1)
        
        # Add duration to each note token if not already present
        notes_with_duration = []
        for note in note_tokens:
            # If note doesn't have a duration, append the bracket's duration
            if not re.search(r'\d', note):
                notes_with_duration.append(f"{note}{duration}")
            else:
                notes_with_duration.append(note)
        
        content_expanded = ' '.join(notes_with_duration)
        
        # Store the tuplet with a unique ID
        idx = len(tuplet_tokens)
        tuplet_tokens.append({
            'type': 'tuplet',
            'numerator': numerator,
            'denominator': denominator,
            'content': content_expanded,
            'id': idx,
            'shorthand': True  # Mark as shorthand for diagnostics
        })
        # Return a placeholder token that won't interfere with normal tokenization
        return f' __TUPLET_{idx}__ '
    
    # Replace both standard and shorthand tuplets with placeholders
    body = re.sub(tuplet_pattern_standard, replace_tuplet_standard, body)
    body = re.sub(tuplet_pattern_shorthand, replace_tuplet_shorthand, body)
    
    # Token pattern: 
    # - Note/rest letter: [a-gr]
    # - Optional accidental: (is|es|eses|isis|bmol|mol|#|b)?
    # - Optional octave markers: [',]*
    # - Optional duration: \d+\.?
    # OR
    # - Chord: <...>duration
    # OR
    # - Tuplet placeholder: __TUPLET_N__
    
    # Pattern explanation:
    # German notes need special handling:
    # - Standalone "es" (E-flat) and "as" (A-flat) are complete pitch names
    # - But "bes" (B-flat), "des" (D-flat) use -es as a suffix  
    # Strategy: Use word boundaries to detect standalone es/as vs. suffix es/as
    # GRACE NOTES: Prefix ~ indicates grace note (e.g., ~d16)
    # SUFFIX CONTAINER: () contains zero-duration modifiers (e.g., c4(., p, themeA))
    # TIES: Suffix ~ indicates tie (e.g., c4~) - comes AFTER suffix container
    
    token_pattern = r'''
        __TUPLET_\d+__                   # Tuplet placeholder
        |
        <[^>]+>\d*\.?(?:\([^)]*\))?~?        # Chords: <c e g>4(mods)~ with optional container + tie
        |
        ~?(?:heses|ces|eses|ases|des|fes)  # Grace note prefix + D/F/other + es (always combined)
        [',]*\d*\.?(?:\([^)]*\))?~?          # Octave markers, duration, suffix container, tie
        |
        ~?(?:es|as)                      # Grace note prefix + Standalone E-flat or A-flat
        (?![a-z])                        # NOT followed by another letter (negative lookahead)
        [',]*\d*\.?(?:\([^)]*\))?~?          # Octave markers, duration, suffix container, tie
        |
        ~?[a-gr]                         # Grace note prefix + Note/rest letter
        (?:isis|ises|eses|is|es|bmol|mol|\#|b)?   # Accidental suffix (including localized bmol/mol)
        [',]*\d*\.?(?:\([^)]*\))?~?          # Octave markers, duration, suffix container, tie
    '''
    
    tokens = re.findall(token_pattern, body, re.VERBOSE)
    
    # Filter out empty strings and whitespace
    tokens = [t.strip() for t in tokens if t.strip()]
    
    # Replace tuplet placeholders with actual tuplet data
    result_tokens = []
    for token in tokens:
        if token.startswith('__TUPLET_'):
            # Extract tuplet ID and replace with tuplet data
            tuplet_id = int(token.replace('__TUPLET_', '').replace('__', ''))
            result_tokens.append(tuplet_tokens[tuplet_id])
        else:
            result_tokens.append(token)
    
    return result_tokens


def split_complex_token(token: str) -> List[str]:
    """
    Split complex LilyPond tokens that contain multiple notes.
    
    This handles tokens like 'e4.( d8~ d4)' which are valid LilyPond
    but need to be split for our parser to process correctly.
    
    Strategy: Look for note-words (a-g, r) followed by duration/modifiers.
    
    Args:
        token: A single token that may contain multiple notes
    
    Returns:
        List of split tokens, or [token] if no split needed
    
    Examples:
        >>> split_complex_token('e4.( d8~ d4)')
        ['e4.(', 'd8~', 'd4)']
        >>> split_complex_token('c4')
        ['c4']
    """
    # Pattern to match note-words with their suffixes
    # Note-word: a-g or r (rest)
    # Suffix: octaves (', ,) + duration (4, 8.) + modifiers (~, -, .) + slurs/expressions
    note_pattern = r"([a-gr]['\,]*\d*\.?[~\-._^+>()\\a-z]*)"
    
    matches = re.findall(note_pattern, token)
    
    # If we found multiple note-words, split them
    if len(matches) > 1:
        # Verify these are actually separate notes (not just capturing fragments)
        # Each match should start with a note letter
        valid_matches = []
        for match in matches:
            if match and match[0] in 'abcdefgr':
                valid_matches.append(match)
        
        if len(valid_matches) > 1:
            return valid_matches
    
    # No split needed
    return [token]


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
    raw_tokens = tokenize_body(snippet)
    
    # Split complex tokens that contain multiple notes
    tokens = []
    for token in raw_tokens:
        split_tokens = split_complex_token(token)
        tokens.extend(split_tokens)
    
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
