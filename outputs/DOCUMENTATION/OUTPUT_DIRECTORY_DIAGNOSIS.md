# Output Directory Issue - Diagnosis Report

## 🔍 PROBLEM IDENTIFIED

**Symptom**: Outputs are being generated in `studies/outputs/` instead of root `outputs/`

**Root Cause**: The `Path('outputs')` in `project_template.py` is **relative to the current working directory (CWD)**, not to the repository root.

---

## 📊 EVIDENCE

### Directory Structure Found
```
/workspaces/Codempose/
├── outputs/               ← INTENDED (root level)
│   ├── eighth.pdf
│   ├── eleventh.pdf
│   ├── fifteenth.pdf
│   └── ... (older outputs)
│
└── studies/
    ├── outputs/           ← PROBLEM (nested in studies/)
    │   ├── eighteenth.pdf
    │   ├── first.pdf
    │   ├── seventeenth.pdf
    │   └── ... (newer outputs)
    │
    ├── first.py
    ├── eighteenth.py
    └── _study_path.py
```

### Testing Results

**When running from root**:
```bash
cd /workspaces/Codempose
python studies/first.py
# CWD: /workspaces/Codempose
# outputs → /workspaces/Codempose/outputs  ✅ CORRECT
```

**When running from studies directory**:
```bash
cd /workspaces/Codempose/studies
python first.py
# CWD: /workspaces/Codempose/studies
# outputs → /workspaces/Codempose/studies/outputs  ❌ WRONG
```

---

## 🔧 ROOT CAUSE ANALYSIS

### Current Code (project_template.py, line 272)
```python
def engrave_with_abjad(score_data: dict, output_basename: str, source_file: str = None):
    print(f"🎶 Engraving '{score_data.get('metadata', {}).get('title', '')}'...")
    out_dir = Path('outputs')  # ← RELATIVE PATH! Depends on CWD
    out_dir.mkdir(parents=True, exist_ok=True)
    ly_path = out_dir / f"{output_basename}.ly"
    # ...
```

**Problem**: `Path('outputs')` creates a path **relative to wherever Python was invoked from**.

### How _study_path.py Works

The `_study_path.py` module correctly adds the root to `sys.path` for imports:
```python
study_dir = Path(__file__).parent.resolve()  # /workspaces/Codempose/studies
root_dir = study_dir.parent                   # /workspaces/Codempose
sys.path.insert(0, str(root_dir))             # Imports work from root
```

**BUT**: This only fixes imports, not the current working directory!

When you run `cd studies && python first.py`:
- ✅ Imports work (because `sys.path` includes root)
- ❌ File operations use CWD = `/workspaces/Codempose/studies`
- ❌ `Path('outputs')` → `/workspaces/Codempose/studies/outputs`

---

## 🎯 AFFECTED LOCATIONS

Searching for `Path('outputs')` in the codebase:

### project_template.py (PRIMARY ISSUE)
1. **Line 272**: `engrave_with_abjad()` - Main engraving function
2. **Line 743**: `export_to_musicxml()` - MusicXML export
3. **Line 837**: `export_midi_explicit()` - MIDI export
4. **Line 1172**: `promote_to_tinynotation()` - TinyNotation promotion
5. **Line 1328**: `run_pipeline_from_file()` - Pipeline orchestrator

### Tests (ALSO AFFECTED)
- `tests/test_midi_generation.py`
- `tests/test_only_engrave.py`
- `tests/test_similarity_threshold.py`
- `tests/test_first.py`
- `tests/test_verbatim_route.py`

### Cleanup/Tools (ALSO AFFECTED)
- `cleanup/tools/render_snippets.py`
- `cleanup/test_lilypond_multi_voice.py`

**Total**: ~15 locations that use relative `Path('outputs')`

---

## 💡 SOLUTION OPTIONS

### Option 1: Use Absolute Path Based on Module Location (RECOMMENDED)
```python
# At top of project_template.py
PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'

def engrave_with_abjad(...):
    out_dir = OUTPUTS_DIR  # Always points to /workspaces/Codempose/outputs
    out_dir.mkdir(parents=True, exist_ok=True)
    # ...
```

**Pros**:
- ✅ Works regardless of CWD
- ✅ Single source of truth
- ✅ No need to change how studies are run
- ✅ Consistent behavior

**Cons**:
- Requires updating ~15 locations in project_template.py

---

### Option 2: Change Working Directory in _study_path.py (NOT RECOMMENDED)
```python
# In _study_path.py
import os
os.chdir(root_dir)  # Force CWD to root
```

**Pros**:
- Only one file to change

**Cons**:
- ❌ Unexpected behavior (files are relative to root, not script location)
- ❌ Breaks if study files write other output files
- ❌ Can cause confusion for users
- ❌ May break tests or other tools

---

### Option 3: Document "Always Run from Root" (NOT RECOMMENDED)
Just document that users must run:
```bash
cd /workspaces/Codempose
python studies/first.py
```

**Pros**:
- No code changes

**Cons**:
- ❌ User-unfriendly
- ❌ Breaks intuitive workflow (`cd studies && python first.py`)
- ❌ Will be forgotten and cause issues
- ❌ Doesn't fix tests or tools

---

## ✅ RECOMMENDED SOLUTION: Option 1

### Implementation Plan

1. **Add constants to project_template.py**:
```python
# Near the top of project_template.py (after imports)
from pathlib import Path

# Establish absolute paths based on this module's location
PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
```

2. **Replace all `Path('outputs')` with `OUTPUTS_DIR`**:
   - Line 272: `engrave_with_abjad()`
   - Line 743: `export_to_musicxml()`
   - Line 837: `export_midi_explicit()`
   - Line 1172: `promote_to_tinynotation()`
   - Any other occurrences

3. **Update tests to use absolute paths** (or import `OUTPUTS_DIR` from project_template)

4. **Consolidate outputs**:
   - Move files from `studies/outputs/` to root `outputs/`
   - Remove `studies/outputs/` directory

---

## 🧪 VERIFICATION STEPS

After implementing the fix:

1. **Test from root**:
```bash
cd /workspaces/Codempose
python studies/first.py
# Should create: /workspaces/Codempose/outputs/first.pdf ✅
```

2. **Test from studies directory**:
```bash
cd /workspaces/Codempose/studies
python first.py
# Should STILL create: /workspaces/Codempose/outputs/first.pdf ✅
```

3. **Test from anywhere**:
```bash
cd /tmp
python /workspaces/Codempose/studies/first.py
# Should create: /workspaces/Codempose/outputs/first.pdf ✅
```

4. **Verify outputs location**:
```bash
ls -la /workspaces/Codempose/outputs/
# Should contain all generated files

ls -la /workspaces/Codempose/studies/outputs/
# Should NOT exist (or be empty)
```

---

## 📝 MIGRATION STEPS

### Step 1: Backup Current Outputs
```bash
# In case we need to rollback
cp -r /workspaces/Codempose/outputs /workspaces/Codempose/outputs.backup
cp -r /workspaces/Codempose/studies/outputs /workspaces/Codempose/studies/outputs.backup
```

### Step 2: Implement Code Changes
- Add `PROJECT_ROOT` and `OUTPUTS_DIR` constants
- Replace all `Path('outputs')` with `OUTPUTS_DIR`
- Update tests if needed

### Step 3: Consolidate Outputs
```bash
# Move newer outputs from studies/outputs to root outputs
cp -n /workspaces/Codempose/studies/outputs/* /workspaces/Codempose/outputs/

# Remove the nested outputs directory
rm -rf /workspaces/Codempose/studies/outputs
```

### Step 4: Test All Workflows
- Generate new study
- Run existing studies
- Run tests
- Verify all outputs go to correct location

---

## 🎯 IMPACT ASSESSMENT

### Breaking Changes
- ❌ None! This is a bug fix that makes behavior more consistent

### User Impact
- ✅ **Positive**: Can now run studies from any directory
- ✅ **Positive**: All outputs in one predictable location
- ✅ **Positive**: No more confusion about where files went

### System Impact
- Files affected: `project_template.py` (primary), tests (secondary)
- Lines changed: ~10-15 replacements
- Risk level: **Low** (simple path change, easy to verify)

---

## 📌 SUMMARY

| Aspect | Details |
|--------|---------|
| **Problem** | Outputs created in wrong directory based on CWD |
| **Root Cause** | Relative path `Path('outputs')` depends on CWD |
| **Solution** | Use absolute path based on module location |
| **Files to Change** | Primarily `project_template.py` (~10-15 lines) |
| **Risk** | Low (simple, testable change) |
| **User Benefit** | Can run studies from anywhere, consistent output location |

---

## 🚀 READY TO PROCEED?

The diagnosis is complete. The fix is straightforward and low-risk.

**Recommendation**: Implement Option 1 (absolute paths) immediately to prevent further fragmentation of output files.

**Next Action**: Update `project_template.py` to use absolute paths for outputs directory.
