"""
Musical Transformations Module
===============================

This module provides reusable music21-based transformation functions for
melodic and harmonic manipulation. All transformations work on music21.stream.Part
objects and return new, independent Part objects (non-destructive).

Transformations Available:
- identity: Return independent copy
- transpose_part: Transpose by interval
- invert_part: Melodic inversion around center pitch
- retrograde_part: Reverse note order
- augment_part: Increase durations by factor
- diminish_part: Decrease durations by factor
- chordify_part: Convert to harmony (triadic chords)

Usage Example:
    from transformations import transpose_part, invert_part
    from music_data import data_to_part, extract_data_from_part
    
    # Transform a melody
    transposed = transpose_part(melody_part, 'P5')
    inverted = invert_part(melody_part, 'C4')
    
    # Extract back to event data
    transposed_events = extract_data_from_part(transposed)
"""

from typing import Union
import copy
import music21
from music21 import pitch, interval, note, chord, stream


# ============================================================================
# CORE TRANSFORMATIONS
# ============================================================================

def identity(part: stream.Part) -> stream.Part:
    """
    Return an independent copy of the part.
    
    Args:
        part: The music21 Part to copy
        
    Returns:
        A deep copy of the original part
        
    Example:
        >>> original = data_to_part(events)
        >>> copy = identity(original)
    """
    return copy.deepcopy(part)


def transpose_part(part: stream.Part, interval_str: str) -> stream.Part:
    """
    Transpose the part by a musical interval.
    
    Args:
        part: The music21 Part to transpose
        interval_str: Interval notation (e.g., 'P5', 'm3', 'M2', '-P8')
                     Prefix with '-' for downward transposition
        
    Returns:
        A new Part transposed by the specified interval
        
    Example:
        >>> # Transpose up a perfect fifth
        >>> transposed = transpose_part(melody, 'P5')
        >>> 
        >>> # Transpose down an octave
        >>> lower = transpose_part(melody, '-P8')
    """
    return part.transpose(interval_str)


def invert_part(part: stream.Part, center_pitch: str) -> stream.Part:
    """
    Invert pitches around a center pitch (melodic inversion).
    
    This creates a mirror image of the melody around the specified center pitch.
    Intervals are inverted: ascending becomes descending, and vice versa.
    
    Args:
        part: The music21 Part to invert
        center_pitch: The pivot pitch for inversion (e.g., 'C4', 'G5')
        
    Returns:
        A new Part with inverted pitches
        
    Example:
        >>> # Invert around middle C
        >>> inverted = invert_part(melody, 'C4')
        >>> 
        >>> # If original has C4→E4 (up M3), inverted has C4→Ab3 (down M3)
    """
    p = copy.deepcopy(part)
    center = pitch.Pitch(center_pitch)
    notes = list(p.recurse().getElementsByClass(note.Note))
    
    for n in notes:
        try:
            # Calculate interval from center to note
            iv = interval.Interval(noteStart=center, noteEnd=n.pitch)
            # Get the complement (inverted interval)
            inv = iv.complement
            # Apply inverted interval from center
            n.pitch = center.transpose(inv)
        except Exception:
            # If inversion fails, keep original pitch
            continue
    
    return p


def retrograde_part(part: stream.Part) -> stream.Part:
    """
    Reverse the order of notes and rests (retrograde/cancrizans).
    
    This creates a "backwards" version of the melody, preserving all
    pitches and durations but reversing their temporal order.
    
    Args:
        part: The music21 Part to reverse
        
    Returns:
        A new Part with reversed note order
        
    Example:
        >>> # If original is C-D-E-F, retrograde is F-E-D-C
        >>> reversed_melody = retrograde_part(melody)
    """
    p = copy.deepcopy(part)
    elems = [e for e in p.recurse().notesAndRests]
    
    # Create new part with reversed elements
    newp = stream.Part()
    for e in reversed(elems):
        try:
            # Try to use clone() for efficiency
            newp.append(e.clone())
        except Exception:
            # Fall back to deep copy if clone fails
            newp.append(copy.deepcopy(e))
    
    return newp


def augment_part(part: stream.Part, factor: float = 2.0) -> stream.Part:
    """
    Augment durations by a factor (rhythmic augmentation).
    
    All note and rest durations are multiplied by the specified factor.
    This creates a slower version of the melody.
    
    Args:
        part: The music21 Part to augment
        factor: Multiplication factor (default: 2.0 = double durations)
        
    Returns:
        A new Part with augmented durations
        
    Example:
        >>> # Double all durations (quarter notes become half notes)
        >>> augmented = augment_part(melody, 2.0)
        >>> 
        >>> # Triple durations
        >>> triple = augment_part(melody, 3.0)
    """
    p = copy.deepcopy(part)
    for n in p.flat.notesAndRests:
        n.quarterLength *= factor
    return p


def diminish_part(part: stream.Part, factor: float = 2.0) -> stream.Part:
    """
    Diminish durations by a factor (rhythmic diminution).
    
    All note and rest durations are divided by the specified factor.
    This creates a faster version of the melody.
    
    Args:
        part: The music21 Part to diminish
        factor: Division factor (default: 2.0 = half durations)
        
    Returns:
        A new Part with diminished durations
        
    Example:
        >>> # Halve all durations (half notes become quarter notes)
        >>> diminished = diminish_part(melody, 2.0)
        >>> 
        >>> # Quarter durations (twice as fast)
        >>> faster = diminish_part(melody, 4.0)
    """
    p = copy.deepcopy(part)
    for n in p.flat.notesAndRests:
        n.quarterLength /= factor
    return p


# ============================================================================
# HARMONIC TRANSFORMATIONS
# ============================================================================

def chordify_part(part: stream.Part, chord_type: str = 'major') -> stream.Part:
    """
    Convert melody to harmony by adding thirds and fifths (chordification).
    
    Each note is transformed into a three-note chord (triad) by adding
    a third and fifth above the original pitch. Rests are preserved.
    
    Args:
        part: The music21 Part to harmonize
        chord_type: Type of chord to build ('major' or 'minor')
                   Default: 'major' (root + M3 + P5)
        
    Returns:
        A new Part with chords instead of single notes
        
    Example:
        >>> # Harmonize with major triads
        >>> harmony = chordify_part(melody)
        >>> 
        >>> # If melody has C4, chord becomes [C4, E4, G4]
    """
    harmonized = stream.Part()
    
    # Determine intervals based on chord type
    if chord_type == 'minor':
        third_interval = 'm3'  # Minor third
        fifth_interval = 'P5'  # Perfect fifth
    else:  # major (default)
        third_interval = 'M3'  # Major third
        fifth_interval = 'P5'  # Perfect fifth
    
    for el in part.flatten().notesAndRests:
        if isinstance(el, note.Rest):
            # Preserve rests as-is
            harmonized.append(copy.deepcopy(el))
        elif isinstance(el, note.Note):
            # Create a triad from the note
            root = el.pitch
            third = root.transpose(third_interval)
            fifth = root.transpose(fifth_interval)
            
            # Build chord with same duration as original note
            triad = chord.Chord(
                [root, third, fifth],
                quarterLength=el.quarterLength
            )
            harmonized.append(triad)
    
    return harmonized


# ============================================================================
# COMPOUND TRANSFORMATIONS
# ============================================================================

def retrograde_inversion(part: stream.Part, center_pitch: str) -> stream.Part:
    """
    Apply both retrograde and inversion (retrograde inversion).
    
    This is a compound transformation: first inverts the melody around
    the center pitch, then reverses the order of notes.
    
    Args:
        part: The music21 Part to transform
        center_pitch: The pivot pitch for inversion
        
    Returns:
        A new Part with retrograde inversion applied
        
    Example:
        >>> # Classical 12-tone technique
        >>> ri = retrograde_inversion(melody, 'C4')
    """
    inverted = invert_part(part, center_pitch)
    return retrograde_part(inverted)


def transpose_and_augment(part: stream.Part, interval_str: str, factor: float = 2.0) -> stream.Part:
    """
    Transpose and augment in one operation.
    
    Useful for creating variations that are both higher/lower and slower.
    
    Args:
        part: The music21 Part to transform
        interval_str: Transposition interval (e.g., 'P5')
        factor: Augmentation factor (default: 2.0)
        
    Returns:
        A new Part transposed and augmented
        
    Example:
        >>> # Up a fifth and twice as slow
        >>> variation = transpose_and_augment(melody, 'P5', 2.0)
    """
    transposed = transpose_part(part, interval_str)
    return augment_part(transposed, factor)


# ============================================================================
# HARMONIC INTELLIGENCE TRANSFORMATIONS
# ============================================================================

def harmonize_part(melody_part: stream.Part, progression_string: str, key: str = 'C') -> stream.Score:
    """
    Generate harmonic accompaniment (bass line) for a melody.
    
    Uses harmonic intelligence to analyze structural tones in the melody
    and fit a chord progression, then generates a bass line that follows
    the harmonic structure.
    
    Args:
        melody_part: music21.stream.Part containing the melody
        progression_string: Chord progression in Roman numeral notation
                           Examples: "I-IV-V-I", "I-vi-IV-V", "I-IV-I-V-I"
        key: Key signature for the progression (e.g., "C", "Dm", "G")
    
    Returns:
        music21.stream.Score with two parts:
        - Part 0 (.id = 'melody'): Original melody (possibly with harmonic analysis annotations)
        - Part 1 (.id = 'harmony'): Generated bass line
    
    Example Blueprint Usage:
        VOICE_STAVE_DEF = "Melody & Bass"
        
        VOICE_STAVE_DATA = '''
            harmonize_part(THEME, 'I-IV-V-I', 'C'):melody
            &
            harmonize_part(THEME, 'I-IV-V-I', 'C'):harmony
        '''
    
    Note:
        This transformation returns a Score (multi-part) instead of a Part.
        When used in Blueprint Strings, you MUST use the :melody or :harmony
        suffix to specify which part you want for each staff.
    """
    try:
        from harmonic_engine import harmonize_melody
    except ImportError:
        raise ImportError(
            "Harmonic intelligence system not available. "
            "Check that harmonic_engine.py and harmonic_analysis.py are present."
        )
    
    # Generate harmonization using harmonic intelligence
    harmonized_score = harmonize_melody(
        melody_part=melody_part,
        progression_string=progression_string,
        key=key,
        harmonic_rhythm="auto"  # Automatically distribute chords
    )
    
    # SET PART IDs (CRITICAL for hybrid suffix model)
    harmonized_score.parts[0].id = 'melody'
    harmonized_score.parts[1].id = 'harmony'
    
    return harmonized_score


def analyze_structural_tones(melody_part: stream.Part) -> stream.Part:
    """
    Identify structural vs. ornamental tones in a melody.
    
    Structural tones are melodic notes that define the harmonic framework:
    - Fall on strong beats (beat 1, or beat 3 in 4/4 time)
    - Have longer durations (quarter note or longer)
    - Form the "skeleton" that harmonies can be aligned with
    
    Ornamental tones embellish the structural framework with passing tones,
    neighbor tones, and other decorative elements.
    
    Args:
        melody_part: music21.stream.Part containing the melody
    
    Returns:
        music21.stream.Part with structural tones annotated in the
        editorial namespace (element.editorial.structural = True/False)
    
    Example:
        >>> melody = data_to_part(melody_events)
        >>> analyzed = analyze_structural_tones(melody)
        >>> 
        >>> # Get only structural notes
        >>> from harmonic_analysis import get_structural_notes
        >>> structural = get_structural_notes(analyzed)
        >>> for note in structural:
        ...     print(f"{note.nameWithOctave} on beat {note.beat}")
    
    Note:
        This is primarily useful in Station 4 (programmatic mode) for
        advanced harmonic analysis. The harmonize_part() function uses
        this analysis automatically.
    """
    try:
        from harmonic_analysis import find_structural_tones
    except ImportError:
        raise ImportError(
            "Harmonic analysis system not available. "
            "Check that harmonic_analysis.py is present."
        )
    
    return find_structural_tones(melody_part)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_transformation_name(func) -> str:
    """
    Get a human-readable name for a transformation function.
    
    Args:
        func: The transformation function
        
    Returns:
        Descriptive name string
    """
    names = {
        identity: 'Identity',
        transpose_part: 'Transposition',
        invert_part: 'Melodic Inversion',
        retrograde_part: 'Retrograde',
        augment_part: 'Augmentation',
        diminish_part: 'Diminution',
        chordify_part: 'Chordification',
        retrograde_inversion: 'Retrograde Inversion',
        transpose_and_augment: 'Transposition + Augmentation',
        harmonize_part: 'Harmonization',
        analyze_structural_tones: 'Structural Tone Analysis',
    }
    return names.get(func, func.__name__)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Core transformations
    'identity',
    'transpose_part',
    'invert_part',
    'retrograde_part',
    'augment_part',
    'diminish_part',
    
    # Harmonic transformations
    'chordify_part',
    
    # Compound transformations
    'retrograde_inversion',
    'transpose_and_augment',
    
    # Harmonic intelligence
    'harmonize_part',
    'analyze_structural_tones',
    
    # Utilities
    'get_transformation_name',
]
