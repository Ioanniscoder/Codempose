"""
harmonic_engine.py - Harmonic Fitting Engine for Tonal Harmony

This module provides tools to apply chord progressions to melodies and
generate harmonically correct bass lines based on principles from
"Tonal Harmony with an Introduction to Twentieth-Century Music" textbook.

The core concept is "harmonic fitting": aligning a user-defined chord
progression with the structural tones of a melody, then generating
appropriate bass line from the chord roots.

Usage:
    from harmonic_engine import harmonize_melody
    
    # Harmonize a melody with a progression
    score = harmonize_melody(melody_part, "I - IV - V - I", "C")
    
    # Result: two-part Score with melody + generated bass line
"""

from music21 import roman, key as m21key, note, stream, clef, pitch, metadata
from harmonic_analysis import find_structural_tones, get_structural_notes
import re
from typing import List, Tuple, Optional


def harmonize_melody(
    melody_part: stream.Part, 
    progression_string: str, 
    key: str,
    harmonic_rhythm: str = "auto"
) -> stream.Score:
    """
    Harmonize a melody with a chord progression and generate a bass line.
    
    This function performs the following steps:
    1. Analyze the melody to identify structural tones
    2. Parse the progression string into RomanNumeral chord objects
    3. Align chords with structural tones based on harmonic rhythm
    4. Generate a bass line using chord roots
    5. Return a two-part Score (melody + bass)
    
    Args:
        melody_part: music21.stream.Part with the melody to harmonize
        progression_string: Roman numeral progression (e.g., "I - IV - V - I")
        key: Key signature (e.g., "C", "A minor", "F# major")
        harmonic_rhythm: How to align chords ("auto", "one_per_measure", or custom)
        
    Returns:
        music21.stream.Score with two parts: original melody and generated bass
        
    Example:
        >>> melody = converter.parse("tinynotation: 4/4 c4 d4 e4 f4 g2 e2 f4 e4 d4 c4 c1")
        >>> score = harmonize_melody(melody.parts[0], "I - IV - V - I", "C")
        >>> score.show()  # Display two-stave score
    """
    print(f"\n{'='*70}")
    print("HARMONIC FITTING ENGINE")
    print(f"{'='*70}\n")
    print(f"Key: {key}")
    print(f"Progression: {progression_string}")
    print()
    
    # Step 1: Analyze structural tones
    print("[1/5] Analyzing structural tones...")
    analyzed_melody = find_structural_tones(melody_part)
    structural_notes = get_structural_notes(analyzed_melody)
    print(f"   ✓ Found {len(structural_notes)} structural tones")
    
    # Step 2: Parse progression string
    print("\n[2/5] Parsing chord progression...")
    chords = parse_progression(progression_string, key)
    print(f"   ✓ Parsed {len(chords)} chords:")
    for i, chord_obj in enumerate(chords, 1):
        print(f"      {i}. {chord_obj.figure} ({chord_obj.pitchedCommonName})")
    
    # Step 3: Align chords with structural tones
    print("\n[3/5] Aligning chords with structural tones...")
    chord_alignment = align_chords_with_melody(structural_notes, chords, harmonic_rhythm)
    print(f"   ✓ Created {len(chord_alignment)} harmonic events")
    
    # Step 4: Generate bass line
    print("\n[4/5] Generating bass line...")
    bass_part = generate_bass_line(chord_alignment, key)
    print(f"   ✓ Bass line generated ({len(bass_part.flatten().notes)} notes)")
    
    # Step 5: Create score
    print("\n[5/5] Assembling two-part score...")
    score = stream.Score()
    
    # Set score metadata
    score.metadata = metadata.Metadata()
    score.metadata.title = "Harmonized Melody"
    
    # Add melody part (on top)
    analyzed_melody.id = "Melody"
    analyzed_melody.partName = "Melody"
    score.insert(0, analyzed_melody)
    
    # Add bass part (on bottom)
    bass_part.id = "Bass"
    bass_part.partName = "Bass"
    score.insert(0, bass_part)
    
    print("   ✓ Score complete!\n")
    print(f"{'='*70}\n")
    
    return score


def parse_progression(progression_string: str, key: str) -> List[roman.RomanNumeral]:
    """
    Parse a progression string into music21 RomanNumeral objects.
    
    Args:
        progression_string: String like "I - IV - V - I" or "vi - ii - V - I"
        key: Key signature (e.g., "C", "A minor")
        
    Returns:
        List of music21.roman.RomanNumeral objects
        
    Example:
        >>> chords = parse_progression("I - IV - V - I", "C")
        >>> [c.pitchedCommonName for c in chords]
        ['C major triad', 'F major triad', 'G major triad', 'C major triad']
    """
    # Create key object
    key_obj = m21key.Key(key)
    
    # Split progression string by separators (-, |, comma, or whitespace)
    import re
    chord_symbols = re.split(r'[-|,\s]+', progression_string.strip())
    
    # Filter out empty strings
    chord_symbols = [s.strip() for s in chord_symbols if s.strip()]
    
    # Convert to RomanNumeral objects
    chords = []
    for symbol in chord_symbols:
        try:
            rn = roman.RomanNumeral(symbol, key_obj)
            chords.append(rn)
        except Exception as e:
            print(f"   ⚠️  Warning: Could not parse '{symbol}': {e}")
            # Skip invalid symbols
            continue
    
    return chords


def align_chords_with_melody(
    structural_notes: List[note.Note],
    chords: List[roman.RomanNumeral],
    harmonic_rhythm: str = "auto"
) -> List[Tuple[float, float, roman.RomanNumeral]]:
    """
    Align chord progression with structural tones in the melody.
    
    Args:
        structural_notes: List of structural notes from the melody
        chords: List of RomanNumeral chord objects
        harmonic_rhythm: How to distribute chords ("auto", "one_per_measure", etc.)
        
    Returns:
        List of tuples: (start_offset, duration, chord_object)
        
    Example:
        >>> alignment = align_chords_with_melody(structural_notes, chords, "auto")
        >>> for offset, duration, chord in alignment:
        ...     print(f"Offset {offset}: {chord.figure} for {duration} beats")
    """
    if not structural_notes or not chords:
        return []
    
    alignment = []
    
    if harmonic_rhythm == "auto":
        # Distribute chords evenly across structural notes
        notes_per_chord = len(structural_notes) // len(chords)
        if notes_per_chord < 1:
            notes_per_chord = 1
        
        chord_index = 0
        for i, note_obj in enumerate(structural_notes):
            # Determine which chord to use
            chord_index = min(i // notes_per_chord, len(chords) - 1)
            chord = chords[chord_index]
            
            # Determine duration for this chord event
            start_offset = note_obj.offset
            
            # Calculate duration until next chord change or end
            if i + notes_per_chord < len(structural_notes):
                next_note = structural_notes[i + notes_per_chord]
                duration = next_note.offset - start_offset
            else:
                # Last chord: use remaining melody duration
                last_note = structural_notes[-1]
                duration = last_note.quarterLength
            
            # Only add if this is a new chord (not a continuation)
            if not alignment or alignment[-1][2] != chord:
                alignment.append((start_offset, duration, chord))
    
    elif harmonic_rhythm == "one_per_measure":
        # One chord per measure
        # Group structural notes by measure
        measure_groups = {}
        for note_obj in structural_notes:
            measure_num = int(note_obj.offset // 4.0)  # Assuming 4/4 time
            if measure_num not in measure_groups:
                measure_groups[measure_num] = []
            measure_groups[measure_num].append(note_obj)
        
        # Assign chords to measures
        for measure_num in sorted(measure_groups.keys()):
            chord_index = min(measure_num, len(chords) - 1)
            chord = chords[chord_index]
            
            # Use first note of measure as start
            first_note = measure_groups[measure_num][0]
            start_offset = first_note.offset
            duration = 4.0  # Full measure in 4/4
            
            alignment.append((start_offset, duration, chord))
    
    return alignment


def generate_bass_line(
    chord_alignment: List[Tuple[float, float, roman.RomanNumeral]],
    key: str
) -> stream.Part:
    """
    Generate a bass line from aligned chords.
    
    Args:
        chord_alignment: List of (offset, duration, chord) tuples
        key: Key signature
        
    Returns:
        music21.stream.Part with bass line
        
    Example:
        >>> bass = generate_bass_line(alignment, "C")
        >>> for n in bass.flatten().notes:
        ...     print(n.nameWithOctave, n.quarterLength)
    """
    bass_part = stream.Part()
    
    # Add bass clef
    bass_part.insert(0, clef.BassClef())
    
    # Get key object
    key_obj = m21key.Key(key)
    
    for start_offset, duration, chord_obj in chord_alignment:
        # Use chord root for bass note
        bass_pitch = chord_obj.root()
        
        # Transpose to bass register (octave 2 or 3)
        # Start with octave 3
        target_octave = 3
        bass_pitch.octave = target_octave
        
        # If pitch is too high, drop an octave
        if bass_pitch.midi > 60:  # Middle C
            bass_pitch.octave = target_octave - 1
        
        # Create bass note
        bass_note = note.Note(bass_pitch)
        bass_note.quarterLength = duration
        
        # Insert at appropriate offset
        bass_part.insert(start_offset, bass_note)
    
    return bass_part


def validate_progression(progression_string: str, key: str) -> bool:
    """
    Validate whether a chord progression follows common practice rules.
    
    This is a basic validator based on standard harmonic progression rules
    from "Tonal Harmony" textbook (Chapter 7).
    
    Args:
        progression_string: Roman numeral progression to validate
        key: Key signature
        
    Returns:
        True if progression is valid, False otherwise
        
    Example:
        >>> validate_progression("I - IV - V - I", "C")
        True
        >>> validate_progression("V - IV - I", "C")  # Less common
        False
    """
    # Standard progression rules (simplified)
    # Based on functional harmony: Tonic → Pre-dominant → Dominant → Tonic
    progression_rules = {
        'I': ['ii', 'iii', 'IV', 'V', 'vi', 'I'],  # Tonic can go anywhere
        'ii': ['V', 'vii°', 'viio'],               # Pre-dominant → Dominant
        'iii': ['vi', 'IV'],                        # Mediant
        'IV': ['V', 'vii°', 'viio', 'I', 'ii'],    # Pre-dominant
        'V': ['I', 'vi'],                           # Dominant → Tonic (or deceptive)
        'vi': ['ii', 'IV', 'V'],                    # Submediant → Pre-dominant or Dominant
        'vii°': ['I', 'iii'],                       # Leading tone → Tonic
        'viio': ['I', 'iii'],                       # Alternative spelling
    }
    
    try:
        chords = parse_progression(progression_string, key)
        
        for i in range(len(chords) - 1):
            current_chord = chords[i]
            next_chord = chords[i + 1]
            
            current_figure = current_chord.figure
            next_figure = next_chord.figure
            
            # Check if progression is allowed
            allowed_next = progression_rules.get(current_figure, [])
            
            if next_figure not in allowed_next:
                print(f"⚠️  Non-standard progression: {current_figure} → {next_figure}")
                return False
        
        print("✓ Progression follows common practice rules")
        return True
        
    except Exception as e:
        print(f"❌ Error validating progression: {e}")
        return False


# Public API
__all__ = [
    'harmonize_melody',
    'parse_progression',
    'align_chords_with_melody',
    'generate_bass_line',
    'validate_progression'
]
