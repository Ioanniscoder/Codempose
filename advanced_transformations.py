"""
Advanced Transformations Library
=================================

This module provides complex, music-theory-aware transformation functions
designed for programmatic use within the hybrid model.

These functions:
- Accept complex arguments (lists, dictionaries, context information)
- Implement sophisticated music theory algorithms
- Leverage the full power of music21's API
- Are called directly from Python code (e.g., in build_score_data())

For simple transformations suitable for shorthand strings,
use composition_shorthand.py instead.
"""

from typing import List, Dict, Any
from music21 import stream, pitch, note, chord
from composition_shorthand import transpose_events


def create_melodic_sequence(
    events: List[Dict[str, Any]],
    interval_pattern: List[int],
    key: str = 'C major',
    preserve_rhythm: bool = True
) -> List[Dict[str, Any]]:
    """
    Creates a melodic sequence from a list of events.

    A melodic sequence repeats a musical fragment at different pitch levels.
    This is a fundamental technique in tonal composition.

    Args:
        events: The original melodic fragment (list of event dictionaries)
        interval_pattern: List of semitone intervals for each repetition
                         e.g., [-2, -2, 2] = down a step, down a step, up a step
        key: Key context for the sequence (default: 'C major')
        preserve_rhythm: If True, keeps original rhythms; if False, can modify

    Returns:
        List of events containing the full melodic sequence

    Example:
        >>> theme_events = [
        ...     {'type': 'note', 'step': 'C', 'octave': 4, 'alter': 0, 'ql': 1.0},
        ...     {'type': 'note', 'step': 'E', 'octave': 4, 'alter': 0, 'ql': 1.0}
        ... ]
        >>> sequence = create_melodic_sequence(
        ...     theme_events,
        ...     interval_pattern=[-2, -2, 2],
        ...     key='C major'
        ... )
        # Returns: C-E, then Bb-D, then Ab-C, then Bb-D (transposed fragments)
    """
    # Start with the original fragment
    full_sequence = events[:]

    # For each interval in the pattern, transpose and add
    for semitones in interval_pattern:
        # Transpose the entire pattern by the interval
        transposed_fragment = transpose_events(events, semitones)

        # Optionally modify rhythm for variety
        if not preserve_rhythm:
            for ev in transposed_fragment:
                if 'ql' in ev:
                    ev['ql'] *= 0.75  # Slightly shorter each time

        full_sequence.extend(transposed_fragment)

    return full_sequence


def realize_figured_bass(
    bass_events: List[Dict[str, Any]],
    figures: str,
    num_voices: int = 4
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Realizes a figured bass line into full harmony (upper voices).

    This is a placeholder implementation that provides a basic framework.
    A full implementation would use music21's figuredBass module extensively.

    Args:
        bass_events: List of bass note events
        figures: Figured bass notation string (e.g., "6 6 5 6/4 3")
        num_voices: Number of voices to generate (default: 4 for SATB)

    Returns:
        Dictionary mapping voice names to event lists, e.g.,
        {'Soprano': [...], 'Alto': [...], 'Tenor': [...], 'Bass': [...]})

    Example:
        >>> bass_line = [
        ...     {'type': 'note', 'step': 'C', 'octave': 3, 'alter': 0, 'ql': 4.0}
        ... ]
        >>> harmony = realize_figured_bass(bass_line, figures="5/3")
        # Returns SATB voices with C major triad

    Note:
        This is a template function. Full figured bass realization is complex
        and requires extensive music theory rules. This implementation provides
        a basic structure that can be enhanced with music21's figuredBass module.
    """
    # Parse figures (simplified - actual parsing would be more complex)
    figure_tokens = figures.split()

    # Initialize voice parts
    voices = {
        'Soprano': [],
        'Alto': [],
        'Tenor': [],
        'Bass': bass_events[:]  # Bass is the given line
    }

    # For each bass note, generate upper voices
    for i, bass_event in enumerate(bass_events):
        if bass_event['type'] != 'note':
            # For rests, add rests to all voices
            for voice_name in ['Soprano', 'Alto', 'Tenor']:
                voices[voice_name].append(bass_event.copy())
            continue

        # Get the figure for this note (cycle through if needed)
        figure = figure_tokens[i % len(figure_tokens)] if figure_tokens else "5/3"

        # Create a simple chord based on the figure
        # This is a simplified implementation - a full version would use music21.figuredBass
        bass_pitch = pitch.Pitch()
        bass_pitch.step = bass_event['step']
        bass_pitch.octave = bass_event['octave']
        if bass_event.get('alter', 0) != 0:
            bass_pitch.accidental = pitch.Accidental(bass_event['alter'])

        # Generate upper voices (simple triadic harmony as example)
        if figure in ["5/3", "3", ""]:  # Root position triad
            # Simple triad: root, third, fifth
            intervals_from_bass = [0, 4, 7]  # Root, major third, perfect fifth
        elif figure in ["6", "6/3"]:  # First inversion
            intervals_from_bass = [0, 3, 8]  # Third in bass
        elif figure in ["6/4", "4/6"]:  # Second inversion
            intervals_from_bass = [0, 5, 9]  # Fifth in bass
        else:
            # Default to simple triad
            intervals_from_bass = [0, 4, 7]

        # Create notes for each voice
        soprano_pitch = bass_pitch.transpose(intervals_from_bass[2] + 12)  # Up an octave + interval
        alto_pitch = bass_pitch.transpose(intervals_from_bass[1] + 12)
        tenor_pitch = bass_pitch.transpose(intervals_from_bass[0] + 12)

        # Add to voice events
        voices['Soprano'].append({
            'type': 'note',
            'step': soprano_pitch.step,
            'octave': soprano_pitch.octave,
            'alter': soprano_pitch.accidental.alter if soprano_pitch.accidental else 0,
            'ql': bass_event['ql']
        })

        voices['Alto'].append({
            'type': 'note',
            'step': alto_pitch.step,
            'octave': alto_pitch.octave,
            'alter': alto_pitch.accidental.alter if alto_pitch.accidental else 0,
            'ql': bass_event['ql']
        })

        voices['Tenor'].append({
            'type': 'note',
            'step': tenor_pitch.step,
            'octave': tenor_pitch.octave,
            'alter': tenor_pitch.accidental.alter if tenor_pitch.accidental else 0,
            'ql': bass_event['ql']
        })

    return voices


def apply_modal_mixture(
    events: List[Dict[str, Any]],
    key: str = 'C major',
    borrow_from: str = 'parallel_minor'
) -> List[Dict[str, Any]]:
    """
    Applies modal mixture by borrowing notes from a parallel mode.

    Modal mixture (or modal interchange) involves using notes from the
    parallel key (e.g., borrowing from C minor while in C major).

    Args:
        events: List of note/chord events
        key: The original key (e.g., 'C major')
        borrow_from: Which mode to borrow from ('parallel_minor' or 'parallel_major')

    Returns:
        Modified list of events with borrowed notes

    Example:
        >>> melody = [
        ...     {'type': 'note', 'step': 'E', 'octave': 4, 'alter': 0, 'ql': 1.0},
        ...     {'type': 'note', 'step': 'A', 'octave': 4, 'alter': 0, 'ql': 1.0}
        ... ]
        >>> borrowed = apply_modal_mixture(melody, key='C major', borrow_from='parallel_minor')
        # Might lower E to Eb and A to Ab (from C minor)

    Note:
        This is a simplified implementation. True modal mixture requires
        understanding of harmonic context and voice leading.
    """
    from music21 import key as m21key

    # Parse the key
    key_obj = m21key.Key(key)

    # Determine what to borrow from
    if borrow_from == 'parallel_minor' and key_obj.mode == 'major':
        # Create the parallel minor key
        parallel_key = m21key.Key(key_obj.tonic, 'minor')
    elif borrow_from == 'parallel_major' and key_obj.mode == 'minor':
        # Create the parallel major key
        parallel_key = m21key.Key(key_obj.tonic, 'major')
    else:
        # No change needed
        return events[:]

    # Get the scale alterations
    original_scale = key_obj.getScale()
    parallel_scale = parallel_key.getScale()

    # Create a mapping of which degrees are different
    alterations = {}
    for degree in range(1, 8):
        orig_pitch = original_scale.pitchFromDegree(degree)
        parallel_pitch = parallel_scale.pitchFromDegree(degree)

        if orig_pitch.pitchClass != parallel_pitch.pitchClass:
            # This degree differs between major and minor
            alterations[orig_pitch.step] = parallel_pitch.pitchClass - orig_pitch.pitchClass

    # Apply alterations to events (selectively - not to every note)
    new_events = []
    for i, ev in enumerate(events):
        new_ev = ev.copy()

        if ev['type'] == 'note':
            # Only alter some notes (e.g., scale degrees 3, 6, 7)
            # This is simplified - real implementation would be context-aware
            if ev['step'] in alterations and i % 2 == 0:  # Alter every other occurrence
                new_ev['alter'] = new_ev.get('alter', 0) + alterations[ev['step']]

        new_events.append(new_ev)

    return new_events


def _events_to_part(events: List[Dict[str, Any]]) -> stream.Part:
    """
    Helper function to convert event dictionaries to a music21 Part.

    Args:
        events: List of event dictionaries

    Returns:
        music21.stream.Part object
    """
    part = stream.Part()

    for ev in events:
        if ev['type'] == 'note':
            p = pitch.Pitch()
            p.step = ev['step']
            p.octave = ev['octave']
            if ev.get('alter', 0) != 0:
                p.accidental = pitch.Accidental(ev['alter'])

            n = note.Note(p, quarterLength=ev.get('ql', 1.0))
            part.append(n)

        elif ev['type'] == 'rest':
            r = note.Rest(quarterLength=ev.get('ql', 1.0))
            part.append(r)

        elif ev['type'] == 'chord':
            pitches = []
            for p_data in ev.get('pitches', []):
                p = pitch.Pitch()
                p.step = p_data['step']
                p.octave = p_data['octave']
                if p_data.get('alter', 0) != 0:
                    p.accidental = pitch.Accidental(p_data['alter'])
                pitches.append(p)

            c = chord.Chord(pitches, quarterLength=ev.get('ql', 1.0))
            part.append(c)

    return part


def _part_to_events(part: stream.Part) -> List[Dict[str, Any]]:
    """
    Helper function to convert a music21 Part to event dictionaries.

    Args:
        part: music21.stream.Part object

    Returns:
        List of event dictionaries
    """
    events = []

    for el in part.flatten().notesAndRests:
        if isinstance(el, note.Note):
            event = {
                'type': 'note',
                'step': el.pitch.step,
                'octave': el.pitch.octave,
                'alter': el.pitch.accidental.alter if el.pitch.accidental else 0,
                'ql': el.quarterLength
            }
            events.append(event)

        elif isinstance(el, note.Rest):
            event = {
                'type': 'rest',
                'ql': el.quarterLength
            }
            events.append(event)

        elif isinstance(el, chord.Chord):
            event = {
                'type': 'chord',
                'ql': el.quarterLength,
                'pitches': []
            }
            for p in el.pitches:
                pitch_data = {
                    'step': p.step,
                    'octave': p.octave,
                    'alter': p.accidental.alter if p.accidental else 0
                }
                event['pitches'].append(pitch_data)
            events.append(event)

    return events
