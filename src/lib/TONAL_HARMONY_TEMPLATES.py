"""
MUSIC21 TONAL HARMONY ROADMAP - COMPLETE FUNCTION TEMPLATES

This file provides programmatic templates for ALL music21 functions identified
in the Tonal Harmony implementation roadmap. Each template is ready to be
integrated into study files.

Organization:
- Part Two: Diatonic Triads & Voice Leading
- Part Three: Diatonic Seventh Chords
- Part Four: Chromaticism 1 (Secondary Dominants & Modulation)
- Part Five: Chromaticism 2 (Neapolitan & Augmented Sixth Chords)
- Part Six: Form & Analysis Tools

All functions are documented with:
- Purpose and textbook reference
- music21 functions used
- Complete working code
- Usage examples
- Integration points for study files
"""

from music21 import (
    stream, note, chord, pitch, key, roman, interval,
    voiceLeading, analysis, meter, clef
)
from typing import List, Dict, Tuple, Optional


# ============================================================================
# PART TWO: DIATONIC TRIADS & VOICE LEADING
# ============================================================================

def check_voice_leading_errors(score: stream.Score) -> Dict[str, List]:
    """
    Check for common voice-leading errors in a multi-part score.
    
    Textbook Reference: Chapter 6 - Voice Leading Principles
    
    Checks for:
    - Parallel fifths
    - Parallel octaves
    - Direct (hidden) fifths
    - Direct (hidden) octaves
    - Voice crossing
    - Spacing errors (> octave between adjacent upper voices)
    
    music21 Functions Used:
    - music21.voiceLeading.VoiceLeadingQuartet()
    - music21.voiceLeading.Verticality()
    
    Args:
        score: music21.stream.Score with multiple parts
        
    Returns:
        Dictionary with error types as keys, list of locations as values
        
    Usage in Study File:
        score = build_four_part_score()
        errors = check_voice_leading_errors(score)
        if errors['parallel_fifths']:
            print("Parallel fifths found at:", errors['parallel_fifths'])
    """
    errors = {
        'parallel_fifths': [],
        'parallel_octaves': [],
        'hidden_fifths': [],
        'hidden_octaves': [],
        'voice_crossing': [],
        'spacing_errors': []
    }
    
    # Extract all parts
    parts = list(score.parts)
    if len(parts) < 2:
        return errors
    
    # Get all vertical slices (simultaneities)
    chordified = score.chordify()
    
    # Check each consecutive pair of chords
    prev_chord = None
    for i, element in enumerate(chordified.flatten()):
        if not isinstance(element, chord.Chord):
            continue
            
        current_chord = element
        
        if prev_chord is not None:
            # Check all voice pairs
            for v1_idx in range(len(parts)):
                for v2_idx in range(v1_idx + 1, len(parts)):
                    try:
                        # Get the four notes (v1_prev, v1_curr, v2_prev, v2_curr)
                        v1_prev = prev_chord.pitches[v1_idx] if v1_idx < len(prev_chord.pitches) else None
                        v1_curr = current_chord.pitches[v1_idx] if v1_idx < len(current_chord.pitches) else None
                        v2_prev = prev_chord.pitches[v2_idx] if v2_idx < len(prev_chord.pitches) else None
                        v2_curr = current_chord.pitches[v2_idx] if v2_idx < len(current_chord.pitches) else None
                        
                        if all([v1_prev, v1_curr, v2_prev, v2_curr]):
                            # Create VoiceLeadingQuartet
                            vlq = voiceLeading.VoiceLeadingQuartet(
                                v1_prev, v1_curr, v2_prev, v2_curr
                            )
                            
                            # Check for parallel fifths
                            if vlq.parallelFifth():
                                errors['parallel_fifths'].append({
                                    'measure': element.measureNumber,
                                    'offset': element.offset,
                                    'voices': (v1_idx, v2_idx)
                                })
                            
                            # Check for parallel octaves
                            if vlq.parallelOctave():
                                errors['parallel_octaves'].append({
                                    'measure': element.measureNumber,
                                    'offset': element.offset,
                                    'voices': (v1_idx, v2_idx)
                                })
                            
                            # Check for hidden fifths (same direction, outer voices, leap to fifth)
                            if vlq.hiddenFifth():
                                errors['hidden_fifths'].append({
                                    'measure': element.measureNumber,
                                    'offset': element.offset,
                                    'voices': (v1_idx, v2_idx)
                                })
                            
                            # Check for hidden octaves
                            if vlq.hiddenOctave():
                                errors['hidden_octaves'].append({
                                    'measure': element.measureNumber,
                                    'offset': element.offset,
                                    'voices': (v1_idx, v2_idx)
                                })
                    except Exception:
                        continue
        
        # Check voice crossing in current chord
        pitches = current_chord.pitches
        for i in range(len(pitches) - 1):
            if pitches[i].midi < pitches[i + 1].midi:
                errors['voice_crossing'].append({
                    'measure': element.measureNumber,
                    'offset': element.offset,
                    'voices': (i, i + 1)
                })
        
        # Check spacing (no more than octave between upper voices)
        if len(pitches) >= 3:
            for i in range(len(pitches) - 2):  # Check S-A and A-T
                spacing_interval = interval.Interval(pitches[i + 1], pitches[i])
                if spacing_interval.semitones > 12:
                    errors['spacing_errors'].append({
                        'measure': element.measureNumber,
                        'offset': element.offset,
                        'voices': (i, i + 1),
                        'interval': spacing_interval.semitones
                    })
        
        prev_chord = current_chord
    
    return errors


def validate_harmonic_progression(progression_string: str, key_str: str) -> Dict:
    """
    Validate a chord progression according to common practice rules.
    
    Textbook Reference: Chapter 7 - Harmonic Progression
    
    Rules checked:
    - V or vii° should resolve to I (or vi as deceptive)
    - IV often moves to V or I
    - vi often precedes V or ii
    - No regression (moving backwards in circle of fifths)
    
    music21 Functions Used:
    - music21.roman.RomanNumeral()
    - music21.key.Key()
    
    Args:
        progression_string: e.g., "I - IV - V - I"
        key_str: e.g., "C major"
        
    Returns:
        Dict with 'valid': bool and 'errors': list of error messages
        
    Usage in Study File:
        result = validate_harmonic_progression("I - IV - V - I", "C major")
        if not result['valid']:
            for error in result['errors']:
                print(f"Warning: {error}")
    """
    import re
    
    result = {'valid': True, 'errors': []}
    
    # Parse key
    key_obj = key.Key(key_str)
    
    # Parse progression
    chord_symbols = re.split(r'[-|,\s]+', progression_string.strip())
    chord_symbols = [s.strip() for s in chord_symbols if s.strip()]
    
    # Create RomanNumeral objects
    try:
        chords = [roman.RomanNumeral(sym, key_obj) for sym in chord_symbols]
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Failed to parse progression: {e}")
        return result
    
    # Define common practice rules
    # Dictionary: chord_figure -> list of preferred next chords
    common_progressions = {
        'I': ['ii', 'iii', 'IV', 'V', 'vi', 'vii°'],  # Tonic can go anywhere
        'ii': ['V', 'vii°'],  # Predominant to dominant
        'iii': ['vi', 'IV'],
        'IV': ['V', 'I', 'vii°'],  # Predominant to dominant or tonic
        'V': ['I', 'vi'],  # Dominant to tonic (or deceptive to vi)
        'vi': ['ii', 'IV', 'V'],  # Submediant to predominant
        'vii°': ['I', 'vi']  # Leading tone to tonic
    }
    
    # Check each progression
    for i in range(len(chords) - 1):
        current = chords[i]
        next_chord = chords[i + 1]
        
        current_figure = current.figure
        next_figure = next_chord.figure
        
        # Check V or vii° resolution
        if current_figure in ['V', 'V7', 'vii°', 'viio7']:
            if next_figure not in ['I', 'vi']:
                result['valid'] = False
                result['errors'].append(
                    f"Measure {i+1}: {current_figure} should resolve to I or vi, "
                    f"but goes to {next_figure}"
                )
        
        # Check if progression is in common practice
        base_figure = current_figure.replace('7', '').replace('6', '')
        if base_figure in common_progressions:
            preferred = common_progressions[base_figure]
            next_base = next_figure.replace('7', '').replace('6', '')
            
            if next_base not in preferred and next_base != base_figure:
                result['errors'].append(
                    f"Measure {i+1}: Unusual progression {current_figure} → {next_figure}. "
                    f"More common: {current_figure} → {', '.join(preferred)}"
                )
    
    # Check for deceptive cadence (V-vi)
    if len(chords) >= 2:
        for i in range(len(chords) - 1):
            if chords[i].figure == 'V' and chords[i + 1].figure == 'vi':
                result['errors'].append(
                    f"Measure {i+1}: Deceptive cadence found (V-vi)"
                )
    
    return result


def analyze_cadence_type(score: stream.Score, measure_range: Tuple[int, int]) -> str:
    """
    Identify the type of cadence in a given measure range.
    
    Textbook Reference: Chapter 8 - Cadences
    
    Cadence types:
    - Authentic (V-I or V7-I)
      - Perfect Authentic (PAC): Root position, soprano on tonic
      - Imperfect Authentic (IAC): Other V-I progressions
    - Half Cadence (HC): Ends on V
    - Plagal (PC): IV-I
    - Deceptive (DC): V-vi
    
    music21 Functions Used:
    - music21.analysis.reduceChords()
    - music21.roman.romanNumeralFromChord()
    
    Args:
        score: music21.stream.Score
        measure_range: (start_measure, end_measure)
        
    Returns:
        String describing cadence type or "No clear cadence"
        
    Usage in Study File:
        cadence = analyze_cadence_type(score, (7, 8))
        print(f"Cadence type: {cadence}")
    """
    start_m, end_m = measure_range
    
    # Extract measures
    excerpt = score.measures(start_m, end_m)
    
    # Get the last two chords
    chordified = excerpt.chordify()
    chords_list = list(chordified.flatten().getElementsByClass('Chord'))
    
    if len(chords_list) < 2:
        return "Insufficient chords for cadence analysis"
    
    penultimate = chords_list[-2]
    final = chords_list[-1]
    
    # Analyze with Roman numerals
    key_obj = score.analyze('key')
    
    try:
        penult_rn = roman.romanNumeralFromChord(penultimate, key_obj)
        final_rn = roman.romanNumeralFromChord(final, key_obj)
        
        penult_fig = penult_rn.figure
        final_fig = final_rn.figure
        
        # Check for Perfect Authentic Cadence (PAC)
        if penult_fig in ['V', 'V7'] and final_fig == 'I':
            # Check if both root position
            if penult_rn.inversion() == 0 and final_rn.inversion() == 0:
                # Check if soprano ends on tonic
                soprano_pitch = final.pitches[-1]  # Highest pitch
                if soprano_pitch.name == key_obj.tonic.name:
                    return "Perfect Authentic Cadence (PAC)"
            return "Imperfect Authentic Cadence (IAC)"
        
        # Check for Half Cadence (HC)
        if final_fig in ['V', 'V7']:
            return "Half Cadence (HC)"
        
        # Check for Plagal Cadence (PC)
        if penult_fig == 'IV' and final_fig == 'I':
            return "Plagal Cadence (PC)"
        
        # Check for Deceptive Cadence (DC)
        if penult_fig in ['V', 'V7'] and final_fig == 'vi':
            return "Deceptive Cadence (DC)"
        
        return f"Unclear cadence: {penult_fig} - {final_fig}"
        
    except Exception as e:
        return f"Analysis error: {e}"


# ============================================================================
# PART THREE: DIATONIC SEVENTH CHORDS
# ============================================================================

def check_seventh_resolution(score: stream.Score) -> List[Dict]:
    """
    Check that all seventh chord resolutions follow proper voice leading.
    
    Textbook Reference: Chapter 11 - Seventh Chords
    
    Rule: The 7th of a seventh chord must resolve down by step.
    
    music21 Functions Used:
    - music21.chord.Chord.seventh
    - music21.interval.Interval()
    - music21.roman.RomanNumeral()
    
    Args:
        score: music21.stream.Score
        
    Returns:
        List of dictionaries describing resolution errors
        
    Usage in Study File:
        errors = check_seventh_resolution(score)
        for error in errors:
            print(f"Seventh resolution error at measure {error['measure']}")
    """
    errors = []
    
    # Get all chords
    chordified = score.chordify()
    chord_list = list(chordified.flatten().getElementsByClass('Chord'))
    
    for i in range(len(chord_list) - 1):
        current_chord = chord_list[i]
        next_chord = chord_list[i + 1]
        
        # Check if current chord is a seventh chord
        if current_chord.seventh is None:
            continue
        
        # Get the seventh of the chord
        seventh_pitch = current_chord.seventh
        
        # Find which voice has the seventh
        current_pitches = current_chord.pitches
        seventh_index = None
        for idx, p in enumerate(current_pitches):
            if p.nameWithOctave == seventh_pitch.nameWithOctave:
                seventh_index = idx
                break
        
        if seventh_index is None:
            continue
        
        # Get the resolution pitch (same voice in next chord)
        next_pitches = next_chord.pitches
        if seventh_index >= len(next_pitches):
            errors.append({
                'measure': current_chord.measureNumber,
                'offset': current_chord.offset,
                'error': 'Voice disappears',
                'seventh_pitch': seventh_pitch.nameWithOctave
            })
            continue
        
        resolution_pitch = next_pitches[seventh_index]
        
        # Check the interval
        resolution_interval = interval.Interval(seventh_pitch, resolution_pitch)
        
        # Should be descending step (minor or major 2nd down)
        if resolution_interval.direction != -1 or resolution_interval.generic.value != 2:
            errors.append({
                'measure': current_chord.measureNumber,
                'offset': current_chord.offset,
                'error': 'Seventh does not resolve down by step',
                'seventh_pitch': seventh_pitch.nameWithOctave,
                'resolution_pitch': resolution_pitch.nameWithOctave,
                'interval': resolution_interval.name
            })
    
    return errors


def create_diatonic_seventh_chord(scale_degree: int, key_str: str, inversion: int = 0) -> chord.Chord:
    """
    Create a diatonic seventh chord on any scale degree.
    
    Textbook Reference: Chapter 11 - Diatonic Seventh Chords
    
    Seventh chord types by scale degree (in major):
    - I7: Major seventh (rare)
    - ii7: Minor seventh
    - iii7: Minor seventh
    - IV7: Major seventh
    - V7: Dominant seventh
    - vi7: Minor seventh
    - vii°7: Half-diminished seventh
    
    music21 Functions Used:
    - music21.roman.RomanNumeral()
    - music21.key.Key()
    
    Args:
        scale_degree: 1-7
        key_str: e.g., "C major"
        inversion: 0 (root), 1 (6/5), 2 (4/3), 3 (4/2)
        
    Returns:
        music21.chord.Chord object
        
    Usage in Study File:
        # Create ii7 chord in C major
        ii7 = create_diatonic_seventh_chord(2, "C major")
        # Create V6/5 in G major (first inversion V7)
        V65 = create_diatonic_seventh_chord(5, "G major", inversion=1)
    """
    key_obj = key.Key(key_str)
    
    # Map scale degree to Roman numeral
    major_numerals = ['I7', 'ii7', 'iii7', 'IV7', 'V7', 'vi7', 'viiø7']
    minor_numerals = ['i7', 'iiø7', 'III7', 'iv7', 'v7', 'VI7', 'vii°7']
    
    if key_obj.mode == 'major':
        numeral_str = major_numerals[scale_degree - 1]
    else:
        numeral_str = minor_numerals[scale_degree - 1]
    
    # Create Roman numeral
    rn = roman.RomanNumeral(numeral_str, key_obj)
    
    # Apply inversion
    if inversion > 0:
        rn = rn.inversion(inversion)
    
    return rn


# ============================================================================
# PART FOUR: CHROMATICISM 1 (SECONDARY DOMINANTS & MODULATION)
# ============================================================================

def parse_secondary_dominant(numeral_str: str, key_str: str) -> roman.RomanNumeral:
    """
    Parse and create secondary dominant chords.
    
    Textbook Reference: Chapter 16 - Secondary Dominants
    
    Secondary dominants: V7/x where x is any diatonic chord
    Examples: V7/V, V7/IV, V7/ii
    
    music21 Functions Used:
    - music21.roman.RomanNumeral() with slash notation
    
    Args:
        numeral_str: e.g., "V7/V", "V/IV", "viio7/vi"
        key_str: e.g., "C major"
        
    Returns:
        music21.roman.RomanNumeral object
        
    Usage in Study File:
        # Create V7/V in C major (D7 chord)
        secondary_dom = parse_secondary_dominant("V7/V", "C major")
        print(secondary_dom.pitches)  # [D, F#, A, C]
    """
    key_obj = key.Key(key_str)
    
    try:
        rn = roman.RomanNumeral(numeral_str, key_obj)
        return rn
    except Exception as e:
        raise ValueError(f"Invalid secondary dominant notation '{numeral_str}': {e}")


def find_pivot_chords(key1_str: str, key2_str: str) -> List[Dict]:
    """
    Find all common chords (pivot chords) between two keys for modulation.
    
    Textbook Reference: Chapter 17 - Modulation
    
    A pivot chord is diatonic in both keys and can facilitate smooth modulation.
    
    music21 Functions Used:
    - music21.key.Key()
    - music21.scale.MajorScale() / MinorScale()
    - music21.roman.RomanNumeral()
    
    Args:
        key1_str: Starting key, e.g., "C major"
        key2_str: Target key, e.g., "G major"
        
    Returns:
        List of dicts with pivot chord info
        
    Usage in Study File:
        pivots = find_pivot_chords("C major", "G major")
        for pivot in pivots:
            print(f"In C: {pivot['key1_numeral']}, In G: {pivot['key2_numeral']}")
            print(f"   Pitches: {pivot['pitches']}")
        
        # Example output:
        # In C: I, In G: IV (C major triad)
        # In C: V, In G: I (G major triad)
        # In C: vi, In G: ii (A minor triad)
    """
    key1 = key.Key(key1_str)
    key2 = key.Key(key2_str)
    
    # Get all diatonic triads in each key
    triads_key1 = []
    triads_key2 = []
    
    # Major key triads: I, ii, iii, IV, V, vi, vii°
    # Minor key triads: i, ii°, III, iv, v, VI, VII
    
    major_numerals = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']
    minor_numerals = ['i', 'ii°', 'III', 'iv', 'v', 'VI', 'VII']
    
    # Build triads for key 1
    numerals1 = major_numerals if key1.mode == 'major' else minor_numerals
    for numeral in numerals1:
        try:
            rn = roman.RomanNumeral(numeral, key1)
            triads_key1.append({
                'numeral': numeral,
                'pitches': tuple(sorted([p.name for p in rn.pitches]))
            })
        except:
            continue
    
    # Build triads for key 2
    numerals2 = major_numerals if key2.mode == 'major' else minor_numerals
    for numeral in numerals2:
        try:
            rn = roman.RomanNumeral(numeral, key2)
            triads_key2.append({
                'numeral': numeral,
                'pitches': tuple(sorted([p.name for p in rn.pitches]))
            })
        except:
            continue
    
    # Find common chords
    pivot_chords = []
    for t1 in triads_key1:
        for t2 in triads_key2:
            if t1['pitches'] == t2['pitches']:
                pivot_chords.append({
                    'key1_numeral': t1['numeral'],
                    'key2_numeral': t2['numeral'],
                    'pitches': t1['pitches'],
                    'description': f"{t1['numeral']} in {key1_str} = {t2['numeral']} in {key2_str}"
                })
    
    return pivot_chords


def create_modulation_progression(
    start_key: str,
    end_key: str,
    use_pivot: bool = True
) -> List[Tuple[str, str]]:
    """
    Generate a chord progression that modulates from one key to another.
    
    Textbook Reference: Chapter 17 - Modulation Techniques
    
    Strategies:
    - Common chord (pivot) modulation
    - Direct modulation
    
    music21 Functions Used:
    - find_pivot_chords() (our function)
    - music21.key.Key()
    
    Args:
        start_key: e.g., "C major"
        end_key: e.g., "G major"
        use_pivot: If True, use common chord modulation
        
    Returns:
        List of (numeral, key) tuples representing the progression
        
    Usage in Study File:
        progression = create_modulation_progression("C major", "G major")
        for numeral, key_str in progression:
            print(f"{numeral} in {key_str}")
    """
    progression = []
    
    # Start in original key
    progression.append(('I', start_key))
    
    if use_pivot:
        # Find pivot chords
        pivots = find_pivot_chords(start_key, end_key)
        
        if pivots:
            # Use the first pivot (usually I in old key)
            pivot = pivots[0]
            
            # Approach pivot from start key
            progression.append((pivot['key1_numeral'], start_key))
            
            # Cadence in new key
            progression.append(('V', end_key))
            progression.append(('I', end_key))
        else:
            # No pivot available, direct modulation
            progression.append(('V', end_key))
            progression.append(('I', end_key))
    else:
        # Direct modulation
        progression.append(('V', end_key))
        progression.append(('I', end_key))
    
    return progression


# ============================================================================
# PART FIVE: CHROMATICISM 2 (NEAPOLITAN & AUGMENTED SIXTH)
# ============================================================================

def create_neapolitan_chord(key_str: str, inversion: int = 1) -> chord.Chord:
    """
    Create a Neapolitan sixth chord (N6 or ♭II6).
    
    Textbook Reference: Chapter 20 - The Neapolitan Chord
    
    The Neapolitan is a major triad built on the lowered second scale degree.
    It typically appears in first inversion (hence "sixth" chord).
    
    Construction in C major/minor:
    - Root: D♭ (lowered 2nd)
    - Third: F
    - Fifth: A♭
    
    music21 Functions Used:
    - music21.pitch.Pitch()
    - music21.chord.Chord()
    - music21.key.Key()
    
    Args:
        key_str: e.g., "C minor" or "C major"
        inversion: 0 (root), 1 (first inversion, typical), 2 (second inversion)
        
    Returns:
        music21.chord.Chord object
        
    Usage in Study File:
        # Create N6 in C minor
        neapolitan = create_neapolitan_chord("C minor")
        print(neapolitan.pitches)  # [F3, A-3, D-4] (first inversion)
    """
    key_obj = key.Key(key_str)
    tonic = key_obj.tonic
    
    # Get the lowered 2nd scale degree
    lowered_second = pitch.Pitch(tonic.name)
    lowered_second.transpose(1, inPlace=True)  # Up a half step
    lowered_second.accidental = pitch.Accidental('flat')
    
    # Build major triad on lowered 2nd
    # Root: lowered 2nd
    # Third: +4 semitones (major third)
    # Fifth: +7 semitones (perfect fifth)
    
    root = lowered_second
    third = pitch.Pitch(midi=root.midi + 4)
    fifth = pitch.Pitch(midi=root.midi + 7)
    
    # Create chord
    neap_chord = chord.Chord([root, third, fifth])
    
    # Apply inversion
    if inversion == 1:
        # First inversion: third in bass
        neap_chord = neap_chord.inversion(1)
    elif inversion == 2:
        # Second inversion: fifth in bass
        neap_chord = neap_chord.inversion(2)
    
    return neap_chord


def create_italian_augmented_sixth(key_str: str) -> chord.Chord:
    """
    Create an Italian augmented sixth chord (It+6).
    
    Textbook Reference: Chapter 21 - Augmented Sixth Chords
    
    In C major/minor, the Italian sixth consists of:
    - A♭ (♭6)
    - C (tonic)
    - F# (♯4)
    
    The interval from A♭ to F# is an augmented sixth.
    
    music21 Functions Used:
    - music21.pitch.Pitch()
    - music21.chord.Chord()
    
    Args:
        key_str: e.g., "C major" or "C minor"
        
    Returns:
        music21.chord.Chord object
        
    Usage in Study File:
        it6 = create_italian_augmented_sixth("C major")
        print(it6.pitches)  # [A-3, C4, F#4]
    """
    key_obj = key.Key(key_str)
    tonic = key_obj.tonic
    
    # Get scale degrees
    # ♭6: 8 semitones up, then flatten
    flat_six = pitch.Pitch(tonic.name)
    flat_six.transpose(8, inPlace=True)
    if flat_six.accidental is None or flat_six.accidental.name == 'natural':
        flat_six.accidental = pitch.Accidental('flat')
    
    # Tonic
    tonic_pitch = pitch.Pitch(tonic.name)
    tonic_pitch.octave = flat_six.octave
    if tonic_pitch.midi < flat_six.midi:
        tonic_pitch.octave += 1
    
    # ♯4: 5 semitones up from tonic, then sharpen
    sharp_four = pitch.Pitch(tonic.name)
    sharp_four.transpose(5, inPlace=True)
    sharp_four.accidental = pitch.Accidental('sharp')
    sharp_four.octave = tonic_pitch.octave
    
    # Create chord
    it6 = chord.Chord([flat_six, tonic_pitch, sharp_four])
    
    return it6


def create_french_augmented_sixth(key_str: str) -> chord.Chord:
    """
    Create a French augmented sixth chord (Fr+6).
    
    Textbook Reference: Chapter 21 - Augmented Sixth Chords
    
    In C major/minor, the French sixth consists of:
    - A♭ (♭6)
    - C (tonic)
    - D (2nd)
    - F# (♯4)
    
    music21 Functions Used:
    - music21.pitch.Pitch()
    - music21.chord.Chord()
    
    Args:
        key_str: e.g., "C major"
        
    Returns:
        music21.chord.Chord object
        
    Usage in Study File:
        fr6 = create_french_augmented_sixth("C major")
        print(fr6.pitches)  # [A-3, C4, D4, F#4]
    """
    key_obj = key.Key(key_str)
    tonic = key_obj.tonic
    
    # Start with Italian sixth
    it6 = create_italian_augmented_sixth(key_str)
    
    # Add the 2nd scale degree
    second = pitch.Pitch(tonic.name)
    second.transpose(2, inPlace=True)  # Whole step up
    second.octave = it6.pitches[1].octave  # Same octave as tonic
    
    # Create new chord with all four pitches
    fr6 = chord.Chord(list(it6.pitches) + [second])
    
    return fr6


def create_german_augmented_sixth(key_str: str) -> chord.Chord:
    """
    Create a German augmented sixth chord (Ger+6).
    
    Textbook Reference: Chapter 21 - Augmented Sixth Chords
    
    In C major/minor, the German sixth consists of:
    - A♭ (♭6)
    - C (tonic)
    - E♭ (♭3)
    - F# (♯4)
    
    music21 Functions Used:
    - music21.pitch.Pitch()
    - music21.chord.Chord()
    
    Args:
        key_str: e.g., "C major"
        
    Returns:
        music21.chord.Chord object
        
    Usage in Study File:
        ger6 = create_german_augmented_sixth("C major")
        print(ger6.pitches)  # [A-3, C4, E-4, F#4]
    """
    key_obj = key.Key(key_str)
    tonic = key_obj.tonic
    
    # Start with Italian sixth
    it6 = create_italian_augmented_sixth(key_str)
    
    # Add the ♭3 scale degree
    flat_three = pitch.Pitch(tonic.name)
    flat_three.transpose(3, inPlace=True)  # Minor third up
    if flat_three.accidental is None:
        flat_three.accidental = pitch.Accidental('flat')
    flat_three.octave = it6.pitches[1].octave
    
    # Create new chord
    ger6 = chord.Chord(list(it6.pitches) + [flat_three])
    
    return ger6


# ============================================================================
# PART SIX: FORM & ANALYSIS TOOLS
# ============================================================================

def analyze_phrase_structure(score: stream.Score) -> List[Dict]:
    """
    Analyze the phrase structure of a piece.
    
    Textbook Reference: Chapter 9 - Melodic Figuration, Phrase Structure
    
    Identifies:
    - Phrase boundaries (usually at cadences)
    - Phrase lengths
    - Parallel vs. contrasting periods
    
    music21 Functions Used:
    - music21.analysis.phraseAnalysis()
    - Cadence detection (our analyze_cadence_type function)
    
    Args:
        score: music21.stream.Score
        
    Returns:
        List of phrase dictionaries
        
    Usage in Study File:
        phrases = analyze_phrase_structure(score)
        for i, phrase in enumerate(phrases, 1):
            print(f"Phrase {i}: measures {phrase['start']}-{phrase['end']}")
            print(f"  Length: {phrase['length']} measures")
            print(f"  Ends with: {phrase['cadence']}")
    """
    phrases = []
    
    # Get all measures
    measures = list(score.parts[0].getElementsByClass('Measure'))
    
    # Simple heuristic: phrases typically end at cadences (every 4-8 measures)
    # This would need refinement based on actual cadence analysis
    
    phrase_start = 1
    for i, measure in enumerate(measures, 1):
        # Check if this could be a cadence point
        if i % 4 == 0:  # Simplified: assume 4-bar phrases
            # Analyze cadence
            cadence = analyze_cadence_type(score, (max(1, i-1), i))
            
            if 'Cadence' in cadence or i == len(measures):
                phrases.append({
                    'start': phrase_start,
                    'end': i,
                    'length': i - phrase_start + 1,
                    'cadence': cadence
                })
                phrase_start = i + 1
    
    return phrases


def identify_sequence(score: stream.Score, min_repetitions: int = 2) -> List[Dict]:
    """
    Identify sequential passages in the score.
    
    Textbook Reference: Chapter 10 - Sequences
    
    A sequence is a pattern that repeats at different pitch levels.
    
    music21 Functions Used:
    - music21.search.serial (for pattern matching)
    - music21.interval.Interval()
    
    Args:
        score: music21.stream.Score
        min_repetitions: Minimum number of times pattern must repeat
        
    Returns:
        List of sequence dictionaries
        
    Usage in Study File:
        sequences = identify_sequence(score)
        for seq in sequences:
            print(f"Sequence found at measure {seq['start_measure']}")
            print(f"  Pattern length: {seq['pattern_length']} notes")
            print(f"  Repetitions: {seq['repetitions']}")
            print(f"  Transposition: {seq['interval']}")
    """
    sequences = []
    
    # Get melody
    melody = score.parts[0].flatten().notes
    
    # Try different pattern lengths (2-8 notes)
    for pattern_length in range(2, 9):
        for i in range(len(melody) - pattern_length * min_repetitions):
            pattern = melody[i:i + pattern_length]
            
            # Get intervals of pattern
            pattern_intervals = []
            for j in range(len(pattern) - 1):
                intv = interval.Interval(pattern[j], pattern[j + 1])
                pattern_intervals.append(intv.semitones)
            
            # Look for repetitions
            repetitions = 1
            transposition_intervals = []
            
            for k in range(i + pattern_length, len(melody) - pattern_length + 1, pattern_length):
                candidate = melody[k:k + pattern_length]
                
                # Get intervals of candidate
                candidate_intervals = []
                for j in range(len(candidate) - 1):
                    intv = interval.Interval(candidate[j], candidate[j + 1])
                    candidate_intervals.append(intv.semitones)
                
                # Check if intervals match
                if pattern_intervals == candidate_intervals:
                    repetitions += 1
                    # Get transposition interval
                    trans_intv = interval.Interval(pattern[0], candidate[0])
                    transposition_intervals.append(trans_intv.semitones)
                else:
                    break
            
            if repetitions >= min_repetitions:
                sequences.append({
                    'start_measure': pattern[0].measureNumber,
                    'start_offset': pattern[0].offset,
                    'pattern_length': pattern_length,
                    'repetitions': repetitions,
                    'interval': transposition_intervals[0] if transposition_intervals else 0
                })
    
    return sequences


# ============================================================================
# INTEGRATION EXAMPLES
# ============================================================================

def example_complete_harmonic_analysis(score: stream.Score, key_str: str):
    """
    Complete harmonic analysis combining all tools.
    
    This demonstrates how to use all the template functions together
    in a study file for comprehensive analysis.
    """
    print("="*70)
    print("COMPLETE HARMONIC ANALYSIS")
    print("="*70)
    
    # 1. Check voice leading
    print("\n[1] Voice Leading Analysis:")
    vl_errors = check_voice_leading_errors(score)
    if any(vl_errors.values()):
        for error_type, errors in vl_errors.items():
            if errors:
                print(f"  ⚠ {error_type}: {len(errors)} instance(s)")
                for e in errors[:3]:  # Show first 3
                    print(f"     Measure {e.get('measure', '?')}")
    else:
        print("  ✓ No voice leading errors detected")
    
    # 2. Analyze cadences
    print("\n[2] Cadence Analysis:")
    # Assuming 8-bar piece with cadences at measures 4 and 8
    for measure in [4, 8]:
        cadence = analyze_cadence_type(score, (measure - 1, measure))
        print(f"  Measure {measure}: {cadence}")
    
    # 3. Check seventh resolutions
    print("\n[3] Seventh Chord Resolutions:")
    seventh_errors = check_seventh_resolution(score)
    if seventh_errors:
        print(f"  ⚠ {len(seventh_errors)} resolution error(s)")
        for e in seventh_errors[:3]:
            print(f"     Measure {e['measure']}: {e['error']}")
    else:
        print("  ✓ All sevenths resolve correctly")
    
    # 4. Analyze phrase structure
    print("\n[4] Phrase Structure:")
    phrases = analyze_phrase_structure(score)
    for i, phrase in enumerate(phrases, 1):
        print(f"  Phrase {i}: mm. {phrase['start']}-{phrase['end']} ({phrase['length']} bars)")
        print(f"     Cadence: {phrase['cadence']}")
    
    # 5. Identify sequences
    print("\n[5] Sequential Passages:")
    sequences = identify_sequence(score)
    if sequences:
        for seq in sequences[:3]:  # Show first 3
            print(f"  Sequence at m.{seq['start_measure']}:")
            print(f"     {seq['repetitions']} repetitions of {seq['pattern_length']}-note pattern")
    else:
        print("  No sequences detected")
    
    print("\n" + "="*70)


"""
STUDY FILE INTEGRATION TEMPLATE
================================

Here's how to use these functions in a study file (e.g., eighteenth.py):

```python
# eighteenth.py - Complete Harmonic Analysis Study

from music21 import converter
from TONAL_HARMONY_TEMPLATES import (
    check_voice_leading_errors,
    validate_harmonic_progression,
    analyze_cadence_type,
    check_seventh_resolution,
    create_neapolitan_chord,
    example_complete_harmonic_analysis
)

# Your composition
SOPRANO_LILY = r"..."
ALTO_LILY = r"..."
TENOR_LILY = r"..."
BASS_LILY = r"..."

def build_score_data():
    # Build your score...
    score = build_four_part_score()
    
    # Run complete analysis
    example_complete_harmonic_analysis(score, "C major")
    
    return score_data

if __name__ == '__main__':
    run_pipeline_from_file(__file__)
```

END OF TEMPLATES
"""
