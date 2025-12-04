# Root Directory Python Files Analysis

Analysis performed: October 16, 2025
Total files: 17

## ✅ CORE LIBRARY - ACTIVE (13 files)

### Pipeline Core (3 files)
1. **project_template.py** ✓ ACTIVE
   - Main pipeline orchestrator
   - Imported by: 74 files (all study files, tests, templates)
   - Purpose: run_pipeline_from_file() - central execution engine
   - Status: **ESSENTIAL - Core of system**

2. **lilypond_parser.py** ✓ ACTIVE
   - LilyPond syntax parser
   - Imported by: 76 files (all studies, tests)
   - Purpose: parse_lilypond_to_data() - converts LilyPond → canonical format
   - Status: **ESSENTIAL - Core parser**

3. **music_data.py** ✓ ACTIVE
   - Data structure conversions
   - Imported by: 50 files (all studies that use music21)
   - Purpose: data_to_part(), part_to_data() - canonical ↔ music21
   - Status: **ESSENTIAL - Core conversion layer**

### Parser Components (5 files)
4. **lily_to_tiny.py** ✓ ACTIVE
   - LilyPond → TinyNotation converter
   - Imported by: 7 files (lilypond_parser, tests)
   - Purpose: Intermediate conversion step
   - Status: **ACTIVE - Parser component**

5. **lily_token_parser.py** ✓ ACTIVE
   - Token parsing logic
   - Imported by: 12 files (lily_to_tiny, lilypond_parser)
   - Purpose: Parse tokenized LilyPond
   - Status: **ACTIVE - Parser component**

6. **lily_tokenizer.py** ✓ ACTIVE
   - LilyPond tokenization
   - Imported by: 5 files (lily_to_tiny, lily_token_parser)
   - Purpose: Tokenize LilyPond strings
   - Status: **ACTIVE - Parser component**

7. **data_structures.py** ✓ ACTIVE
   - Data structure definitions
   - Imported by: 5 files (lily_to_tiny, parser_project)
   - Purpose: Core data types for parser
   - Status: **ACTIVE - Parser component**

8. **relative_octave_logic.py** ✓ ACTIVE
   - Relative octave calculation
   - Imported by: 3 files (lily_to_tiny, lilypond_parser)
   - Purpose: Handle \relative mode in LilyPond
   - Status: **ACTIVE - Parser component**

### Utilities (3 files)
9. **lily_converter.py** ✓ ACTIVE
   - Event → LilyPond conversion
   - Imported by: 7 files (project_template, thirteenth.py)
   - Purpose: Reverse conversion (canonical → LilyPond)
   - Status: **ACTIVE - Utility**

10. **score_builder.py** ✓ ACTIVE
    - Blueprint-based score construction
    - Imported by: 8 files (thirteenth.py, fourteenth.py)
    - Purpose: build_score_from_blueprint() for complex compositions
    - Status: **ACTIVE - Used by studies 13-14**

11. **transformations.py** ✓ ACTIVE
    - Music21 transformations
    - Imported by: 13 files (eleventh.py, thirteenth.py)
    - Purpose: transpose_part(), invert_part(), etc.
    - Status: **ACTIVE - Used by advanced studies**

### Harmonic Intelligence (2 files - NEW)
12. **harmonic_analysis.py** ✓ ACTIVE
    - Structural tone analysis
    - Imported by: 6 files (harmonic_engine, fifteenth.py)
    - Purpose: find_structural_tones() - analyze melody
    - Status: **ACTIVE - Priority 3B feature**

13. **harmonic_engine.py** ✓ ACTIVE
    - Harmonization engine
    - Imported by: 7 files (sixteenth.py, seventeenth.py)
    - Purpose: harmonize_melody() - auto-generate bass lines
    - Status: **ACTIVE - Priority 3B feature**

---

## 📚 TEMPLATE FILES - DOCUMENTATION (2 files)

14. **CODEMPOSE_STUDY_TEMPLATES.py** ✓ TEMPLATE/DOC
    - Template collection for creating new studies
    - NOT imported (used as reference)
    - Purpose: Copy/paste templates for new compositions
    - Status: **KEEP - Documentation/templates**
    - Recommendation: Consider moving to templates/ directory

15. **voice_documentation.py** ✓ UTILITY
    - Helper for documenting programmatic voices
    - Imported by: 9 files (tenth.py, templates)
    - Purpose: register_and_document_voice() - metadata generation
    - Status: **ACTIVE - Documentation helper**

---

## ⚠️ DEPRECATED FILES (1 file)

16. **main.py** ⚠️ DEPRECATED
    - Old entry point (pre-Oct 3, 2025)
    - Imported by: 30 files (mostly .venv, not actual code)
    - Purpose: OLD WORKFLOW: python main.py first.py
    - Status: **DEPRECATED - Kept for backward compatibility**
    - Recommendation: **MOVE TO CLEANUP** (no longer needed)

---

## 🤔 UNCLEAR FILES (1 file)

17. **composition_shorthand.py** ❓ UNCLEAR
    - Imported by: 26 files (mostly cleanup/, outputs/TEMPLATES/)
    - NOT imported by any active study files (first-seventeenth.py)
    - Purpose: Unknown - needs investigation
    - Status: **INVESTIGATE - May be old utility**

---

## 📊 Summary

| Category | Count | Action |
|----------|-------|--------|
| ✅ Core Library (Essential) | 13 | **KEEP in root** |
| 📚 Templates/Documentation | 2 | **KEEP** (consider moving to templates/) |
| ⚠️ Deprecated | 1 | **MOVE to cleanup/** |
| 🤔 Unclear | 1 | **INVESTIGATE** |
| **TOTAL** | **17** | |

---

## 🎯 Recommendations

### Immediate Actions:
1. **Move to cleanup/**: main.py (deprecated)
2. **Investigate**: composition_shorthand.py (not used by active studies)
3. **Consider moving**: CODEMPOSE_STUDY_TEMPLATES.py → templates/

### Directory Structure:
```
Codempose/
├── [CORE LIBRARY - 13 files]
│   ├── project_template.py
│   ├── lilypond_parser.py
│   ├── music_data.py
│   ├── lily_*.py (5 files)
│   ├── data_structures.py
│   ├── relative_octave_logic.py
│   ├── score_builder.py
│   ├── transformations.py
│   ├── harmonic_*.py (2 files)
│   └── voice_documentation.py
│
├── templates/
│   └── CODEMPOSE_STUDY_TEMPLATES.py (consider moving here)
│
├── studies/ (17 study files)
├── cleanup/ (old files + main.py)
└── ...
```

### Core Library Dependencies:
```
project_template.py
  ├─→ lilypond_parser.py
  │    ├─→ lily_to_tiny.py
  │    │    ├─→ lily_token_parser.py
  │    │    │    └─→ lily_tokenizer.py
  │    │    ├─→ data_structures.py
  │    │    └─→ relative_octave_logic.py
  │    └─→ relative_octave_logic.py
  │
  ├─→ music_data.py
  ├─→ lily_converter.py
  └─→ (optional) harmonic_engine.py
       └─→ harmonic_analysis.py
```

All 13 core files are actively used and essential for the system to function.
