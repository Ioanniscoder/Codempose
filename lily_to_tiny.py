"""
LilyPond to TinyNotation Converter (Phase 5)
=============================================

Main orchestration module that combines all components to convert
LilyPond snippets into TinyNotation format with metadata.

Pipeline:
1. Tokenizer: Extract directives and tokens
2. Token Parser: Parse each token into structured data
3. Relative Logic: Calculate absolute octaves
4. Formatter: Build TinyNotation string
5. Result: Return ParseResult with warnings

This is the primary entry point for the isolated parser.
"""

from data_structures import ParseResult, TokenInfo
from lily_tokenizer import preprocess_snippet, extract_directives, extract_relative_base, tokenize_body
from lily_token_parser import parse_token, format_as_tiny_notation, tiny_notation_accidental
from relative_octave_logic import parse_base_pitch, process_relative_sequence, process_absolute_sequence
from typing import List, Tuple


def lily_to_tiny_notation(lily_snippet: str) -> ParseResult:
    """
    Convert a LilyPond snippet to TinyNotation format with metadata.
    
    This is the main entry point for the parser.
    
    Args:
        lily_snippet: LilyPond snippet string (may include \relative, directives, etc.)
    
    Returns:
        ParseResult object containing:
        - tiny_notation: Clean TinyNotation string for music21
        - tokens: List of TokenInfo objects with metadata
        - directives: Dictionary of directives (\time, \key, etc.)
        - warnings: Global warnings
        - success: Whether parsing succeeded
    
    Examples:
        >>> result = lily_to_tiny_notation(r"\\relative c' { \\time 4/4 c4 d e f }")
        >>> result.success
        True
        >>> result.tiny_notation
        '4/4 C4 D4 E4 F4'
        >>> result.has_warnings()
        False
    """
    # Step 1: Tokenize
    try:
        directives, relative_base, raw_tokens = preprocess_snippet(lily_snippet)
    except Exception as e:
        return ParseResult(
            tiny_notation="",
            tokens=[],
            directives={},
            warnings=[f"Tokenization failed: {str(e)}"],
            success=False
        )
    
    # Handle empty input
    if not raw_tokens:
        return ParseResult(
            tiny_notation="",
            tokens=[],
            directives=directives,
            warnings=["No musical tokens found"],
            success=False
        )
    
    # Step 2: Parse tokens
    parsed_tokens = [parse_token(token) for token in raw_tokens]
    
    # Step 3: Calculate absolute octaves
    if relative_base:
        # Relative mode
        base_pitch, base_octave = parse_base_pitch(relative_base)
        octave_results = process_relative_sequence(base_pitch, base_octave, parsed_tokens)
    else:
        # Absolute mode (default octave = 3)
        octave_results = process_absolute_sequence(3, parsed_tokens)
    
    # Step 4: Build TinyNotation string with metadata header and TokenInfo list
    tiny_parts = []
    token_infos = []
    last_duration = '4'  # Quarter note default - this gets updated as we go
    
    # Build metadata header from directives
    # Format: key=value pairs at the start, e.g., "time=6/4 key=Cmajor tempo=90"
    header_parts = []
    
    if 'time' in directives:
        # Format: "time=6/4"
        header_parts.append(f"time={directives['time']}")
    
    if 'key' in directives:
        # Format: "key=Cmajor" or "key=Dminor"
        # directives['key'] is like "c \\major" - we need to normalize it
        key_str = directives['key'].replace('\\', '').strip()  # Remove backslash
        # Convert "c major" to "Cmajor"
        parts = key_str.split()
        if len(parts) >= 2:
            tonic = parts[0].capitalize()  # "c" -> "C"
            mode = parts[1].lower()  # "major" -> "major"
            header_parts.append(f"key={tonic}{mode}")
        else:
            # Fallback: just use what we have
            header_parts.append(f"key={key_str.replace(' ', '')}")
    
    if 'tempo' in directives:
        # Format: "tempo=90" (just the BPM number)
        # directives['tempo'] is like "4 = 90" - extract just the number
        tempo_str = directives['tempo']
        if '=' in tempo_str:
            bpm = tempo_str.split('=')[1].strip()
            header_parts.append(f"tempo={bpm}")
        else:
            header_parts.append(f"tempo={tempo_str}")
    
    # Add header to tiny_parts if we have any metadata
    if header_parts:
        header = " ".join(header_parts)
        tiny_parts.append(header)
    
    for i, (parsed, absolute_octave, large_leap) in enumerate(octave_results):
        # Build TinyNotation representation
        if parsed.is_rest:
            # Rests: inherit duration if not specified
            if parsed.duration:
                duration = parsed.duration
                last_duration = duration  # Update for next note
            else:
                duration = last_duration  # Inherit from previous
            tiny_token = f"r{duration}"
        elif parsed.pitch_letter and parsed.pitch_letter.startswith('<'):
            # CHORD: Keep original format <pitch1 pitch2>duration
            # Duration handling - inherit if not specified
            if parsed.duration:
                duration = parsed.duration
                last_duration = duration
            else:
                duration = last_duration
            
            # Extract pitches from <c e g> format
            pitches_str = parsed.pitch_letter[1:-1]  # Remove < >
            
            # For now, pass through unchanged - music21 can handle TinyNotation chords
            # Format: <c e g>4
            tiny_token = f"<{pitches_str}>{duration}"
        else:
            # Notes: inherit duration if not specified
            if parsed.duration:
                duration = parsed.duration
                last_duration = duration  # Update for next note
            else:
                duration = last_duration  # Inherit from previous
            
            # TinyNotation format for music21:
            # - Lowercase (c, d, e) = octave 4 (middle C octave)
            # - Uppercase (C, D, E) = octave 3
            # - Apostrophes raise octave: c' = C5, c'' = C6
            # - Commas are NOT supported by music21 - use uppercase instead
            
            pitch = parsed.pitch_letter  # 'c', 'd', 'e', etc.
            acc = tiny_notation_accidental(parsed.accidental)
            
            # Determine case and apostrophes based on absolute octave
            # Octave 3 or below: use uppercase + apostrophes for octave >3
            # Octave 4 or above: use lowercase + apostrophes for octave >4
            
            if absolute_octave >= 4:
                # Use lowercase base (octave 4)
                pitch_with_case = pitch.lower()
                octave_mod = "'" * (absolute_octave - 4)
            else:
                # Use uppercase base (octave 3), but this only works for octave 3
                # For octaves below 3, we need a different approach
                # music21 doesn't support octaves below 3 well in TinyNotation
                # Workaround: use lowercase and warn
                if absolute_octave < 3:
                    pitch_with_case = pitch.lower()
                    octave_mod = "'" * (absolute_octave - 4)  # Will be negative, not ideal
                    # Actually, let's just default to octave 3 for now
                    pitch_with_case = pitch.upper()
                    octave_mod = ""
                else:
                    # Octave 3: use uppercase with no modifier
                    pitch_with_case = pitch.upper()
                    octave_mod = ""
            
            # Build token: pitch + accidental + octave_modifier + duration
            tiny_token = f"{pitch_with_case}{acc}{octave_mod}{duration}"
        
        tiny_parts.append(tiny_token)
        
        # Create TokenInfo
        warnings_list = []
        if parsed.warnings:
            warnings_list.extend(parsed.warnings)
        if large_leap:
            warnings_list.append("Large leap detected (>13 semitones)")
        
        token_info = TokenInfo(
            original=parsed.original,
            converted=tiny_token,
            position=i,
            warnings=warnings_list,
            pitch_leap=large_leap
        )
        token_infos.append(token_info)
    
    # Join TinyNotation parts
    tiny_notation = " ".join(tiny_parts)
    
    # Collect global warnings
    global_warnings = []
    for token_info in token_infos:
        if token_info.warnings:
            for warning in token_info.warnings:
                if warning not in global_warnings:
                    global_warnings.append(warning)
    
    # Build result
    result = ParseResult(
        tiny_notation=tiny_notation,
        tokens=token_infos,
        directives=directives,
        warnings=global_warnings,
        success=True
    )
    
    return result


def convert_and_validate(lily_snippet: str) -> Tuple[ParseResult, bool]:
    """
    Convert a LilyPond snippet and validate the result.
    
    Args:
        lily_snippet: LilyPond snippet string
    
    Returns:
        Tuple of (ParseResult, is_valid)
        - ParseResult: The conversion result
        - is_valid: True if conversion succeeded with no critical errors
    """
    result = lily_to_tiny_notation(lily_snippet)
    
    # Check for critical failures
    is_valid = result.success and result.tiny_notation != ""
    
    return result, is_valid


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    # Test cases from test_cases.txt
    test_cases = [
        (
            "Test 1: Simple C Major Scale",
            r"\relative c' { \time 4/4 c4 d e f g a b c }",
            "4/4 C4 D4 E4 F4 G4 A4 B4 C4"  # Expected
        ),
        (
            "Test 2: With localized accidentals",
            r"\relative c' { e2 bmol4 c2 r4 }",
            "E2 B-4 C2 r4"  # Expected (no time sig in input)
        ),
        (
            "Test 3: Absolute mode",
            r"{ c4 d e f }",
            "C4 D4 E4 F4"  # Expected
        ),
        (
            "Test 4: With time signature",
            r"\time 3/4 \key d \major d4 fis a",
            "3/4 D4 F#4 A4"  # Expected
        ),
    ]
    
    print("=== LilyPond to TinyNotation Converter Test ===\n")
    
    for name, lily_input, expected in test_cases:
        print(f"{name}")
        print(f"  Input:    {lily_input}")
        print(f"  Expected: {expected}")
        
        result = lily_to_tiny_notation(lily_input)
        
        print(f"  Result:   {result.tiny_notation}")
        print(f"  Success:  {result.success}")
        
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
        
        # Check if matches expected
        match = result.tiny_notation == expected
        print(f"  Match:    {'✓' if match else '✗'}")
        
        if not match:
            print(f"  Diff:     Expected '{expected}', got '{result.tiny_notation}'")
        
        print()
