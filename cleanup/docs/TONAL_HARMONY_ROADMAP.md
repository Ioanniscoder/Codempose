# Programmatic Roadmap for a Tonal Harmony Assistant

This document outlines a framework for building a programmatic compositional assistant. The goal is to create a set of tools that handle the rules of tonal harmony, allowing the user (composer) to focus on creative decisions. The framework is structured to follow the chapters of the textbook *Tonal Harmony with an Introduction to Twentieth-Century Music*.

---

## **Part One: Fundamentals (Chapters 1-4)**

This section establishes the basic building blocks of music. Programmatic support will focus on generating and identifying these elements on demand.

### 🎵 **Feature: Scale & Interval Generator**

Based on **Chapter 1: Elements of Pitch**, this feature provides functions to create scales and manipulate intervals programmatically.

  * **Programmatic Support:** A function that, given a tonic and mode, returns a `music21.scale` object. Another function would transpose a note by a specific interval.
  * **Sample `music21` Code:**
    ```python
    from music21 import scale, note, interval

    # Generate a G natural minor scale object
    g_minor_scale = scale.MinorScale('G', 'natural')
    print([p.name for p in g_minor_scale.getPitches()])
    # Output: ['G', 'A', 'B-', 'C', 'D', 'E-', 'F']

    # Transpose a note up by a minor third
    c4 = note.Note('C4')
    minor_third = interval.Interval('m3')
    e_flat_4 = c4.transpose(minor_third)
    print(e_flat_4.nameWithOctave)
    # Output: E-4
    ```

---

## **Part Two: Diatonic Triads (Chapters 5-9)**

Here, the book introduces the core principles of connecting chords. Our tools will focus on validating these connections and generating correct harmonic structures.

### 🎵 **Feature: Voice-Leading Rules Engine**

Based on **Chapter 5: Principles of Voice Leading**, this is a crucial feature that checks a given musical passage for common voice-leading errors.

  * **Programmatic Support:** A function that takes a four-part `music21.stream.Score` and flags issues like parallel fifths and octaves.
  * **Sample `music21` Code:**
    ```python
    from music21 import stream, note, chord, voiceLeading

    # Create a progression with parallel fifths (C-G -> D-A)
    part1 = stream.Part([note.Note('G4'), note.Note('A4')])
    part2 = stream.Part([note.Note('C4'), note.Note('D4')])
    score_with_parallels = stream.Score([part1, part2])

    # music21's built-in checker
    errors = voiceLeading.checkAnalysis(score_with_parallels, 'parallel5')
    print(f"Found {len(errors)} parallel fifths.")
    # Output: Found 1 parallel fifths.
    ```

### 🎵 **Feature: Harmonic Progression Validator**

Based on **Chapter 7: Harmonic Progression**, this tool validates whether a user-defined chord progression follows the standard functional harmony chart presented in the book.

  * **Programmatic Support:** A function that takes a list of `music21.roman.RomanNumeral` objects and a key, and returns `True` if the progression is valid according to the textbook's rules.
  * **Sample `music21` Code:**
    ```python
    from music21 import roman

    # Rules adapted from the textbook's diagram
    progression_rules = {
        'I': ['ii', 'iii', 'IV', 'V', 'vi'],
        'ii': ['V', 'vii°'], 'iii': ['vi'],
        'IV': ['V', 'vii°', 'I', 'ii'], 'V': ['I', 'vi'],
        'vi': ['ii', 'IV'], 'vii°': ['I', 'iii']
    }

    def validate_progression(progression_list):
        for i in range(len(progression_list) - 1):
            current_chord = progression_list[i]
            next_chord = progression_list[i+1]
            if next_chord.figure not in progression_rules.get(current_chord.figure, []):
                print(f"Invalid progression: {current_chord.figure} -> {next_chord.figure}")
                return False
        print("Progression is valid.")
        return True

    # Test a valid progression vs. an invalid one
    valid_prog = [roman.RomanNumeral('vi'), roman.RomanNumeral('ii'), roman.RomanNumeral('V'), roman.RomanNumeral('I')]
    invalid_prog = [roman.RomanNumeral('V'), roman.RomanNumeral('IV')]
    validate_progression(valid_prog) # Output: Progression is valid.
    validate_progression(invalid_prog) # Output: Invalid progression: V -> IV
    ```

---

## **Part Three: Diatonic Seventh Chords (Chapters 13-15)**

This section details the behavior of seventh chords. Our tools will specifically check for the correct resolution of dissonances.

### 🎵 **Feature: Seventh Chord Resolution Checker**

Based on **Chapter 13: The V7 Chord**, this function checks that the dissonant notes of a seventh chord (especially the chordal 7th) resolve correctly.

  * **Programmatic Support:** A function that finds all V7 chords in a stream and verifies that the 7th resolves down by step.
  * **Sample `music21` Code:**
    ```python
    from music21 import stream, chord, interval

    # Create a correct (V7 -> I) resolution where F4 resolves down to E4
    v7_correct = chord.Chord(['G3', 'B3', 'D4', 'F4'])
    i_correct = chord.Chord(['C4', 'E4', 'G4'])

    def check_v7_resolution(c1, c2):
        # Find the 7th of the V7 chord
        chordal_seventh = None
        for p in c1.pitches:
            iv = interval.Interval(c1.root(), p)
            if iv.name == 'm7':
                chordal_seventh = p
                break
        
        if chordal_seventh:
            # Check if it resolves down by step in the next chord
            target_note = chordal_seventh.transpose('m-2')
            if any(p.name == target_note.name for p in c2.pitches):
                print(f"Correct resolution: {chordal_seventh.name} -> {target_note.name}")
            else:
                print(f"Incorrect resolution for {chordal_seventh.name}!")

    check_v7_resolution(v7_correct, i_correct)
    # Output: Correct resolution: F -> E
    ```

---

## **Part Four: Chromaticism 1 (Chapters 16-19)**

Here the book introduces chords outside the key. Our tools will focus on generating and identifying these chromatic chords based on their function.

### 🎵 **Feature: Secondary Dominant Generator**

Based on **Chapter 16: Secondary Functions 1**, this function creates secondary dominant chords (like V/V, "five of five").

  * **Programmatic Support:** A function that, given a key and a target chord, generates the correct secondary dominant.
  * **Sample `music21` Code:**
    ```python
    from music21 import roman

    # Create V7/V in C Major
    # The target is 'V' (the G major chord)
    # The secondary dominant is the V7 of G, which is D7
    secondary_dominant = roman.RomanNumeral('V7/V', 'C')
    print(f"V7/V in C Major is: {secondary_dominant.pitchedCommonName}")
    # Output: V7/V in C Major is: D Dominant 7th
    ```

### 🎵 **Feature: Common Chord Finder for Modulation**

Based on **Chapter 18: Modulations Using Diatonic Common Chords**, this tool helps plan a smooth modulation by identifying all possible pivot chords between two keys.

  * **Programmatic Support:** A function that takes two keys as input and returns a list of chords that are diatonic to both.
  * **Sample `music21` Code:**
    ```python
    from music21 import key

    def find_common_chords(key1_str, key2_str):
        k1 = key.Key(key1_str)
        k2 = key.Key(key2_str)

        # Get the diatonic triads for each key
        chords1 = {c.pitchedCommonName for c in k1.getDiatonicTriads()}
        chords2 = {c.pitchedCommonName for c in k2.getDiatonicTriads()}

        # Find the intersection
        common_chords = chords1.intersection(chords2)
        print(f"Common chords between {key1_str} and {key2_str}: {sorted(list(common_chords))}")

    find_common_chords('C', 'G')
    # Output: Common chords between C and G: ['A minor triad', 'C major triad', 'E minor triad', 'G major triad']
    ```

---

## **Part Five: Chromaticism 2 (Chapters 21-25)**

This section covers more advanced chromatic chords. Our framework will provide specific "constructor" functions for these special cases.

### 🎵 **Feature: Neapolitan and Augmented Sixth Chord Constructors**

Based on **Chapters 21 & 22**, these functions build these specific, highly chromatic pre-dominant chords according to their textbook definitions.

  * **Programmatic Support:** Functions that take a key and return a `music21.Chord` object for the Neapolitan (N6) or one of the three types of Augmented Sixth chords (It+6, Fr+6, Ger+6).
  * **Sample `music21` Code:**
    ```python
    from music21 import chord, key, pitch

    def create_neapolitan_sixth(k):
        # The Neapolitan is a major triad on the lowered supertonic
        supertonic = k.getScale('major').pitchFromDegree(2)
        root = supertonic.transpose('-a1') # Lowered by one half step
        n_chord = chord.Chord([root, root.transpose('M3'), root.transpose('P5')])
        
        # Return in first inversion (N6)
        n_chord.inversion(1)
        print(f"N6 in {k.name}: {n_chord.pitchedCommonName}")
        return n_chord

    def create_italian_augmented_sixth(k):
        # The It+6 is built on scale degree b6, with 1 and #4
        tonic = k.getScale('major').pitchFromDegree(1)
        le = tonic.transpose('m-3')  # b6
        fi = tonic.transpose('a4')   # #4
        it6 = chord.Chord([le, tonic, fi])
        print(f"It+6 in {k.name}: {it6.pitchedCommonName}")
        return it6

    create_neapolitan_sixth(key.Key('c'))
    # Output: N6 in c minor: F-A--D- Major Triad in first inversion

    create_italian_augmented_sixth(key.Key('C'))
    # Output: It+6 in C Major: A--C-F# augmented sixth chord
    ```

---

## **Mapping to Codempose Priority 3B: Harmonic Intelligence System**

### Alignment Analysis

The roadmap document provides an excellent foundation for implementing Priority 3B. Here's how the textbook-based features map to our planned architecture:

#### **Component 1: Structural Tone Analyzer**
- **Relevant Roadmap Sections:** Part One (Fundamentals)
- **Key Features to Leverage:**
  - Scale & Interval Generator → Identify diatonic context
  - Foundation for analyzing melodic motion and identifying structural vs. ornamental tones

#### **Component 2: Harmonic Fitting Engine**
- **Relevant Roadmap Sections:** Part Two (Diatonic Triads), Part Three (Seventh Chords), Part Four (Chromaticism 1)
- **Key Features to Leverage:**
  - **Harmonic Progression Validator** → Ensure generated progressions follow functional harmony rules
  - **Seventh Chord Resolution Checker** → Validate voice leading of dissonances
  - **Secondary Dominant Generator** → Enrich harmonic palette beyond diatonic chords
  - **Common Chord Finder** → Enable smooth modulations between keys

#### **Component 3: Voice Leading Generator**
- **Relevant Roadmap Sections:** Part Two (Voice-Leading Rules Engine), Part Five (Advanced Chromatic Chords)
- **Key Features to Leverage:**
  - **Voice-Leading Rules Engine** → Automatic detection/prevention of parallel fifths/octaves
  - **Neapolitan and Augmented Sixth Constructors** → Pre-dominant chord generators for dramatic harmonic motion

### Implementation Strategy

1. **Phase 1 (Foundation):** Implement Scale & Interval Generator + Harmonic Progression Validator
2. **Phase 2 (Core Intelligence):** Add Voice-Leading Rules Engine + Seventh Chord Resolution Checker
3. **Phase 3 (Enrichment):** Integrate Secondary Dominant Generator + Common Chord Finder
4. **Phase 4 (Advanced):** Add Neapolitan/Augmented Sixth constructors for chromatic harmony

### Key Insights

- **music21 Library Alignment:** The roadmap extensively uses `music21.roman.RomanNumeral`, `music21.chord`, and `music21.voiceLeading` modules—all available in our existing infrastructure
- **Rule-Based Validation:** The progression_rules dictionary pattern is directly applicable to our harmonic fitting engine
- **Modular Architecture:** Each feature is self-contained, allowing incremental implementation
- **Textbook Grounding:** Rules derived from *Tonal Harmony* provide academic rigor and pedagogical value

---

## Next Steps for Priority 3B

When ready to begin, we should:

1. **Audit Existing Code:** Check what harmony-related functionality already exists in `music_data.py`, `composition_shorthand.py`, and `transformations.py`
2. **Design Data Structures:** Define how to represent chord progressions, voice leading constraints, and harmonic analysis results
3. **Prototype Core Validator:** Start with the Harmonic Progression Validator as proof-of-concept
4. **Integrate with Parser:** Ensure the harmony assistant can consume our LilyPond/TinyNotation parsed events
5. **Create Demonstration Study:** Build `fourteenth.py` or similar to showcase harmonic intelligence in action

---

**Document created:** October 13, 2025  
**Status:** Stored for Priority 3B implementation  
**Related:** PRIORITY_3A_SUMMARY.md, PARSER_QUICK_WINS.md
