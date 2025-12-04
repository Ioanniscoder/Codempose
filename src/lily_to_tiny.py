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

import re
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
    
    # Step 2: Parse tokens and flatten tuplets for octave resolution
    # Tuplets are expanded: [d e f]8 → [d8, e8, f8] for pitch sequence
    parsed_tokens = []
    tuplet_map = {}  # Track which tokens belong to tuplets for later reconstruction
    
    for token in raw_tokens:
        parsed = parse_token(token)
        if parsed.is_tuplet and parsed.tuplet_notes:
            # Flatten tuplet: add its notes to the sequence
            tuplet_start_idx = len(parsed_tokens)
            for note_token in parsed.tuplet_notes:
                parsed_tokens.append(note_token)
            tuplet_end_idx = len(parsed_tokens)
            # Remember this tuplet's position and content
            tuplet_map[tuplet_start_idx] = {
                'end_idx': tuplet_end_idx,
                'ratio': parsed.tuplet_ratio,
                'original': parsed.original
            }
        else:
            parsed_tokens.append(parsed)
    
    # Step 3: Calculate absolute octaves (tuplet notes are now flattened)
    if relative_base:
        # Relative mode
        base_pitch, base_octave = parse_base_pitch(relative_base)
        octave_results = process_relative_sequence(base_pitch, base_octave, parsed_tokens)
    else:
        # Absolute mode (default octave = 3)
        octave_results = process_absolute_sequence(3, parsed_tokens)
    
    # Step 4: Build TinyNotation string and TokenInfo list (reconstruct tuplets)
    tiny_parts = []
    token_infos = []
    last_duration = '4'  # Quarter note default - this gets updated as we go
    i = 0  # Manual index for tuplet handling
    
    # Add time signature if present
    if 'time' in directives:
        tiny_parts.append(directives['time'])
    
    while i < len(octave_results):
        # Check if this position starts a tuplet
        if i in tuplet_map:
            tuplet_info = tuplet_map[i]
            end_idx = tuplet_info['end_idx']
            numerator, denominator = tuplet_info['ratio']
            
            # Build tuplet with resolved pitches: [d4 e4 f4]8
            tuplet_notes = []
            for j in range(i, end_idx):
                parsed, absolute_octave, large_leap = octave_results[j]
                
                # Format note with resolved octave
                pitch = parsed.pitch_letter
                acc = tiny_notation_accidental(parsed.accidental)
                octave_diff = absolute_octave - 4
                if octave_diff > 0:
                    octave_mod = "'" * octave_diff
                elif octave_diff < 0:
                    octave_mod = "," * abs(octave_diff)
                else:
                    octave_mod = ""
                
                # Note: duration is from the bracket, not individual notes
                tuplet_notes.append(f"{pitch}{acc}{octave_mod}")
            
            # Extract duration from tuplet content or original
            # Original stores the expanded LilyPond format: \tuplet 3/2 { d8 e8 f8 }
            orig = tuplet_info['original']
            
            if isinstance(orig, dict) and 'content' in orig:
                # Dict format: extract from content "d8 e8 f8" → "8"
                content = orig['content']
                duration_match = re.search(r'(\d+\.?)', content)
                duration = duration_match.group(1) if duration_match else '4'
            elif isinstance(orig, str):
                # String format: extract from expanded "\tuplet 3/2 { d8 e8 f8 }" → "8"
                # Look for first duration number inside the braces
                duration_match = re.search(r'\{\s*[a-gr]\d*\'*,*(\d+\.?)', orig)
                duration = duration_match.group(1) if duration_match else '4'
            else:
                duration = '4'
            last_duration = duration
            
            # Build tuplet token: [d4 e4 f4]8
            tiny_token = f"[{' '.join(tuplet_notes)}]{duration}"
            tiny_parts.append(tiny_token)
            
            # Create single TokenInfo for the entire tuplet
            token_info = TokenInfo(
                original=tuplet_info['original'],
                converted=tiny_token,
                position=i,
                warnings=[f"Tuplet {numerator}/{denominator}"],
                pitch_leap=False
            )
            token_infos.append(token_info)
            
            # Skip to after the tuplet
            i = end_idx
            continue
        
        # Regular note/rest/chord processing
        parsed, absolute_octave, large_leap = octave_results[i]
        
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
        elif parsed.pitch_letter is None:
            # Barline or unparseable token - skip in TinyNotation output
            # BUT: Add barlines to TokenInfo list so parser can track bar boundaries
            if parsed.original == '|':
                token_info = TokenInfo(
                    original='|',
                    converted='|',  # Keep original barline marker
                    position=i,
                    warnings=[],
                    pitch_leap=False
                )
                token_infos.append(token_info)
            i += 1
            continue
        else:
            # Notes: inherit duration if not specified
            if parsed.duration:
                duration = parsed.duration
                last_duration = duration  # Update for next note
            else:
                duration = last_duration  # Inherit from previous
            
            # TinyNotation format uses lowercase letters with octave modifiers
            # c = C4 (middle C octave)
            # c' = C5, c'' = C6, c''' = C7
            # c, = C3, c,, = C2
            pitch = parsed.pitch_letter  # Keep lowercase!
            acc = tiny_notation_accidental(parsed.accidental)
            
            # Calculate octave modifier relative to base octave 4
            octave_diff = absolute_octave - 4
            if octave_diff > 0:
                octave_mod = "'" * octave_diff
            elif octave_diff < 0:
                octave_mod = "," * abs(octave_diff)
            else:
                octave_mod = ""
            
            # Build token: pitch + accidental + octave_modifier + duration
            tiny_token = f"{pitch}{acc}{octave_mod}{duration}"
        
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
        
        i += 1  # Move to next token
    
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
