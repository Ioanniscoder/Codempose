# Snippet Length Analysis - ninetyninth.py

**Date:** October 20, 2025  
**Issue:** Staves have mismatched durations, causing layout problems

---

## Snippet Durations (in 3/4 time)

| Snippet       | Events | Duration (QL) | Bars | Notes |
|---------------|--------|---------------|------|-------|
| THEME_A       | 15     | 16.0 QL       | 5.3  | Long melodic phrase |
| THEME_B       | 5      | 10.0 QL       | 3.3  | Shorter phrase |
| BASS_FIGURE   | 9      | 12.0 QL       | 4.0  | Standard 4-bar pattern |
| HARMONY_CHORDS| 3      | 9.0 QL        | 3.0  | Simple 3-bar chords |

---

## Blueprint Structure Analysis

```
VOICE_STAVE_DATA = """
    # Section 1: Exposition
    THEME_A & BASS_FIGURE;           # Melody: 16 QL, Bass: 12 QL → MISMATCH (4 QL difference)

    # Section 2: Development with transposition
    transpose_part(THEME_A, 'P4') & BASS_FIGURE;   # Melody: 16 QL, Bass: 12 QL → MISMATCH (4 QL difference)

    # Section 3: Contrasting material
    THEME_B & r;                     # Melody: 10 QL, Bass: auto-rest → OK (framework fills)

    # Section 4: Recapitulation with repetition
    THEME_A * 2 & BASS_FIGURE * 2    # Melody: 32 QL, Bass: 24 QL → MISMATCH (8 QL difference)
"""
```

---

## Problem Breakdown

### Section 1: THEME_A & BASS_FIGURE
- **Melody (THEME_A):** 16.0 QL (5.3 bars)
- **Bass (BASS_FIGURE):** 12.0 QL (4.0 bars)
- **Gap:** 4 QL = 1.3 bars
- **Result:** Melody continues for 1.3 bars after bass finishes

### Section 2: transpose_part(THEME_A, 'P4') & BASS_FIGURE
- **Melody (transposed THEME_A):** 16.0 QL (5.3 bars)
- **Bass (BASS_FIGURE):** 12.0 QL (4.0 bars)
- **Gap:** 4 QL = 1.3 bars
- **Result:** Same mismatch as Section 1

### Section 3: THEME_B & r
- **Melody (THEME_B):** 10.0 QL (3.3 bars)
- **Bass (auto-rest):** Framework auto-fills to match
- **Result:** ✅ OK - framework handles this correctly

### Section 4: THEME_A * 2 & BASS_FIGURE * 2
- **Melody (THEME_A × 2):** 32.0 QL (10.7 bars)
- **Bass (BASS_FIGURE × 2):** 24.0 QL (8.0 bars)
- **Gap:** 8 QL = 2.7 bars
- **Result:** Melody continues for 2.7 bars after bass finishes

---

## What Happens in LilyPond Output

When staves have mismatched durations within a section:
1. **LilyPond continues both staves** - shorter one gets implicit rests
2. **Visual layout problem** - staves appear "out of sync"
3. **Musical coherence issue** - melody plays solo without accompaniment

---

## Solutions

### Option 1: Adjust BASS_FIGURE to match THEME_A (16 QL)
**Add 4 QL (1.3 bars) to BASS_FIGURE:**
```lilypond
BASS_FIGURE_LILY = r"""
\relative c {
    \clef bass
    \key g \major
    \time 3/4
    g4 d' b |      % Bar 1 (3 QL)
    c2 b4 |        % Bar 2 (3 QL)
    a4 g fis |     % Bar 3 (3 QL)
    g2.            % Bar 4 (3 QL)
    g2.            % Bar 5 (3 QL) ← ADD THIS
}
"""
```
**Result:** BASS_FIGURE = 15 QL (5 bars) - closer to THEME_A's 16 QL

### Option 2: Shorten THEME_A to match BASS_FIGURE (12 QL)
**Remove last bar from THEME_A:**
```lilypond
THEME_A_LILY = r"""
\relative c'' {
    \key g \major
    \time 3/4
    \tempo "Andante" 4=90
    d4-.\p( fis8 g) a4~ |      % Bar 1
    a4 g4->( fis) |             % Bar 2
    e4.( d8~ d4) |              % Bar 3
    % b'4\f c4 d4              % Bar 4 ← REMOVE THIS
}
"""
```
**Result:** THEME_A = 12 QL (4 bars) - matches BASS_FIGURE

### Option 3: Use Two Different Bass Patterns
**Create BASS_FIGURE_LONG for sections with THEME_A:**
```lilypond
BASS_FIGURE_LONG_LILY = r"""
\relative c {
    \clef bass
    \key g \major
    \time 3/4
    g4 d' b |
    c2 b4 |
    a4 g fis |
    g2. |
    d4 a' fis |
    g2.
}
"""
```
**Blueprint:**
```
THEME_A & BASS_FIGURE_LONG;
THEME_B & BASS_FIGURE;   # Shorter version for shorter melody
```

### Option 4: Accept Mismatches, Add Explicit Rests
**Let melody continue solo, make it intentional:**
```
# Section 1: Theme with cadenza
THEME_A & BASS_FIGURE;   # Bass stops, melody continues as solo cadenza
```
**Comment in score:** "Bass cadence followed by melodic solo"

---

## Recommendation

**For a learning/demo study:** Option 1 (extend BASS_FIGURE)
- Simple fix
- Shows how to balance durations
- Musical result: sustained bass note holds under final melody phrase

**For a real composition:** Option 3 (multiple bass patterns)
- Most musical flexibility
- Each section gets appropriate accompaniment
- Requires more snippet definitions but gives best result

---

## Framework Enhancement Idea

**Add snippet metadata with duration info in .ly header:**
```lilypond
% ========================================
% ORIGINAL SNIPPETS (Station 1 & 2)
% ========================================
%
% LilyPond Format:
%   THEME_A (16.0 QL, 5.3 bars):
%     \relative c'' { ... }
%
%   BASS_FIGURE (12.0 QL, 4.0 bars):
%     \relative c { ... }
```

This would help composers immediately see duration mismatches when reviewing the .ly file!

---

## Next Action

**User should decide:**
1. Which solution to use for ninetyninth.py?
2. Should framework auto-display durations in .ly header comments?
