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


def parse_lilypond_to_data(lily_string: str, part_name: str = "Part 1") -> dict:
    """
    Parses a LilyPond shorthand string into the standard data dictionary.
    Returns a dict: {"metadata": {...}, "parts": { part_name: [events...] }}
    
    Now uses the validated lily_to_tiny_notation() parser with correct
    relative octave logic (alphabetical tie-breaking, not shortest diatonic path).
    """
    # Basic sanitization (strip control chars that break tokenization)
    if lily_string is None:
        lily_string = ''
    lily_string = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", '', lily_string)

    # Use the new validated parser
    parse_result = lily_to_tiny_notation(lily_string)
    
    # Handle errors
    if not parse_result.success:
        raise ValueError(f"Parser error: {parse_result.error}")
    
    # Parse the complete TinyNotation string using music21
    # This is more reliable than parsing individual tokens
    part = music21.stream.Part()
    
    try:
        # Use the complete TinyNotation string from the parser
        tiny_string = parse_result.tiny_notation
        
        # Parse with music21's TinyNotation parser
        tiny_obj = music21.converter.parse(f"tinynotation: {tiny_string}")
        
        # Extract notes and rests
        for element in tiny_obj.flatten().notesAndRests:
            part.append(element)
        
        # Add time signature if present (music21 may have already added it, but ensure it's at position 0)
        if 'time' in parse_result.directives:
            ts_str = parse_result.directives['time']
            numerator, denominator = map(int, ts_str.split('/'))
            ts = music21.meter.TimeSignature(f"{numerator}/{denominator}")
            # Remove any existing time signatures
            for existing_ts in part.getElementsByClass(music21.meter.TimeSignature):
                part.remove(existing_ts)
            part.insert(0, ts)
            
    except Exception as e:
        raise ValueError(f"Failed to build music21 Part from tokens: {e}")

    # Extract metadata - start with defaults
    metadata = {"title": "LilyPond Score", "composer": "Codempose"}
    
    # Extract from directives dictionary (not list)
    if parse_result.directives:
        # Time signature
        if 'time' in parse_result.directives:
            metadata["time_signature"] = parse_result.directives['time']
        
        # Key signature: parse "c \\major" or "d \\minor"
        if 'key' in parse_result.directives:
            key_str = parse_result.directives['key']
            # Format is "c \\major" or "d \\minor"
            match = re.match(r'([a-g](?:es|is)?)\s+\\(major|minor)', key_str)
            if match:
                tonic = match.group(1)
                mode = match.group(2)
                metadata["key_signature"] = {"tonic": tonic, "mode": mode}
        
        # Tempo: parse "4 = 120" format
        if 'tempo' in parse_result.directives:
            tempo_str = parse_result.directives['tempo']
            # Format is "4 = 120" or similar
            match = re.match(r'(\d+)\s*=\s*(\d+)', tempo_str)
            if match:
                beat_duration = int(match.group(1))
                bpm = int(match.group(2))
                metadata["tempo"] = {
                    "beat_duration": beat_duration,
                    "bpm": bpm
                }
    
    # Also check music21 Part for metadata (fallback)
    ts = part.getElementsByClass(music21.meter.TimeSignature)
    if ts and "time_signature" not in metadata:
        metadata["time_signature"] = ts[0].ratioString
    ks = part.getElementsByClass(music21.key.Key)
    if ks and "key_signature" not in metadata:
        k = ks[0]
        metadata["key_signature"] = {
            "tonic": getattr(k.tonic if hasattr(k, 'tonic') else k.tonicPitch, 'name', 'C'),
            "mode": getattr(k, 'mode', 'major')
        }
    tm = part.getElementsByClass(music21.tempo.MetronomeMark)
    if tm and "tempo" not in metadata:
        metadata["tempo"] = int(getattr(tm[0], 'number', 120))

    # Convert the music21 Part to the canonical event list
    # Pass TokenInfo data for event-level tracking (direct parsing only)
    events = extract_data_from_part(part, token_infos=parse_result.tokens)

    # Attach any parsing warnings to the metadata
    if parse_result.warnings:
        metadata['warnings'] = parse_result.warnings
    
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


