# Promotion Feature & Note Tracking - Summary

## ✅ Implementation Complete

### 1. **Promotion Feature: LilyPond → TinyNotation**

The system now supports automatic promotion of LilyPond snippets to TinyNotation format.

#### How It Works:

1. **Add Toggle to Study File:**
   ```python
   PROMOTE_TO_TINYNOTATION = True
   SOURCE_MELODY_LILY = r"\relative c' { c4 d e f }"
   ```

2. **Run the File:**
   ```bash
   python3 first.py
   ```

3. **Automatic Promotion:**
   - Creates backup: `first.20251004_220314.bak`
   - Converts LilyPond to TinyNotation
   - Rewrites file with `SOURCE_MELODY_TINY`
   - Disables the toggle automatically
   - Asks you to re-run

4. **Result:**
   ```python
   # PROMOTE_TO_TINYNOTATION = False  # Promotion completed, toggle disabled
   # SOURCE_MELODY_LILY = r"\relative c' { c4 d e f }"  # Promoted to TinyNotation
   
   # Promoted from LilyPond to TinyNotation
   SOURCE_MELODY_TINY = "4/4 c4 d4 e4 f4"
   ```

#### Priority Order (Updated):

1. `build_score_data()` function (programmatic composition)
2. `SOURCE_MELODY_TINY` variable (promoted TinyNotation) ⭐ NEW
3. `SOURCE_MELODY_LILY` variable (raw LilyPond)
4. `build_part()` function (music21.Part)

---

### 2. **Note Tracking System**

Every musical event in the system has complete provenance tracking:

#### Tracking Data Structure:

```python
{
    'metadata': {
        'original_input': r"\relative e { e2 bmol4 c2 }",
        'parser_tokens': [
            {
                'original': 'e2',           # What you typed
                'converted': 'E2',          # TinyNotation format
                'position': 0,              # Order in sequence
                'warnings': []              # Parser alerts
            },
            {
                'original': 'bmol4',
                'converted': 'B-4',
                'position': 1,
                'warnings': ['Localized accidental: mol']
            }
        ],
        'warnings': ['Localized accidental: mol']
    },
    'parts': {
        'Melody': [
            {
                'original_token': 'e2',     # Links back to input
                'position': 0,
                'type': 'note',
                'step': 'E',
                'octave': 3,
                'alter': 0,
                'ql': 2.0
            },
            {
                'original_token': 'bmol4',
                'position': 1,
                'parser_warnings': ['Localized accidental: mol'],
                'type': 'note',
                'step': 'B',
                'octave': 3,
                'alter': -1.0,
                'ql': 1.0
            }
        ]
    }
}
```

#### Tracking Flow:

```
INPUT                PARSER              CONVERTER           MUSIC21            EVENTS
─────────────────────────────────────────────────────────────────────────────────────
"e2"          →     ParsedToken    →    "E2"          →    Note(E3)      →    {step: 'E',
                     pitch='e'           (TinyNotation)     ql=2.0              octave: 3,
                     duration='2'                                               ql: 2.0,
                     octave_calc                                                original_token: 'e2'}

"bmol4"       →     ParsedToken    →    "B-4"         →    Note(B♭3)     →    {step: 'B',
                     pitch='b'           (TinyNotation)     ql=1.0              octave: 3,
                     accidental='flat'                                          alter: -1.0,
                     duration='4'                                               ql: 1.0,
                     warning='mol'                                              original_token: 'bmol4',
                                                                                warnings: ['Localized...']}
```

#### Benefits:

1. **Debugging:**
   - See exactly what input caused each note
   - Trace parser decisions
   - Identify conversion issues

2. **Validation:**
   - Verify relative octave calculations
   - Check accidental handling
   - Confirm duration parsing

3. **Analysis:**
   - Understand parser behavior
   - Audit transformations
   - Educational insight into the pipeline

4. **Testing:**
   - Compare input → output
   - Validate round-trip conversions
   - Regression testing

---

### 3. **Enhanced Engraver**

The engraver now writes complete LilyPond metadata:

```lilypond
\version "2.24.1"
% ========================================
% ORIGINAL LILYPOND INPUT (for reference)
% ========================================
% \relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 }
%
% ========================================

\header { title = "LilyPond Score" }
\score {
  \new Staff {
    \clef treble
    \time 6/4
    \key c \major
    \tempo 4 = 90
    e,2 bes,4 c2 r4 ...
  }
  \layout { }
  \midi { }
}
```

All directives from the input are preserved in the output!

---

### 4. **Files Updated**

- **`project_template.py`**: Added promotion logic and SOURCE_MELODY_TINY support
- **`lilypond_parser.py`**: Fixed metadata extraction
- **`lily_to_tiny.py`**: Fixed TinyNotation format for music21 compatibility
- **Demo files**: `demo_note_tracking.py`, `test_promotion.py`

---

### 5. **Usage Examples**

#### Example 1: Simple Promotion
```python
# study_file.py
PROMOTE_TO_TINYNOTATION = True
SOURCE_MELODY_LILY = r"\relative c' { c4 d e f }"

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
```

#### Example 2: Direct TinyNotation
```python
# Already promoted - no conversion needed
SOURCE_MELODY_TINY = "4/4 c4 d4 e4 f4"

if __name__ == '__main__':
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
```

#### Example 3: Inspect Tracking Data
```python
from lilypond_parser import parse_lilypond_to_data

score_data = parse_lilypond_to_data(r"\relative e { e2 bmol4 c2 }")

# Access tracking
for token in score_data['metadata']['parser_tokens']:
    print(f"{token['original']} → {token['converted']}")
    if token['warnings']:
        print(f"  ⚠️  {token['warnings']}")

# Access final events
for event in score_data['parts']['Melody']:
    print(f"Position {event['position']}: {event['original_token']} → {event['step']}{event['octave']}")
```

---

### 6. **Next Steps / Enhancements**

Potential improvements you might want:

1. **Metadata Preservation:**
   - Should TinyNotation files preserve key/tempo metadata?
   - How to annotate TinyNotation with directives?

2. **Reverse Conversion:**
   - TinyNotation → LilyPond?
   - Useful for editing promoted files?

3. **Batch Promotion:**
   - Promote all study files at once?
   - Script to scan and promote marked files?

4. **Tracking Visualization:**
   - HTML report showing input→output mappings?
   - Side-by-side comparison viewer?

5. **Warning Management:**
   - Auto-fix localized accidentals?
   - Suggest corrections for parser warnings?

---

### 7. **Testing**

Run the demos:
```bash
# Test promotion
python3 test_promotion.py

# See note tracking
python3 demo_note_tracking.py

# Test parser fixes
python3 first.py
```

All features are working! 🎵
