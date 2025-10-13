"""
STATION 4 PROGRAMMATIC EXAMPLES
================================

This file demonstrates the FULL POWER of music21 transformations in Station 4.
These are ready-to-use examples showing complex musical operations.

Music21 is a powerful music analysis and generation library. This file shows
how to leverage its capabilities in the Codempose framework.

CATEGORIES:
1. Pitch Transformations (transpose, invert, retrograde)
2. Rhythm Transformations (augmentation, diminution, meter changes)
3. Harmonic Analysis (chord identification, voice leading)
4. Contrapuntal Techniques (canon, fugue subjects)
5. Algorithmic Composition (pattern generation, cellular automata)
6. Advanced Analysis (Roman numeral analysis, key detection)
"""

from lilypond_parser import parse_lilypond_to_data
from music_data import extract_data_from_part, data_to_part
from voice_documentation import register_and_document_voice
import music21


# ============================================================================
# CATEGORY 1: PITCH TRANSFORMATIONS
# ============================================================================

def example_transpose_diatonic(events, voice_lookup, metadata):
    """
    Transpose by diatonic intervals (stays in key).
    
    Music21 Feature: Part.transpose() with diatonic intervals
    """
    part = data_to_part(events)
    
    # Transpose up a diatonic fifth (C→G in C major, staying in key)
    transposed_part = part.transpose('P5')  # Perfect 5th
    
    result = extract_data_from_part(transposed_part)
    register_and_document_voice('DIATONIC_UP_5TH', result, voice_lookup, metadata)
    return result


def example_transpose_chromatic(events, voice_lookup, metadata):
    """
    Transpose by chromatic semitones (may leave key).
    
    Music21 Feature: Part.transpose() with integer semitones
    """
    part = data_to_part(events)
    
    # Transpose up 7 semitones (perfect fifth chromatically)
    transposed_part = part.transpose(7)
    
    result = extract_data_from_part(transposed_part)
    register_and_document_voice('CHROMATIC_UP_7', result, voice_lookup, metadata)
    return result


def example_inversion_mirror(events, axis_pitch='C4', voice_lookup=None, metadata=None):
    """
    Mirror inversion around a pitch axis.
    
    Music21 Feature: Note.transpose() with calculated intervals
    Uses the composition_shorthand.invert_events() implementation
    """
    from composition_shorthand import invert_events
    
    # Invert around middle C
    inverted = invert_events(events, axis_pitch)
    
    if voice_lookup and metadata:
        register_and_document_voice('MIRROR_INVERSION', inverted, voice_lookup, metadata)
    return inverted


def example_retrograde(events, voice_lookup, metadata):
    """
    Reverse the order of notes (crab motion).
    
    Music21 Feature: List reversal of Part elements
    """
    # Simple reversal
    retrograde = list(reversed(events))
    
    register_and_document_voice('RETROGRADE', retrograde, voice_lookup, metadata)
    return retrograde


def example_retrograde_inversion(events, axis_pitch='C4', voice_lookup=None, metadata=None):
    """
    Combine retrograde and inversion (crab inversion).
    
    Music21 Feature: Combining transformations
    """
    from composition_shorthand import invert_events
    
    # First invert, then reverse
    inverted = invert_events(events, axis_pitch)
    retro_inv = list(reversed(inverted))
    
    if voice_lookup and metadata:
        register_and_document_voice('RETROGRADE_INVERSION', retro_inv, voice_lookup, metadata)
    return retro_inv


# ============================================================================
# CATEGORY 2: RHYTHM TRANSFORMATIONS
# ============================================================================

def example_augmentation(events, factor=2.0, voice_lookup=None, metadata=None):
    """
    Stretch rhythm by a factor (augmentation).
    
    Music21 Feature: Modify quarterLength of all notes
    Example: factor=2.0 doubles all durations (whole note → breve)
    """
    augmented = []
    for event in events:
        aug_event = event.copy()
        aug_event['ql'] = event['ql'] * factor
        augmented.append(aug_event)
    
    if voice_lookup and metadata:
        register_and_document_voice(f'AUGMENTED_x{factor}', augmented, voice_lookup, metadata)
    return augmented


def example_diminution(events, factor=0.5, voice_lookup=None, metadata=None):
    """
    Compress rhythm by a factor (diminution).
    
    Music21 Feature: Modify quarterLength of all notes
    Example: factor=0.5 halves all durations (quarter → eighth)
    """
    diminished = []
    for event in events:
        dim_event = event.copy()
        dim_event['ql'] = event['ql'] * factor
        diminished.append(dim_event)
    
    if voice_lookup and metadata:
        register_and_document_voice(f'DIMINISHED_x{factor}', diminished, voice_lookup, metadata)
    return diminished


def example_rhythmic_displacement(events, offset_ql=1.0, voice_lookup=None, metadata=None):
    """
    Add a rest at the beginning to displace the rhythm.
    
    Music21 Feature: Insert rests to create syncopation/hocket effects
    """
    rest_event = {
        'type': 'rest',
        'ql': offset_ql,
        'step': None,
        'octave': None,
        'alter': 0
    }
    
    displaced = [rest_event] + events
    
    if voice_lookup and metadata:
        register_and_document_voice('DISPLACED', displaced, voice_lookup, metadata)
    return displaced


def example_swing_rhythm(events, voice_lookup=None, metadata=None):
    """
    Convert straight eighths to swing rhythm (long-short pattern).
    
    Music21 Feature: Modify quarterLength patterns
    """
    swung = []
    for i, event in enumerate(events):
        if event['ql'] == 0.5:  # Eighth note
            swung_event = event.copy()
            # Alternate: long (2/3 beat) and short (1/3 beat)
            swung_event['ql'] = 0.666 if i % 2 == 0 else 0.333
            swung.append(swung_event)
        else:
            swung.append(event.copy())
    
    if voice_lookup and metadata:
        register_and_document_voice('SWING_RHYTHM', swung, voice_lookup, metadata)
    return swung


# ============================================================================
# CATEGORY 3: HARMONIC ANALYSIS & GENERATION
# ============================================================================

def example_extract_harmony(melody_events, voice_lookup, metadata):
    """
    Extract implied harmony from melody using music21 analysis.
    
    Music21 Feature: chordify() - reduces music to vertical harmonies
    """
    melody_part = data_to_part(melody_events)
    
    # Analyze harmony
    chords = melody_part.chordify()
    
    # Extract bass notes (root of each chord)
    bass_events = []
    for chord in chords.flatten().notesAndRests:
        if isinstance(chord, music21.chord.Chord):
            bass_note = chord.bass()
            bass_events.append({
                'type': 'note',
                'step': bass_note.pitch.step,
                'octave': max(2, bass_note.pitch.octave - 1),  # Lower octave
                'alter': bass_note.pitch.accidental.alter if bass_note.pitch.accidental else 0,
                'ql': chord.quarterLength
            })
        elif isinstance(chord, music21.note.Rest):
            bass_events.append({
                'type': 'rest',
                'ql': chord.quarterLength,
                'step': None,
                'octave': None,
                'alter': 0
            })
    
    register_and_document_voice('EXTRACTED_BASS', bass_events, voice_lookup, metadata)
    return bass_events


def example_chord_voicing(events, voice_lookup, metadata):
    """
    Generate chord voicing from a melody.
    
    Music21 Feature: Chord construction with specific intervals
    """
    voiced_events = []
    
    for event in events:
        if event['type'] == 'note':
            # Create a triad (root, third, fifth)
            root_pitch = music21.pitch.Pitch(
                step=event['step'],
                octave=event['octave'],
                accidental=event['alter']
            )
            
            # Build major or minor triad
            third = root_pitch.transpose('M3')  # Major third
            fifth = root_pitch.transpose('P5')  # Perfect fifth
            
            # Create chord event (simplified - uses first pitch as representative)
            voiced_events.append({
                'type': 'chord',
                'pitches': [
                    {'step': root_pitch.step, 'octave': root_pitch.octave, 
                     'alter': root_pitch.accidental.alter if root_pitch.accidental else 0},
                    {'step': third.step, 'octave': third.octave,
                     'alter': third.accidental.alter if third.accidental else 0},
                    {'step': fifth.step, 'octave': fifth.octave,
                     'alter': fifth.accidental.alter if fifth.accidental else 0},
                ],
                'step': root_pitch.step,
                'octave': root_pitch.octave,
                'alter': root_pitch.accidental.alter if root_pitch.accidental else 0,
                'ql': event['ql']
            })
        else:
            voiced_events.append(event)
    
    register_and_document_voice('CHORD_VOICING', voiced_events, voice_lookup, metadata)
    return voiced_events


# ============================================================================
# CATEGORY 4: CONTRAPUNTAL TECHNIQUES
# ============================================================================

def example_canon_at_interval(events, interval=7, delay_ql=4.0, voice_lookup=None, metadata=None):
    """
    Create a canon (strict imitation) at a given interval and time delay.
    
    Music21 Feature: transpose() + rhythmic offset
    Classical technique: Canon at the fifth (interval=7 semitones)
    """
    from composition_shorthand import transpose_events
    
    # Transpose the melody
    follower = transpose_events(events, interval)
    
    # Add delay (rests at the beginning)
    rest_event = {'type': 'rest', 'ql': delay_ql, 'step': None, 'octave': None, 'alter': 0}
    delayed_follower = [rest_event] + follower
    
    if voice_lookup and metadata:
        register_and_document_voice(f'CANON_FOLLOWER_{interval}', delayed_follower, voice_lookup, metadata)
    return delayed_follower


def example_augmentation_canon(events, voice_lookup, metadata):
    """
    Create a canon where the follower is in augmentation (twice as slow).
    
    Music21 Feature: Rhythmic transformation in imitation
    Bach's Musical Offering features this technique
    """
    # Double all durations for the follower
    augmented_follower = []
    for event in events:
        aug_event = event.copy()
        aug_event['ql'] = event['ql'] * 2.0
        augmented_follower.append(aug_event)
    
    register_and_document_voice('AUGMENTATION_CANON', augmented_follower, voice_lookup, metadata)
    return augmented_follower


def example_invertible_counterpoint(melody_events, counterpoint_events, voice_lookup, metadata):
    """
    Swap melody and counterpoint by octave (invertible counterpoint).
    
    Music21 Feature: transpose() by octave
    Used extensively in fugues and inventions
    """
    from composition_shorthand import transpose_events
    
    # Transpose melody down an octave
    melody_low = transpose_events(melody_events, -12)
    
    # Transpose counterpoint up an octave
    counterpoint_high = transpose_events(counterpoint_events, 12)
    
    register_and_document_voice('MELODY_INVERTED_LOW', melody_low, voice_lookup, metadata)
    register_and_document_voice('COUNTERPOINT_INVERTED_HIGH', counterpoint_high, voice_lookup, metadata)
    
    return melody_low, counterpoint_high


# ============================================================================
# CATEGORY 5: ALGORITHMIC COMPOSITION
# ============================================================================

def example_sequence_pattern(events, repetitions=3, transpose_step=2, voice_lookup=None, metadata=None):
    """
    Create a melodic sequence (pattern repeated at different pitches).
    
    Music21 Feature: Pattern repetition with transposition
    Common in Baroque and Classical music
    """
    from composition_shorthand import transpose_events
    
    sequence = []
    for i in range(repetitions):
        transposed = transpose_events(events, transpose_step * i)
        sequence.extend(transposed)
    
    if voice_lookup and metadata:
        register_and_document_voice(f'SEQUENCE_x{repetitions}', sequence, voice_lookup, metadata)
    return sequence


def example_fragmentation(events, fragment_length=2, voice_lookup=None, metadata=None):
    """
    Take fragments of a melody and develop them.
    
    Music21 Feature: Slice and manipulate event lists
    Developmental technique in sonata form
    """
    # Take only the first N events as a motive
    fragment = events[:fragment_length]
    
    if voice_lookup and metadata:
        register_and_document_voice(f'FRAGMENT_{fragment_length}', fragment, voice_lookup, metadata)
    return fragment


def example_motivic_development(events, voice_lookup, metadata):
    """
    Develop a motive through multiple transformations.
    
    Music21 Feature: Combining multiple transformations
    Beethoven's technique of motivic development
    """
    from composition_shorthand import transpose_events, invert_events
    
    # Original motive (first 4 notes)
    motive = events[:4]
    
    # Development 1: Transposed up
    dev1 = transpose_events(motive, 7)
    
    # Development 2: Inverted
    dev2 = invert_events(motive, 'c4')
    
    # Development 3: Retrograde
    dev3 = list(reversed(motive))
    
    # Combine all developments
    development = motive + dev1 + dev2 + dev3
    
    register_and_document_voice('MOTIVIC_DEVELOPMENT', development, voice_lookup, metadata)
    return development


def example_rhythmic_ostinato(pattern_events, repetitions=8, voice_lookup=None, metadata=None):
    """
    Create a rhythmic ostinato (repeated pattern).
    
    Music21 Feature: Pattern repetition
    Common in minimalist and dance music
    """
    ostinato = pattern_events * repetitions
    
    if voice_lookup and metadata:
        register_and_document_voice(f'OSTINATO_x{repetitions}', ostinato, voice_lookup, metadata)
    return ostinato


# ============================================================================
# CATEGORY 6: ADVANCED ANALYSIS
# ============================================================================

def example_extract_contour(events, voice_lookup, metadata):
    """
    Extract the melodic contour (up/down/same pattern).
    
    Music21 Feature: Pitch comparison and analysis
    Useful for melodic similarity analysis
    """
    if len(events) < 2:
        return events
    
    # Calculate intervals between consecutive notes
    contour = []
    prev_pitch = None
    
    for event in events:
        if event['type'] == 'note':
            current_pitch = event['octave'] * 12 + \
                           {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}[event['step'].lower()] + \
                           event['alter']
            
            if prev_pitch is not None:
                interval = current_pitch - prev_pitch
                contour.append(interval)
            
            prev_pitch = current_pitch
    
    # Store as metadata (contour is a list of intervals, not events)
    if metadata:
        metadata['contour_analysis'] = {
            'intervals': contour,
            'ascending_steps': sum(1 for i in contour if i > 0),
            'descending_steps': sum(1 for i in contour if i < 0),
            'repeated_notes': sum(1 for i in contour if i == 0)
        }
    
    return events  # Return original events with analysis added to metadata


def example_rhythmic_density(events, voice_lookup, metadata):
    """
    Analyze rhythmic density (notes per measure).
    
    Music21 Feature: Duration analysis
    """
    total_duration = sum(e['ql'] for e in events)
    note_count = sum(1 for e in events if e['type'] == 'note')
    
    density = note_count / (total_duration / 4.0) if total_duration > 0 else 0
    
    if metadata:
        metadata['rhythmic_analysis'] = {
            'total_duration_quarters': total_duration,
            'note_count': note_count,
            'notes_per_measure': density,
            'average_note_duration': total_duration / note_count if note_count > 0 else 0
        }
    
    return events


# ============================================================================
# COMPLETE EXAMPLE: FUGUE SUBJECT TREATMENT
# ============================================================================

def example_fugue_exposition(subject_events, voice_lookup, metadata):
    """
    Create a simple fugue exposition with subject, answer, and countersubject.
    
    Music21 Feature: Complete contrapuntal framework
    Demonstrates: transposition, inversion, counterpoint
    """
    from composition_shorthand import transpose_events, invert_events
    
    # Subject (original)
    subject = subject_events
    register_and_document_voice('FUGUE_SUBJECT', subject, voice_lookup, metadata)
    
    # Answer (transposed to dominant - up perfect 5th = 7 semitones)
    answer = transpose_events(subject, 7)
    register_and_document_voice('FUGUE_ANSWER', answer, voice_lookup, metadata)
    
    # Countersubject (inverted subject)
    countersubject = invert_events(subject, 'c4')
    register_and_document_voice('FUGUE_COUNTERSUBJECT', countersubject, voice_lookup, metadata)
    
    # Subject in augmentation (twice as slow, for stretto)
    augmented_subject = []
    for event in subject:
        aug_event = event.copy()
        aug_event['ql'] = event['ql'] * 2.0
        augmented_subject.append(aug_event)
    register_and_document_voice('FUGUE_SUBJECT_AUGMENTED', augmented_subject, voice_lookup, metadata)
    
    return {
        'subject': subject,
        'answer': answer,
        'countersubject': countersubject,
        'subject_augmented': augmented_subject
    }


# ============================================================================
# USAGE EXAMPLE IN build_score_data()
# ============================================================================

"""
USAGE IN A STUDY FILE:

def build_score_data():
    metadata = {...}
    
    # Parse original snippet
    theme_data = parse_lilypond_to_data(THEME_LILY, 'Theme')
    theme = theme_data['parts']['Theme']
    
    voice_lookup = {'THEME': theme}
    
    # === APPLY TRANSFORMATIONS ===
    
    # 1. Basic transformations
    soprano = example_transpose_diatonic(theme, voice_lookup, metadata)
    alto = example_inversion_mirror(theme, 'c4', voice_lookup, metadata)
    
    # 2. Rhythmic variations
    tenor = example_augmentation(theme, factor=2.0, voice_lookup, metadata)
    
    # 3. Contrapuntal techniques
    bass = example_canon_at_interval(theme, interval=7, delay_ql=4.0, voice_lookup, metadata)
    
    # 4. Algorithmic development
    development = example_motivic_development(theme, voice_lookup, metadata)
    
    # 5. Advanced: Fugue treatment
    fugue_parts = example_fugue_exposition(theme, voice_lookup, metadata)
    
    # Build final score
    return {
        'metadata': metadata,
        'parts': {
            'Soprano': soprano,
            'Alto': alto,
            'Tenor': tenor,
            'Bass': bass
        }
    }
"""
