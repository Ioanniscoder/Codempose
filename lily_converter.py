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
        ql = ev.get('ql', 1.0)
        dur_str = _ql_to_lily_duration(ql)
        
        if ev.get('type') == 'rest':
            lily_tokens.append(f"r{dur_str}")
        elif ev.get('type') == 'chord':
            pitches = []
            for p in ev.get('pitches', []):
                pitch_str = _pitch_to_lily(p['step'], p['octave'], p.get('alter', 0))
                pitches.append(pitch_str)
            lily_tokens.append(f"<{' '.join(pitches)}>{dur_str}")
        elif ev.get('type') == 'note':
            pitch_str = _pitch_to_lily(
                ev.get('step', 'c'),
                ev.get('octave', 4),
                ev.get('alter', 0)
            )
            lily_tokens.append(f"{pitch_str}{dur_str}")
    
    notes_content = ' '.join(lily_tokens)
    
    # Determine base pitch for \relative
    first_note = next((ev for ev in events if ev.get('type') in ['note', 'chord']), None)
    if first_note:
        if first_note.get('type') == 'chord':
            first_octave = first_note['pitches'][0]['octave']
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
