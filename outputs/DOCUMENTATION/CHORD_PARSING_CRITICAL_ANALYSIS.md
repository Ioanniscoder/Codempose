# CHORD PARSING - CRITICAL EVALUATION POINT
**Date:** October 15, 2025  
**Context:** Blueprint String Framework Implementation (v2.0)

---

## 🔴 CRITICAL ISSUE IDENTIFIED

There are **TWO DIFFERENT** chord resolution implementations in the codebase:

### **Implementation 1: `lilypond_parser.py` (Lines 298-330)**
**Strategy:** Chord notes resolve **relative to each other** (progressive resolution)

```python
# Line 276: Get base note octave from TinyNotation
base_octave = _extract_octave_from_tiny(tiny_token)

# Lines 298-330: Other notes resolve relative to PREVIOUS note in chord
prev_pitch = base_step.upper()
prev_octave = base_octave

for note_str in parsed.chord_other_notes:
    # Calculate closest octave relative to PREVIOUS NOTE in chord
    if abs(curr_idx - prev_idx) <= 3:
        note_octave = prev_octave  # Same octave as previous chord note
    elif curr_idx < prev_idx:
        note_octave = prev_octave + 1
    else:
        note_octave = prev_octave - 1
    
    # Update for NEXT chord note
    prev_pitch = note_step
    prev_octave = note_octave
```

**Example:** `<c e g>4` with base at C4
- `c` → C4 (base note from TinyNotation)
- `e` → E4 (closest to C4)
- `g` → G4 (closest to E4)

---

### **Implementation 2: `relative_octave_logic.py` (Lines 290-310)**
**Strategy:** Only **base note** resolves relative to previous reference pitch

```python
elif token.is_chord:
    # CHORD: Process base note through relative octave logic
    base_note = token.chord_base_note
    octave, new_midi, large_leap = calculate_relative_octave(
        current_midi,
        base_note.pitch_letter,
        base_note.accidental,
        base_note.octave_markers,
        current_pitch
    )
    
    # Return the resolved octave for the base note ONLY
    results.append((token, octave, large_leap))
    
    # Update reference pitch based on base note
    current_midi = new_midi
    current_pitch = base_note.pitch_letter
```

**Note:** This function does **NOT** resolve the other notes in the chord - it only tracks the base note for the reference pitch chain.

---

## 🎯 WHICH IS CORRECT?

### **Analysis:**

1. **`relative_octave_logic.py`** is used for **TinyNotation generation** (the reference output)
   - It only resolves the base note
   - Other chord notes are left in their **raw LilyPond form**

2. **`lilypond_parser.py`** is used for **music21 conversion** (the final output)
   - It must resolve ALL notes in the chord to absolute pitches
   - It uses TinyNotation's base octave as the starting point
   - Then resolves other notes relative to each other

### **Critical Dependency:**

```
LilyPond Input → relative_octave_logic.py → TinyNotation (base note octave)
                                               ↓
                          lilypond_parser.py reads TinyNotation
                                               ↓
                          Uses base octave to resolve other chord notes
```

**The two implementations are COMPLEMENTARY, not contradictory:**
- `relative_octave_logic.py` → Establishes base note octave
- `lilypond_parser.py` → Uses that base to resolve other notes

---

## ⚠️ POTENTIAL PROBLEM

### **What if there's a mismatch?**

If `lilypond_parser.py`'s chord resolution logic doesn't match LilyPond's actual behavior, we get **wrong pitches**.

### **LilyPond's Actual Chord Behavior:**

According to LilyPond documentation:
- In `\relative` mode, **only the first note** of a chord is affected by the previous note
- **All other notes** in the chord are relative to the **first note** of that chord
- This is EXACTLY what `lilypond_parser.py` implements!

**Example in LilyPond:**
```lilypond
\relative c' {
  c4 <e g c>  % e is relative to c, g is relative to e, c is relative to g
}
```

Result:
- First `c` → C4 (from `\relative c'`)
- `<e g c>` chord:
  - `e` → E4 (closest to C4)
  - `g` → G4 (closest to E4)  
  - `c` → C5 (closest to G4)

---

## ✅ CONCLUSION

**The current implementation is CORRECT!**

1. **`relative_octave_logic.py`**: Correctly tracks only the base note for TinyNotation
2. **`lilypond_parser.py`**: Correctly resolves all chord notes relative to each other

**However:**
- This is a **critical dependency chain** that must be preserved
- Any Blueprint String Framework implementation must respect this logic
- The TinyNotation reference is ESSENTIAL for chord parsing accuracy

---

## 📋 IMPLICATIONS FOR BLUEPRINT FRAMEWORK

### **What the Blueprint Framework Must Preserve:**

1. **TinyNotation Generation** must still happen for chord snippets
   - This establishes the base note octave
   - Without it, chord parsing will fail

2. **Chord Resolution Logic** in `lilypond_parser.py` must remain unchanged
   - It depends on TinyNotation's base octave

3. **The Three-Station Workflow is VALIDATED:**
   - Station 1: LilyPond Input (composer writes `<c e g>2`)
   - Station 2: TinyNotation Reference (**critical** for chord base octave)
   - Station 3: Blueprint Strings (assembly layer)

### **Blueprint Framework Requirements:**

✅ **Can** replace manual score assembly  
✅ **Can** use blueprint strings for layout  
❌ **Cannot** skip TinyNotation generation for snippets with chords  
❌ **Cannot** bypass relative octave resolution  

---

## 🔧 BLUEPRINT IMPLEMENTATION STRATEGY

### **Modified Approach:**

1. **Parse Blueprint Strings** → Identify which snippets are needed
2. **For each snippet:**
   - Parse LilyPond → Generate TinyNotation (preserves chord base octaves)
   - Convert to music21 events (uses TinyNotation for chord resolution)
3. **Assemble score** using blueprint layout definition
4. **Auto-generate rests** where needed

**Key Insight:** The Blueprint Framework is an **assembly layer**, not a parsing bypass.

---

## 📌 VALIDATION CHECKPOINT

Before proceeding with Blueprint Framework implementation:

✅ **Confirm:** TinyNotation generation is mandatory for chord-containing snippets  
✅ **Confirm:** `lilypond_parser.py` chord resolution logic is correct  
✅ **Confirm:** Station 2 (TinyNotation) is a critical dependency, not just a reference  

**This understanding is CRITICAL for correct implementation.**

---

**Status:** Ready to implement Blueprint Framework v2.0 with full understanding of chord parsing requirements.
