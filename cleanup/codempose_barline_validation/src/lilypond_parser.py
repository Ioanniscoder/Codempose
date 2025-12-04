import re
import music21
from music_data import extract_data_from_part
from lily_to_tiny import lily_to_tiny_notation
from lily_token_parser import parse_token


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


def _parse_duration_to_ql(duration_str: str, last_ql: float = 1.0) -> float:
    """Convert LilyPond duration string to quarterLength.
    
    Args:
        duration_str: Duration string like '4', '8.', '2' or empty for implicit duration
        last_ql: Previous note's quarterLength (used when duration_str is empty)
    
    Returns:
        Quarter length value
    """
    if not duration_str:
        # IMPLICIT DURATION: Inherit from previous note (LilyPond feature)
        return last_ql
    
    # Extract base duration and dot
    match = re.match(r'(\d+)(\.{0,3})', duration_str)
    if not match:
        return last_ql  # Fallback to last duration on parse error
    
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


def _validate_barlines_in_tokens(tokens: list, directives: dict, warnings: list) -> list:
    """
    Validate barlines in TokenInfo list BEFORE tie merging.
    This counts individual notes, not merged tied notes.
    
    Returns corrected list of TokenInfo objects with barlines validated/inserted.
    """
    from lily_to_tiny import TokenInfo
    
    time_sig = directives.get('time', '4/4')
    standard_bar_length = _parse_time_signature(time_sig, warnings)
    
    corrected_tokens = []
    cumulative_ql = 0.0
    bar_number = 1
    last_ql = 1.0  # Track last duration for implicit durations
    
    just_inserted_barline = False  # Track if we just inserted a calculated barline
    
    i = 0
    while i < len(tokens):
        token_info = tokens[i]
        
        # Handle barlines
        if token_info.original == '|':
            # Check if this manual barline comes right after a calculated insertion
            if just_inserted_barline:
                # This manual barline is at the same position as calculated one - skip it
                warnings.append(
                    f"Bar {bar_number}: Manual barline skipped (calculated barline already inserted)"
                )
                just_inserted_barline = False
                i += 1
                continue
            
            just_inserted_barline = False  # Reset flag
            
            if bar_number == 1:
                # First barline: TRUSTED
                corrected_tokens.append(token_info)
                if abs(cumulative_ql - standard_bar_length) > 0.001:
                    warnings.append(
                        f"Bar 1: {cumulative_ql:.1f} QL pickup bar "
                        f"(time signature expects {standard_bar_length:.1f} QL)"
                    )
                bar_number += 1
                cumulative_ql = 0.0
                
            elif abs(cumulative_ql - standard_bar_length) < 0.001:
                # Duration matches: Accept barline
                corrected_tokens.append(token_info)
                bar_number += 1
                cumulative_ql = 0.0
                
            else:
                # Duration doesn't match: Skip this barline
                warnings.append(
                    f"Bar {bar_number}: Manual barline at {cumulative_ql:.1f} QL skipped "
                    f"(expected {standard_bar_length:.1f} QL)"
                )
                # Don't add, counter continues
            
            i += 1
            continue
        
        # Parse token to get duration
        parsed = parse_token(token_info.original)
        note_ql = None
        
        if parsed.is_rest:
            note_ql = _parse_duration_to_ql(parsed.duration, last_ql)
            if parsed.duration:
                last_ql = note_ql
                
        elif parsed.pitch_letter and not parsed.pitch_letter.startswith('<'):
            # Regular note
            note_ql = _parse_duration_to_ql(parsed.duration, last_ql)
            if parsed.duration:
                last_ql = note_ql
        
        # Add token and update cumulative
        corrected_tokens.append(token_info)
        if note_ql:
            cumulative_ql += note_ql
            just_inserted_barline = False  # Reset flag when processing notes
            
            # Check if we've reached bar boundary
            if cumulative_ql >= standard_bar_length - 0.001:
                # Check if next token is a manual barline at correct position
                next_is_barline = (i + 1 < len(tokens) and tokens[i + 1].original == '|')
                
                if next_is_barline:
                    # Manual barline exists at correct position - will be processed next iteration
                    # Don't insert calculated barline, let the manual one be accepted
                    pass
                elif i + 1 < len(tokens):
                    # No manual barline and not at end - need to insert calculated barline
                    barline_token = TokenInfo(
                        original='|',
                        converted='|',
                        position=token_info.position,
                        warnings=[],
                        pitch_leap=False
                    )
                    corrected_tokens.append(barline_token)
                    just_inserted_barline = True  # Set flag for next iteration
                    
                    if cumulative_ql > standard_bar_length + 0.001:
                        warnings.append(
                            f"Bar {bar_number}: Inserted barline after {cumulative_ql:.1f} QL "
                            f"(exceeds {standard_bar_length:.1f} QL)"
                        )
                    else:
                        warnings.append(f"Bar {bar_number}: Inserted barline at {cumulative_ql:.1f} QL")
                    
                    bar_number += 1
                    cumulative_ql = 0.0
                # else: At end of piece - don't insert closing barline
        
        i += 1
    
    return corrected_tokens


def _validate_and_correct_barlines(events: list, directives: dict, warnings: list) -> list:
    """
    Validate barlines against time signature and insert missing ones.
    
    Rules:
    1. First barline is TRUSTED (establishes bar length, could be pickup)
    2. All other barlines: Check if cumulative_ql matches standard_bar_length
       - Matches: Accept barline, reset counter (tie crossing is OK if duration correct)
       - Doesn't match: Skip barline, counter continues (will insert calculated barline)
    3. When counter reaches bar boundary: Insert calculated barline
    
    Result: Misplaced barlines are replaced by correctly positioned ones with warnings.
    
    Args:
        events: List of event dictionaries
        directives: Dictionary with 'time' signature if present
        warnings: List to append warnings to (modified in place)
    
    Returns:
        List of events with corrected/inserted barlines
    """
    # Parse time signature to get standard bar length in quarter notes
    time_sig = directives.get('time', '4/4')
    standard_bar_length = _parse_time_signature(time_sig, warnings)
    
    corrected_events = []
    cumulative_ql = 0.0
    bar_number = 1
    first_bar_length = None
    skip_next_note_ql_adjustment = 0.0  # Track partial QL already counted for tied notes
    
    i = 0
    while i < len(events):
        event = events[i]
        
        if event['type'] == 'barline':
            # Check if next event is a tied note (merged note appears after barline)
            # If so, we need to account for the FIRST note's duration in the bar length check
            check_ql = cumulative_ql
            next_is_tied = False
            if i + 1 < len(events) and events[i+1]['type'] == 'note':
                next_token = events[i+1].get('original_token', '')
                if '~' in next_token:
                    # This is a merged tied note like 'a4~ a4'
                    # Parse the first note's duration (the part before the barline)
                    # Split on space to get first note token
                    first_note_token = next_token.split()[0] if ' ' in next_token else next_token
                    # Extract duration from first note (e.g., 'a4~' -> '4')
                    import re
                    duration_match = re.search(r'(\d+)(\.*)~', first_note_token)
                    if duration_match:
                        duration_num = int(duration_match.group(1))
                        dots = len(duration_match.group(2))
                        # Calculate QL for first note
                        first_note_ql = 4.0 / duration_num
                        for _ in range(dots):
                            first_note_ql += first_note_ql / 2
                        check_ql += first_note_ql
                        next_is_tied = True
            
            if bar_number == 1:
                # First barline: TRUSTED (establishes bar length, could be pickup)
                corrected_events.append(event)
                first_bar_length = check_ql
                if abs(first_bar_length - standard_bar_length) > 0.001:
                    warnings.append(
                        f"Bar 1: {first_bar_length:.1f} QL pickup bar "
                        f"(time signature expects {standard_bar_length:.1f} QL)"
                    )
                bar_number += 1
                # If tied note follows, mark how much QL was already counted (first note's duration)
                if next_is_tied:
                    skip_next_note_ql_adjustment = check_ql - cumulative_ql
                cumulative_ql = 0.0
                
            elif abs(check_ql - standard_bar_length) < 0.001:
                # Duration matches: Accept barline (tie or not)
                corrected_events.append(event)
                bar_number += 1
                # If tied note follows, mark how much QL was already counted (first note's duration)
                if next_is_tied:
                    skip_next_note_ql_adjustment = check_ql - cumulative_ql
                cumulative_ql = 0.0
                
            else:
                # Duration doesn't match: Skip this barline
                # Counter continues, calculated barline will be inserted at correct position
                tie_note = f" (tie crossing)" if next_is_tied else ""
                warnings.append(
                    f"Bar {bar_number}: Manual barline at {check_ql:.1f} QL skipped{tie_note} "
                    f"(expected {standard_bar_length:.1f} QL)"
                )
                # Don't add to corrected_events, don't reset counter
            
            i += 1
            continue
        
        # Add note/rest/chord
        event_ql = event.get('ql', 0.0)
        corrected_events.append(event)
        
        # Adjust cumulative based on whether this note was already partially counted
        if skip_next_note_ql_adjustment > 0:
            # This is a tied note - only count the continuation part
            cumulative_ql += (event_ql - skip_next_note_ql_adjustment)
            skip_next_note_ql_adjustment = 0.0
        else:
            cumulative_ql += event_ql
        
        # Check if counter reached bar boundary
        if cumulative_ql >= standard_bar_length - 0.001:
            # Insert calculated barline
            corrected_events.append({
                'type': 'barline',
                'style': '|',
                'ql': 0.0,
                'original_token': '| (calculated)',
                'position': len(corrected_events)
            })
            
            if i + 1 < len(events):  # Only warn if not at end
                if cumulative_ql > standard_bar_length + 0.001:
                    warnings.append(
                        f"Bar {bar_number}: Inserted barline after {cumulative_ql:.1f} QL "
                        f"(exceeds {standard_bar_length:.1f} QL)"
                    )
                else:
                    warnings.append(
                        f"Bar {bar_number}: Inserted barline at {cumulative_ql:.1f} QL"
                    )
            
            bar_number += 1
            cumulative_ql = 0.0
            trust_next_barline = False
        
        i += 1
    
    return corrected_events


def _parse_time_signature(time_sig_str: str, warnings: list) -> float:
    """
    Parse time signature string to quarter note length per bar.
    
    Args:
        time_sig_str: Time signature like "3/4", "4/4", "6/8"
        warnings: List to append warning if no time signature
    
    Returns:
        Quarter note length per bar
    
    Examples:
        "3/4" → 3.0 (3 quarter notes)
        "4/4" → 4.0 (4 quarter notes)
        "6/8" → 3.0 (6 eighth notes = 3 quarter notes)
    """
    if not time_sig_str:
        warnings.append("No time signature found, using 4/4 default")
        return 4.0
    
    match = re.match(r'(\d+)/(\d+)', time_sig_str)
    if not match:
        warnings.append(f"Invalid time signature '{time_sig_str}', using 4/4 default")
        return 4.0
    
    numerator = int(match.group(1))
    denominator = int(match.group(2))
    
    # Calculate quarter note equivalents
    # denominator 4 = quarter notes, 8 = eighth notes (half), 2 = half notes (double)
    beat_length = 4.0 / denominator
    bar_length = numerator * beat_length
    
    return bar_length


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
    
    # Validate and correct barlines BEFORE processing (using individual note durations)
    barline_warnings = []
    corrected_tokens = _validate_barlines_in_tokens(
        parse_result.tokens, 
        parse_result.directives, 
        barline_warnings
    )
    
    # Convert parsed tokens DIRECTLY to event dictionaries
    # This avoids the broken TinyNotation string intermediary
    events = []
    
    # Tie tracking state
    tie_pending = None  # Will store the event waiting for tie resolution
    
    # Duration tracking state (for implicit durations)
    last_ql = 1.0  # Default to quarter note
    
    for token_info in corrected_tokens:
        # Parse the ORIGINAL LilyPond token to get structured data
        from lily_token_parser import parse_token, pitch_to_midi
        from relative_octave_logic import parse_base_pitch
        
        # Check if this is a tuplet (converted format starts with [)
        if token_info.converted.startswith('[') and ']' in token_info.converted:
            # Tuplet - parse converted TinyNotation to get resolved notes
            # Format: [d e f]8 means: 3 eighth notes in time of 2 eighths
            # The number after ] is the NOTATED duration of each note
            match = re.match(r'\[([^\]]+)\](\d+\.?)', token_info.converted)
            if match:
                notes_str = match.group(1)
                notated_duration_str = match.group(2)
                
                # Count notes in tuplet
                note_tokens = notes_str.split()
                n = len(note_tokens)
                
                # Calculate tuplet ratio
                # Standard tuplet: n notes in time of (n-1)
                # Example: [d e f]8 → 3 notes in time of 2 → ratio 3/2
                numerator = n
                denominator = n - 1 if n > 1 else n
                
                # Parse each note in the tuplet with NOTATED duration
                # (music21 will handle the tuplet timing internally)
                tuplet_note_events = []
                notated_ql = _parse_duration_to_ql(notated_duration_str, last_ql)
                if notated_duration_str:
                    last_ql = notated_ql
                
                for note_str in note_tokens:
                    # Extract pitch, octave, accidental from notation like "d" or "e'"
                    note_match = re.match(r"([a-gr])(#|b|is|es)?([',]*)(\d+\.?)?", note_str)
                    if note_match:
                        pitch = note_match.group(1)
                        acc = note_match.group(2) or ''
                        octave_mod = note_match.group(3) or ''
                        
                        # Calculate absolute octave from TinyNotation format
                        base_octave = 4
                        octave = base_octave + octave_mod.count("'") - octave_mod.count(",")
                        
                        # Convert accidental
                        alter = 0
                        if acc in ['#', 'is']:
                            alter = 1
                        elif acc in ['b', 'es']:
                            alter = -1
                        
                        # Create note event with NOTATED duration
                        # (tuplet timing handled by parent tuplet event)
                        note_event = {
                            'type': 'note',
                            'step': pitch.upper(),
                            'octave': octave,
                            'alter': alter,
                            'ql': notated_ql,  # Use NOTATED duration
                            'original_token': note_str,
                        }
                        tuplet_note_events.append(note_event)
                
                # Create structured tuplet event containing nested notes
                tuplet_event = {
                    'type': 'tuplet',
                    'numerator': numerator,
                    'denominator': denominator,
                    'notes': tuplet_note_events,
                    'original_token': token_info.original if isinstance(token_info.original, str) else str(token_info.original),
                    'position': len(events),
                }
                events.append(tuplet_event)
            continue
        
        parsed = parse_token(token_info.original)
        
        # Check for barline first (before processing other token types)
        if token_info.original == '|':
            # Add barline event (do NOT finalize pending ties - they can cross barlines!)
            events.append({
                'type': 'barline',
                'style': '|',
                'ql': 0.0,
                'original_token': '|',
                'position': token_info.position
            })
            continue
        
        # For now, we need to extract octave from the converted TinyNotation
        # This is a temporary bridge until we refactor to store absolute octave in TokenInfo
        tiny_token = token_info.converted
        
        if parsed.is_tuplet:
            # Tuplet event - store ratio and nested notes
            tuplet_events = []
            tuplet_last_ql = last_ql  # Track duration within tuplet
            
            # Process each note in the tuplet
            for tuplet_note in parsed.tuplet_notes:
                if tuplet_note.is_rest:
                    rest_ql = _parse_duration_to_ql(tuplet_note.duration, tuplet_last_ql)
                    if tuplet_note.duration:
                        tuplet_last_ql = rest_ql
                    
                    tuplet_events.append({
                        'type': 'rest',
                        'ql': rest_ql,
                        'original_token': tuplet_note.original,
                        'position': token_info.position
                    })
                elif tuplet_note.pitch_letter and not tuplet_note.pitch_letter.startswith('<'):
                    # For tuplet notes, we need octave resolution
                    # This requires processing through relative octave logic
                    # For now, assume default octave 4 (will need refinement)
                    octave = 4  # TODO: Proper octave resolution for tuplet notes
                    
                    note_ql = _parse_duration_to_ql(tuplet_note.duration, tuplet_last_ql)
                    if tuplet_note.duration:
                        tuplet_last_ql = note_ql
                    
                    tuplet_events.append({
                        'type': 'note',
                        'step': tuplet_note.pitch_letter.upper(),
                        'octave': octave,
                        'alter': _accidental_to_alter(tuplet_note.accidental),
                        'ql': note_ql,
                        'original_token': tuplet_note.original,
                        'position': token_info.position
                    })
            
            # Update main last_ql to the last duration seen in tuplet
            last_ql = tuplet_last_ql
            
            # Create tuplet event with nested notes
            events.append({
                'type': 'tuplet',
                'numerator': parsed.tuplet_ratio[0],
                'denominator': parsed.tuplet_ratio[1],
                'notes': tuplet_events,
                'original_token': token_info.original,
                'position': token_info.position
            })
            
        elif parsed.is_rest:
            # Rest event - finalize any pending tie first
            if tie_pending is not None:
                events.append(tie_pending)
                tie_pending = None
            
            rest_ql = _parse_duration_to_ql(parsed.duration, last_ql)
            if parsed.duration:  # Only update last_ql if duration was explicit
                last_ql = rest_ql
            
            events.append({
                'type': 'rest',
                'ql': rest_ql,
                'original_token': token_info.original,
                'position': token_info.position
            })
        elif parsed.is_chord:
            # Chord event - use "parse first note" strategy
            # 1. Get the base note's octave from TinyNotation (already resolved by relative logic)
            tiny_token = token_info.converted
            base_octave = _extract_octave_from_tiny(tiny_token)
            
            # Build pitch list starting with base note
            pitches_list = []
            
            # Add base note (first note in chord)
            base_parsed = parsed.chord_base_note
            base_step = base_parsed.pitch_letter
            base_alter = 0
            if base_parsed.accidental == 'sharp':
                base_alter = 1
            elif base_parsed.accidental == 'flat':
                base_alter = -1
            elif base_parsed.accidental == 'double-sharp':
                base_alter = 2
            elif base_parsed.accidental == 'double-flat':
                base_alter = -2
            
            pitches_list.append({
                'step': base_step.upper(),
                'octave': base_octave,
                'alter': base_alter
            })
            
            # Resolve other notes relative to previous note in chord
            prev_pitch = base_step.upper()
            prev_octave = base_octave
            
            for note_str in parsed.chord_other_notes:
                # Parse this note token
                note_parsed = parse_token(note_str)
                note_step = note_parsed.pitch_letter.upper()
                
                # Count octave markers in the original string
                octave_up = note_str.count("'")
                octave_down = note_str.count(",")
                
                # Calculate closest octave relative to previous note
                # (using same logic as relative_octave_logic.py)
                pitch_order = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
                prev_idx = pitch_order.index(prev_pitch)
                curr_idx = pitch_order.index(note_step)
                
                # Find closest instance
                if abs(curr_idx - prev_idx) <= 3:
                    note_octave = prev_octave
                elif curr_idx < prev_idx:
                    note_octave = prev_octave + 1
                else:
                    note_octave = prev_octave - 1
                
                # Apply explicit octave markers
                note_octave += octave_up - octave_down
                
                # Parse accidentals
                note_alter = 0
                if note_parsed.accidental == 'sharp':
                    note_alter = 1
                elif note_parsed.accidental == 'flat':
                    note_alter = -1
                elif note_parsed.accidental == 'double-sharp':
                    note_alter = 2
                elif note_parsed.accidental == 'double-flat':
                    note_alter = -2
                
                pitches_list.append({
                    'step': note_step,
                    'octave': note_octave,
                    'alter': note_alter
                })
                
                # Update previous note for next iteration
                prev_pitch = note_step
                prev_octave = note_octave
            
            chord_ql = _parse_duration_to_ql(parsed.duration, last_ql)
            if parsed.duration:  # Only update last_ql if duration was explicit
                last_ql = chord_ql
            
            events.append({
                'type': 'chord',
                'pitches': pitches_list,  # List of pitch dicts
                'ql': chord_ql,
                'original_token': token_info.original,
                'position': token_info.position
            })
        else:
            # Note event - extract octave from TinyNotation
            octave = _extract_octave_from_tiny(tiny_token)
            
            # Grace notes get zero duration (don't count toward measure)
            if parsed.is_grace:
                note_ql = 0.0
            else:
                note_ql = _parse_duration_to_ql(parsed.duration, last_ql)
                if parsed.duration:  # Only update last_ql if duration was explicit
                    last_ql = note_ql
            
            note_event = {
                'type': 'note',
                'step': parsed.pitch_letter.upper(),
                'octave': octave,
                'alter': _accidental_to_alter(parsed.accidental),
                'ql': note_ql,
                'is_grace': parsed.is_grace,
                'original_token': token_info.original,
                'position': token_info.position
            }
            
            # Add optional fields from suffix container (only if present)
            if parsed.articulations:
                note_event['articulations'] = parsed.articulations
            if parsed.dynamics:
                note_event['dynamics'] = parsed.dynamics
            if parsed.tracker:
                note_event['tracker'] = parsed.tracker
            
            # Handle tie merging
            if tie_pending is not None:
                # Check if this note matches the tied note (same pitch)
                if (tie_pending['step'] == note_event['step'] and 
                    tie_pending['octave'] == note_event['octave'] and
                    tie_pending['alter'] == note_event['alter']):
                    # Merge durations - add to pending note instead of creating new event
                    tie_pending['ql'] += note_event['ql']
                    # Update original token to show both notes
                    tie_pending['original_token'] += f" {note_event['original_token']}"
                    
                    # Check if this note also has a tie
                    if parsed.has_tie:
                        # Keep tie pending for next note
                        pass
                    else:
                        # Tie chain complete - add merged event
                        events.append(tie_pending)
                        tie_pending = None
                    continue  # Don't process further
                else:
                    # Pitch mismatch - finalize pending tie and start new note
                    events.append(tie_pending)
                    tie_pending = None
            
            # Check if this note starts a tie
            if parsed.has_tie:
                tie_pending = note_event
                # Don't append yet - wait for next note
            else:
                events.append(note_event)

    # Finalize any pending tie at end of piece
    if tie_pending is not None:
        events.append(tie_pending)
    
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
    all_warnings = []
    if parse_result.warnings:
        all_warnings.extend(parse_result.warnings)
    if barline_warnings:
        all_warnings.extend(barline_warnings)
    if all_warnings:
        metadata['warnings'] = all_warnings
    
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


