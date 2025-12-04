"""
Codempose music21 API Templates and Examples

This file provides comprehensive templates for all music21 functionality
that has been integrated into Codempose, plus additional capabilities
that are available for future extensions.

SECTIONS:
1. Basic Note and Rest Creation
2. Pitch Manipulation
3. Duration and Rhythm
4. Articulations and Expressions
5. Dynamics
6. Ornaments (Grace Notes, Trills, etc.)
7. Tuplets
8. Ties and Slurs
9. Chords
10. Measures and Time Signatures
11. Key Signatures
12. Tempo Markings
13. Parts and Voices
14. Score Assembly
15. Roman Numeral Analysis (Harmonic)
16. Analysis Tools
17. Export and Conversion
"""

from music21 import (
    note, pitch, duration, articulations, expressions, dynamics,
    tempo, meter, key, clef, chord, stream, tie, spanner,
    roman, interval, scale, harmony
)

# ============================================================================
# 1. BASIC NOTE AND REST CREATION
# ============================================================================

def create_basic_notes():
    """Create notes in various ways."""
    
    # Method 1: Simple pitch string
    n1 = note.Note('C4')
    n1.quarterLength = 1.0
    
    # Method 2: Pitch name + octave
    n2 = note.Note('D')
    n2.octave = 5
    n2.quarterLength = 2.0  # Half note
    
    # Method 3: MIDI number
    n3 = note.Note()
    n3.pitch.midi = 60  # Middle C
    n3.quarterLength = 0.5  # Eighth note
    
    # Method 4: Pitch class + accidental
    n4 = note.Note()
    n4.pitch.step = 'E'
    n4.pitch.octave = 4
    n4.pitch.accidental = 'sharp'  # or 'flat', 'natural', 'double-sharp', etc.
    
    # Create a rest
    r1 = note.Rest()
    r1.quarterLength = 1.0
    
    # Full rest (whole measure)
    r2 = note.Rest()
    r2.duration.type = 'whole'
    
    return [n1, n2, n3, n4, r1, r2]


# ============================================================================
# 2. PITCH MANIPULATION
# ============================================================================

def manipulate_pitches():
    """Advanced pitch operations."""
    
    n = note.Note('C4')
    
    # Get pitch properties
    step = n.pitch.step                    # 'C'
    octave = n.pitch.octave                # 4
    midi_number = n.pitch.midi             # 60
    frequency = n.pitch.frequency          # 261.63 Hz
    pitch_class = n.pitch.pitchClass       # 0 (C=0, C#=1, D=2, etc.)
    
    # Transpose
    n_up = n.transpose('M3')               # Up major third (C -> E)
    n_down = n.transpose('-P5')            # Down perfect fifth (C -> F below)
    n_octave = n.transpose('P8')           # Up one octave
    
    # Alter pitch
    n.pitch.octave = 5                     # Change octave
    n.pitch.accidental = pitch.Accidental('sharp')
    
    # Name with octave
    name = n.nameWithOctave                # 'C#5'
    
    return n


def pitch_intervals():
    """Work with intervals between pitches."""
    
    n1 = note.Note('C4')
    n2 = note.Note('E4')
    
    # Get interval
    i = interval.Interval(n1, n2)
    print(f"Interval: {i.name}")           # 'M3' (major third)
    print(f"Semitones: {i.semitones}")     # 4
    print(f"Direction: {i.direction}")     # 1 (ascending)
    
    # Create interval
    perfect_fifth = interval.Interval('P5')
    n3 = n1.transpose(perfect_fifth)       # C4 -> G4
    
    return i


# ============================================================================
# 3. DURATION AND RHYTHM
# ============================================================================

def note_durations():
    """All standard note durations."""
    
    # By quarter length
    whole = note.Note('C4', quarterLength=4.0)
    half = note.Note('C4', quarterLength=2.0)
    quarter = note.Note('C4', quarterLength=1.0)
    eighth = note.Note('C4', quarterLength=0.5)
    sixteenth = note.Note('C4', quarterLength=0.25)
    thirty_second = note.Note('C4', quarterLength=0.125)
    
    # By duration type
    n = note.Note('C4')
    n.duration.type = 'whole'              # or 'half', 'quarter', 'eighth', '16th', '32nd'
    
    # Dotted notes
    dotted_quarter = note.Note('C4')
    dotted_quarter.duration.dots = 1       # Adds 50% to duration
    dotted_quarter.quarterLength           # = 1.5
    
    double_dotted = note.Note('C4')
    double_dotted.duration.dots = 2        # Adds 75% to duration
    
    # Tied notes (see section 8)
    
    return [whole, half, quarter, eighth, dotted_quarter]


# ============================================================================
# 4. ARTICULATIONS AND EXPRESSIONS
# ============================================================================

def add_articulations():
    """Add articulation marks to notes."""
    
    n = note.Note('C4')
    
    # Single articulations
    n.articulations.append(articulations.Staccato())
    n.articulations.append(articulations.Accent())
    n.articulations.append(articulations.Tenuto())
    n.articulations.append(articulations.Staccatissimo())
    n.articulations.append(articulations.Marcato())
    
    # Other articulations
    # articulations.StrongAccent()
    # articulations.DetachedLegato()
    # articulations.Spiccato()
    # articulations.Snap()
    # articulations.Doit()
    # articulations.Falloff()
    # articulations.BreathMark()
    # articulations.Caesura()
    
    # Fermata
    n.expressions.append(expressions.Fermata())
    
    # Trill (see ornaments section)
    
    return n


def add_expressions():
    """Add expression marks."""
    
    n = note.Note('C4')
    
    # Fermata
    n.expressions.append(expressions.Fermata())
    
    # Turns and mordents (see ornaments)
    n.expressions.append(expressions.Turn())
    n.expressions.append(expressions.InvertedTurn())
    n.expressions.append(expressions.Mordent())
    n.expressions.append(expressions.InvertedMordent())
    
    # Tremolo
    n.expressions.append(expressions.Tremolo())
    
    # Trill
    n.expressions.append(expressions.Trill())
    
    return n


# ============================================================================
# 5. DYNAMICS
# ============================================================================

def add_dynamics():
    """Add dynamic markings."""
    
    n = note.Note('C4')
    
    # Common dynamics
    n.volume.velocity = 90                 # MIDI velocity (0-127)
    
    # Dynamic marks (attach to notes or measures)
    pp = dynamics.Dynamic('pp')            # pianissimo
    p = dynamics.Dynamic('p')              # piano
    mp = dynamics.Dynamic('mp')            # mezzo-piano
    mf = dynamics.Dynamic('mf')            # mezzo-forte
    f = dynamics.Dynamic('f')              # forte
    ff = dynamics.Dynamic('ff')            # fortissimo
    fff = dynamics.Dynamic('fff')          # fortississimo
    
    # Attach to note
    n.insertIntoNoteOrChord(0, f)
    
    # Wedges (crescendo/diminuendo) - see spanners section
    
    return n


def create_dynamic_wedges():
    """Create crescendo and diminuendo."""
    
    from music21 import dynamics
    
    # Crescendo
    cresc = dynamics.Crescendo()
    
    # Diminuendo
    dim = dynamics.Diminuendo()
    
    # Apply to a range of notes (see spanners)
    
    return cresc, dim


# ============================================================================
# 6. ORNAMENTS (GRACE NOTES, TRILLS, ETC.)
# ============================================================================

def create_grace_notes():
    """Create grace notes and other ornaments."""
    
    # Acciaccatura (slashed grace note)
    grace = note.Note('C5', quarterLength=0.0)  # Zero duration
    grace.duration.slash = True
    grace.duration.type = '16th'
    
    # Appoggiatura (unslashed grace note)
    grace2 = note.Note('D5', quarterLength=0.0)
    grace2.duration.slash = False
    grace2.duration.type = 'eighth'
    
    # Main note
    main = note.Note('E5', quarterLength=1.0)
    
    # Attach grace note (implementation varies by export format)
    
    return grace, main


def create_ornaments():
    """Create trill, turn, mordent marks."""
    
    n = note.Note('C4')
    
    # Trill
    trill = expressions.Trill()
    n.expressions.append(trill)
    
    # Turn
    turn = expressions.Turn()
    n.expressions.append(turn)
    
    # Inverted turn
    inv_turn = expressions.InvertedTurn()
    
    # Mordent
    mordent = expressions.Mordent()
    n.expressions.append(mordent)
    
    # Inverted mordent (prall)
    inv_mordent = expressions.InvertedMordent()
    
    return n


# ============================================================================
# 7. TUPLETS
# ============================================================================

def create_tuplets():
    """Create various tuplet types."""
    
    # Triplet (3 notes in space of 2)
    n1 = note.Note('C4', quarterLength=2.0/3)  # Each note is 2/3 of a quarter
    n2 = note.Note('D4', quarterLength=2.0/3)
    n3 = note.Note('E4', quarterLength=2.0/3)
    
    # Mark as tuplet
    from music21 import duration
    tup = duration.Tuplet(3, 2)  # 3 notes in space of 2
    n1.duration.appendTuplet(tup)
    n2.duration.appendTuplet(tup)
    n3.duration.appendTuplet(tup)
    
    # Quintuplet (5 in space of 4)
    q1 = note.Note('C4', quarterLength=4.0/5)
    quintuplet = duration.Tuplet(5, 4)
    q1.duration.appendTuplet(quintuplet)
    
    # Nested tuplets (3 in space of 2, within another tuplet)
    # More complex - see music21 documentation
    
    return [n1, n2, n3]


# ============================================================================
# 8. TIES AND SLURS
# ============================================================================

def create_ties():
    """Create tied notes."""
    
    # Two notes tied together
    n1 = note.Note('C4', quarterLength=1.0)
    n2 = note.Note('C4', quarterLength=1.0)
    
    # Create tie
    n1.tie = tie.Tie('start')
    n2.tie = tie.Tie('stop')
    
    # Three notes tied
    n3 = note.Note('C4', quarterLength=1.0)
    n3.tie = tie.Tie('continue')
    # Order: n1 (start), n3 (continue), n2 (stop)
    
    return [n1, n2]


def create_slurs():
    """Create slurs (phrasing)."""
    
    # Slurs are spanners that connect multiple notes
    n1 = note.Note('C4')
    n2 = note.Note('D4')
    n3 = note.Note('E4')
    
    # Create slur
    slur = spanner.Slur([n1, n2, n3])
    
    # Or attach individually
    # n1.insertIntoNoteOrChord(0, slur)
    
    return slur


# ============================================================================
# 9. CHORDS
# ============================================================================

def create_chords():
    """Create and manipulate chords."""
    
    # Method 1: From pitch strings
    c_major = chord.Chord(['C4', 'E4', 'G4'])
    c_major.quarterLength = 1.0
    
    # Method 2: From notes
    c_major2 = chord.Chord([
        note.Note('C4'),
        note.Note('E4'),
        note.Note('G4')
    ])
    
    # Method 3: From pitch objects
    c_major3 = chord.Chord([
        pitch.Pitch('C4'),
        pitch.Pitch('E4'),
        pitch.Pitch('G4')
    ])
    
    # Get chord properties
    root = c_major.root()                  # C
    bass = c_major.bass()                  # Lowest note (C)
    pitches = c_major.pitches              # All pitches
    
    # Chord quality
    quality = c_major.quality              # 'major'
    common_name = c_major.commonName       # 'major triad'
    
    # Add articulations to chord
    c_major.articulations.append(articulations.Accent())
    
    # Arpeggiate
    # (implementation varies by export)
    
    return c_major


def chord_analysis():
    """Analyze chord properties."""
    
    c = chord.Chord(['C4', 'E4', 'G4'])
    
    # Basic properties
    is_major = c.isMajorTriad()            # True
    is_minor = c.isMinorTriad()            # False
    is_dim = c.isDiminishedTriad()         # False
    is_aug = c.isAugmentedTriad()          # False
    
    # Seventh chords
    dom7 = chord.Chord(['C4', 'E4', 'G4', 'B-4'])
    is_dom7 = dom7.isDominantSeventh()     # True
    
    # Inversions
    inversion = c.inversion()              # 0 (root position)
    first_inv = c.inverted(1)              # First inversion (E-G-C)
    
    return c


# ============================================================================
# 10. MEASURES AND TIME SIGNATURES
# ============================================================================

def create_measures():
    """Create measures with time signatures."""
    
    # Create measure
    m = stream.Measure()
    m.number = 1
    
    # Add time signature
    ts = meter.TimeSignature('4/4')
    m.insert(0, ts)
    
    # Add notes
    m.append(note.Note('C4', quarterLength=1.0))
    m.append(note.Note('D4', quarterLength=1.0))
    m.append(note.Note('E4', quarterLength=1.0))
    m.append(note.Note('F4', quarterLength=1.0))
    
    # Common time signatures
    common_time = meter.TimeSignature('4/4')
    cut_time = meter.TimeSignature('2/2')
    three_four = meter.TimeSignature('3/4')
    six_eight = meter.TimeSignature('6/8')
    five_four = meter.TimeSignature('5/4')
    seven_eight = meter.TimeSignature('7/8')
    
    # Compound meters
    nine_eight = meter.TimeSignature('9/8')
    twelve_eight = meter.TimeSignature('12/8')
    
    return m


def measure_properties():
    """Work with measure properties."""
    
    m = stream.Measure()
    
    # Measure number
    m.number = 1
    
    # Barline types
    from music21 import bar
    m.rightBarline = bar.Barline('double')  # or 'final', 'heavy', 'dashed', etc.
    m.leftBarline = bar.Barline('heavy')
    
    # Pickup/anacrusis measure
    m.padAsAnacrusis()
    
    # Get measure duration
    duration = m.duration.quarterLength
    
    return m


# ============================================================================
# 11. KEY SIGNATURES
# ============================================================================

def create_key_signatures():
    """Create and work with key signatures."""
    
    # Major keys
    c_major = key.Key('C')
    g_major = key.Key('G')
    d_major = key.Key('D')
    f_major = key.Key('F')
    
    # Minor keys
    a_minor = key.Key('a')  # lowercase for minor
    e_minor = key.Key('e')
    d_minor = key.Key('d')
    
    # Or explicitly
    c_minor = key.Key('C', 'minor')
    
    # Get key properties
    tonic = c_major.tonic                  # C
    mode = c_major.mode                    # 'major'
    sharps = g_major.sharps                # 1
    flats = f_major.flats                  # 1
    
    # Get scale
    scale_pitches = c_major.pitches        # [C, D, E, F, G, A, B]
    
    # Relative keys
    relative_minor = c_major.relative      # a minor
    parallel_minor = c_major.parallel      # c minor
    
    return c_major


def key_analysis():
    """Analyze notes in context of key."""
    
    k = key.Key('C')
    
    # Scale degrees
    tonic = k.pitchFromDegree(1)           # C
    dominant = k.pitchFromDegree(5)        # G
    leading_tone = k.pitchFromDegree(7)    # B
    
    # Get degree from pitch
    degree = k.getScaleDegreeFromPitch('E')  # 3
    
    return k


# ============================================================================
# 12. TEMPO MARKINGS
# ============================================================================

def create_tempo():
    """Create tempo markings."""
    
    # Metronome mark (BPM)
    mm = tempo.MetronomeMark(number=120)   # 120 BPM
    mm_with_text = tempo.MetronomeMark(text='Allegro', number=120)
    
    # Specify beat unit
    quarter_120 = tempo.MetronomeMark(referent=1.0, number=120)  # Quarter = 120
    half_60 = tempo.MetronomeMark(referent=2.0, number=60)       # Half = 60
    
    # Text-only tempo
    allegro = tempo.TempoText('Allegro')
    andante = tempo.TempoText('Andante')
    presto = tempo.TempoText('Presto')
    
    # Get tempo in various units
    bpm = mm.number                        # 120
    quarter_bpm = mm.getQuarterBPM()       # Convert to quarter note BPM
    
    return mm


# ============================================================================
# 13. PARTS AND VOICES
# ============================================================================

def create_parts():
    """Create instrumental parts."""
    
    # Create part
    violin = stream.Part()
    violin.id = 'Violin'
    violin.partName = 'Violin'
    
    # Add clef
    violin.insert(0, clef.TrebleClef())
    
    # Add key signature
    violin.insert(0, key.Key('D'))
    
    # Add time signature
    violin.insert(0, meter.TimeSignature('4/4'))
    
    # Add tempo
    violin.insert(0, tempo.MetronomeMark(number=120))
    
    # Add measures
    m1 = stream.Measure(number=1)
    m1.append(note.Note('D5', quarterLength=4.0))
    violin.append(m1)
    
    return violin


def create_voices():
    """Create multiple voices in one staff."""
    
    # Voice 1
    voice1 = stream.Voice()
    voice1.id = 'voice1'
    voice1.append(note.Note('C5', quarterLength=4.0))
    
    # Voice 2 (simultaneous)
    voice2 = stream.Voice()
    voice2.id = 'voice2'
    voice2.append(note.Note('E4', quarterLength=2.0))
    voice2.append(note.Note('F4', quarterLength=2.0))
    
    # Add to measure
    m = stream.Measure()
    m.insert(0, voice1)
    m.insert(0, voice2)
    
    return m


# ============================================================================
# 14. SCORE ASSEMBLY
# ============================================================================

def create_score():
    """Assemble a complete score."""
    
    # Create score
    s = stream.Score()
    
    # Add metadata
    from music21 import metadata
    s.metadata = metadata.Metadata()
    s.metadata.title = 'My Composition'
    s.metadata.composer = 'Composer Name'
    
    # Create parts
    violin = stream.Part()
    violin.id = 'Violin'
    violin.partName = 'Violin'
    violin.insert(0, clef.TrebleClef())
    
    cello = stream.Part()
    cello.id = 'Cello'
    cello.partName = 'Cello'
    cello.insert(0, clef.BassClef())
    
    # Add measures to parts
    m1_vln = stream.Measure(number=1)
    m1_vln.append(note.Note('E5', quarterLength=4.0))
    violin.append(m1_vln)
    
    m1_cello = stream.Measure(number=1)
    m1_cello.append(note.Note('C3', quarterLength=4.0))
    cello.append(m1_cello)
    
    # Add parts to score
    s.insert(0, violin)
    s.insert(0, cello)
    
    return s


# ============================================================================
# 15. ROMAN NUMERAL ANALYSIS (HARMONIC)
# ============================================================================

def roman_numeral_analysis():
    """Analyze and create chords from Roman numerals."""
    
    # Create key context
    k = key.Key('C')
    
    # Create Roman numeral chords
    I = roman.RomanNumeral('I', k)         # C major triad
    IV = roman.RomanNumeral('IV', k)       # F major triad
    V = roman.RomanNumeral('V', k)         # G major triad
    vi = roman.RomanNumeral('vi', k)       # a minor triad
    
    # Get chord properties
    root = I.root()                        # C
    pitches = I.pitches                    # [C, E, G]
    bass = I.bass()                        # C
    quality = I.quality                    # 'major'
    
    # Seventh chords
    V7 = roman.RomanNumeral('V7', k)       # G dominant seventh
    ii7 = roman.RomanNumeral('ii7', k)     # d minor seventh
    
    # Inversions
    I6 = roman.RomanNumeral('I6', k)       # First inversion (C major)
    V64 = roman.RomanNumeral('V64', k)     # Second inversion (G major)
    
    # Secondary dominants
    V_of_V = roman.RomanNumeral('V/V', k)  # D major (V of V)
    
    # Augmented and diminished
    viio = roman.RomanNumeral('viio', k)   # B diminished
    III_plus = roman.RomanNumeral('III+', 'a')  # C augmented (in a minor)
    
    # Get scale degree
    degree = I.scaleDegree                 # 1
    
    return I, IV, V, vi


def chord_symbol_analysis():
    """Work with chord symbols (jazz notation)."""
    
    # Create from chord symbol
    from music21 import harmony
    
    c_maj = harmony.ChordSymbol('C')       # C major triad
    c_min = harmony.ChordSymbol('Cm')      # C minor triad
    c7 = harmony.ChordSymbol('C7')         # C dominant seventh
    c_maj7 = harmony.ChordSymbol('Cmaj7')  # C major seventh
    c_min7 = harmony.ChordSymbol('Cm7')    # C minor seventh
    
    # More complex symbols
    c_dim7 = harmony.ChordSymbol('Cdim7')
    c_half_dim = harmony.ChordSymbol('Cm7b5')
    c_aug = harmony.ChordSymbol('Caug')
    
    # Extensions
    c9 = harmony.ChordSymbol('C9')
    c13 = harmony.ChordSymbol('C13')
    
    # Slash chords (inversions)
    c_over_e = harmony.ChordSymbol('C/E')  # C major over E bass
    
    return c_maj


# ============================================================================
# 16. ANALYSIS TOOLS
# ============================================================================

def analyze_stream():
    """Analyze a stream of music."""
    
    s = stream.Stream()
    s.append(note.Note('C4'))
    s.append(note.Note('D4'))
    s.append(note.Note('E4'))
    
    # Get all notes
    all_notes = s.flatten().notes
    
    # Get highest/lowest pitch
    highest = s.flatten().notes.sorted.pitches[-1]
    lowest = s.flatten().notes.sorted.pitches[0]
    
    # Ambitus (range)
    ambitus = interval.Interval(lowest, highest)
    
    # Count notes
    num_notes = len(s.flatten().notes)
    
    # Duration
    total_duration = s.duration.quarterLength
    
    return s


def interval_analysis():
    """Analyze intervals in a melody."""
    
    s = stream.Stream()
    s.append(note.Note('C4'))
    s.append(note.Note('E4'))
    s.append(note.Note('G4'))
    
    # Get melodic intervals
    notes = list(s.flatten().notes)
    intervals = []
    for i in range(len(notes) - 1):
        intv = interval.Interval(notes[i], notes[i+1])
        intervals.append(intv.name)
    
    # intervals = ['M3', 'm3']
    
    return intervals


# ============================================================================
# 17. EXPORT AND CONVERSION
# ============================================================================

def export_formats():
    """Export to various formats."""
    
    s = stream.Score()
    # ... add content ...
    
    # Write to MusicXML
    s.write('musicxml', fp='output.musicxml')
    s.write('xml', fp='output.xml')  # Same as musicxml
    
    # Write to MIDI
    s.write('midi', fp='output.mid')
    
    # Write to LilyPond
    s.write('lily', fp='output.ly')
    s.write('lilypond', fp='output.ly')
    
    # Write to text
    s.write('text', fp='output.txt')
    
    # Show in notation software (if available)
    # s.show()
    # s.show('musicxml')
    # s.show('lily')
    
    # PDF (via LilyPond)
    # s.write('lily.pdf', fp='output.pdf')  # Requires LilyPond installed
    
    return s


def import_formats():
    """Import from various formats."""
    
    from music21 import converter
    
    # Parse MusicXML
    score = converter.parse('input.musicxml')
    
    # Parse MIDI
    score = converter.parse('input.mid')
    
    # Parse LilyPond
    score = converter.parse('input.ly')
    
    # Parse from string
    score = converter.parse("tinynotation: 4/4 c4 d e f g2 a")
    
    # Get specific format parser
    # xml_parser = converter.subConverters.ConverterMusicXML()
    
    return score


# ============================================================================
# PUTTING IT ALL TOGETHER: COMPLETE EXAMPLE
# ============================================================================

def complete_example():
    """
    Complete example: Create a simple two-part score with harmonic analysis.
    """
    
    # Create score
    s = stream.Score()
    s.metadata = metadata.Metadata()
    s.metadata.title = 'Simple Two-Part Example'
    s.metadata.composer = 'music21 Template'
    
    # Create melody part
    melody = stream.Part()
    melody.id = 'Melody'
    melody.partName = 'Melody'
    melody.insert(0, clef.TrebleClef())
    melody.insert(0, key.Key('C'))
    melody.insert(0, meter.TimeSignature('4/4'))
    melody.insert(0, tempo.MetronomeMark(number=120))
    
    # Measure 1
    m1 = stream.Measure(number=1)
    m1.append(note.Note('C5', quarterLength=1.0))
    n = note.Note('D5', quarterLength=1.0)
    n.articulations.append(articulations.Staccato())
    m1.append(n)
    m1.append(note.Note('E5', quarterLength=1.0))
    m1.append(note.Note('F5', quarterLength=1.0))
    melody.append(m1)
    
    # Measure 2
    m2 = stream.Measure(number=2)
    m2.append(note.Note('G5', quarterLength=2.0))
    m2.append(note.Note('E5', quarterLength=2.0))
    melody.append(m2)
    
    # Create bass part (from Roman numerals)
    bass = stream.Part()
    bass.id = 'Bass'
    bass.partName = 'Bass'
    bass.insert(0, clef.BassClef())
    bass.insert(0, key.Key('C'))
    bass.insert(0, meter.TimeSignature('4/4'))
    
    # Generate bass from harmonic analysis
    k = key.Key('C')
    progression = ['I', 'V', 'I']
    
    b1 = stream.Measure(number=1)
    I = roman.RomanNumeral('I', k)
    b1.append(note.Note(I.root(), quarterLength=2.0))
    V = roman.RomanNumeral('V', k)
    b1.append(note.Note(V.root(), quarterLength=2.0))
    bass.append(b1)
    
    b2 = stream.Measure(number=2)
    b2.append(note.Note(I.root(), quarterLength=4.0))
    bass.append(b2)
    
    # Add parts to score
    s.insert(0, melody)
    s.insert(0, bass)
    
    # Export
    # s.write('musicxml', fp='example.musicxml')
    # s.write('midi', fp='example.mid')
    
    return s


# ============================================================================
# ADDITIONAL RESOURCES
# ============================================================================

"""
MUSIC21 DOCUMENTATION:
https://web.mit.edu/music21/doc/

KEY MODULES:
- music21.note - Notes and rests
- music21.pitch - Pitch representation
- music21.duration - Note durations
- music21.stream - Containers (Score, Part, Measure)
- music21.chord - Chords
- music21.key - Key signatures
- music21.meter - Time signatures
- music21.tempo - Tempo markings
- music21.roman - Roman numeral analysis
- music21.harmony - Chord symbols
- music21.interval - Intervals
- music21.scale - Scales
- music21.articulations - Articulation marks
- music21.expressions - Expression marks
- music21.dynamics - Dynamic markings
- music21.clef - Clefs
- music21.bar - Barlines
- music21.spanner - Slurs, crescendos, etc.
- music21.metadata - Score metadata

CODEMPOSE INTEGRATION:
This template shows how music21 objects can be created and manipulated.
In Codempose:
1. LilyPond is parsed to canonical format
2. Canonical format is converted to music21 via data_to_part()
3. music21 objects are analyzed/transformed (e.g., harmonic_engine)
4. music21 objects are converted back via part_to_data()
5. Canonical format is exported to PDF/MusicXML/MIDI
"""

if __name__ == '__main__':
    # Run complete example
    score = complete_example()
    print("Complete example score created!")
    print(f"Duration: {score.duration.quarterLength} quarter notes")
    print(f"Parts: {len(score.parts)}")
    print(f"Measures in melody: {len(score.parts[0].getElementsByClass('Measure'))}")
