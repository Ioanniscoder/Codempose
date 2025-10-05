# Codempose Archive Index

## Available Tarballs

### 1. Complete Archive (RECOMMENDED) ⭐
**Filename**: `codempose_complete_20251005_000154.tar.gz`  
**Size**: 54 KB  
**Created**: October 5, 2025, 00:01 UTC

**Contents**:
- ✅ All Python files (22 files)
  - Core pipeline modules
  - Study file templates
  - Test suite
  - Demo files
- ✅ Key documentation (10 files)
  - Promotion system guides
  - Quick reference
  - Fix summaries
  - Documentation index
- ✅ Configuration files
  - requirements.txt

**Use case**: Full project distribution, deployment, or comprehensive backup

**Extract**:
```bash
tar -xzf codempose_complete_20251005_000154.tar.gz
```

---

### 2. Python Files Only
**Filename**: `codempose_python_files_20251005_000108.tar.gz`  
**Size**: 34 KB  
**Created**: October 5, 2025, 00:01 UTC

**Contents**:
- ✅ All Python files (22 files)
  - Core pipeline modules
  - Study file templates
  - Test suite
  - Demo files
- ❌ No documentation
- ❌ No configuration files

**Use case**: Code-only backup, importing into existing project

**Extract**:
```bash
tar -xzf codempose_python_files_20251005_000108.tar.gz
```

---

### 3. Legacy Archive (Historical)
**Filename**: `codempose_current_working_20251004_102533.tar.gz`  
**Size**: 293 KB  
**Created**: October 4, 2025, 10:25 UTC

**Contents**: Earlier version of the entire workspace

**Use case**: Historical reference, rollback if needed

**Note**: This archive predates the promotion system update and staff order fixes.

---

## Recommendation

For most use cases, use **codempose_complete_20251005_000154.tar.gz** as it includes:

1. All necessary Python code
2. Comprehensive documentation
3. Configuration files
4. Latest bug fixes (staff order, octave)
5. Updated promotion system (dual-format workflow)

## Version Information

All current archives (Python files and Complete) contain:

- **Promotion System**: v2.0 (dual-format workflow)
- **Staff Order Fix**: ✅ Applied (reverse=True)
- **Octave Fix**: ✅ Applied (e' notation)
- **Documentation**: Complete suite (10+ guides)

## Verification

To verify archive contents:

```bash
# List files
tar -tzf codempose_complete_20251005_000154.tar.gz

# Count files
tar -tzf codempose_complete_20251005_000154.tar.gz | wc -l

# Extract to test directory
mkdir test_extract
cd test_extract
tar -xzf ../codempose_complete_20251005_000154.tar.gz
```

## Quick Start After Extraction

```bash
# 1. Extract
tar -xzf codempose_complete_20251005_000154.tar.gz

# 2. Install dependencies
pip install -r requirements.txt

# 3. Read documentation
cat DOCUMENTATION_INDEX.md

# 4. Run test
python3 first.py

# 5. Check results
ls outputs/
```

## Archive Locations

All tarballs are stored in:
```
/workspaces/Codempose/
```

## Creation Commands

### Complete Archive
```bash
tar -czf codempose_complete_$(date +%Y%m%d_%H%M%S).tar.gz \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='codempose_*.tar.gz' \
  --exclude='.venv' \
  --exclude='.git' \
  *.py \
  PROMOTION_*.md \
  FIX_COMPLETE.md \
  DOCUMENTATION_INDEX.md \
  TARBALL_CONTENTS.md \
  README_DOCUMENTATION.md \
  FIRST_PY_DOCUMENTATION.md \
  requirements.txt
```

### Python Files Only
```bash
tar -czf codempose_python_files_$(date +%Y%m%d_%H%M%S).tar.gz \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.bak' \
  --exclude='.venv' \
  *.py
```

## File Manifest

### Python Files (22)
1. project_template.py
2. music_data.py
3. lilypond_parser.py
4. lily_to_tiny.py
5. lily_tokenizer.py
6. lily_token_parser.py
7. relative_octave_logic.py
8. main.py
9. first.py ⭐
10. second.py
11. third.py
12. fourth.py
13. fifth.py
14. test_promotion.py
15. test_promotion_full.py
16. test_lily_to_tiny_debug.py
17. test_parser_debug.py
18. test_music21_tiny.py
19. test_new_tiny.py
20. test_tiny_formats.py
21. demo_note_tracking.py
22. data_structures.py

### Documentation (10 - in Complete archive only)
1. DOCUMENTATION_INDEX.md
2. README_DOCUMENTATION.md
3. FIRST_PY_DOCUMENTATION.md
4. TARBALL_CONTENTS.md
5. PROMOTION_WORKFLOW.md ⭐
6. PROMOTION_UPDATE.md
7. PROMOTION_VERIFICATION.md
8. PROMOTION_QUICK_REFERENCE.md
9. PROMOTION_SYSTEM.md
10. FIX_COMPLETE.md

### Configuration (1 - in Complete archive only)
1. requirements.txt

---

**Total Files in Complete Archive**: 33  
**Total Size (compressed)**: 54 KB  
**Recommended for**: Distribution, deployment, backup

---

**Created**: October 5, 2025  
**Project**: Codempose  
**Branch**: experimental/project_template_sanitizer_fix  
**Status**: Production-ready ✅
