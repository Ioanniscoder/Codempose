# Root Directory Files Analysis

## 📊 CLASSIFICATION OF ALL ROOT `.py` FILES

### ✅ KEEP IN ROOT (3 files)

#### 1. `generate_study.py` ⭐
**Type**: User-facing script  
**Purpose**: Generate new study files from templates  
**Why in root**: Primary user interface - run with `python generate_study.py 21`  
**Dependencies**: Imports from `CODEMPOSE_STUDY_TEMPLATES.py`  
**Decision**: ✅ **MUST STAY IN ROOT**

---

#### 2. `CODEMPOSE_STUDY_TEMPLATES.py` 📚
**Type**: Template library (not active code)  
**Purpose**: Contains 6 study templates used by `generate_study.py`  
**Why in root**: Source of truth for templates, easier to edit/maintain  
**Contains**:
- `TEMPLATE_BLUEPRINT` (Blueprint Strings - 400 lines)
- `TEMPLATE_BASIC` (Single voice)
- `TEMPLATE_MULTI` (SATB)
- `TEMPLATE_HARMONIZED` (with harmonic engine)
- `TEMPLATE_ADVANCED` (complex features)
- `TEMPLATE_CUSTOM` (custom build_score_data)
- `create_study_file()` helper function

**Note**: This is **NOT active code** - it's a **template library**  
**Decision**: ✅ **KEEP IN ROOT** (companion to generate_study.py)  
**Alternative**: Could move to `outputs/TEMPLATES/` but that makes editing harder

---

#### 3. `fix_browser.sh` & `fix_devcontainer.sh` 🔧
**Type**: Shell scripts (not Python)  
**Purpose**: Environment fixes for dev container  
**Why in root**: System-level scripts, need to be easily accessible  
**Decision**: ✅ **KEEP IN ROOT** (as you suggested)

---

### 🔀 MOVE TO `src/` (16 files - Active Core Code)

#### Core Pipeline
1. **`project_template.py`** - Main pipeline (engrave, export, promote, run_pipeline_from_file)
2. **`lilypond_parser.py`** - Parse LilyPond to data structures
3. **`score_builder.py`** - Build scores (including Blueprint Strings!)
4. **`music_data.py`** - Data <-> Music21 conversion
5. **`lily_converter.py`** - Events to LilyPond notation

#### Composition Features
6. **`composition_shorthand.py`** - VOICE_ASSIGNMENTS DSL (V1 + V2, transpose, etc.)
7. **`transformations.py`** - Musical transformations (transpose, invert, retrograde)
8. **`harmonic_analysis.py`** - Structural tone analysis
9. **`harmonic_engine.py`** - Melody harmonization

#### Parser Components
10. **`lily_to_tiny.py`** - LilyPond to TinyNotation converter
11. **`lily_token_parser.py`** - Token-level parser
12. **`lily_tokenizer.py`** - Lexical tokenizer
13. **`data_structures.py`** - ParseResult, TokenInfo classes
14. **`relative_octave_logic.py`** - Relative octave resolution

#### Documentation/Helper
15. **`voice_documentation.py`** - Helper for documenting programmatic voices
16. **`CODEMPOSE_STUDY_TEMPLATES.py`** - See note above ⚠️

**Decision**: 🔀 **MOVE ALL TO `src/`**

---

### ❓ SPECIAL CASE: Template Library Location

**Question**: Where should `CODEMPOSE_STUDY_TEMPLATES.py` live?

**Option A**: Keep in root with `generate_study.py`
- ✅ Easy to find and edit
- ✅ Logically grouped with its consumer
- ❌ Adds one more file to root

**Option B**: Move to `outputs/TEMPLATES/`
- ✅ Already have a TEMPLATES directory
- ✅ Consistent with other templates there
- ❌ Harder to find/edit (buried in outputs/)
- ❌ `generate_study.py` would need path logic

**Option C**: Move to `src/templates/` (new subdirectory)
- ✅ Clean organization
- ✅ Part of codebase
- ❌ Mixes templates with active code
- ❌ One more directory level

**Recommendation**: **Option A** - Keep in root with `generate_study.py`  
It's a template library, not active execution code. Having it beside its consumer makes sense.

---

## 📂 PROPOSED FINAL STRUCTURE

```
/workspaces/Codempose/
├── generate_study.py                    ← User script (ONLY .py in root)
├── CODEMPOSE_STUDY_TEMPLATES.py         ← Template library (companion)
├── fix_browser.sh                       ← System script
├── fix_devcontainer.sh                  ← System script
│
├── outputs/                             ← Browser root, all generated files
│   ├── TEMPLATES/                       ← Output templates (not code)
│   ├── OLD/                             ← Archived outputs
│   └── DOCUMENTATION/                   ← Generated docs
│
├── studies/                             ← User composition files
│   ├── _study_path.py                   ← Import helper
│   ├── first.py, second.py, ...
│   └── OLD/                             ← Archived studies
│
├── src/                                 ← ALL ACTIVE CODE LIVES HERE
│   ├── project_template.py              ← Main pipeline
│   ├── lilypond_parser.py
│   ├── score_builder.py
│   ├── music_data.py
│   ├── lily_converter.py
│   ├── composition_shorthand.py
│   ├── transformations.py
│   ├── harmonic_analysis.py
│   ├── harmonic_engine.py
│   ├── lily_to_tiny.py
│   ├── lily_token_parser.py
│   ├── lily_tokenizer.py
│   ├── data_structures.py
│   ├── relative_octave_logic.py
│   └── voice_documentation.py
│
├── tests/                               ← All test files
├── DOCUMENTATION/                       ← Project documentation
├── cleanup/                             ← Old code/experiments
├── parser_project/                      ← Standalone parser project
└── scripts/                             ← Utility scripts
```

---

## 🎯 FINAL ROOT DIRECTORY CONTENTS

After migration, root will have:

### Files (5 total):
1. `generate_study.py` - User script
2. `CODEMPOSE_STUDY_TEMPLATES.py` - Template library
3. `fix_browser.sh` - System fix
4. `fix_devcontainer.sh` - System fix
5. `.gitignore` - Git config

### Directories (9 total):
1. `src/` - Active code
2. `studies/` - User compositions
3. `outputs/` - Generated files
4. `tests/` - Test suite
5. `DOCUMENTATION/` - Project docs
6. `cleanup/` - Archive
7. `parser_project/` - Standalone parser
8. `scripts/` - Utilities
9. `Gemini/` - Session logs
10. `.venv/`, `.git/`, `.devcontainer/`, etc. - Standard

**Result**: Clean, professional, organized! 🎵

---

## 💡 RECOMMENDATIONS

### 1. Template Library Decision
**Keep `CODEMPOSE_STUDY_TEMPLATES.py` in root** with `generate_study.py`

**Rationale**:
- It's a **template source**, not active execution code
- Users may want to edit templates directly
- Logically belongs with its only consumer (`generate_study.py`)
- Only adds 1 file to root (acceptable for companion to main script)

---

### 2. Alternative: outputs/TEMPLATES/
If you really want **ONLY** `generate_study.py` in root:

**Move to**: `outputs/TEMPLATES/CODEMPOSE_STUDY_TEMPLATES.py`

**Pros**:
- Absolutely minimal root directory
- Templates directory already exists

**Cons**:
- Harder to find when editing templates
- `generate_study.py` needs path logic:
  ```python
  sys.path.insert(0, str(Path(__file__).parent / 'outputs' / 'TEMPLATES'))
  from CODEMPOSE_STUDY_TEMPLATES import create_study_file
  ```
- Mixes source templates (input) with generated outputs

**My vote**: Keep in root. It's not "clutter" - it's the legitimate companion to `generate_study.py`.

---

### 3. outputs/TEMPLATES/ Contents
The `outputs/TEMPLATES/` directory should contain:
- **Output templates** (what gets generated)
- **Example files** (for users to browse)
- **NOT** source code or Python template libraries

Current contents are correct:
```
MUSIC21_API_TEMPLATES.py       # API reference (for users)
TONAL_HARMONY_TEMPLATES.py     # Harmony reference (for users)
study_template.py              # Example study (for users)
eleventh_example.py            # Example study (for users)
station4_music21_examples.py   # API examples (for users)
README.md                      # Documentation
```

These are **reference materials**, not code that runs. Perfect location!

---

## 🚀 IMPLEMENTATION PLAN

### Phase 1: Prepare Code Changes
1. Update `project_template.py` - Fix `PROJECT_ROOT` path logic
2. Update `studies/_study_path.py` - Add `src/` to sys.path
3. Update `generate_study.py` template - Use `from src.` imports
4. Update test files - Use `from src.` imports

### Phase 2: Move Files
```bash
# Move all 16 active code files to src/
mv project_template.py src/
mv lilypond_parser.py src/
mv score_builder.py src/
mv music_data.py src/
mv lily_converter.py src/
mv composition_shorthand.py src/
mv transformations.py src/
mv harmonic_analysis.py src/
mv harmonic_engine.py src/
mv lily_to_tiny.py src/
mv lily_token_parser.py src/
mv lily_tokenizer.py src/
mv data_structures.py src/
mv relative_octave_logic.py src/
mv voice_documentation.py src/

# Keep in root:
# - generate_study.py
# - CODEMPOSE_STUDY_TEMPLATES.py
# - fix_browser.sh
# - fix_devcontainer.sh
```

### Phase 3: Verify
1. Generate new study: `python generate_study.py 99 "Test"`
2. Run from root: `python studies/ninetyninth.py`
3. Run from studies/: `cd studies && python ninetyninth.py`
4. Check outputs: `ls outputs/ninetyninth.*`
5. Run tests: `python -m pytest tests/`

---

## 📋 SUMMARY

**Root directory will contain:**
- ✅ `generate_study.py` - Primary user script
- ✅ `CODEMPOSE_STUDY_TEMPLATES.py` - Template library (companion)
- ✅ `fix_browser.sh` & `fix_devcontainer.sh` - System scripts
- ✅ Standard directories (src/, studies/, outputs/, tests/, etc.)

**Total Python files in root**: **2** (generate_study.py + templates)  
**Total shell scripts in root**: **2** (fix_*.sh)

This gives you a **clean, professional structure** while keeping related files together! 🎵

Ready to proceed with the migration? Just say the word!
