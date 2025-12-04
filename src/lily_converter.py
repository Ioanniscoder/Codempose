"""Convert event dictionaries to complete LilyPond notation."""

def events_to_lily(events, metadata=None):
    """
    Convert canonical event dictionaries to complete LilyPond snippet.
    
    Produces output like: \\relative c' { \\time 4/4 \\key c \\major e4 b4 e'4 b4 }
    
    Args:
        events: List of event dictionaries (canonical format)
        metadata: Optional metadata dict with time/key/tempo info
        
    Returns:
        Complete LilyPond snippet string with directives
    """
    if not events:
        return r"\relative c' { r1 }"
    
    # Generate note tokens
    lily_tokens = []
    for ev in events:
        # Handle text marks (rehearsal marks, section labels)
        if ev.get('type') == 'text_mark':
            mark_text = ev.get('text', '')
            lily_tokens.append(f"\\mark \"{mark_text}\"")
            continue
        
        # Handle barlines
        if ev.get('type') == 'barline':
            barline_style = ev.get('style', '|')
            lily_tokens.append(barline_style)
            continue
        
        ql = ev.get('ql', 1.0)
        dur_str = _ql_to_lily_duration(ql)
        
        if ev.get('type') == 'rest':
            lily_tokens.append(f"r{dur_str}")
        elif ev.get('type') == 'chord':
            pitches = []
            for p in ev.get('pitches', []):
                pitch_str = _pitch_to_lily(p['step'], p['octave'], p.get('alter', 0))
                pitches.append(pitch_str)
            token = f"<{' '.join(pitches)}>{dur_str}"
            # Add articulations and dynamics
            token = _add_articulations_and_dynamics(token, ev)
            lily_tokens.append(token)
        elif ev.get('type') == 'tuplet':
            # Handle tuplet: \tuplet N/D { note1 note2 ... }
            numerator = ev.get('numerator', 3)
            denominator = ev.get('denominator', 2)
            tuplet_notes = ev.get('notes', [])
            
            # Generate LilyPond notation for each note in tuplet
            tuplet_tokens = []
            for note_ev in tuplet_notes:
                if note_ev.get('type') == 'note':
                    note_ql = note_ev.get('ql', 1.0)
                    note_dur = _ql_to_lily_duration(note_ql)
                    pitch_str = _pitch_to_lily(
                        note_ev.get('step', 'c'),
                        note_ev.get('octave', 4),
                        note_ev.get('alter', 0)
                    )
                    note_token = f"{pitch_str}{note_dur}"
                    # Add articulations/dynamics to tuplet notes
                    note_token = _add_articulations_and_dynamics(note_token, note_ev)
                    tuplet_tokens.append(note_token)
                elif note_ev.get('type') == 'rest':
                    rest_ql = note_ev.get('ql', 1.0)
                    rest_dur = _ql_to_lily_duration(rest_ql)
                    tuplet_tokens.append(f"r{rest_dur}")
            
            # Construct tuplet notation
            tuplet_content = ' '.join(tuplet_tokens)
            lily_tokens.append(f"\\tuplet {numerator}/{denominator} {{ {tuplet_content} }}")
        elif ev.get('type') == 'chord':
            # Chord event - reconstruct <c e g> format from pitch list
            pitches_list = ev.get('pitches', [])
            pitch_strs = []
            for pitch_data in pitches_list:
                pitch_str = _pitch_to_lily(
                    pitch_data.get('step', 'c'),
                    pitch_data.get('octave', 4),
                    pitch_data.get('alter', 0)
                )
                pitch_strs.append(pitch_str)
            dur_str = _ql_to_lily_duration(ev.get('ql', 1.0))
            chord_notation = f"<{' '.join(pitch_strs)}>{dur_str}"
            lily_tokens.append(chord_notation)
        elif ev.get('type') == 'note':
            pitch_str = _pitch_to_lily(
                ev.get('step', 'c'),
                ev.get('octave', 4),
                ev.get('alter', 0)
            )
            token = f"{pitch_str}{dur_str}"
            # Add articulations and dynamics
            token = _add_articulations_and_dynamics(token, ev)
            lily_tokens.append(token)
    
    notes_content = ' '.join(lily_tokens)
    
    # Determine base pitch for \relative
    first_note = next((ev for ev in events if ev.get('type') in ['note', 'chord', 'tuplet']), None)
    if first_note:
        if first_note.get('type') == 'chord':
            first_octave = first_note['pitches'][0]['octave']
        elif first_note.get('type') == 'tuplet':
            # Get octave from first note in tuplet
            tuplet_notes = first_note.get('notes', [])
            if tuplet_notes and tuplet_notes[0].get('type') == 'note':
                first_octave = tuplet_notes[0].get('octave', 4)
            else:
                first_octave = 4
        else:
            first_octave = first_note.get('octave', 4)
        
        # Choose base pitch based on octave range
        if first_octave <= 3:
            base_pitch = "c"
        elif first_octave == 4:
            base_pitch = "c'"
        else:
            base_pitch = "c''"
    else:
        base_pitch = "c'"
    
    # Build directives
    directives = []
    
    if metadata:
        # Time signature
        if 'time_signature' in metadata:
            directives.append(f"\\time {metadata['time_signature']}")
        
        # Key signature
        if 'key_signature' in metadata:
            key_sig = metadata['key_signature']
            if isinstance(key_sig, dict):
                tonic = key_sig.get('tonic', 'c')
                mode = key_sig.get('mode', 'major')
                directives.append(f"\\key {tonic} \\{mode}")
        
        # Tempo
        if 'tempo' in metadata:
            tempo_data = metadata['tempo']
            if isinstance(tempo_data, dict):
                beat_duration = tempo_data.get('beat_duration', 4)
                bpm = tempo_data.get('bpm', 120)
                directives.append(f"\\tempo {beat_duration}={bpm}")
            elif isinstance(tempo_data, int):
                directives.append(f"\\tempo 4={tempo_data}")
    
    # Assemble complete snippet
    directives_str = ' '.join(directives)
    if directives_str:
        return f"\\relative {base_pitch} {{ {directives_str} {notes_content} }}"
    else:
        return f"\\relative {base_pitch} {{ {notes_content} }}"


def _ql_to_lily_duration(ql: float) -> str:
    """Convert quarter lengths to LilyPond duration."""
    duration_map = {
        4.0: '1',   # whole note
        3.0: '2.',  # dotted half
        2.0: '2',   # half note
        1.5: '4.',  # dotted quarter
        1.0: '4',   # quarter note
        0.75: '8.', # dotted eighth
        0.5: '8',   # eighth note
        0.25: '16', # sixteenth note
    }
    return duration_map.get(ql, '4')  # Default to quarter


def _add_articulations_and_dynamics(token: str, event: dict) -> str:
    """
    Add articulation marks and dynamics to a LilyPond note/chord token.
    
    Args:
        token: Base note/chord token (e.g., "c4" or "<c e g>4")
        event: Event dictionary with optional 'articulations' and 'dynamics' fields
        
    Returns:
        Token with articulations and dynamics appended
    """
    # Add articulations
    articulations = event.get('articulations', [])
    for artic in articulations:
        if artic == 'staccato':
            token += '-.'
        elif artic == 'tenuto':
            token += '--'
        elif artic == 'accent':
            token += '->'
        elif artic == 'marcato':
            token += '-^'
        elif artic == 'staccatissimo':
            token += '-!'
    
    # Add dynamics
    dynamics = event.get('dynamics')
    if dynamics:
        # LilyPond dynamics use backslash prefix
        token += f"\\{dynamics}"
    
    return token


def _pitch_to_lily(step: str, octave: int, alter: int) -> str:
    """Convert pitch components to LilyPond notation."""
    step_lower = step.lower()
    
    # Add accidental
    if alter == 1:
        step_lower += 'is'
    elif alter == -1:
        step_lower += 'es'
    elif alter == 2:
        step_lower += 'isis'
    elif alter == -2:
        step_lower += 'eses'
    
    # Add octave markers (LilyPond absolute octaves)
    if octave >= 4:
        # c4 and above: use ticks
        ticks = "'" * (octave - 3)
        return step_lower + ticks
    else:
        # Below c4: use commas
        commas = "," * (4 - octave)
        return step_lower + commas


def events_to_tinynotation(events, metadata=None):
    """
    Convert canonical event dictionaries to TinyNotation format for pitch resolution verification.
    
    TinyNotation shows absolute pitches (e.g., "C6" instead of "c''"), making it easy to verify
    that octave resolution is correct. This is critical for validating transformations.
    
    Example output: "tinynotation: 4/4 C64 D64 E64 F64 G62 F62"
    
    Args:
        events: List of event dictionaries (canonical format)
        metadata: Optional metadata dict with time/key info
        
    Returns:
        TinyNotation string showing absolute pitches with durations
    """
    if not events:
        return "tinynotation: 4/4 r1"
    
    tokens = []
    
    # Add time signature if available
    if metadata and 'time_signature' in metadata:
        tokens.append(metadata['time_signature'])
    else:
        tokens.append("4/4")
    
    # Convert events to tinynotation format
    for ev in events:
        ql = ev.get('ql', 1.0)
        
        if ev.get('type') == 'rest':
            dur_str = _ql_to_tinynotation_duration(ql)
            tokens.append(f"r{dur_str}")
            
        elif ev.get('type') == 'chord':
            # Chord: <C4 E4 G4>2
            pitches = []
            for p in ev.get('pitches', []):
                pitch_str = _pitch_to_tinynotation(p['step'], p['octave'], p.get('alter', 0))
                pitches.append(pitch_str)
            dur_str = _ql_to_tinynotation_duration(ql)
            tokens.append(f"<{' '.join(pitches)}>{dur_str}")
            
        elif ev.get('type') == 'note':
            # Note: C64 (C in octave 6, quarter note)
            step = ev.get('step', 'C')
            octave = ev.get('octave', 4)
            alter = ev.get('alter', 0)
            pitch_str = _pitch_to_tinynotation(step, octave, alter)
            dur_str = _ql_to_tinynotation_duration(ql)
            
            # Add grace note indicator
            if ev.get('is_grace'):
                tokens.append(f"{pitch_str}{dur_str}grace")
            else:
                tokens.append(f"{pitch_str}{dur_str}")
                
        elif ev.get('type') == 'tuplet':
            # Simplified tuplet representation
            tokens.append("[")
            for note_ev in ev.get('notes', []):
                if note_ev.get('type') == 'note':
                    step = note_ev.get('step', 'C')
                    octave = note_ev.get('octave', 4)
                    alter = note_ev.get('alter', 0)
                    pitch_str = _pitch_to_tinynotation(step, octave, alter)
                    note_ql = note_ev.get('ql', 1.0)
                    dur_str = _ql_to_tinynotation_duration(note_ql)
                    tokens.append(f"{pitch_str}{dur_str}")
            tokens.append("]")
    
    return "tinynotation: " + " ".join(tokens)


def _pitch_to_tinynotation(step, octave, alter=0):
    """
    Convert pitch to TinyNotation format (e.g., C#6, Bb3).
    
    Args:
        step: Note name (C, D, E, F, G, A, B)
        octave: Octave number (MIDI convention: C4 = middle C)
        alter: Semitone alteration (-1 = flat, 0 = natural, 1 = sharp)
    
    Returns:
        TinyNotation pitch string (e.g., "C6", "F#5", "Bb3")
    """
    step_upper = step.upper()
    
    # Add accidental
    if alter == 1:
        step_upper += "#"
    elif alter == -1:
        step_upper += "b"
    elif alter == 2:
        step_upper += "##"
    elif alter == -2:
        step_upper += "bb"
    
    return f"{step_upper}{octave}"


def _ql_to_tinynotation_duration(ql):
    """
    Convert quarterLength to TinyNotation duration suffix.
    
    Args:
        ql: Quarter length (1.0 = quarter note, 2.0 = half note, etc.)
    
    Returns:
        Duration string (e.g., "4", "2", "8", "1")
    """
    # Common durations
    if ql == 4.0:
        return "1"  # whole note
    elif ql == 2.0:
        return "2"  # half note
    elif ql == 1.0:
        return "4"  # quarter note
    elif ql == 0.5:
        return "8"  # eighth note
    elif ql == 0.25:
        return "16"  # sixteenth note
    elif ql == 0.125:
        return "32"  # thirty-second note
    elif ql == 3.0:
        return "2."  # dotted half
    elif ql == 1.5:
        return "4."  # dotted quarter
    elif ql == 0.75:
        return "8."  # dotted eighth
    elif ql == 0.375:
        return "16."  # dotted sixteenth
    else:
        # For other durations, approximate
        if ql >= 2.0:
            return "2"
        elif ql >= 1.0:
            return "4"
        elif ql >= 0.5:
            return "8"
        else:
            return "16"
