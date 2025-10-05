# Codempose Python Files Archive

**Created**: October 5, 2025  
**Archive**: codempose_python_files_TIMESTAMP.tar.gz

## Contents

This archive contains all active Python files from the Codempose project.

### Core Pipeline Files

1. **project_template.py** - Central pipeline orchestrator
   - `run_pipeline_from_file()` - Main entry point
   - `engrave_with_abjad()` - LilyPond engraving
   - `promote_lilypond_to_tinynotation()` - Format conversion & toggle

2. **music_data.py** - Data structure conversions
   - `extract_data_from_part()` - music21.Part → score_data
   - `data_to_part()` - score_data → music21.Part

3. **lilypond_parser.py** - LilyPond → score_data parser
   - `parse_lilypond_to_data()` - Main parser function
   - Metadata extraction (time, key, tempo)

4. **lily_to_tiny.py** - LilyPond → TinyNotation converter
   - `lily_to_tiny_notation()` - Conversion function
   - Metadata header generation

5. **lily_tokenizer.py** - LilyPond lexical analysis
   - Token extraction from LilyPond source

6. **lily_token_parser.py** - LilyPond token parsing
   - Token → musical elements conversion

7. **relative_octave_logic.py** - Octave calculation
   - `\relative` notation parser
   - Octave inference logic

### Study Files (Templates)

1. **first.py** - Two-stave composition with dual formats
   - `build_score_data()` function
   - SOURCE_MELODY_LILY (LilyPond format)
   - SOURCE_MELODY_TINY (TinyNotation format)
   - MELODY_SNIPPETS and HARMONY_SNIPPETS collections
   - Music21 transformations (transpose, chordify, etc.)

2. **second.py** - Study file template
3. **third.py** - Study file template
4. **fourth.py** - Study file template
5. **fifth.py** - Study file template

### Test Files

1. **test_promotion.py** - Promotion system tests
2. **test_promotion_full.py** - Comprehensive promotion tests
3. **test_lily_to_tiny_debug.py** - Conversion debugging
4. **test_parser_debug.py** - Parser debugging
5. **test_music21_tiny.py** - Music21 integration tests
6. **test_new_tiny.py** - TinyNotation tests
7. **test_tiny_formats.py** - Format testing

### Demo Files

1. **demo_note_tracking.py** - Note tracking demonstration
2. **data_structures.py** - Data structure examples

## Recent Updates (October 4-5, 2025)

### Promotion System v2.0 - Dual-Format Workflow
- ✅ Both LilyPond and TinyNotation formats coexist from the start
- ✅ PROMOTE_TO_TINYNOTATION toggle controls dominance
- ✅ Automatic backups to outputs/ directory
- ✅ Modified files written to root and outputs/

### Staff Order & Octave Fixes
- ✅ Fixed staff ordering (reverse=True in sorted())
- ✅ Fixed melody octave (e' instead of e)
- ✅ Minimal code changes (2 lines total)

## Key Features

### Pipeline Priority Order
1. `build_score_data()` function (highest)
2. `SOURCE_MELODY_TINY` variable (if PROMOTE_TO_TINYNOTATION = True)
3. `SOURCE_MELODY_LILY` variable (if PROMOTE_TO_TINYNOTATION = False)
4. `build_part()` function (lowest)

### File Management
- **Root**: Working versions of study files
- **outputs/**: Generated files (.ly, .pdf, .midi) + inspection copies
- **Backups**: outputs/filename.TIMESTAMP.bak (when promoted)

### Dual-Format Support
- **LilyPond**: Verbose, explicit notation
- **TinyNotation**: Compact, metadata header format
- **Visual Correlation**: Both formats in same file for learning

## Usage

### Extract Archive
```bash
tar -xzf codempose_python_files_TIMESTAMP.tar.gz
```

### Run a Study File
```bash
python3 first.py
```

### Check Outputs
```bash
ls -lh outputs/
```

### View Generated Score
```bash
$BROWSER outputs/first.pdf
```

## Dependencies

Required Python packages:
- music21
- abjad
- (see requirements.txt for full list)

Required external tools:
- LilyPond (for PDF/MIDI generation)

## Documentation

For complete documentation, see:
- **PROMOTION_WORKFLOW.md** - Dual-format system guide
- **PROMOTION_QUICK_REFERENCE.md** - Command cheat sheet
- **FIX_COMPLETE.md** - Staff order & octave fixes
- **DOCUMENTATION_INDEX.md** - Complete doc index

## Project Info

**Repository**: Ioanniscoder/Codempose  
**Branch**: experimental/project_template_sanitizer_fix  
**Python Version**: 3.11+  
**License**: (See project repository)

## Contact

For issues or questions, refer to the project repository documentation.
