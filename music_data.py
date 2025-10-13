# music_data.py
import music21
from typing import List, Optional

def extract_data_from_part(part: music21.stream.Part, token_infos: Optional[List] = None):
    """Converts a music21.Part into a list of canonical event dictionaries.
    
    Now supports Chord objects in addition to Notes and Rests.
    
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

def data_to_part(events: list, metadata: dict = None) -> music21.stream.Part:
    """Converts a list of canonical event dictionaries back into a music21.Part.
    
    Now supports chord events in addition to notes and rests.
    """
    part = music21.stream.Part()
    for ev in events:
        ql = ev.get('ql', 1.0)
        if ev.get('type') == 'rest':
            el = music21.note.Rest(quarterLength=ql)
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
        else:
            continue
        part.append(el)
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
