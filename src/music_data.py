# music_data.py
import music21
from typing import List, Optional

def extract_data_from_part(part: music21.stream.Part, token_infos: Optional[List] = None):
    """Converts a music21.Part into a list of canonical event dictionaries.
    
    Now supports Chord objects in addition to Notes and Rests.
    Preserves articulations, dynamics, and tracking labels stored in music21 objects.
    
    Args:
        part: music21.Part to convert
        token_infos: Optional list of TokenInfo objects from parser for tracking
                     (only available when parsing LilyPond input directly)
    
    Returns:
        List of event dictionaries with tracking data if available
    """
    events = []
    for i, el in enumerate(part.flatten().notesAndRests):
        ev = {'ql': el.quarterLength}
        
        # Add tracking data from TokenInfo if available (direct parsing only)
        if token_infos and i < len(token_infos):
            token = token_infos[i]
            ev['original_token'] = token.original
            ev['position'] = token.position
            if token.warnings:
                ev['parser_warnings'] = token.warnings
        
        # Extract metadata from music21 object's .editorial namespace
        # (This is where we store articulations, dynamics, tracker during data_to_part)
        if hasattr(el, 'editorial'):
            if hasattr(el.editorial, 'articulations') and el.editorial.articulations:
                ev['articulations'] = el.editorial.articulations
            if hasattr(el.editorial, 'dynamics') and el.editorial.dynamics:
                ev['dynamics'] = el.editorial.dynamics
            if hasattr(el.editorial, 'tracker') and el.editorial.tracker:
                ev['tracker'] = el.editorial.tracker
        
        if getattr(el, 'isRest', False):
            ev['type'] = 'rest'
        elif isinstance(el, music21.chord.Chord):
            # Handle Chord objects - they have .pitches (plural), not .pitch
            ev['type'] = 'chord'
            ev['pitches'] = []
            for p in el.pitches:
                pitch_data = {
                    'step': p.step,
                    'octave': p.octave,
                    'alter': getattr(p.accidental, 'alter', 0) if p.accidental else 0
                }
                ev['pitches'].append(pitch_data)
        elif isinstance(el, music21.note.Note):
            # Handle Note objects - they have .pitch (singular)
            ev['type'] = 'note'
            ev['step'] = el.pitch.step
            ev['octave'] = el.pitch.octave
            ev['alter'] = getattr(el.pitch.accidental, 'alter', 0) if el.pitch.accidental else 0
        events.append(ev)
    return events


def _event_to_music21(ev: dict):
    """Helper function to convert a single event dictionary to a music21 element.
    
    Used by multi-voice section handling to convert voice events.
    Preserves articulations, dynamics, and tracking labels in music21.editorial namespace.
    """
    ql = ev.get('ql', 1.0)
    element = None
    
    if ev.get('type') == 'rest':
        element = music21.note.Rest(quarterLength=ql)
    
    elif ev.get('type') == 'chord':
        pitches = []
        for pitch_data in ev.get('pitches', []):
            step = pitch_data.get('step', 'c')
            octave = pitch_data.get('octave', 4)
            alter = pitch_data.get('alter', 0)
            pitch = music21.pitch.Pitch()
            pitch.step = step.upper()
            pitch.octave = octave
            if alter != 0:
                pitch.accidental = music21.pitch.Accidental(alter)
            pitches.append(pitch)
        element = music21.chord.Chord(pitches, quarterLength=ql)
    
    elif ev.get('type') == 'note':
        step = ev.get('step', 'c')
        octave = ev.get('octave', 4)
        alter = ev.get('alter', 0)
        pitch = music21.pitch.Pitch()
        pitch.step = step.upper()
        pitch.octave = octave
        if alter != 0:
            pitch.accidental = music21.pitch.Accidental(alter)
        element = music21.note.Note(pitch, quarterLength=ql)
        
        # Handle tie notation (for split merged ties)
        tie_type = ev.get('tie', None)
        if tie_type == 'start':
            element.tie = music21.tie.Tie('start')
        elif tie_type == 'stop':
            element.tie = music21.tie.Tie('stop')
        elif tie_type == 'continue':
            element.tie = music21.tie.Tie('continue')
    
    elif ev.get('type') == 'barline':
        # Barlines are typically handled at the measure level, not as individual elements
        return None
    
    elif ev.get('type') == 'raw_lilypond':
        # Bypass mode: raw_lilypond events should be converted to parsed events
        # BEFORE reaching this function (in the export pipeline)
        # If we see one here, it means the conversion wasn't done
        return None
    
    elif ev.get('type') == 'text_mark':
        # Text marks (rehearsal marks, section labels)
        # Can be converted to music21.expressions.RehearsalMark if needed
        return None
    
    # Attach metadata to element's editorial namespace if present
    if element is not None:
        if 'articulations' in ev:
            element.editorial.articulations = ev['articulations']
        if 'dynamics' in ev:
            element.editorial.dynamics = ev['dynamics']
        if 'tracker' in ev:
            element.editorial.tracker = ev['tracker']
    
    return element


def _split_tied_notes_at_barlines(events: list, measure_length: float) -> list:
    """
    Pre-process events to split merged tied notes that span barlines.
    
    IMPORTANT: This function only splits notes WITHOUT tie notation.
    Notes that already have tie='start'/'stop'/'continue' were correctly
    split by the parser and should NOT be split again.
    
    This function is for backward compatibility with OLD code that merged ties.
    """
    result = []
    current_measure_ql = 0.0
    
    for ev in events:
        if ev.get('type') == 'barline':
            # Reset counter for next measure
            result.append(ev)
            current_measure_ql = 0.0
            continue
        
        if ev.get('type') in ['note', 'rest', 'chord']:
            event_ql = ev.get('ql', 1.0)
            remaining_space = measure_length - current_measure_ql
            
            # CRITICAL: Don't split notes that already have tie notation!
            # Parser already split these correctly
            has_tie = ev.get('tie') is not None
            
            if not has_tie and event_ql > remaining_space + 0.001:  # Tolerance for floating point
                # This note overflows the measure - split it
                
                # First part (completes current measure)
                first_part = ev.copy()
                first_part['ql'] = remaining_space
                if ev.get('type') == 'note':
                    first_part['tie'] = 'start'
                result.append(first_part)
                current_measure_ql += remaining_space
                
                # Add implicit barline
                result.append({'type': 'barline', 'style': '|', 'ql': 0.0})
                current_measure_ql = 0.0
                
                # Second part (starts next measure)
                second_part = ev.copy()
                second_part['ql'] = event_ql - remaining_space
                if ev.get('type') == 'note':
                    second_part['tie'] = 'stop'
                result.append(second_part)
                current_measure_ql += (event_ql - remaining_space)
            else:
                # Fits normally (or already has tie notation)
                result.append(ev)
                current_measure_ql += event_ql
        else:
            # Other event types (pass through)
            result.append(ev)
    
    return result


def _split_long_rest_into_measures(ql: float, time_sig: str = '4/4') -> list:
    """
    Split a long rest into measure-sized rest objects for proper MusicXML export.
    
    Args:
        ql: Quarter-length duration of the rest
        time_sig: Time signature (e.g., '4/4', '3/4')
    
    Returns:
        List of music21.note.Rest objects, one per measure
    """
    try:
        num, denom = map(int, time_sig.split('/'))
        ql_per_measure = (4.0 / denom) * num
    except:
        ql_per_measure = 4.0  # Default to 4/4
    
    rests = []
    remaining = ql
    
    # Create full-measure rests
    while remaining >= ql_per_measure - 0.001:  # Small tolerance for floating point
        rests.append(music21.note.Rest(quarterLength=ql_per_measure))
        remaining -= ql_per_measure
    
    # Add partial measure rest if needed
    if remaining > 0.001:
        rests.append(music21.note.Rest(quarterLength=remaining))
    
    return rests


def data_to_part(events: list, metadata: dict = None) -> music21.stream.Part:
    """Converts a list of canonical event dictionaries back into a music21.Part.
    
    Now supports:
    - chord and tuplet events in addition to notes and rests
    - multi_voice_section events for polyphonic staves
    - barline events for proper measure structure
    - CRITICAL: Handles merged tied notes that span barline boundaries
      by splitting them at measure boundaries with proper tie notation
    - CRITICAL: Splits long rests (>= 1 measure) into separate measure objects
      to prevent MusicXML export crashes
    """
    part = music21.stream.Part()
    
    # Track if we need to create measures from barlines
    has_barlines = any(ev.get('type') == 'barline' for ev in events)
    
    if has_barlines:
        # Get expected measure length from time signature
        measure_length = 4.0  # Default to 4/4
        if metadata and 'time_signature' in metadata:
            time_sig = metadata['time_signature']
            try:
                num, denom = map(int, time_sig.split('/'))
                measure_length = float(num) * (4.0 / float(denom))
            except:
                pass
        
        # PRE-PROCESS: Split any remaining merged ties (backward compatibility)
        # Parser now handles ties correctly, so this only affects notes WITHOUT tie notation
        events = _split_tied_notes_at_barlines(events, measure_length)
        
        # Create measures based on barline positions
        current_measure = music21.stream.Measure()
        measure_number = 1
        current_measure_ql = 0.0  # Track QL used in current measure
        
        # Add metadata to first measure
        if metadata:
            if 'clef' in metadata:
                clef_type = metadata['clef']
                try:
                    # Map LilyPond clef names to music21 clef types
                    if clef_type == 'bass':
                        current_measure.clef = music21.clef.BassClef()
                    elif clef_type == 'treble':
                        current_measure.clef = music21.clef.TrebleClef()
                    elif clef_type == 'alto':
                        current_measure.clef = music21.clef.AltoClef()
                    elif clef_type == 'tenor':
                        current_measure.clef = music21.clef.TenorClef()
                    else:
                        # Default to treble for unknown clefs
                        current_measure.clef = music21.clef.TrebleClef()
                except:
                    pass
            
            if 'time_signature' in metadata:
                time_sig = metadata['time_signature']
                try:
                    num, denom = map(int, time_sig.split('/'))
                    ts = music21.meter.TimeSignature(f'{num}/{denom}')
                    current_measure.timeSignature = ts
                except:
                    pass
            
            if 'key_signature' in metadata:
                key_sig = metadata['key_signature']
                if isinstance(key_sig, dict):
                    tonic = key_sig.get('tonic', 'c')
                    mode = key_sig.get('mode', 'major')
                    try:
                        ks = music21.key.Key(tonic, mode)
                        current_measure.keySignature = ks
                    except:
                        pass
        
        for ev in events:
            if ev.get('type') == 'barline':
                # Finalize current measure and start new one
                # (All barline types - |, ||, |. etc. - end the current measure)
                current_measure.number = measure_number
                part.append(current_measure)
                current_measure = music21.stream.Measure()
                measure_number += 1
                continue
            
            # Add element to current measure
            element = _event_to_music21(ev)
            if element:
                current_measure.append(element)
        
        # Don't forget the last measure if it has content
        if len(current_measure) > 0:
            current_measure.number = measure_number
            part.append(current_measure)
        
        return part
    
    # Original behavior for non-barline events (backward compatibility)
    for ev in events:
        ql = ev.get('ql', 1.0)
        
        # NEW: Handle multi-voice sections (polyphonic staves)
        if ev.get('type') == 'multi_voice_section':
            voices_dict = ev.get('voices', {})
            
            # Create Voice objects for each voice
            voice_objects = []
            for voice_idx, (voice_name, voice_events) in enumerate(voices_dict.items()):
                if voice_events is None:
                    # Skip rest placeholder voices for now
                    continue
                
                voice_stream = music21.stream.Voice()
                voice_stream.id = voice_name
                
                # Add events to this voice
                for v_event in voice_events:
                    element = _event_to_music21(v_event)
                    if element:
                        voice_stream.append(element)
                
                # Set stem direction (alternating up/down)
                if voice_idx % 2 == 0:
                    # Upper voice: stems up
                    for note in voice_stream.flatten().notes:
                        note.stemDirection = 'up'
                else:
                    # Lower voice: stems down
                    for note in voice_stream.flatten().notes:
                        note.stemDirection = 'down'
                
                voice_objects.append(voice_stream)
            
            # Create measure and insert all voices at offset 0
            if voice_objects:
                measure = music21.stream.Measure()
                for voice_obj in voice_objects:
                    measure.insert(0, voice_obj)
                
                part.append(measure)
            
            continue  # Skip to next event
        
        # EXISTING: Single-event handling
        if ev.get('type') == 'rest':
            ql = ev.get('ql', 1.0)
            
            # Get time signature from metadata
            time_sig = '4/4'  # default
            if metadata and 'time_signature' in metadata:
                time_sig = metadata['time_signature']
            
            # Parse time signature to get measure length
            try:
                num, denom = map(int, time_sig.split('/'))
                ql_per_measure = (4.0 / denom) * num
            except:
                ql_per_measure = 4.0
            
            # Split long rests into measures to prevent MusicXML export crashes
            if ql >= ql_per_measure:
                rest_measures = _split_long_rest_into_measures(ql, time_sig)
                for rest in rest_measures:
                    # Preserve metadata
                    if 'dynamics' in ev:
                        rest.editorial.dynamics = ev['dynamics']
                    if 'tracker' in ev:
                        rest.editorial.tracker = ev['tracker']
                    part.append(rest)
            else:
                # Short rest: keep as single object
                el = music21.note.Rest(quarterLength=ql)
                # Store metadata in editorial namespace for round-trip preservation
                if 'dynamics' in ev:
                    el.editorial.dynamics = ev['dynamics']
                if 'tracker' in ev:
                    el.editorial.tracker = ev['tracker']
                part.append(el)
        elif ev.get('type') == 'tuplet':
            # Handle tuplet events - create music21 tuplet
            numerator = ev.get('numerator', 3)
            denominator = ev.get('denominator', 2)
            tuplet_notes_data = ev.get('notes', [])
            
            # Create a tuplet group
            # music21 tuplets are created by setting tuplet properties on notes
            tuplet_notes = []
            for note_data in tuplet_notes_data:
                if note_data.get('type') == 'rest':
                    n = music21.note.Rest(quarterLength=note_data.get('ql', 1.0))
                elif note_data.get('type') == 'note':
                    step = note_data.get('step', 'c')
                    octave = note_data.get('octave', 4)
                    alter = note_data.get('alter', 0)
                    pitch = music21.pitch.Pitch()
                    pitch.step = step.upper()
                    pitch.octave = octave
                    if alter != 0:
                        pitch.accidental = music21.pitch.Accidental(alter)
                    n = music21.note.Note(pitch, quarterLength=note_data.get('ql', 1.0))
                    
                    # Add articulations to tuplet notes
                    articulations = note_data.get('articulations', [])
                    for artic in articulations:
                        if artic == 'staccato':
                            n.articulations.append(music21.articulations.Staccato())
                        elif artic == 'tenuto':
                            n.articulations.append(music21.articulations.Tenuto())
                        elif artic == 'accent':
                            n.articulations.append(music21.articulations.Accent())
                        elif artic == 'marcato':
                            n.articulations.append(music21.articulations.StrongAccent())
                        elif artic == 'staccatissimo':
                            n.articulations.append(music21.articulations.Staccatissimo())
                else:
                    continue
                tuplet_notes.append(n)
            
            # Set tuplet on all notes in the group
            if tuplet_notes:
                tup = music21.duration.Tuplet(numberNotesActual=numerator, numberNotesNormal=denominator)
                for n in tuplet_notes:
                    n.duration.appendTuplet(tup)
                    part.append(n)
                    
                    # Add dynamics after each tuplet note if present
                    if hasattr(n, 'step'):  # Only for notes, not rests
                        note_idx = tuplet_notes.index(n)
                        if note_idx < len(tuplet_notes_data):
                            dynamics = tuplet_notes_data[note_idx].get('dynamics')
                            if dynamics:
                                dyn = music21.dynamics.Dynamic(dynamics)
                                part.append(dyn)
                    
        elif ev.get('type') == 'chord':
            # Handle chord events - reconstruct Chord from pitches list
            pitches = []
            for pitch_data in ev.get('pitches', []):
                step = pitch_data.get('step', 'c')
                octave = pitch_data.get('octave', 4)
                alter = pitch_data.get('alter', 0)
                pitch = music21.pitch.Pitch()
                pitch.step = step.upper()
                pitch.octave = octave
                if alter != 0:
                    pitch.accidental = music21.pitch.Accidental(alter)
                pitches.append(pitch)
            el = music21.chord.Chord(pitches, quarterLength=ql)
            
            # Add articulations from event dictionary
            articulations = ev.get('articulations', [])
            for artic in articulations:
                if artic == 'staccato':
                    el.articulations.append(music21.articulations.Staccato())
                elif artic == 'tenuto':
                    el.articulations.append(music21.articulations.Tenuto())
                elif artic == 'accent':
                    el.articulations.append(music21.articulations.Accent())
                elif artic == 'marcato':
                    el.articulations.append(music21.articulations.StrongAccent())
                elif artic == 'staccatissimo':
                    el.articulations.append(music21.articulations.Staccatissimo())
            
            # ALSO store in editorial namespace for round-trip preservation
            if articulations:
                el.editorial.articulations = articulations
            
            # Store dynamics and tracker in editorial namespace
            if 'dynamics' in ev:
                el.editorial.dynamics = ev['dynamics']
            if 'tracker' in ev:
                el.editorial.tracker = ev['tracker']
            
            part.append(el)
            
            # Add dynamics after the chord (as a separate element in the stream)
            dynamics = ev.get('dynamics')
            if dynamics:
                dyn = music21.dynamics.Dynamic(dynamics)
                part.append(dyn)
        elif ev.get('type') == 'note':
            step = ev.get('step', 'c')
            octave = ev.get('octave', 4)
            alter = ev.get('alter', 0)
            pitch = music21.pitch.Pitch()
            pitch.step = step.upper()
            pitch.octave = octave
            if alter != 0:
                pitch.accidental = music21.pitch.Accidental(alter)
            el = music21.note.Note(pitch, quarterLength=ql)
            
            # Add articulations from event dictionary
            articulations = ev.get('articulations', [])
            for artic in articulations:
                if artic == 'staccato':
                    el.articulations.append(music21.articulations.Staccato())
                elif artic == 'tenuto':
                    el.articulations.append(music21.articulations.Tenuto())
                elif artic == 'accent':
                    el.articulations.append(music21.articulations.Accent())
                elif artic == 'marcato':
                    el.articulations.append(music21.articulations.StrongAccent())
                elif artic == 'staccatissimo':
                    el.articulations.append(music21.articulations.Staccatissimo())
            
            # ALSO store in editorial namespace for round-trip preservation
            if articulations:
                el.editorial.articulations = articulations
            
            # Store dynamics and tracker in editorial namespace
            if 'dynamics' in ev:
                el.editorial.dynamics = ev['dynamics']
            if 'tracker' in ev:
                el.editorial.tracker = ev['tracker']
            
            part.append(el)
            
            # Add dynamics after the note (as a separate element in the stream)
            dynamics = ev.get('dynamics')
            if dynamics:
                dyn = music21.dynamics.Dynamic(dynamics)
                part.append(dyn)
        else:
            continue
    return part


def build_lilypond_file(score_data: dict, output_basename: str, source_file: str = None):
    """
    Build and write LilyPond file with documentation.
    
    This is a wrapper around engrave_with_abjad() for backward compatibility
    with tenth.py's expected interface.
    
    Args:
        score_data: Complete score data dictionary
        output_basename: Base name for output file (e.g., 'tenth')
        source_file: Optional path to source Python file for attribution
    """
    from project_template import engrave_with_abjad
    from pathlib import Path
    
    # Extract basename without extension
    basename = Path(output_basename).stem
    
    # Delegate to existing function
    engrave_with_abjad(score_data, basename, source_file=source_file)


def part_to_data(part: music21.stream.Part) -> list:
    """
    Convert a music21.stream.Part back to canonical event format.
    
    This is the inverse of data_to_part(). It extracts notes, rests, chords,
    and other musical elements from a music21 Part and converts them to the
    canonical event dictionary format used by Codempose.
    
    PRESERVES MEASURE BOUNDARIES: If the Part contains Measure objects,
    barline events are inserted between measures to preserve structure.
    
    Args:
        part: music21.stream.Part to convert
        
    Returns:
        list: Canonical event dictionaries
        
    Example:
        >>> part = music21.stream.Part()
        >>> part.append(music21.note.Note('C4', quarterLength=1.0))
        >>> events = part_to_data(part)
        >>> events[0]
        {'type': 'note', 'step': 'C', 'octave': 4, 'alter': 0, 'ql': 1.0}
    """
    events = []
    
    def _convert_element(element):
        """Helper to convert a single music21 element to event dict."""
        if isinstance(element, music21.note.Note):
            # Convert Note to canonical format
            event = {
                'type': 'note',
                'step': element.pitch.step,
                'octave': element.pitch.octave,
                'alter': element.pitch.alter if element.pitch.alter else 0,
                'ql': element.quarterLength
            }
            
            # Add articulations if present
            if element.articulations:
                artic_names = []
                for artic in element.articulations:
                    artic_name = artic.name.lower()
                    if 'staccato' in artic_name:
                        artic_names.append('staccato')
                    elif 'tenuto' in artic_name:
                        artic_names.append('tenuto')
                    elif 'accent' in artic_name:
                        artic_names.append('accent')
                    elif 'marcato' in artic_name or 'strong' in artic_name:
                        artic_names.append('marcato')
                if artic_names:
                    event['articulations'] = artic_names
            
            # Add dynamics if present
            if hasattr(element, 'volume') and element.volume.velocity:
                if element.volume.velocity < 50:
                    event['dynamic'] = 'p'
                elif element.volume.velocity < 80:
                    event['dynamic'] = 'mf'
                else:
                    event['dynamic'] = 'f'
            
            return event
            
        elif isinstance(element, music21.note.Rest):
            # Convert Rest to canonical format
            return {
                'type': 'rest',
                'ql': element.quarterLength
            }
            
        elif isinstance(element, music21.chord.Chord):
            # Convert Chord to canonical format
            pitches = []
            for pitch in element.pitches:
                pitches.append({
                    'step': pitch.step,
                    'octave': pitch.octave,
                    'alter': pitch.alter if pitch.alter else 0
                })
            
            event = {
                'type': 'chord',
                'pitches': pitches,
                'ql': element.quarterLength
            }
            
            # Add articulations if present
            if element.articulations:
                artic_names = []
                for artic in element.articulations:
                    artic_name = artic.name.lower()
                    if 'staccato' in artic_name:
                        artic_names.append('staccato')
                    elif 'tenuto' in artic_name:
                        artic_names.append('tenuto')
                    elif 'accent' in artic_name:
                        artic_names.append('accent')
                if artic_names:
                    event['articulations'] = artic_names
            
            return event
        
        return None
    
    # Check if part has Measure objects (structured) or is flat
    measures = part.getElementsByClass('Measure')
    
    if len(measures) > 0:
        # Part has measures - preserve measure boundaries with barlines
        for measure_idx, measure in enumerate(measures):
            # Extract elements from this measure
            for element in measure.flatten():
                event = _convert_element(element)
                if event:
                    events.append(event)
            
            # Add barline after each measure (except the last)
            if measure_idx < len(measures) - 1:
                events.append({
                    'type': 'barline',
                    'style': '|',
                    'ql': 0.0
                })
    else:
        # Part is flat - no measure structure
        for element in part.flatten():
            event = _convert_element(element)
            if event:
                events.append(event)
    
    return events
