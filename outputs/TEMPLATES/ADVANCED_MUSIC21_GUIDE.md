# Codempose Function Reference & Code Structure Guide

**Purpose**: Complete function reference for Station 3 & 4, with detailed Python code structure explanation.

**For system overview**, see: `SYSTEM_OVERVIEW.md`

**Target Audience**: Users who know basic programming but need Python-specific guidance.

---

## 🎯 The Hybrid Model: Two Ways to Transform Music

Codempose supports **two distinct approaches** for transforming music:

### Approach 1: Blueprint Syntax (Station 3) - **Composer-Friendly**

**Use `transpose_part()` syntax** - works with snippet names:

```python
# In Blueprint strings (Station 3)
VOICE_STAVE_DATA = """
    transpose_part(THEME, 'P5')    # ← Snippet NAME as string
"""
```

**What happens**: Framework automatically:
1. Looks up `THEME` in SNIPPETS dictionary
2. Converts events to music21 Part
3. Calls transformation
4. Converts result back to events
5. Caches in SNIPPETS for reuse

### Approach 2: Python API (Station 4) - **Programmer Control**

**Use `transpose_events()` function** - works with event lists:

```python
# In Python code (Station 4)
def build_score_data():
    theme_events = parse_lilypond_to_data(THEME_LILY)['parts']['theme']  # Get event list
    transposed_events = transpose_events(theme_events, 7)  # ← Event LIST as variable
    return {'parts': {'Voice': transposed_events}}
```

**What you control**: Manual conversion workflow:
1. Parse LilyPond → events
2. Optionally: events → music21 Part (if using music21 API)
3. Apply transformations
4. Optionally: Part → events (convert back)
5. Return events in score_data dict

---

### Key Differences

| Feature | Blueprint (`transpose_part`) | Python API (`transpose_events`) |
|---------|----------------------------|--------------------------------|
| **Input** | Snippet NAME (string) | Event list (variable) |
| **Location** | VOICE_STAVE_DATA string | Python function code |
| **Caching** | Automatic | Manual |
| **Best For** | Quick arrangements | Complex logic |
| **Example** | `transpose_part(THEME, 'P5')` | `transpose_events(events, 7)` |

---

## Quick Navigation

- [Part 1: Station 3 Functions](#part-1-station-3-complete-function-reference) - Blueprint transformation functions
- [Station 4 Code Structure](#station-4-code-structure-explained) - **Python anatomy for basic programmers**
- [Part 2: Station 4 Functions](#part-2-station-4-complete-function-reference) - Programmatic functions
- [Part 3: Practical Recipes](#part-3-practical-recipes) - Common composition patterns
- [Part 4: Troubleshooting](#part-4-troubleshooting-guide) - Error fixes

---

## Part 1: Station 3 Complete Function Reference

### 📘 Blueprint Syntax Overview

| Syntax | Meaning | Example |
|--------|---------|---------|
| `SNIPPET_NAME` | Use a defined snippet | `THEME` |
| `A & B` | Vertical stacking (simultaneous) | `MELODY & BASS` |
| `A \| B` | Horizontal sequence | `THEME \| THEME_VARIATION` |
| `A ; B` | Section break | `INTRO & BASS ; THEME & HARMONY` |
| `A, B` | Multi-voice (same staff) | `VOICE1, VOICE2` |
| `SNIPPET * N` | Repeat N times | `THEME * 3` |
| `r` | Auto-rest (fill with rest) | `MELODY & r` |

### 📘 All Available Transformation Functions (Station 3)

**Source File**: `src/transformations.py`

These functions work on music21 Part objects internally. The Blueprint parser calls them automatically.

#### Single-Part Transformations (Return one part)

| Function | What It Does | Example | Result |
|----------|--------------|---------|--------|
| `transpose_part(SNIPPET, 'P5')` | Transpose up/down by interval | `transpose_part(THEME, 'P5')` | Theme up perfect 5th |
| `transpose_part(SNIPPET, 'm3')` | Transpose by minor 3rd | `transpose_part(THEME, 'm3')` | Theme up minor 3rd |
| `transpose_part(SNIPPET, '-M2')` | Transpose down | `transpose_part(THEME, '-M2')` | Theme down major 2nd |
| `invert_part(SNIPPET, 'c4')` | Melodic inversion around axis | `invert_part(THEME, 'c4')` | Theme inverted around C4 |
| `retrograde_part(SNIPPET)` | Reverse order of notes | `retrograde_part(THEME)` | Theme played backwards |
| `augment_part(SNIPPET)` | Double note durations | `augment_part(THEME)` | Theme at half speed |
| `augment_part(SNIPPET, 3.0)` | Triple note durations | `augment_part(THEME, 3.0)` | Theme at 1/3 speed |
| `diminish_part(SNIPPET)` | Half note durations | `diminish_part(THEME)` | Theme at double speed |
| `diminish_part(SNIPPET, 4.0)` | Quarter note durations | `diminish_part(THEME, 4.0)` | Theme at 4x speed |
| `chordify_part(SNIPPET, 'major')` | Add harmony (chord type) | `chordify_part(MELODY, 'major')` | Chordified melody |

**Interval Notation Reference**:
- `P1` = Perfect Unison, `m2` = Minor 2nd, `M2` = Major 2nd
- `m3` = Minor 3rd, `M3` = Major 3rd, `P4` = Perfect 4th
- `A4` = Augmented 4th, `d5` = Diminished 5th, `P5` = Perfect 5th
- `m6` = Minor 6th, `M6` = Major 6th, `m7` = Minor 7th, `M7` = Major 7th
- `P8` = Octave
- Add `-` prefix for downward: `-P5`, `-M3`, etc.

#### Multi-Part Transformations (Return Score with multiple parts)

| Function | What It Does | Parts Returned | Example |
|----------|--------------|----------------|---------|
| `harmonize_part(SNIPPET, 'I-IV-V-I', 'C')` | Add bass line following progression | `:melody`, `:harmony` | `harmonize_part(THEME, 'I-IV-V-I', 'C'):melody` |

**CRITICAL**: Multi-part functions require **suffix notation**:

```python
# WRONG (will error):
VOICE_STAVE_DATA = "harmonize_part(THEME, 'I-IV-V-I', 'C')"

# CORRECT (specify which part):
VOICE_STAVE_DATA = """
    harmonize_part(THEME, 'I-IV-V-I', 'C'):melody  &
    harmonize_part(THEME, 'I-IV-V-I', 'C'):harmony
"""

# How it works:
# 1. First call runs the function, caches BOTH parts
# 2. :melody suffix extracts melody part
# 3. Second call is FREE (cached), :harmony extracts harmony part
```

### 📘 Blueprint Complete Examples

#### Example 1: Simple Sequence
```python
VOICE_STAVE_DEF = "Melody"

VOICE_STAVE_DATA = """
    THEME | transpose_part(THEME, 'P5') | retrograde_part(THEME)
"""
# Result: Theme, then theme up 5th, then theme backwards
```

#### Example 2: Two Staves (Piano)
```python
VOICE_STAVE_DEF = "RH & LH"

VOICE_STAVE_DATA = """
    MELODY & BASS;
    transpose_part(MELODY, 'P8') & transpose_part(BASS, 'P8')
"""
# Result: Two sections, second section up one octave
```

#### Example 3: Multi-Voice (SATB Choir)
```python
VOICE_STAVE_DEF = "(Soprano, Alto) & (Tenor, Bass)"

VOICE_STAVE_DATA = """
    SOPRANO, ALTO  &  TENOR, BASS
"""
# Result: Two staves, each with two voices
```

#### Example 4: Canon (Manual Delay)
```python
VOICE_STAVE_DEF = "Leader & Follower"

# Define a rest snippet in Station 1:
REST_4_LILY = r"{ R1 }"  # Whole rest

VOICE_STAVE_DATA = """
    THEME  &  REST_4 | transpose_part(THEME, 'P8')
"""
# Result: Leader starts immediately, Follower waits 4 beats then plays octave higher
```

#### Example 5: Harmonization
```python
VOICE_STAVE_DEF = "Melody & Harmony"

VOICE_STAVE_DATA = """
    harmonize_part(THEME, 'I-IV-V-I', 'C'):melody  &
    harmonize_part(THEME, 'I-IV-V-I', 'C'):harmony
"""
# Result: Melody + auto-generated bass line
```

#### Example 6: Complex Sections
```python
VOICE_STAVE_DEF = "Voice1 & Voice2"

VOICE_STAVE_DATA = """
    # Section 1: Exposition
    THEME & BASS;
    
    # Section 2: Development (inverted)
    invert_part(THEME, 'g4') & transpose_part(BASS, '-P5');
    
    # Section 3: Recapitulation (augmented)
    augment_part(THEME, 2.0) & augment_part(BASS, 2.0)
"""
# Result: Three sections with different transformations
```

---

## Station 4 Code Structure Explained

**This section is for programmers with basic experience who need Python-specific guidance.**

### The Basics: What is Station 4?

Station 4 lets you write **custom Python code** instead of using Blueprint strings. You implement a function called `build_score_data()` that returns your composition as a Python dictionary.

**Key concept**: Instead of writing `"THEME | transpose_part(THEME, 'P5')"`, you write Python loops, conditionals, and function calls.

---

### Activating Station 4

Add this line BEFORE your function definition:

```python
PROMOTE_TO_PROGRAMMATIC = True  # This tells the framework to use Station 4
```

Without this line, the framework will use Station 3 (Blueprint strings).

---

### The Required Function: `build_score_data()`

This is the function you MUST implement. The framework calls it automatically.

**Function Signature**:
```python
def build_score_data() -> Dict:
    """Your description here."""
    # Your code here
    return {'parts': { ... }}
```

**Breakdown**:
- `def` = Python keyword for defining a function
- `build_score_data` = The exact name required (don't change this!)
- `()` = No parameters (you don't pass anything in)
- `-> Dict` = Type hint (optional but helpful) - tells you this returns a dictionary
- `:` = Start of function body
- `"""docstring"""` = Optional description
- `return` = Python keyword to send back the result

---

### The Return Structure: What You Must Return

Your function MUST return a dictionary with this exact structure:

```python
{
    'parts': {
        'VoiceName1': [list, of, events],
        'VoiceName2': [list, of, events],
        # ... more voices
    }
}
```

**Anatomy**:
```python
return {                    # ← Start of dictionary (use curly braces { })
    'parts': {              # ← Key named 'parts' (required, don't change)
        'Melody': events1,  # ← Key = voice name (you choose), value = list of events
        'Bass': events2,    # ← Another voice
    }
}
```

**Critical points**:
- Use `{ }` for dictionaries, `[ ]` for lists
- The key `'parts'` is REQUIRED (framework expects it)
- Voice names (like `'Melody'`, `'Bass'`) are YOUR choice
- Each value is a **list of event dictionaries** (more on this below)

---

### Data Types You Need to Know

#### 1. Lists (Arrays)

Lists hold multiple items in order:

```python
# Creating a list:
my_list = [1, 2, 3, 4]
another_list = ['a', 'b', 'c']

# Adding items:
my_list.append(5)           # Now: [1, 2, 3, 4, 5]
my_list += [6, 7]           # Now: [1, 2, 3, 4, 5, 6, 7]

# Concatenating lists:
combined = my_list + another_list  # [1, 2, 3, 4, 5, 6, 7, 'a', 'b', 'c']
```

**In Codempose**:
```python
theme = [event1, event2, event3]        # A list of events
transposed = [event4, event5, event6]   # Another list
sequence = theme + transposed           # Combine them
```

#### 2. Dictionaries (Objects)

Dictionaries store key-value pairs:

```python
# Creating a dictionary:
person = {
    'name': 'John',      # Key: 'name', Value: 'John'
    'age': 30,           # Key: 'age', Value: 30
    'city': 'NYC'        # Key: 'city', Value: 'NYC'
}

# Accessing values:
print(person['name'])    # Output: John
print(person['age'])     # Output: 30

# Nested dictionaries:
data = {
    'parts': {           # Outer key: 'parts'
        'Voice1': [...],  # Inner key: 'Voice1'
        'Voice2': [...]   # Inner key: 'Voice2'
    }
}
```

**In Codempose**:
```python
# Event dictionaries (you usually don't create these manually):
event = {
    'type': 'note',
    'pitch': 'c4',
    'duration': 1.0,
    'lilypond_code': 'c4'
}

# Return structure:
return {
    'parts': {
        'Soprano': soprano_events,  # List of event dicts
        'Alto': alto_events          # List of event dicts
    }
}
```

#### 3. Strings

Text in quotes:

```python
single_quotes = 'Hello'
double_quotes = "World"
multi_line = """
    This spans
    multiple lines
"""

# String concatenation:
full = single_quotes + " " + double_quotes  # "Hello World"
```

**In Codempose**:
```python
# Pitch names:
pitch = 'c4'         # Middle C
axis = 'g4'          # G above middle C

# Function arguments:
transpose_events(theme, 7)            # 7 is a number
invert_events(theme, 'c4')            # 'c4' is a string
```

---

### Getting Data from Station 1: `parse_lilypond_to_data()`

This function converts your LilyPond snippets into event lists.

**Usage**:
```python
# You defined this in Station 1:
THEME_LILY = r"""
\relative c' { c4 d e f }
"""

# In Station 4, convert it:
result = parse_lilypond_to_data(THEME_LILY)

# 'result' is a dictionary:
# {
#     'parts': {
#         'theme': [event1, event2, event3, event4]
#     }
# }

# Extract the event list:
theme_events = result['parts']['theme']
# Now 'theme_events' is a list you can work with
```

**Breakdown**:
```python
result = parse_lilypond_to_data(THEME_LILY)
#        ^^^^^^^^^^^^^^^^^^^^^ Function call
#                               ^^^^^^^^^^^ Your LilyPond string

# Result structure:
{
    'parts': {              # ← Always has this key
        'theme': [...]      # ← Part name (lowercase version of variable name)
    }
}

# Extract the list:
theme = result['parts']['theme']
#       ^^^^^^ Dictionary access
#              ^^^^^^^ Nested dictionary access
#                      ^^^^^^^ Key is lowercase of THEME_LILY → 'theme'
```

---

### Imports: Bringing in Functions

To use functions from other files, you must **import** them:

```python
# Format:
from module_name import function_name

# Examples:
from src.composition_shorthand import transpose_events
from src.composition_shorthand import transpose_events, invert_events  # Multiple
from src.music_data import data_to_part, part_to_data
```

**Common imports for Station 4**:
```python
def build_score_data():
    # Event-level transformations:
    from src.composition_shorthand import transpose_events, invert_events, retrograde_events
    
    # Conversion functions:
    from src.music_data import data_to_part, part_to_data
    
    # Analysis tools:
    from src.lib.TONAL_HARMONY_TEMPLATES import check_voice_leading_errors
    
    # Python standard library:
    import random  # For random.choice(), random.randint(), etc.
    
    # Your code here...
```

**Why inside the function?**  
You CAN put imports at the top of the file, but putting them inside `build_score_data()` keeps Station 4 code self-contained.

---

### Complete Annotated Example

```python
# ============================================
# ACTIVATE STATION 4
# ============================================
PROMOTE_TO_PROGRAMMATIC = True


# ============================================
# IMPLEMENT THE REQUIRED FUNCTION
# ============================================
def build_score_data():
    """
    Build score programmatically.
    
    Returns:
        dict: {'parts': {'VoiceName': [events]}}
    """
    
    # --- STEP 1: Import functions you need ---
    from src.composition_shorthand import transpose_events, retrograde_events
    #    ^^^ Module path             ^^^ Functions to import
    
    
    # --- STEP 2: Get parsed snippets from Station 1 ---
    theme_data = parse_lilypond_to_data(THEME_LILY)
    #            ^^^^^^^^^^^^^^^^^^^^^^ Function (already available)
    #                                    ^^^^^^^^^^ Your LilyPond string
    
    # 'theme_data' is now:
    # {'parts': {'theme': [event1, event2, ...]}}
    
    
    # --- STEP 3: Extract the event list ---
    theme = theme_data['parts']['theme']
    #       ^^^^^^^^^^ Dictionary
    #                  ^^^^^^^^^ Key: 'parts'
    #                            ^^^^^^^^ Key: 'theme' (auto-generated)
    
    # 'theme' is now: [event1, event2, event3, ...]
    
    
    # --- STEP 4: Transform using Python logic ---
    sequence = []  # Empty list to build up
    
    for semitones in [0, 2, 4, 5, 7]:  # Loop 5 times
        #            ^^^^^^^^^^^^^^^^^^ List of numbers
        
        transposed = transpose_events(theme, semitones)
        #            ^^^^^^^^^^^^^^^^ Function call
        #                             ^^^^^ First argument
        #                                    ^^^^^^^^^^ Second argument
        
        sequence += transposed  # Add to list (same as: sequence = sequence + transposed)
        #        ^^ Shorthand for concatenation
    
    # After loop, 'sequence' contains 5 copies of theme at different pitches
    
    
    # --- STEP 5: Return the required structure ---
    return {
        #  ^ Start dictionary
        'parts': {
            #    ^ Required key
            'Melody': sequence
            #         ^^^^^^^^ Your event list
        }
    }
```

**Line-by-line explanation**:

| Line | What It Does |
|------|--------------|
| `PROMOTE_TO_PROGRAMMATIC = True` | Activates Station 4 mode |
| `def build_score_data():` | Defines the required function |
| `from src... import ...` | Brings in functions from other files |
| `theme_data = parse_lilypond_to_data(...)` | Converts LilyPond to events |
| `theme = theme_data['parts']['theme']` | Extracts the event list from nested dict |
| `sequence = []` | Creates empty list |
| `for semitones in [...]` | Loops over each number in list |
| `transposed = transpose_events(...)` | Calls transformation function |
| `sequence += transposed` | Adds result to list |
| `return { 'parts': {...} }` | Returns required structure |

---

### Common Python Patterns in Station 4

#### Pattern 1: Building Lists with Loops

```python
# Initialize empty list:
result = []

# Add items one by one:
for i in range(5):  # Loop 5 times (i = 0, 1, 2, 3, 4)
    result.append(i)

# Result: [0, 1, 2, 3, 4]
```

**Music example**:
```python
sequence = []
for semitones in [0, 2, 4]:
    transposed = transpose_events(theme, semitones)
    sequence += transposed  # or: sequence.append(transposed) - different!

# Note: 
# sequence += transposed     → Adds each EVENT from transposed to sequence
# sequence.append(transposed) → Adds the entire LIST as one item
```

#### Pattern 2: Conditionals (if/else)

```python
if condition:
    # Do this
else:
    # Do that

# Example:
mode = 'major'

if mode == 'major':
    result = transpose_events(theme, 7)  # Up P5
else:
    result = invert_events(theme, 'c4')  # Invert
```

#### Pattern 3: List Comprehensions (Advanced but Common)

```python
# Verbose way:
result = []
for i in range(5):
    result.append(i * 2)

# List comprehension (one line):
result = [i * 2 for i in range(5)]

# Both produce: [0, 2, 4, 6, 8]
```

**Music example**:
```python
# Create sequence at multiple transpositions:
sequence = [transpose_events(theme, s) for s in [0, 2, 4, 5, 7]]

# This creates a LIST OF LISTS:
# [[events_at_0], [events_at_2], [events_at_4], ...]

# To flatten:
sequence_flat = []
for chunk in sequence:
    sequence_flat += chunk

# Or using sum():
sequence_flat = sum(sequence, [])  # Concatenates all inner lists
```

#### Pattern 4: Dictionary Access

```python
data = {
    'parts': {
        'melody': [1, 2, 3],
        'bass': [4, 5, 6]
    }
}

# Access nested values:
melody = data['parts']['melody']  # [1, 2, 3]
bass = data['parts']['bass']      # [4, 5, 6]

# Access with variable:
voice_name = 'melody'
notes = data['parts'][voice_name]  # [1, 2, 3]
```

---

### Debugging Tips for Basic Programmers

#### Use `print()` to See What's Happening

```python
def build_score_data():
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    print("Theme events:", len(theme))  # How many events?
    print("First event:", theme[0])     # What does an event look like?
    
    transposed = transpose_events(theme, 7)
    print("Transposed events:", len(transposed))
    
    return {'parts': {'Melody': transposed}}
```

#### Check Types

```python
# Is it a list or dict?
print(type(theme))          # <class 'list'>
print(type(result))         # <class 'dict'>

# How many items?
print(len(theme))           # Number of events
print(len(result['parts'])) # Number of voices
```

#### Common Mistakes

**Mistake 1**: Returning the wrong structure
```python
# WRONG:
return theme  # Just a list

# CORRECT:
return {'parts': {'Voice1': theme}}
```

**Mistake 2**: Forgetting to extract from nested dict
```python
# WRONG:
theme = parse_lilypond_to_data(THEME_LILY)
transposed = transpose_events(theme, 7)  # Error! 'theme' is a dict, not a list

# CORRECT:
theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']  # Extract list
transposed = transpose_events(theme, 7)  # Works!
```

**Mistake 3**: Using `append()` instead of `+=` for lists
```python
sequence = []

# WRONG (creates nested lists):
sequence.append(transposed)  # sequence = [[event1, event2, ...]]

# CORRECT (flattens):
sequence += transposed        # sequence = [event1, event2, ...]
```

---

## Part 2: Station 4 Complete Function Reference

### When to Use Station 4

Use Station 4 (programmatic) when you need:
- ✅ **Conditional logic**: `if key == 'minor': ...`
- ✅ **Loops**: `for i in range(10): ...`
- ✅ **Random/algorithmic**: `random.choice(notes)`
- ✅ **Analysis before generation**: Check if melody has certain pattern
- ✅ **Complex transformations**: Chain multiple operations with logic
- ✅ **Validation**: Use `check_voice_leading_errors()` before rendering

### Station 4 Code Structure

```python
# 1. Toggle to Station 4
PROMOTE_TO_PROGRAMMATIC = True

# 2. Implement this function
def build_score_data():
    """
    Your custom composition logic.
    
    Returns:
        dict: {'parts': {'VoiceName': [event_list, ...]}}
    """
    # Step 1: Get snippets from Station 1
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    # Step 2: Your logic here
    # ...
    
    # Step 3: Return the structure
    return {
        'parts': {
            'Voice1': event_list_1,
            'Voice2': event_list_2,
        }
    }
```

### 📘 Station 4 Function Categories

#### Category 1: Event-Level Functions (Work on event dicts)

**Source**: `src/composition_shorthand.py`

| Function | Input Type | Output Type | Purpose |
|----------|------------|-------------|---------|
| `transpose_events(events, semitones)` | `List[Dict]` | `List[Dict]` | Transpose by semitones |
| `invert_events(events, axis_pitch)` | `List[Dict]` | `List[Dict]` | Melodic inversion |
| `retrograde_events(events)` | `List[Dict]` | `List[Dict]` | Reverse order |
| `filter_events(events, exclude_types)` | `List[Dict]` | `List[Dict]` | Remove unwanted events |

**Example**:
```python
def build_score_data():
    # Get events from Station 1
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    # Transform at event level (fast, simple)
    transposed = transpose_events(theme, 7)  # Up P5 (7 semitones)
    inverted = invert_events(theme, 'c4')
    backwards = retrograde_events(theme)
    
    # Combine
    sequence = theme + transposed + inverted + backwards
    
    return {'parts': {'Melody': sequence}}
```

#### Category 2: Conversion Functions (Event ↔ music21)

**Source**: `src/music_data.py`

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `data_to_part(events)` | `List[Dict]` | `music21.stream.Part` | Convert to music21 |
| `part_to_data(part)` | `music21.stream.Part` | `List[Dict]` | Convert back to events |

**⚠️ CRITICAL: music21 Parts Access**

When working with `music21.stream.Score` objects:
- **CORRECT**: `score.parts[0]` (access by index)
- **WRONG**: `score.parts['melody']` (will crash - not a dict!)

Example:
```python
score = harmonize_part(melody, 'I-IV-V-I', 'C')  # Returns Score
first_part = score.parts[0]   # ✅ Correct
second_part = score.parts[1]  # ✅ Correct
wrong = score.parts['bass']   # ❌ TypeError!
```

**Example**:
```python
def build_score_data():
    from src.music_data import data_to_part, part_to_data
    from music21 import interval
    
    # Get events
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    # Convert to music21 to use music21 API
    part = data_to_part(theme)
    
    # Use music21 functions
    part.transpose(interval.Interval('P5'), inPlace=True)
    
    # Convert back to events
    result = part_to_data(part)
    
    return {'parts': {'Voice1': result}}
```

#### Category 3: Analysis & Validation Functions

**Source**: `src/lib/TONAL_HARMONY_TEMPLATES.py`

| Function | Purpose | Returns |
|----------|---------|---------|
| `check_voice_leading_errors(score)` | Find parallel 5ths/8ves | Dict of errors |
| `validate_harmonic_progression(prog_str, key)` | Check if progression is valid | Dict with validity |
| `create_neapolitan_chord(key_str, inversion)` | Create N6 chord | `music21.chord.Chord` |
| `create_german_augmented_sixth(key_str)` | Create Ger+6 chord | `music21.chord.Chord` |
| `create_italian_augmented_sixth(key_str)` | Create It+6 chord | `music21.chord.Chord` |
| `create_french_augmented_sixth(key_str)` | Create Fr+6 chord | `music21.chord.Chord` |

**Example**:
```python
def build_score_data():
    from src.lib.TONAL_HARMONY_TEMPLATES import check_voice_leading_errors
    from src.music_data import data_to_part
    from music21 import stream
    
    # Build SATB
    soprano = parse_lilypond_to_data(SOPRANO_LILY)['parts']['soprano']
    alto = parse_lilypond_to_data(ALTO_LILY)['parts']['alto']
    tenor = parse_lilypond_to_data(TENOR_LILY)['parts']['tenor']
    bass = parse_lilypond_to_data(BASS_LILY)['parts']['bass']
    
    # Assemble for analysis
    score = stream.Score()
    score.append(data_to_part(soprano))
    score.append(data_to_part(alto))
    score.append(data_to_part(tenor))
    score.append(data_to_part(bass))
    
    # Validate
    errors = check_voice_leading_errors(score)
    
    if errors['parallel_fifths']:
        print("⚠️ WARNING: Parallel fifths detected!")
        for err in errors['parallel_fifths']:
            print(f"  Measure {err['measure']}, {err['voices']}")
    
    # Only return if valid
    if not any(errors.values()):
        return {
            'parts': {
                'Soprano': soprano,
                'Alto': alto,
                'Tenor': tenor,
                'Bass': bass
            }
        }
    else:
        raise ValueError("Fix voice leading errors before rendering!")
```

### 📘 Station 4 Complete Examples

#### Example 1: Simple Algorithmic Sequence

```python
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    """Generate ascending transposition sequence."""
    from src.composition_shorthand import transpose_events
    
    # Get base theme
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    # Build sequence: C, D, E, F, G (0, 2, 4, 5, 7 semitones up)
    sequence = []
    for semitones in [0, 2, 4, 5, 7]:
        sequence += transpose_events(theme, semitones)
    
    return {'parts': {'Melody': sequence}}
```

#### Example 2: Conditional Transformation

```python
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    """Apply different transformations based on mode."""
    from src.composition_shorthand import transpose_events, invert_events
    
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    # User setting
    mode = 'major'  # or 'minor'
    
    if mode == 'major':
        # Major mode: transpose up
        result = transpose_events(theme, 7)  # Up P5
    else:
        # Minor mode: invert
        result = invert_events(theme, 'c4')
    
    return {'parts': {'Voice1': result}}
```

#### Example 3: Random/Algorithmic Composition

```python
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    """Generate random melodic cells."""
    import random
    
    # Define pitch pool
    pitches = ['c4', 'd4', 'e4', 'f4', 'g4', 'a4', 'b4', 'c5']
    durations = [0.25, 0.5, 1.0]
    
    # Generate 32 random notes
    events = []
    for _ in range(32):
        events.append({
            'type': 'note',
            'pitch': random.choice(pitches),
            'duration': random.choice(durations),
            'lilypond_code': ''
        })
    
    return {'parts': {'AlgoMelody': events}}
```

#### Example 4: Data Conversion Workflow

```python
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    """Use music21 API via conversion."""
    from src.music_data import data_to_part, part_to_data
    from music21 import interval
    
    # Get theme
    theme_events = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    # Convert to music21 Part object
    theme_part = data_to_part(theme_events)
    
    # Use music21 API (modifies object in place)
    theme_part.transpose(interval.Interval('P5'), inPlace=True)
    
    # Convert back to event list
    result_events = part_to_data(theme_part)
    
    return {'parts': {'Voice1': result_events}}
```

#### Example 5: Voice Leading Validation

```python
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    """Validate SATB before rendering."""
    from src.lib.TONAL_HARMONY_TEMPLATES import check_voice_leading_errors
    from src.music_data import data_to_part
    from music21 import stream
    
    # Parse all voices
    soprano = parse_lilypond_to_data(SOPRANO_LILY)['parts']['soprano']
    alto = parse_lilypond_to_data(ALTO_LILY)['parts']['alto']
    tenor = parse_lilypond_to_data(TENOR_LILY)['parts']['tenor']
    bass = parse_lilypond_to_data(BASS_LILY)['parts']['bass']
    
    # Assemble score for analysis
    score = stream.Score()
    score.append(data_to_part(soprano))
    score.append(data_to_part(alto))
    score.append(data_to_part(tenor))
    score.append(data_to_part(bass))
    
    # Check errors
    errors = check_voice_leading_errors(score)
    
    # Report findings
    if errors['parallel_fifths']:
        print("⚠️  PARALLEL FIFTHS:")
        for err in errors['parallel_fifths']:
            print(f"    Measure {err['measure']}: {err['voices']}")
    
    if errors['parallel_octaves']:
        print("⚠️  PARALLEL OCTAVES:")
        for err in errors['parallel_octaves']:
            print(f"    Measure {err['measure']}: {err['voices']}")
    
    # Only render if valid
    if any(errors.values()):
        raise ValueError("Fix voice leading before rendering!")
    
    return {
        'parts': {
            'Soprano': soprano,
            'Alto': alto,
            'Tenor': tenor,
            'Bass': bass
        }
    }
```

#### Example 6: Complex Multi-Section Form

```python
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    """Build Sonata form: Exposition → Development → Recapitulation."""
    from src.composition_shorthand import transpose_events, invert_events, retrograde_events
    
    # Parse themes
    theme_1 = parse_lilypond_to_data(THEME_1_LILY)['parts']['theme1']
    theme_2 = parse_lilypond_to_data(THEME_2_LILY)['parts']['theme2']
    
    # === EXPOSITION ===
    exposition = theme_1 + transpose_events(theme_2, 7)  # Theme 2 in dominant
    
    # === DEVELOPMENT ===
    # Fragment themes, invert, retrograde
    theme_1_fragment = theme_1[:len(theme_1)//2]
    
    development = (
        invert_events(theme_1_fragment, 'g4') +
        retrograde_events(theme_2) +
        transpose_events(theme_1_fragment, -5)  # Down P4
    )
    
    # === RECAPITULATION ===
    recapitulation = theme_1 + theme_2  # Both in tonic
    
    # Combine all sections
    full_piece = exposition + development + recapitulation
    
    return {'parts': {'Piano': full_piece}}
```

#### Example 7: Chromatic Voice Exchange

```python
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    """Create chromatic voice exchange between two parts."""
    from src.composition_shorthand import transpose_events
    
    voice1_base = parse_lilypond_to_data(VOICE1_LILY)['parts']['voice1']
    voice2_base = parse_lilypond_to_data(VOICE2_LILY)['parts']['voice2']
    
    # Build 12-tone sequence (chromatic transpositions)
    voice1_sequence = []
    voice2_sequence = []
    
    for semitones in range(12):
        voice1_sequence += transpose_events(voice1_base, semitones)
        voice2_sequence += transpose_events(voice2_base, -semitones)  # Contrary motion
    
    return {
        'parts': {
            'Voice1': voice1_sequence,
            'Voice2': voice2_sequence
        }
    }
```

---

## Part 3: Practical Recipes

### Recipe 1: Baroque Sequence (Rosalia)

**Goal**: Transpose theme up by step, descending

```python
# Station 3 (Blueprint)
VOICE_STAVE_DATA = """
    THEME | 
    transpose_part(THEME, 'M2') | 
    transpose_part(THEME, 'M3') | 
    transpose_part(THEME, 'P4')
"""

# Station 4 (Programmatic)
def build_score_data():
    from src.composition_shorthand import transpose_events
    
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    sequence = []
    for semitones in [0, 2, 4, 5]:  # C, D, E, F
        sequence += transpose_events(theme, semitones)
    
    return {'parts': {'Melody': sequence}}
```

### Recipe 2: Canon at the Octave

**Goal**: Leader + follower delayed 4 beats, octave higher

```python
# Station 1: Define rest
REST_WHOLE = r"{ R1 }"

# Station 3 (Blueprint)
VOICE_STAVE_DEF = "Leader & Follower"
VOICE_STAVE_DATA = """
    THEME  &  REST_WHOLE | transpose_part(THEME, 'P8')
"""

# Station 4 (Programmatic)
def build_score_data():
    from src.composition_shorthand import transpose_events
    
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    # Create 4-beat rest manually (1 whole note rest)
    rest = [{'type': 'rest', 'ql': 4.0, 'step': 'r', 'octave': 0, 'alter': 0}]
    
    leader = theme
    follower = rest + transpose_events(theme, 12)  # 12 semitones = octave
    
    return {
        'parts': {
            'Leader': leader,
            'Follower': follower
        }
    }
```

### Recipe 3: Retrograde Inversion (12-Tone Technique)

**Goal**: Original → Retrograde → Inversion → Retrograde Inversion

```python
# Station 3 (Blueprint)
VOICE_STAVE_DATA = """
    TONE_ROW | 
    retrograde_part(TONE_ROW) | 
    invert_part(TONE_ROW, 'c4') | 
    invert_part(retrograde_part(TONE_ROW), 'c4')
"""

# Station 4 (Programmatic)
def build_score_data():
    from src.composition_shorthand import invert_events, retrograde_events
    
    row = parse_lilypond_to_data(TONE_ROW_LILY)['parts']['row']
    
    original = row
    retrograde = retrograde_events(row)
    inversion = invert_events(row, 'c4')
    retrograde_inversion = retrograde_events(invert_events(row, 'c4'))
    
    sequence = original + retrograde + inversion + retrograde_inversion
    
    return {'parts': {'TwelveTone': sequence}}
```

### Recipe 4: Auto-Harmonization (CORRECTED)

**Goal**: Generate bass line following harmonic progression

**⚠️ CRITICAL**: `harmonize_part()` returns a `Score` object, not a dict. You MUST access parts by index.

```python
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    """Generate harmonized melody + bass."""
    from src.transformations import harmonize_part
    from src.music_data import data_to_part, part_to_data
    
    # 1. Prepare input (melody as music21 Part)
    melody_events = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    melody_part = data_to_part(melody_events)
    
    # 2. Generate harmony (returns Score with 2 parts)
    harmonized_score = harmonize_part(melody_part, 'I-IV-V-I', 'C')
    
    # 3. Extract parts using INDEX (NOT string key!)
    # WRONG: harmonized_score.parts['melody']  ❌ Will crash!
    # RIGHT: harmonized_score.parts[0]         ✅ Works!
    
    melody_part_obj = harmonized_score.parts[0]  # First part = melody
    harmony_part_obj = harmonized_score.parts[1] # Second part = bass
    
    # 4. Convert back to event lists
    melody_result = part_to_data(melody_part_obj)
    harmony_result = part_to_data(harmony_part_obj)
    
    return {
        'parts': {
            'Melody': melody_result,
            'Bass': harmony_result
        }
    }
```

**Key Points**:
- `harmonize_part()` returns a `music21.stream.Score` (not dict)
- Access parts by **index**: `.parts[0]`, `.parts[1]`
- Do NOT use: `.parts['melody']` (will crash with `TypeError`)

### Recipe 5: Validate Harmony Before Rendering

**Goal**: Check SATB for parallel 5ths/8ves, abort if found

```python
# Station 4 ONLY
PROMOTE_TO_PROGRAMMATIC = True

def build_score_data():
    from src.lib.TONAL_HARMONY_TEMPLATES import check_voice_leading_errors
    from src.music_data import data_to_part
    from music21 import stream
    
    # Parse SATB
    s = parse_lilypond_to_data(SOPRANO_LILY)['parts']['soprano']
    a = parse_lilypond_to_data(ALTO_LILY)['parts']['alto']
    t = parse_lilypond_to_data(TENOR_LILY)['parts']['tenor']
    b = parse_lilypond_to_data(BASS_LILY)['parts']['bass']
    
    # Build score
    score = stream.Score()
    for part_events in [s, a, t, b]:
        score.append(data_to_part(part_events))
    
    # Validate
    errors = check_voice_leading_errors(score)
    
    # Report + abort if errors
    has_errors = False
    if errors['parallel_fifths']:
        print("❌ PARALLEL FIFTHS DETECTED")
        has_errors = True
    if errors['parallel_octaves']:
        print("❌ PARALLEL OCTAVES DETECTED")
        has_errors = True
    
    if has_errors:
        raise ValueError("Voice leading errors! Fix before rendering.")
    
    print("✅ Voice leading valid!")
    return {'parts': {'Soprano': s, 'Alto': a, 'Tenor': t, 'Bass': b}}
```

---

## Part 4: Troubleshooting Guide

### Error: `ModuleNotFoundError: No module named 'src.transformations'`

**Cause**: Python can't find the module.

**Fix**:
```python
# Check current directory
import os
print(os.getcwd())

# Should be: /workspaces/Codempose
# If not, add this at top of generate_study.py:
import sys
sys.path.insert(0, '/workspaces/Codempose')
```

### Error: `KeyError: 'melody'` when using `harmonize_part`

**Cause**: Missing suffix on multi-part function in Blueprint.

**Wrong**:
```python
VOICE_STAVE_DATA = "harmonize_part(THEME, 'I-IV-V-I', 'C')"
```

**Fix**:
```python
VOICE_STAVE_DATA = """
    harmonize_part(THEME, 'I-IV-V-I', 'C'):melody  &
    harmonize_part(THEME, 'I-IV-V-I', 'C'):harmony
"""
```

### Error: `TypeError: 'StreamIterator' object is not subscriptable`

**Cause**: Trying to access `music21` parts with string key in Station 4.

**Wrong**:
```python
harmonized = harmonize_part(melody, 'I-IV-V-I', 'C')
melody_part = harmonized.parts['melody']  # ❌ CRASH!
```

**Fix**:
```python
harmonized = harmonize_part(melody, 'I-IV-V-I', 'C')
melody_part = harmonized.parts[0]  # ✅ Use index
harmony_part = harmonized.parts[1]
```

**Explanation**: In `music21`, `.parts` returns a `StreamIterator`, not a dictionary. You MUST access parts by numeric index (0, 1, 2, ...), not by string keys.

### Error: `ValueError: invalid interval string 'P9'`

**Cause**: Invalid interval notation.

**Valid intervals**: P1, m2, M2, m3, M3, P4, A4, d5, P5, m6, M6, m7, M7, P8

**For larger intervals**: Use compound or Station 4:
```python
# Wrong: transpose_part(THEME, 'P9')
# Right (Station 4): transpose_events(theme, 14)  # 14 semitones = major 9th
```

### Error: `TypeError: data_to_part() got unexpected keyword argument 'part_name'`

**Cause**: `data_to_part()` only takes events list.

**Wrong**:
```python
part = data_to_part(events, part_name='Voice1')
```

**Fix**:
```python
part = data_to_part(events)  # No part_name argument
part.id = 'Voice1'  # Set separately if needed
```

### Error: Blueprint parsing fails silently

**Cause**: Syntax error in VOICE_STAVE_DATA.

**Debug**:
```python
# Add this before rendering:
print("Blueprint string:")
print(VOICE_STAVE_DATA)

# Check for:
# - Missing quotes: transpose_part(THEME, P5) ❌ → transpose_part(THEME, 'P5') ✅
# - Wrong delimiters: THEME + BASS ❌ → THEME & BASS ✅
# - Typos: tranpose_part ❌ → transpose_part ✅
# - Wrong function: transpose_events ❌ → transpose_part ✅ (Station 3 uses _part suffix)
```

### Error: `AttributeError: 'Score' object has no attribute 'notes'`

**Cause**: In Station 4, tried to access notes directly on a Score object.

**Wrong**:
```python
score = harmonize_part(...)
for note in score.notes:  # ❌ Score doesn't have .notes!
    ...
```

**Fix**:
```python
score = harmonize_part(...)
for part in score.parts:  # Access parts first
    for note in part.flatten().notes:  # Then get notes from each part
        ...
```

### Performance: Blueprint runs too slow

**Cause**: Repeated function calls not cached.

**Check**:
```python
# This is FAST (caching works):
VOICE_STAVE_DATA = """
    harmonize_part(THEME, 'I-IV-V-I', 'C'):melody  &
    harmonize_part(THEME, 'I-IV-V-I', 'C'):harmony
"""
# Second call uses cached result ✅

# This is SLOW (no caching):
VOICE_STAVE_DATA = """
    transpose_part(THEME, 'P5') | transpose_part(THEME, 'P5')
"""
# Each call re-runs function ❌

# Fix: Use Station 4 for loops:
def build_score_data():
    from src.composition_shorthand import transpose_events
    theme = parse_lilypond_to_data(THEME_LILY)['parts']['theme']
    
    transposed = transpose_events(theme, 7)
    result = transposed + transposed  # Fast concatenation
    
    return {'parts': {'Voice1': result}}
```

---

## Summary: Quick Decision Guide

**Use Station 3 (Blueprint) when:**
- ✅ Simple transformations (transpose, invert, retrograde)
- ✅ Declarative structure (no loops/conditionals needed)
- ✅ Visual readability matters
- ✅ Non-programmers will edit

**Use Station 4 (Programmatic) when:**
- ✅ Need loops, conditionals, randomness
- ✅ Algorithmic/generative composition
- ✅ Voice leading validation required
- ✅ Complex multi-section forms
- ✅ Performance optimization (many transformations)

**Available Functions Recap:**

| Station | Module | Functions |
|---------|--------|-----------|
| 3 (Blueprint) | `src/transformations.py` | `transpose_part`, `invert_part`, `retrograde_part`, `augment_part`, `diminish_part`, `chordify_part`, `harmonize_part` |
| 4 (Programmatic) | `src/composition_shorthand.py` | `transpose_events`, `invert_events`, `retrograde_events`, `filter_events` |
| 4 (Helpers) | `src/music_data.py` | `data_to_part`, `part_to_data` |
| 4 (Analysis) | `src/lib/TONAL_HARMONY_TEMPLATES.py` | `check_voice_leading_errors`, `create_neapolitan_chord`, etc. |

**File Path Reference:**
```
/workspaces/Codempose/
├── generate_study.py              ← Your composition file
├── src/
│   ├── transformations.py         ← Station 3 functions
│   ├── composition_shorthand.py   ← Station 4 event functions
│   ├── music_data.py              ← Converters (events ↔ music21)
│   └── lib/
│       └── TONAL_HARMONY_TEMPLATES.py  ← Analysis tools
└── outputs/
    └── TEMPLATES/
        ├── ADVANCED_MUSIC21_GUIDE.md        ← THIS DOCUMENT
        ├── BLUEPRINT_ADVANCED_FEATURES.md   ← Blueprint-specific tips
        └── README_TEMPLATE.md               ← Quick start guide
```

---

## Station 3 vs Station 4: When to Use Which

### Use Station 3 (Blueprint Shorthand) When:
- Simple transformations on single melodic lines
- Combining existing snippets
- You want Station 2 library auto-generated

```python
VOICE_ASSIGNMENTS = {
    'Piano': {
        'RH': 'THEME + transpose(THEME, 7) + retrograde(THEME)',
        'LH': 'transpose(BASS, -12)'
    }
}
```

### Use Station 4 (Programmatic) When:
- Conditional logic (if/else)
- Loops (generating sequences, patterns)
- Multi-part transformations (harmonization)
- Analysis before generation
- Complex algorithmic composition

```python
def build_score_data():
    # Step 1: Extract the theme as event list
    # Returns: list of dicts like [{'type': 'note', 'step': 'c', 'octave': 4, 'ql': 1.0, ...}, ...]
    theme = parse_lilypond_to_data(THEME)['parts']['theme']
    
    # Step 2: Conditional logic - transpose based on mode
    # Major: transpose up perfect 5th (7 semitones)
    # Minor: transpose up minor 6th (8 semitones)
    if metadata['key_mode'] == 'major':
        answer = transpose_events(theme, 7)  # Returns new event list, doesn't modify theme
    else:
        answer = transpose_events(theme, 8)  # Still returns event list
    
    # Step 3: Loop to build ascending sequence
    # This creates: theme, theme+2 semitones, theme+4 semitones, theme+6 semitones
    # Each iteration adds more events to the sequence
    sequence = []
    for i in range(4):
        transposed = transpose_events(theme, i * 2)  # Returns fresh event list each time
        sequence.extend(transposed)  # Concatenate event lists
    
    # Step 4: Return dict with 'parts' key
    # Framework expects this exact structure to generate output
    return {'parts': {'Voice1': sequence}}
```

---

## Multi-Part Transformations (Harmonization)

### The Suffix System

**Rule**: When a transformation returns **multiple parts** (Score), you MUST use a suffix to specify which part you want.

#### Station 3 Blueprint Syntax

```python
# harmonize_part returns Score with 'melody' and 'harmony' parts
VOICE_STAVE_DATA = '''
    harmonize_part(THEME, 'I-IV-V-I'):melody  &  harmonize_part(THEME, 'I-IV-V-I'):harmony
'''
```

**How it works**:
1. First call to `harmonize_part(THEME, 'I-IV-V-I')` runs the function
2. Framework caches ALL parts: `melody`, `harmony`
3. Returns `melody` part to first voice
4. Second call is FREE (cached lookup), returns `harmony` part

#### Station 4 Programmatic Equivalent

```python
from src.transformations import harmonize_part

def build_score_data():
    # Step 1: Parse LilyPond to get event list
    # theme is now: [{'type': 'note', ...}, {'type': 'note', ...}, ...]
    theme = parse_lilypond_to_data(THEME)['parts']['theme']
    
    # Step 2: Convert event list to music21 Part object
    # Why? harmonize_part() needs music21 objects, not our event dicts
    theme_part = data_to_part(theme)  # Now a music21.stream.Part with Note/Rest objects
    
    # Step 3: Call multi-part transformation
    # Returns: music21.stream.Score containing MULTIPLE parts (not a single part!)
    # This Score has .parts[0] = melody, .parts[1] = harmony
    harmonized_score = harmonize_part(theme_part, progression='I-IV-V-I')
    
    # Step 4: Extract individual parts from the Score
    # harmonized_score.parts is a list of music21.stream.Part objects
    melody_part = harmonized_score.parts[0]      # Part with .id = 'melody'
    harmony_part = harmonized_score.parts[1]     # Part with .id = 'harmony'
    
    # Step 5: Convert music21 Parts back to event lists
    # Why? The framework expects event dicts, not music21 objects
    melody_events = part_to_data(melody_part)    # Back to [{'type': 'note', ...}, ...]
    harmony_events = part_to_data(harmony_part)  # Same format
    
    # Step 6: Return the final structure
    # Keys 'Soprano' and 'Alto' become staff names in the output
    return {
        'parts': {
            'Soprano': melody_events,    # Event list goes to Soprano staff
            'Alto': harmony_events       # Event list goes to Alto staff
        }
    }
```

### Available Multi-Part Transformations

| Function | Returns | Suffixes | Usage |
|----------|---------|----------|-------|
| `harmonize_part(part, progression)` | Score | `:melody`, `:harmony` | Add harmonic accompaniment |
| `create_canon(part, interval, delay)` | Score | `:leader`, `:follower` | Strict imitation |
| `invertible_counterpoint(part1, part2)` | Score | `:upper`, `:lower` | Swap-able voices |

---

## Tonal Harmony Implementation

### Roman Numeral Progressions

**Available in**: `src/lib/TONAL_HARMONY_TEMPLATES.py`

#### Quick Harmonization

```python
from src.transformations import harmonize_part
from src.music_data import data_to_part, part_to_data
from src.lilypond_parser import parse_lilypond_to_data

def build_score_data():
    # Step 1: Parse your melody from Station 1
    melody = parse_lilypond_to_data(MELODY)['parts']['melody']
    melody_part = data_to_part(melody)  # Convert to music21 for analysis
    
    # Step 2: Define chord progression
    # Progression string with Roman numerals separated by hyphens
    # The function automatically distributes chords across the melody duration
    progression = 'I-IV-V-I'
    
    # Step 3: Generate harmony automatically
    # This function analyzes the melody and creates a bass line following the progression
    # Returns: music21.stream.Score with two parts: 'melody' (original) and 'harmony' (generated bass)
    harmonized = harmonize_part(
        melody_part, 
        progression_string=progression,
        key='C'  # Key signature for the progression
    )
    
    # Step 4: Extract the two parts
    # harmonized.parts['melody'] = your original melody (unchanged)
    # harmonized.parts['harmony'] = generated harmony voice (new notes)
    melody_events = part_to_data(harmonized.parts['melody'])
    harmony_events = part_to_data(harmonized.parts['harmony'])
    
    # Step 5: Assign to piano staves
    # RH (right hand) gets the melody
    # LH (left hand) gets the harmony (typically lower notes)
    return {
        'parts': {
            'RH': melody_events,     # Original melody
            'LH': harmony_events     # Auto-generated harmony
        }
    }
```

### Common Chord Progressions (Pre-Built)

```python
# Common progression strings (define these in your study file)
PROGRESSION_I_IV_V_I = 'I-IV-V-I'           # Basic cadence
PROGRESSION_I_VI_IV_V = 'I-vi-IV-V'        # Popular progression  
PROGRESSION_CIRCLE_OF_FIFTHS = 'ii-V-I'    # Jazz standard
PROGRESSION_PACHELBEL = 'I-V-vi-iii-IV-I-IV-V'  # Canon in D

# Use in Blueprint
VOICE_STAVE_DATA = f'''
    harmonize_part(THEME, '{PROGRESSION_I_IV_V_I}', 'C'):melody  &  
    harmonize_part(THEME, '{PROGRESSION_I_IV_V_I}', 'C'):harmony
'''
```

---

## Voice Leading Validation

### Automatic Error Detection

```python
from src.lib.TONAL_HARMONY_TEMPLATES import check_voice_leading_errors

def build_score_data():
    # Build your 4-part harmony
    soprano = parse_lilypond_to_data(SOPRANO)['parts']['soprano']
    alto = parse_lilypond_to_data(ALTO)['parts']['alto']
    tenor = parse_lilypond_to_data(TENOR)['parts']['tenor']
    bass = parse_lilypond_to_data(BASS)['parts']['bass']
    
    # Assemble score
    score = stream.Score()
    score.append(data_to_part(soprano))
    score.append(data_to_part(alto))
    score.append(data_to_part(tenor))
    score.append(data_to_part(bass))
    
    # CHECK FOR ERRORS
    # Returns dict: {'parallel_fifths': [...], 'parallel_octaves': [...], 'voice_crossing': [...], ...}
    # Each error is a dict like: {'measure': 3, 'voices': 'Soprano-Alto', 'beat': 2.0}
    errors = check_voice_leading_errors(score)
    
    # Report problems to user
    # Example output: "⚠️ PARALLEL FIFTHS: Measure 3, between Soprano-Alto"
    if errors['parallel_fifths']:
        print("⚠️ PARALLEL FIFTHS:")
        for err in errors['parallel_fifths']:
            print(f"   Measure {err['measure']}, between {err['voices']}")
    
    # Example: Soprano C4 → D4 while Alto F3 → G3 (both move by step, creating parallel octaves)
    if errors['parallel_octaves']:
        print("⚠️ PARALLEL OCTAVES:")
        for err in errors['parallel_octaves']:
            print(f"   Measure {err['measure']}, between {err['voices']}")
    
    # Optionally: refuse to export if errors found
    if any(errors.values()):
        raise ValueError("Voice leading errors detected! Fix before exporting.")
    
    return {
        'parts': {
            'Soprano': soprano,
            'Alto': alto,
            'Tenor': tenor,
            'Bass': bass
        }
    }
```

### What Gets Checked

- ✅ Parallel fifths
- ✅ Parallel octaves
- ✅ Hidden (direct) fifths
- ✅ Hidden (direct) octaves
- ✅ Voice crossing
- ✅ Spacing errors (>octave between upper voices)

---

## Chromatic Harmony

### Secondary Dominants

```python
from src.lib.TONAL_HARMONY_TEMPLATES import (
    create_secondary_dominant,
    resolve_secondary_dominant
)

def build_score_data():
    # Create V7/V (dominant of dominant)
    v_of_v = create_secondary_dominant(
        target_chord='V',
        key='C major',
        seventh=True  # Make it V7
    )
    
    # Returns: music21.chord.Chord object (D7 chord in C major)
    # Notes: D-F#-A-C (V7 of V in C)
    
    # Use in progression
    progression = [
        'I',              # C major
        'V7/V',           # D7 (secondary dominant)
        'V7',             # G7 (resolves to...)
        'I'               # C major
    ]
    
    harmonized = harmonize_part(
        melody_part,
        progression_string='-'.join(progression),
        key='C'
    )
    
    # Extract parts
    melody_events = part_to_data(harmonized.parts[0])
    harmony_events = part_to_data(harmonized.parts[1])
    
    return {
        'parts': {
            'Melody': melody_events,
            'Harmony': harmony_events
        }
    }
```

### Neapolitan Sixth Chord (♭II6)

```python
from src.lib.TONAL_HARMONY_TEMPLATES import create_neapolitan_chord

def build_score_data():
    # In C minor: Neapolitan = D♭ major (♭II)
    # Used in first inversion: F-A♭-D♭ (♭II6)
    
    n6 = create_neapolitan_chord(
        key='C minor',
        inversion=1  # First inversion (6 chord)
    )
    
    # Use in cadence
    progression = [
        'i',              # C minor
        'N6',             # Neapolitan sixth (♭II6)
        'V7',             # G7
        'i'               # C minor
    ]
    
    harmonized = harmonize_part(
        melody_part,
        progression_string='-'.join(progression),
        key='c'  # Lowercase for minor key
    )
    
    # Extract parts
    melody_events = part_to_data(harmonized.parts[0])
    harmony_events = part_to_data(harmonized.parts[1])
    
    return {
        'parts': {
            'Melody': melody_events,
            'Harmony': harmony_events
        }
    }
```

### Augmented Sixth Chords

```python
from src.lib.TONAL_HARMONY_TEMPLATES import (
    create_italian_augmented_sixth,    # It+6
    create_french_augmented_sixth,     # Fr+6
    create_german_augmented_sixth      # Ger+6
)

def build_score_data():
    # German augmented sixth in C minor
    # Notes: A♭-C-E♭-F# (resolves to V)
    
    ger6 = create_german_augmented_sixth(key_str='c')
    
    # Use in progression (pre-dominant function)
    progression = [
        'i',              # C minor
        'Ger+6',          # German augmented sixth
        'V',              # G major (resolution)
        'i'               # C minor
    ]
    
    harmonized = harmonize_part(
        melody_part,
        progression_string='-'.join(progression),
        key='c'  # Lowercase for minor key
    )
    
    # Extract parts
    melody_events = part_to_data(harmonized.parts[0])
    harmony_events = part_to_data(harmonized.parts[1])
    
    return {
        'parts': {
            'Melody': melody_events,
            'Harmony': harmony_events
        }
    }
```

---

## Custom Transformation Functions

### Template for Single-Part Transformation

```python
from music21 import stream, note, interval
from src.music_data import part_to_data, data_to_part

def my_custom_transformation(events, **kwargs):
    """
    Template for creating custom transformations.
    
    Args:
        events: List of event dictionaries
        **kwargs: Your custom parameters
        
    Returns:
        List of transformed event dictionaries
    """
    # Step 1: Convert events to music21 Part
    # Input: events = [{'type': 'note', 'step': 'c', 'octave': 4, 'ql': 1.0, ...}, ...]
    # Output: part = music21.stream.Part with Note/Rest objects inside
    # Why? music21 functions work with Note objects, not our event dicts
    part = data_to_part(events)
    
    # Step 2: Apply music21 transformations
    # Here you use music21 API: part.transpose(), part.augmentOrDiminish(), etc.
    # transformed_part is still a music21.stream.Part (with modified notes inside)
    transformed_part = do_music21_stuff(part, **kwargs)
    
    # Step 3: Convert back to events
    # Input: transformed_part = music21.stream.Part with transformed Note objects
    # Output: result_events = [{'type': 'note', 'step': 'd', 'octave': 4, 'ql': 2.0, ...}, ...]
    # Why? Framework needs event dicts for rendering to LilyPond/MusicXML/MIDI
    result_events = part_to_data(transformed_part)
    
    # Return the event list (NOT the music21 Part!)
    return result_events


def do_music21_stuff(part, **kwargs):
    """Your actual music21 logic."""
    new_part = stream.Part()
    
    for element in part.flatten().notesAndRests:
        # Example: transpose and augment
        if isinstance(element, note.Note):
            new_note = note.Note(element.pitch)
            new_note.quarterLength = element.quarterLength * 2  # Augment
            new_note.transpose(interval.Interval(7), inPlace=True)  # +P5
            new_part.append(new_note)
    
    return new_part
```

### Template for Multi-Part Transformation

```python
from music21 import stream

def my_multi_part_transformation(events, **kwargs):
    """
    Template for transformations that generate multiple parts.
    
    Returns:
        music21.stream.Score with .id set on each part
    """
    # 1. Convert to music21
    input_part = data_to_part(events)
    
    # 2. Generate multiple parts
    score = stream.Score()
    
    # Part 1: Original
    part1 = stream.Part()
    part1.id = 'original'  # REQUIRED!
    for element in input_part.flatten().notesAndRests:
        part1.append(element)
    
    # Part 2: Harmony
    part2 = stream.Part()
    part2.id = 'harmony'  # REQUIRED!
    for element in input_part.flatten().notesAndRests:
        # Generate harmony (simplified example)
        if isinstance(element, note.Note):
            harmony_note = note.Note(element.pitch)
            harmony_note.transpose(interval.Interval(-7), inPlace=True)  # -P5
            part2.append(harmony_note)
    
    score.append(part1)
    score.append(part2)
    
    return score  # Returns Score, not events!
```

### Using Custom Transformations

**In Station 4:**
```python
def build_score_data():
    theme = parse_lilypond_to_data(THEME)['parts']['theme']
    
    # Single-part transformation
    result = my_custom_transformation(theme, param1='value')
    
    # Multi-part transformation
    multi_result = my_multi_part_transformation(theme)
    original = part_to_data(multi_result.parts['original'])
    harmony = part_to_data(multi_result.parts['harmony'])
    
    return {
        'parts': {
            'Voice1': result,
            'Voice2': original,
            'Voice3': harmony
        }
    }
```

---

## Practical Recipes

### Recipe 1: Baroque Sequence (Descending Fifths)

```python
def build_score_data():
    # Parse your motif (e.g., C-D-E-F in quarter notes)
    motif = parse_lilypond_to_data(MOTIF)['parts']['motif']
    
    # Build sequence by transposing down by fifths
    # Result: C-D-E-F (original), F-G-A-Bb (-7 semitones), Bb-C-D-Eb (-14), Eb-F-G-Ab (-21)
    # This creates the classic Baroque descending sequence pattern
    sequence = []
    intervals = [0, -7, -14, -21]  # 0 = original, -7 = down P5, -14 = down 2 P5s, etc.
    
    for interval_offset in intervals:
        # Each iteration creates a new transposed copy of the motif
        transposed = transpose_events(motif, interval_offset)
        sequence.extend(transposed)  # Append to growing sequence
    
    # Final sequence is 4x longer than original motif
    return {'parts': {'Soprano': sequence}}
```

### Recipe 2: Canon at the Octave (4-beat delay)

```python
def build_score_data():
    # Parse the theme (e.g., C-D-E-F-G in quarter notes = 5 QL total)
    theme = parse_lilypond_to_data(THEME)['parts']['theme']
    
    # Leader voice: plays the theme immediately (no changes)
    leader = theme
    
    # Follower voice: same theme but higher and delayed
    # Step 1: Transpose up one octave (12 semitones)
    follower_theme = transpose_events(theme, 12)  # C-D-E-F-G becomes C5-D5-E5-F5-G5
    
    # Step 2: Create delay by adding rest at the beginning
    # This is ONE event dict representing a 4-beat (whole note) rest
    rest = [{'type': 'rest', 'ql': 4.0, 'step': 'r', 'octave': 0, 'alter': 0}]
    
    # Step 3: Concatenate rest + theme
    # Result: follower starts 4 beats after leader (classic canon delay)
    follower = rest + follower_theme
    
    # Timeline:
    # Beat 1-4: Leader plays theme, Follower rests
    # Beat 5+: Both play together (Leader ahead by 4 beats)
    return {
        'parts': {
            'Leader': leader,      # Starts immediately
            'Follower': follower   # Starts after 4-beat rest
        }
    }
```

### Recipe 3: Validate Harmony Before Export

```python
def build_score_data():
    # Build SATB harmony
    soprano = parse_lilypond_to_data(SOPRANO)['parts']['soprano']
    alto = parse_lilypond_to_data(ALTO)['parts']['alto']
    tenor = parse_lilypond_to_data(TENOR)['parts']['tenor']
    bass = parse_lilypond_to_data(BASS)['parts']['bass']
    
    # Assemble for validation
    score = stream.Score()
    score.append(data_to_part(soprano))
    score.append(data_to_part(alto))
    score.append(data_to_part(tenor))
    score.append(data_to_part(bass))
    
    # Validate
    from src.lib.TONAL_HARMONY_TEMPLATES import check_voice_leading_errors
    errors = check_voice_leading_errors(score)
    
    # Report
    total_errors = sum(len(v) for v in errors.values())
    if total_errors > 0:
        print(f"\n⚠️ Found {total_errors} voice leading errors:")
        for error_type, instances in errors.items():
            if instances:
                print(f"  • {error_type}: {len(instances)} occurrences")
        print("\n💡 Fix errors or use PROMOTE_TO_PROGRAMMATIC to override\n")
    
    return {
        'parts': {
            'Soprano': soprano,
            'Alto': alto,
            'Tenor': tenor,
            'Bass': bass
        }
    }
```

### Recipe 4: Algorithmic Melody + Auto-Harmonization

```python
def build_score_data():
    import random
    
    # Generate algorithmic melody using random scale degrees
    # scale_degrees are semitone offsets from C (0=C, 2=D, 4=E, 5=F, 7=G, 9=A, 11=B)
    scale_degrees = [0, 2, 4, 5, 7, 9, 11]  # C major scale
    melody_events = []
    
    # Create 16 random notes
    for i in range(16):
        # Pick random scale degree (e.g., degree=7 means G)
        degree = random.choice(scale_degrees)
        
        # Pick random rhythm (eighth, quarter, or half note)
        ql = random.choice([0.5, 1.0, 2.0])
        
        # Start with C4 as base note
        event = {
            'type': 'note',
            'step': 'c',      # Will be transposed
            'octave': 4,
            'alter': 0,
            'ql': ql          # Random duration
        }
        
        # Transpose C4 up by the chosen scale degree
        # Example: if degree=7, C4 becomes G4
        melody_events.append(event)
        if degree > 0:
            # transpose_events returns a list, so take first [0] element
            melody_events[-1] = transpose_events([event], degree)[0]
    
    # Convert to Part for harmonization
    melody_part = data_to_part(melody_events)
    
    # Auto-harmonize
    from src.transformations import harmonize_part
    progression = 'I-IV-V-I-I-IV-V-I-I-IV-V-I-I-IV-V-I'  # Repeat 4 times
    
    harmonized = harmonize_part(
        melody_part,
        progression_string=progression,
        key='C'
    )
    
    return {
        'parts': {
            'Melody': part_to_data(harmonized.parts['melody']),
            'Harmony': part_to_data(harmonized.parts['harmony'])
        }
    }
```

---

## Music21 API Quick Reference

### Most-Used Functions

**From `src.composition_shorthand`:**
```python
transpose_events(events, semitones)           # Chromatic transposition
invert_events(events, axis_pitch)             # Melodic inversion
retrograde_events(events)                     # Reverse order
filter_events(events, exclude_types=['barline'])  # Remove artifacts
```

**From `src.transformations`:**
```python
harmonize_part(part, progression_string, key)  # Generate bass line from progression
```

**From `src.lib.TONAL_HARMONY_TEMPLATES`:**
```python
check_voice_leading_errors(score)                    # Validate voice leading
create_neapolitan_chord(key_str, inversion=1)       # N6 chord
create_german_augmented_sixth(key_str)              # Ger+6 chord
create_italian_augmented_sixth(key_str)             # It+6 chord
create_french_augmented_sixth(key_str)              # Fr+6 chord
validate_harmonic_progression(progression_string, key_str)  # Check progression validity
```

**From `src.lib.MUSIC21_API_TEMPLATES`:**
```python
create_basic_notes()          # Note creation patterns
manipulate_pitches()          # Pitch operations
create_tuplets()              # Triplets, quintuplets, etc.
add_articulations()           # Staccato, accent, etc.
add_dynamics()                # p, f, mf, crescendo, etc.
```

### Essential music21 Imports

```python
from music21 import (
    stream,           # Score, Part, Measure containers
    note,             # Note, Rest objects
    chord,            # Chord objects
    pitch,            # Pitch manipulation
    interval,         # Interval calculations
    roman,            # Roman numeral analysis
    key,              # Key signatures
    meter,            # Time signatures
    tempo,            # Tempo markings
)
```

---

## Debugging Tips

### View Internal Events

```python
# After parsing or transformation:
for i, event in enumerate(events[:10]):  # First 10 events
    print(f"{i}: {event['type']} - {event.get('step', 'N/A')}{event.get('octave', '')}, QL={event['ql']}")
```

### Check music21 Part Contents

```python
part = data_to_part(events)
print(f"Part duration: {part.quarterLength} QL")
print(f"Note count: {len(part.flatten().notes)}")
print(f"First 5 notes: {[str(n.pitch) for n in part.flatten().notes[:5]]}")
```

### Validate Transformation Output

```python
result = my_transformation(input_events)
print(f"Input: {len(input_events)} events")
print(f"Output: {len(result)} events")
print(f"Types: {set(e['type'] for e in result)}")  # Should be: note, rest
```

---

## Where to Find More

- **Basic Workflow**: See comments in `study_template.py`
- **Tonal Harmony Functions**: `src/lib/TONAL_HARMONY_TEMPLATES.py` (complete implementations)
- **music21 Patterns**: `src/lib/MUSIC21_API_TEMPLATES.py` (all music21 features)
- **Station 4 Examples**: `src/lib/station4_music21_examples.py` (fugue, canon, etc.)
- **Working Studies**: `studies/100th.py`, `studies/fugue.py`

---

**Remember**: Station 3 for simple arrangements. Station 4 for everything else. Use tonal harmony templates to validate and enhance your compositions programmatically!
