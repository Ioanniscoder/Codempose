"""
Composition Shorthand Extensions
=================================

This module provides simple, callable functions for the composition shorthand
string parser. These functions have clear, simple arguments suitable for
integration into a shorthand DSL.

Functions in this module should:
- Accept simple argument types (strings, numbers, lists of events)
- Return lists of event dictionaries
- Be easily parseable from shorthand strings

For complex, multi-faceted transformations requiring context awareness,
use the advanced_transformations.py module instead.
"""

from typing import List, Dict, Any
from music21 import roman, key, pitch


def from_roman_numerals(progression_str: str, key_str: str, rhythm_str: str) -> List[Dict[str, Any]]:
    """
    Generates a list of chord events from a Roman numeral string.

    This function is designed to be called by the shorthand parser.

    Args:
        progression_str: Roman numerals separated by dashes, e.g., "I-V65-i"
        key_str: Key specification, e.g., "C" for C major, "c" for c minor
        rhythm_str: Rhythm durations separated by dashes, e.g., "w-h-h" or "4-2-2"

    Returns:
        List of chord event dictionaries in canonical format

    Example:
        >>> events = from_roman_numerals("I-V-vi-IV", "C", "w-w-w-w")
        # Returns chord events for C major, G major, A minor, F major
    """
    # Parse the key string
    key_obj = key.Key(key_str)

    # Split the progression and rhythm strings
    roman_numerals = progression_str.split('-')
    rhythms = rhythm_str.split('-')

    # Ensure we have enough rhythms (repeat last if needed)
    while len(rhythms) < len(roman_numerals):
        rhythms.append(rhythms[-1])

    # Generate chord events
    chord_events = []
    for rn_str, rhythm in zip(roman_numerals, rhythms):
        # Create a music21 RomanNumeral object
        rn = roman.RomanNumeral(rn_str, key_obj)

        # Parse the duration
        ql = _parse_rhythm_token(rhythm)

        # Convert the chord to event dictionary format
        chord_event = {
            'type': 'chord',
            'ql': ql,
            'pitches': []
        }

        for p in rn.pitches:
            pitch_data = {
                'step': p.step,
                'alter': p.accidental.alter if p.accidental else 0,
                'octave': p.octave
            }
            chord_event['pitches'].append(pitch_data)

        chord_events.append(chord_event)

    return chord_events


def from_scale_degrees(degree_str: str, key_str: str, rhythm_str: str) -> List[Dict[str, Any]]:
    """
    Generates a list of note events from a string of scale degrees.

    Args:
        degree_str: Scale degrees separated by dashes, e.g., "1-7-1-5-6-4-5"
        key_str: Key specification, e.g., "A" for A major, "a" for a minor
        rhythm_str: Rhythm durations separated by dashes, e.g., "q-e-e-q-q-q-h"

    Returns:
        List of note event dictionaries in canonical format

    Example:
        >>> events = from_scale_degrees("1-2-3-4-5", "C", "q-q-q-q-q")
        # Returns C, D, E, F, G quarter notes in C major
    """
    # Create a music21 key object
    key_obj = key.Key(key_str)

    # Get the scale from the key
    scale_obj = key_obj.getScale()

    # Split the degree and rhythm strings
    degrees = degree_str.split('-')
    rhythms = rhythm_str.split('-')

    # Ensure we have enough rhythms (repeat last if needed)
    while len(rhythms) < len(degrees):
        rhythms.append(rhythms[-1])

    # Generate note events
    note_events = []
    for degree, rhythm in zip(degrees, rhythms):
        # Parse the degree (handle "r" for rest)
        if degree.lower() == 'r':
            ql = _parse_rhythm_token(rhythm)
            note_events.append({
                'type': 'rest',
                'ql': ql
            })
            continue

        # Get the pitch from the scale degree
        degree_int = int(degree)
        p = scale_obj.pitchFromDegree(degree_int)

        # Parse the duration
        ql = _parse_rhythm_token(rhythm)

        # Convert to event dictionary
        note_event = {
            'type': 'note',
            'step': p.step,
            'alter': p.accidental.alter if p.accidental else 0,
            'octave': p.octave,
            'ql': ql
        }

        note_events.append(note_event)

    return note_events


def stretch_events(events: List[Dict[str, Any]], multiplier: float) -> List[Dict[str, Any]]:
    """
    Multiplies the 'ql' (quarterLength) of all events in a list.

    This is useful for rhythmic augmentation (multiplier > 1) or
    diminution (multiplier < 1).

    Args:
        events: List of event dictionaries
        multiplier: Factor by which to multiply durations

    Returns:
        New list of events with modified durations

    Example:
        >>> theme = [{'type': 'note', 'step': 'C', 'octave': 4, 'ql': 1.0}]
        >>> augmented = stretch_events(theme, 2.0)  # Double the duration
        >>> diminished = stretch_events(theme, 0.5)  # Half the duration
    """
    new_events = []
    for ev in events:
        new_ev = ev.copy()
        if 'ql' in new_ev:
            new_ev['ql'] *= multiplier
        new_events.append(new_ev)
    return new_events


def transpose_events(events: List[Dict[str, Any]], semitones: int) -> List[Dict[str, Any]]:
    """
    Transposes all note and chord events by a given number of semitones.

    This is a helper function that can be used by other transformation functions.

    Args:
        events: List of event dictionaries
        semitones: Number of semitones to transpose (positive = up, negative = down)

    Returns:
        New list of transposed events

    Example:
        >>> melody = [{'type': 'note', 'step': 'C', 'octave': 4, 'alter': 0, 'ql': 1.0}]
        >>> transposed = transpose_events(melody, 7)  # Transpose up a perfect fifth
    """
    new_events = []

    for ev in events:
        new_ev = ev.copy()

        if ev['type'] == 'note':
            # Create a music21 pitch from the event data
            p = pitch.Pitch()
            p.step = ev['step']
            p.octave = ev['octave']
            if ev.get('alter', 0) != 0:
                p.accidental = pitch.Accidental(ev['alter'])

            # Transpose
            transposed_pitch = p.transpose(semitones)

            # Update the event
            new_ev['step'] = transposed_pitch.step
            new_ev['octave'] = transposed_pitch.octave
            new_ev['alter'] = transposed_pitch.accidental.alter if transposed_pitch.accidental else 0

        elif ev['type'] == 'chord':
            # Transpose each pitch in the chord
            new_pitches = []
            for p_data in ev.get('pitches', []):
                p = pitch.Pitch()
                p.step = p_data['step']
                p.octave = p_data['octave']
                if p_data.get('alter', 0) != 0:
                    p.accidental = pitch.Accidental(p_data['alter'])

                transposed_pitch = p.transpose(semitones)

                new_pitches.append({
                    'step': transposed_pitch.step,
                    'octave': transposed_pitch.octave,
                    'alter': transposed_pitch.accidental.alter if transposed_pitch.accidental else 0
                })

            new_ev['pitches'] = new_pitches

        new_events.append(new_ev)

    return new_events


def _parse_rhythm_token(rhythm: str) -> float:
    """
    Helper function to parse rhythm tokens into quarterLength values.

    Supports common abbreviations:
    - 'w' or '1' = whole note (4.0 ql)
    - 'h' or '2' = half note (2.0 ql)
    - 'q' or '4' = quarter note (1.0 ql)
    - 'e' or '8' = eighth note (0.5 ql)
    - '16' = sixteenth note (0.25 ql)
    - '32' = thirty-second note (0.125 ql)

    Args:
        rhythm: Rhythm token string

    Returns:
        Quarter length as a float
    """
    rhythm = rhythm.strip().lower()

    # Map common abbreviations
    rhythm_map = {
        'w': 4.0,
        'h': 2.0,
        'q': 1.0,
        'e': 0.5,
        's': 0.25,  # sixteenth
    }

    if rhythm in rhythm_map:
        return rhythm_map[rhythm]

    # Try to parse as a duration number (1, 2, 4, 8, 16, 32)
    try:
        dur_num = int(rhythm)
        return 4.0 / dur_num
    except ValueError:
        # Default to quarter note
        return 1.0


# Convenience aliases for augmentation/diminution
def augment(events: List[Dict[str, Any]], multiplier: float = 2.0) -> List[Dict[str, Any]]:
    """
    Augment (lengthen) the durations of events.
    Default multiplier is 2.0 (double the duration).

    Args:
        events: List of event dictionaries
        multiplier: Factor by which to multiply durations (default: 2.0)

    Returns:
        New list of events with augmented durations
    """
    return stretch_events(events, multiplier)


def diminish(events: List[Dict[str, Any]], multiplier: float = 0.5) -> List[Dict[str, Any]]:
    """
    Diminish (shorten) the durations of events.
    Default multiplier is 0.5 (half the duration).

    Args:
        events: List of event dictionaries
        multiplier: Factor by which to multiply durations (default: 0.5)

    Returns:
        New list of events with diminished durations
    """
    return stretch_events(events, multiplier)
