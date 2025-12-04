"""
harmonic_analysis.py - Structural Tone Analysis for Tonal Harmony

This module provides tools to analyze melodies and identify structural vs.
ornamental tones based on principles from "Tonal Harmony with an Introduction
to Twentieth-Century Music" textbook.

Structural tones are the melodic notes that define the harmonic framework,
while ornamental tones (passing tones, neighbor tones, etc.) embellish the
structural framework.

Usage:
    from harmonic_analysis import find_structural_tones, print_structural_analysis
    
    # Analyze a melody
    analyzed_part = find_structural_tones(melody_part)
    
    # Print results to console
    print_structural_analysis(analyzed_part)
"""

from music21 import stream, note, meter
from typing import List, Tuple


def find_structural_tones(melody_part: stream.Part) -> stream.Part:
    """
    Analyze a melody and tag each note as structural or ornamental.
    
    This function applies basic rules from tonal harmony theory to identify
    which notes are structurally important:
    
    Rules for Structural Tones:
    1. Strong beat position (beat 1 in any meter, beat 3 in 4/4 or 4/2)
    2. Long duration (quarter note or longer in simple meters)
    3. First note of a measure (downbeat)
    
    The function modifies notes in place by adding a custom attribute:
        note.is_structural = True or False
    
    Args:
        melody_part: music21.stream.Part containing the melody to analyze
        
    Returns:
        The modified Part with all notes tagged (same object, modified in place)
        
    Example:
        >>> from music21 import converter
        >>> melody = converter.parse("tinynotation: 4/4 c4 d8 e8 f4 g2")
        >>> analyzed = find_structural_tones(melody.parts[0])
        >>> for n in analyzed.flatten().notes:
        ...     print(f"{n.nameWithOctave}: {n.is_structural}")
        C4: True   (strong beat + quarter note)
        D4: False  (weak beat + eighth note)
        E4: False  (weak beat + eighth note)
        F4: True   (strong beat + quarter note)
        G4: True   (long duration)
    """
    # Check if Part has measures or if notes are directly in Part
    measures = melody_part.getElementsByClass('Measure')
    
    if measures:
        # Process each measure separately
        for measure in measures:
            # Get or infer time signature for this measure
            time_sig = measure.timeSignature
            if not time_sig:
                # Look for time signature in earlier measures or use default
                time_sig = melody_part.getTimeSignatures()[0] if melody_part.getTimeSignatures() else meter.TimeSignature('4/4')
            
            # Determine which beats are strong based on time signature
            strong_beats = _get_strong_beats(time_sig)
            
            # Analyze each note in the measure
            for element in measure.notes:
                if isinstance(element, note.Note):
                    # Get beat position (music21 uses 1-based beat numbering)
                    beat_position = element.beat
                    
                    # Check if note is on a strong beat
                    is_strong_beat = beat_position in strong_beats
                    
                    # Check if note has long duration (quarter note or longer)
                    is_long_duration = element.quarterLength >= 1.0
                    
                    # Tag the note as structural or ornamental
                    # Structural if: strong beat OR long duration
                    element.is_structural = (is_strong_beat or is_long_duration)
                
                elif isinstance(element, note.Rest):
                    # Rests are not structural tones
                    element.is_structural = False
    else:
        # Notes are directly in Part (no measures)
        # Use offset-based analysis
        time_sig = melody_part.getTimeSignatures()[0] if melody_part.getTimeSignatures() else meter.TimeSignature('4/4')
        strong_beats = _get_strong_beats(time_sig)
        measure_length = time_sig.barDuration.quarterLength
        
        for element in melody_part.flatten().notes:
            if isinstance(element, note.Note):
                # Calculate beat position from offset
                offset = element.offset
                beat_in_measure = (offset % measure_length) + 1.0  # 1-based
                
                # Check if note is on a strong beat
                is_strong_beat = beat_in_measure in strong_beats
                
                # Check if note has long duration (quarter note or longer)
                is_long_duration = element.quarterLength >= 1.0
                
                # Tag the note as structural or ornamental
                element.is_structural = (is_strong_beat or is_long_duration)
            
            elif isinstance(element, note.Rest):
                # Rests are not structural tones
                element.is_structural = False
    
    return melody_part


def _get_strong_beats(time_sig: meter.TimeSignature) -> List[float]:
    """
    Determine which beat positions are considered "strong" for a given time signature.
    
    Rules:
    - Beat 1 is always strong (downbeat)
    - In 4/4 or 4/2: beat 3 is also strong
    - In 3/4 or 3/2: only beat 1 is strong
    - In 6/8 or compound meters: beat 1 and beat 4 (second downbeat)
    - In 2/4 or 2/2 (cut time): only beat 1 is strong
    
    Args:
        time_sig: music21.meter.TimeSignature object
        
    Returns:
        List of beat numbers that are considered strong (1-based)
    """
    strong_beats = [1.0]  # Beat 1 (downbeat) is always strong
    
    numerator = time_sig.numerator
    denominator = time_sig.denominator
    
    # Determine meter type
    if numerator == 4 and denominator in [4, 2]:
        # 4/4 or 4/2: beats 1 and 3 are strong
        strong_beats.append(3.0)
    elif numerator == 6 and denominator == 8:
        # 6/8 compound meter: beats 1 and 4 (second downbeat)
        strong_beats.append(4.0)
    elif numerator == 9 and denominator == 8:
        # 9/8 compound meter: beats 1, 4, 7
        strong_beats.extend([4.0, 7.0])
    elif numerator == 12 and denominator == 8:
        # 12/8 compound meter: beats 1, 4, 7, 10
        strong_beats.extend([4.0, 7.0, 10.0])
    # For 3/4, 2/4, 2/2, etc.: only beat 1 is strong (already added)
    
    return strong_beats


def print_structural_analysis(melody_part: stream.Part, verbose: bool = True) -> None:
    """
    Print a formatted analysis of structural vs. ornamental tones to console.
    
    Args:
        melody_part: music21.stream.Part that has been analyzed with find_structural_tones()
        verbose: If True, print detailed information for each note
        
    Example Output:
        ======================================================================
        STRUCTURAL TONE ANALYSIS
        ======================================================================
        Measure 1 (4/4):
          C4 (quarter, beat 1.0) → STRUCTURAL (strong beat)
          D4 (eighth, beat 2.0) → Ornamental
          E4 (eighth, beat 2.5) → Ornamental
          F4 (quarter, beat 3.0) → STRUCTURAL (strong beat)
          
        Measure 2 (4/4):
          G4 (half, beat 1.0) → STRUCTURAL (strong beat + long duration)
          A4 (quarter, beat 3.0) → STRUCTURAL (strong beat)
          
        Summary: 4 structural tones, 2 ornamental tones
    """
    print("\n" + "="*70)
    print("STRUCTURAL TONE ANALYSIS")
    print("="*70)
    
    structural_count = 0
    ornamental_count = 0
    
    # Check if Part has measures
    measures = melody_part.getElementsByClass('Measure')
    
    if measures:
        # Process by measure
        for measure_num, measure in enumerate(measures, start=1):
            # Get time signature for this measure
            time_sig = measure.timeSignature
            if not time_sig:
                time_sig = melody_part.getTimeSignatures()[0] if melody_part.getTimeSignatures() else meter.TimeSignature('4/4')
            
            if verbose:
                print(f"\nMeasure {measure_num} ({time_sig.ratioString}):")
            
            for element in measure.notes:
                if isinstance(element, note.Note):
                    is_structural = getattr(element, 'is_structural', False)
                    
                    if is_structural:
                        structural_count += 1
                        status = "STRUCTURAL"
                    else:
                        ornamental_count += 1
                        status = "Ornamental"
                    
                    if verbose:
                        # Determine reason for classification
                        reasons = []
                        beat_pos = element.beat
                        strong_beats = _get_strong_beats(time_sig)
                        
                        if beat_pos in strong_beats:
                            reasons.append("strong beat")
                        if element.quarterLength >= 1.0:
                            reasons.append("long duration")
                        
                        reason_str = f" ({', '.join(reasons)})" if reasons else ""
                        
                        # Format duration name
                        duration_name = element.duration.type
                        
                        print(f"  {element.nameWithOctave} ({duration_name}, beat {beat_pos}) → {status}{reason_str}")
    else:
        # Notes are directly in Part (no measures) - process by offset
        time_sig = melody_part.getTimeSignatures()[0] if melody_part.getTimeSignatures() else meter.TimeSignature('4/4')
        measure_length = time_sig.barDuration.quarterLength
        strong_beats = _get_strong_beats(time_sig)
        
        current_measure = 0
        if verbose:
            print(f"\n(Notes analyzed by offset - time signature: {time_sig.ratioString})")
        
        for element in melody_part.flatten().notes:
            if isinstance(element, note.Note):
                # Calculate which measure this note is in
                measure_num = int(element.offset // measure_length) + 1
                beat_in_measure = (element.offset % measure_length) + 1.0
                
                # Print measure header if we're in a new measure
                if verbose and measure_num != current_measure:
                    current_measure = measure_num
                    print(f"\nMeasure {measure_num}:")
                
                is_structural = getattr(element, 'is_structural', False)
                
                if is_structural:
                    structural_count += 1
                    status = "STRUCTURAL"
                else:
                    ornamental_count += 1
                    status = "Ornamental"
                
                if verbose:
                    # Determine reason for classification
                    reasons = []
                    
                    if beat_in_measure in strong_beats:
                        reasons.append("strong beat")
                    if element.quarterLength >= 1.0:
                        reasons.append("long duration")
                    
                    reason_str = f" ({', '.join(reasons)})" if reasons else ""
                    
                    # Format duration name
                    duration_name = element.duration.type
                    
                    print(f"  {element.nameWithOctave} ({duration_name}, beat {beat_in_measure:.1f}) → {status}{reason_str}")
    
    # Print summary
    print("\n" + "-"*70)
    print(f"Summary: {structural_count} structural tone{'s' if structural_count != 1 else ''}, "
          f"{ornamental_count} ornamental tone{'s' if ornamental_count != 1 else ''}")
    
    if structural_count + ornamental_count > 0:
        structural_percent = (structural_count / (structural_count + ornamental_count)) * 100
        print(f"Structural ratio: {structural_percent:.1f}%")
    
    print("="*70 + "\n")


def get_structural_notes(melody_part: stream.Part) -> List[note.Note]:
    """
    Extract only the structural notes from an analyzed melody.
    
    Args:
        melody_part: music21.stream.Part that has been analyzed with find_structural_tones()
        
    Returns:
        List of Note objects that are marked as structural
        
    Example:
        >>> analyzed = find_structural_tones(melody_part)
        >>> structural = get_structural_notes(analyzed)
        >>> print(f"Found {len(structural)} structural notes")
    """
    structural_notes = []
    
    for element in melody_part.flatten().notes:
        if isinstance(element, note.Note) and getattr(element, 'is_structural', False):
            structural_notes.append(element)
    
    return structural_notes


# Public API
__all__ = [
    'find_structural_tones',
    'print_structural_analysis',
    'get_structural_notes'
]
