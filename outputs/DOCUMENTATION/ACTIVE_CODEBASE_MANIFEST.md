# Codempose Active Codebase Manifest

**Archive:** `codempose_active_codebase_oct16.tar.gz`  
**Created:** October 16, 2025  
**Size:** 19 MB  
**Total Files:** 185  

## 📦 Contents

### ✅ Core Library (16 Python files in root)

**Pipeline Core (3 files):**
1. `project_template.py` - Main pipeline orchestrator
2. `lilypond_parser.py` - LilyPond syntax parser
3. `music_data.py` - Canonical ↔ music21 conversions

**Parser Components (5 files):**
4. `lily_to_tiny.py` - LilyPond → TinyNotation converter
5. `lily_token_parser.py` - Token parsing logic
6. `lily_tokenizer.py` - LilyPond tokenization
7. `data_structures.py` - Parser data structures
8. `relative_octave_logic.py` - Relative octave calculation

**Utilities (3 files):**
9. `lily_converter.py` - Canonical → LilyPond conversion
10. `score_builder.py` - Blueprint-based composition
11. `transformations.py` - Music21 transformations

**Advanced Features (4 files):**
12. `composition_shorthand.py` - Declarative composition language
13. `harmonic_analysis.py` - Structural tone analysis (Priority 3B)
14. `harmonic_engine.py` - Auto-harmonization (Priority 3B)
15. `voice_documentation.py` - Voice documentation helper

**Templates (1 file):**
16. `CODEMPOSE_STUDY_TEMPLATES.py` - Study file templates

### 📚 Studies Directory (17 example files)

**Study Files:**
- `studies/first.py` through `studies/seventeenth.py`
- Each includes `import _study_path` for automatic path resolution
- Can be run from root: `python studies/first.py`
- Can be run from studies/: `cd studies && python first.py`

**Study Utilities:**
- `studies/_study_path.py` - Automatic path setup
- `studies/__init__.py` - Package initialization
- `studies/README.md` - Documentation

### 🧪 Tests Directory

**Test Files:**
- Complete test suite for all core modules
- Parser tests, data structure tests, integration tests

### 📁 Parser Project

**Standalone Parser:**
- `parser_project/` - Independent parser implementation
- Tests and documentation

### 📄 Documentation

**In Archive:**
- `outputs/DOCUMENTATION/` - All markdown documentation
- `outputs/TEMPLATES/` - Template examples
- Study-specific README files

### 🔧 Utilities

**Shell Scripts:**
- `fix_browser.sh` - Browser fix utility
- `fix_devcontainer.sh` - Dev container setup

## 🚫 Excluded from Archive

**Not Included (cleanup):**
- `backup/` - Old tarballs and backups
- `cleanup/` - Deprecated files (including old main.py)
- `Gemini/` - AI conversation logs
- `__pycache__/` - Python cache
- `.git/` - Git repository
- `*.bak` - Backup files

## ✅ This IS the Active Codebase

All files in this archive are:
- ✅ Currently used by the system
- ✅ Actively maintained
- ✅ Part of production code
- ✅ Required for functionality

No deprecated, test, or temporary files included.

## 🎯 System Capabilities

This archive contains a complete, working music composition system with:

1. **LilyPond Parser** - Full notation support
2. **Canonical Format** - Internal representation layer
3. **Export Pipeline** - PDF (LilyPond), MIDI, MusicXML
4. **Multi-Voice Support** - Up to 4 simultaneous voices
5. **Harmonic Intelligence** - Auto-harmonization and analysis
6. **Advanced Features** - Transformations, shorthand notation
7. **17 Working Examples** - Complete study file collection

## 📊 File Breakdown

| Category | Count |
|----------|-------|
| Core library modules | 16 |
| Study files | 17 |
| Test files | ~23 |
| Documentation files | ~40 |
| Generated outputs | ~68 |
| Utilities | ~20 |
| **TOTAL** | **~185** |

## 🚀 Quick Start

```bash
# Extract archive
tar -xzf codempose_active_codebase_oct16.tar.gz
cd Codempose

# Run a study
python studies/first.py

# Or from studies directory
cd studies
python first.py

# Advanced examples
python studies/fifteenth.py    # Harmonic analysis
python studies/sixteenth.py    # Basic harmonization
python studies/seventeenth.py  # Advanced harmonization
```

## 📝 Notes

- All 16 root Python files are active and essential
- Study files isolated in `studies/` directory
- Automatic path resolution via `_study_path.py`
- Zero deprecated files included
- Clean, production-ready codebase

---

**Archive Status:** ✅ VERIFIED - Active Codebase Only  
**Date:** October 16, 2025  
**Maintainer:** Codempose Project
