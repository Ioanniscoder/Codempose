import re
import music21
from music_data import extract_data_from_part
from lily_to_tiny import lily_to_tiny_notation


def _parse_tiny_pitch(pitch_str: str) -> music21.pitch.Pitch:
    """
    Parse a TinyNotation pitch string into a music21.Pitch object.
    
    Examples: 'c', 'f#', "g'", 'b-', "c,,"
    """
    # Pattern: letter + optional accidental + optional octave markers
    match = re.match(r"([a-g])([#\-]*)([',]*)", pitch_str.lower())
    if not match:
        raise ValueError(f"Cannot parse pitch: {pitch_str}")
    
    step = match.group(1).upper()
    accidentals = match.group(2)
    octave_marks = match.group(3)
    
    # Calculate octave (base = 4 for TinyNotation)
    octave = 4 + octave_marks.count("'") - octave_marks.count(",")
    
    # Create pitch
    pitch = music21.pitch.Pitch(step)
    pitch.octave = octave
    
    # Apply accidentals
    if '#' in accidentals:
        pitch.accidental = music21.pitch.Accidental('sharp')
    elif '-' in accidentals:
        pitch.accidental = music21.pitch.Accidental('flat')
    
    return pitch


def _parse_tiny_duration(dur_str: str) -> float:
    """
    Parse a TinyNotation duration string into quarter lengths.
    
    Examples: '4' → 1.0, '2' → 2.0, '8' → 0.5, '4.' → 1.5
    """
    if not dur_str:
        return 1.0  # Default quarter note
    
    # Check for dots
    has_dot = '.' in dur_str
    base_dur = dur_str.replace('.', '')
    
    if not base_dur.isdigit():
        return 1.0  # Default
    
    # Quarter length = 4.0 / duration_number
    ql = 4.0 / float(base_dur)
    
    # Dotted durations are 1.5x base
    if has_dot:
        ql *= 1.5
    
    return ql


def _parse_duration_to_ql(duration_str: str) -> float:
    """Convert LilyPond duration string to quarterLength."""
    if not duration_str:
        return 1.0  # Default quarter note
    
    # Extract base duration and dot
    match = re.match(r'(\d+)(\.{0,3})', duration_str)
    if not match:
        return 1.0
    
    base = int(match.group(1))
    dots = len(match.group(2))
    
    # Base quarter length (4 = quarter note = 1.0)
    ql = 4.0 / base
    
    # Add dotted duration
    for _ in range(dots):
        ql += ql / 2
    
    return ql


def _accidental_to_alter(accidental: str) -> int:
    """Convert normalized accidental string to MIDI alter value."""
    mapping = {
        '': 0,
        'sharp': 1,
        'flat': -1,
        'double-sharp': 2,
        'double-flat': -2,
    }
    return mapping.get(accidental, 0)


def _extract_octave_from_tiny(tiny_token: str) -> int:
    """Extract octave number from TinyNotation token."""
    # Count octave markers
    up_markers = tiny_token.count("'")
    down_markers = tiny_token.count(",")
    
    # Base octave is 4 in TinyNotation
    return 4 + up_markers - down_markers


def parse_lilypond_to_data(lily_string: str, part_name: str = "Part 1") -> dict:
    """
    Parses a LilyPond shorthand string into the standard data dictionary.
    Returns a dict: {"metadata": {...}, "parts": { part_name: [events...] }}
    
    CORRECTED APPROACH: Directly convert parsed tokens to event dictionaries,
    bypassing TinyNotation string intermediary which causes data loss.
    """
    # Basic sanitization (strip control chars that break tokenization)
    if lily_string is None:
        lily_string = ''
    lily_string = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", '', lily_string)

    # Use the parser to get structured token data
    parse_result = lily_to_tiny_notation(lily_string)
    
    # Handle errors
    if not parse_result.success:
        raise ValueError(f"Parser error: {parse_result.error}")
    
    # Convert parsed tokens DIRECTLY to event dictionaries
    # This avoids the broken TinyNotation string intermediary
    events = []
    
    for token_info in parse_result.tokens:
        # Parse the ORIGINAL LilyPond token to get structured data
        from lily_token_parser import parse_token, pitch_to_midi
        from relative_octave_logic import parse_base_pitch
        
        parsed = parse_token(token_info.original)
        
        # For now, we need to extract octave from the converted TinyNotation
        # This is a temporary bridge until we refactor to store absolute octave in TokenInfo
        tiny_token = token_info.converted
        
        if parsed.is_rest:
            # Rest event
            events.append({
                'type': 'rest',
                'ql': _parse_duration_to_ql(parsed.duration),
                'original_token': token_info.original,
                'position': token_info.position
            })
        elif parsed.pitch_letter and parsed.pitch_letter.startswith('<'):
            # Chord - skip for now (needs special handling)
            continue
        else:
            # Note event - extract octave from TinyNotation
            octave = _extract_octave_from_tiny(tiny_token)
            
            events.append({
                'type': 'note',
                'step': parsed.pitch_letter.upper(),
                'octave': octave,
                'alter': _accidental_to_alter(parsed.accidental),
                'ql': _parse_duration_to_ql(parsed.duration),
                'original_token': token_info.original,
                'position': token_info.position
            })

    # Extract metadata - start with defaults
    metadata = {"title": "LilyPond Score", "composer": "Codempose"}
    
    # Extract from directives
    if parse_result.directives:
        if 'time' in parse_result.directives:
            metadata["time_signature"] = parse_result.directives['time']
        if 'key' in parse_result.directives:
            # Parse key signature (e.g., "c \major")
            key_match = re.match(r'([a-g][#b]?)\s+(\\major|\\minor)', parse_result.directives.get('key', ''))
            if key_match:
                tonic = key_match.group(1)
                mode = 'major' if 'major' in key_match.group(2) else 'minor'
                metadata["key_signature"] = {"tonic": tonic, "mode": mode}
        if 'tempo' in parse_result.directives:
            tempo_match = re.search(r'=\s*(\d+)', parse_result.directives['tempo'])
            if tempo_match:
                metadata["tempo"] = int(tempo_match.group(1))

    # Attach any parsing warnings to the metadata
    if parse_result.warnings:
        metadata['warnings'] = parse_result.warnings
    
    # **INSPECTOR**: Store TinyNotation string for diagnostic purposes
    # This is NOT used in the parsing pipeline, but allows you to verify
    # that pitch resolution is working correctly
    if parse_result.tiny_notation:
        metadata['tinynotation_inspector'] = parse_result.tiny_notation
    
    # Also store the full token tracking data in metadata for reference
    if parse_result.tokens:
        metadata['parser_tokens'] = [
            {
                'original': t.original,
                'converted': t.converted,
                'position': t.position,
                'warnings': t.warnings
            }
            for t in parse_result.tokens
        ]
    
    # Store original input for potential re-use
    metadata['original_input'] = lily_string
    
    score_data = {"metadata": metadata, "parts": {part_name: events}}
    return score_data


