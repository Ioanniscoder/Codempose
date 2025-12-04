# Code Organization Analysis: Moving to src/

## 🎯 PROPOSED STRUCTURE

```
/workspaces/Codempose/
├── generate_study.py          ← ONLY file in root
├── outputs/                   ← Output files (browser root)
├── studies/                   ← Study files (user compositions)
│   ├── _study_path.py        ← Import helper (needs update)
│   ├── first.py
│   ├── second.py
│   └── OLD/                  ← Moved old studies here
├── src/                       ← ALL core modules (NEW LOCATION)
│   ├── project_template.py
│   ├── lilypond_parser.py
│   ├── music_data.py
│   ├── score_builder.py
│   ├── transformations.py
│   ├── composition_shorthand.py
│   ├── harmonic_analysis.py
│   ├── harmonic_engine.py
│   ├── lily_converter.py
│   ├── data_structures.py
│   ├── voice_documentation.py
│   └── ... (all other core modules)
├── tests/                     ← Test files
├── DOCUMENTATION/             ← All .md files
└── cleanup/                   ← Old code/tools
```

---

## 🔍 IMPACT ANALYSIS

### ✅ What Will Still Work

#### 1. **project_template.py** - Uses Absolute Paths ✅
```python
PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
```

**Current** (in root):
- `__file__` = `/workspaces/Codempose/project_template.py`
- `PROJECT_ROOT` = `/workspaces/Codempose`
- `OUTPUTS_DIR` = `/workspaces/Codempose/outputs` ✅

**After moving to src/**:
- `__file__` = `/workspaces/Codempose/src/project_template.py`
- `.parent` = `/workspaces/Codempose/src` ❌
- `OUTPUTS_DIR` = `/workspaces/Codempose/src/outputs` ❌ WRONG!

**PROBLEM**: `PROJECT_ROOT` would point to `src/` instead of repo root!

---

#### 2. **_study_path.py** - Needs Update ⚠️
```python
study_dir = Path(__file__).parent.resolve()  # /workspaces/Codempose/studies
root_dir = study_dir.parent                   # /workspaces/Codempose
sys.path.insert(0, str(root_dir))            # Adds root to path
```

**Current**: Adds `/workspaces/Codempose` to `sys.path`
- Imports work: `from project_template import ...` ✅

**After moving core to src/**: Still adds `/workspaces/Codempose` to `sys.path`
- Imports fail: `from project_template import ...` ❌
- Needs to add `/workspaces/Codempose/src` instead

---

#### 3. **Study File Imports** - Will Break ❌
```python
import _study_path  # Adds root to sys.path
from project_template import run_pipeline_from_file  # ❌ Not in root anymore!
from lilypond_parser import parse_lilypond_to_data   # ❌ Not in root anymore!
from score_builder import build_score_from_blueprint # ❌ Not in root anymore!
```

**Problem**: All study files import from root, not from `src/`

---

#### 4. **generate_study.py** - Needs Template Update ⚠️

Current template has:
```python
from lilypond_parser import parse_lilypond_to_data
from score_builder import build_score_from_blueprint
from project_template import run_pipeline_from_file
```

**After move**: These need to become:
```python
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file
```

OR `sys.path` needs to include `src/`

---

## 🔧 REQUIRED CHANGES

### 1. Update project_template.py Path Logic

**Current**:
```python
PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
```

**Fixed** (works from src/):
```python
# Get actual project root (parent of src/)
if Path(__file__).parent.name == 'src':
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
else:
    PROJECT_ROOT = Path(__file__).parent.resolve()

OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
```

**Better approach**:
```python
# Always go up from src/ to root
PROJECT_ROOT = Path(__file__).parent.parent.resolve()  # src/ -> root
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'
```

---

### 2. Update _study_path.py

**Current**:
```python
study_dir = Path(__file__).parent.resolve()  # studies/
root_dir = study_dir.parent                   # root
sys.path.insert(0, str(root_dir))            # Add root
```

**Fixed** (add src/ to path):
```python
study_dir = Path(__file__).parent.resolve()    # studies/
root_dir = study_dir.parent                     # root
src_dir = root_dir / 'src'                      # src/

# Add src/ to sys.path for imports
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Also add root for backward compatibility (tests, etc.)
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
```

---

### 3. Update generate_study.py Template

**Option A**: Use `src.` prefix (explicit):
```python
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file
```

**Option B**: Add src/ to sys.path in template (implicit):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from lilypond_parser import parse_lilypond_to_data
from score_builder import build_score_from_blueprint
from project_template import run_pipeline_from_file
```

**Recommended**: Option A (explicit is better than implicit)

---

### 4. Update Tests

Tests currently do:
```python
from project_template import ...
from lilypond_parser import ...
```

Need to update to:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from project_template import ...
from lilypond_parser import ...
```

OR use `src.` prefix:
```python
from src.project_template import ...
from src.lilypond_parser import ...
```

---

## 📊 FILES THAT NEED CHANGES

### Critical (Must Update)
1. ✅ `src/project_template.py` - Fix `PROJECT_ROOT` calculation
2. ✅ `studies/_study_path.py` - Add `src/` to `sys.path`
3. ✅ `generate_study.py` - Update template imports

### Secondary (Should Update)
4. ⚠️ All test files in `tests/` - Update imports
5. ⚠️ Tools in `cleanup/tools/` - Update imports (if used)

### Generated (Will be fine)
- Study files in `studies/` - Will work via updated `_study_path.py`

---

## ✅ RECOMMENDED APPROACH

### Phase 1: Prepare the Changes (Don't Move Yet)

1. **Update project_template.py**:
```python
# Change this line:
PROJECT_ROOT = Path(__file__).parent.resolve()

# To this (works from both root and src/):
if Path(__file__).parent.name == 'src':
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
else:
    PROJECT_ROOT = Path(__file__).parent.resolve()
```

2. **Update _study_path.py**:
```python
# Add after root_dir = study_dir.parent
src_dir = root_dir / 'src'

# Add src/ to path first (higher priority)
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Keep root in path for backward compatibility
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
```

3. **Update generate_study.py template**:
```python
# Change imports in STUDY_TEMPLATE to use src.:
from src.lilypond_parser import parse_lilypond_to_data
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file
```

---

### Phase 2: Move the Files

```bash
# Create src directory if it doesn't exist
mkdir -p src

# Move all core modules to src/
mv project_template.py src/
mv lilypond_parser.py src/
mv music_data.py src/
mv score_builder.py src/
mv transformations.py src/
mv composition_shorthand.py src/
mv harmonic_analysis.py src/
mv harmonic_engine.py src/
mv lily_converter.py src/
mv lily_token_parser.py src/
mv lily_tokenizer.py src/
mv lilypond_parser.py src/
mv data_structures.py src/
mv relative_octave_logic.py src/
mv voice_documentation.py src/
mv lily_to_tiny.py src/

# Keep in root:
# - generate_study.py
# - outputs/
# - studies/
# - tests/
# - DOCUMENTATION/
```

---

### Phase 3: Verify Everything Works

```bash
# Test 1: Generate new study
cd /workspaces/Codempose
python generate_study.py 99 "Test After Move"

# Test 2: Run study from root
python studies/ninetyninth.py

# Test 3: Run study from studies/
cd studies
python ninetyninth.py

# Test 4: Check outputs location
ls -la /workspaces/Codempose/outputs/ninetyninth.*

# Test 5: Run tests
cd /workspaces/Codempose
python -m pytest tests/
```

---

## ⚠️ ALTERNATIVE: Keep Current Structure

**Pros of NOT moving to src/**:
- ✅ No code changes needed
- ✅ All imports work as-is
- ✅ Tests work as-is
- ✅ Less risk of breaking things

**Cons**:
- ❌ Root directory cluttered with ~15 .py files
- ❌ Less clear separation of concerns

**Recommendation**: If root clutter bothers you, move to `src/`. Otherwise, current structure is fine.

---

## 🎯 DECISION MATRIX

| Factor | Keep in Root | Move to src/ |
|--------|--------------|--------------|
| **Simplicity** | ✅ No changes | ❌ Multiple updates |
| **Organization** | ❌ Cluttered | ✅ Clean |
| **Risk** | ✅ Zero | ⚠️ Medium |
| **Maintainability** | ⚠️ Okay | ✅ Better |
| **Standard Practice** | ⚠️ Mixed | ✅ Common |

---

## 💡 MY RECOMMENDATION

Given your requirement to **"only have generate_study.py in the root"**, here's what I suggest:

### Option A: Full src/ Migration (Clean, Standard) ⭐ RECOMMENDED

1. Move all core modules to `src/`
2. Update 3 critical files (project_template.py, _study_path.py, generate_study.py)
3. Update tests to use `src.` imports
4. Result: Clean root with only `generate_study.py`

**Effort**: Medium (2-3 hours including testing)  
**Risk**: Low-Medium (well-defined changes)  
**Benefit**: Professional structure, clear organization

---

### Option B: Hybrid (Pragmatic)

1. Move most core modules to `src/`
2. Keep `project_template.py` in root (most imported file)
3. Update `_study_path.py` to add both root and `src/` to path
4. Result: Root has `generate_study.py` + `project_template.py`

**Effort**: Low (1 hour)  
**Risk**: Low  
**Benefit**: Cleaner root, minimal changes

---

### Option C: Current Structure (No Change)

1. Don't move anything
2. Root stays as-is
3. Result: Root has ~15 .py files + `generate_study.py`

**Effort**: Zero  
**Risk**: Zero  
**Benefit**: Everything works perfectly

---

## 🚀 READY TO PROCEED?

**Question**: Which option do you prefer?

- **Option A**: Full migration to `src/` (cleanest, most work)
- **Option B**: Hybrid approach (good balance)
- **Option C**: Keep current structure (easiest)

I'm ready to implement whichever you choose! Just say the word. 🎵
