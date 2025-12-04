# How to Work with AI Assistants on Complex Projects

**Date:** October 19, 2025  
**Written after:** Difficult session with template improvements  
**Author's frustration:** "it is SO HARD to let you KEEP improvements. Before I know it, they are gone."

---

## The Core Problem

AI assistants like me have a **fundamental limitation**: **We don't have persistent memory across sessions.**

Every time you start a new conversation:
- ✅ We can read files in the workspace
- ✅ We can see conversation history in the current session
- ❌ **We don't remember what happened yesterday**
- ❌ **We don't know what you tried before**
- ❌ **We don't understand your project's history**

This leads to:
- **Regression**: Undoing improvements that were already made
- **Repetition**: Suggesting the same failed approaches
- **Confusion**: Not understanding why something exists
- **Frustration**: "I already told you this!"

---

## What Doesn't Work (You Already Tried These)

### ❌ 1. Requirements Documents
**Problem:** AI reads them but doesn't internalize the *why* behind decisions.

**Example from this project:**
```
REQUIREMENTS.md said: "Keep creative examples from second.py"
→ AI removed them anyway to "simplify"
```

### ❌ 2. Reference Files  
**Problem:** AI doesn't know which reference to prioritize or when to use which pattern.

**Example from this project:**
```
IMPROVED_STUDY_TEMPLATE.py existed
→ AI tried to "improve" it again, breaking it
```

### ❌ 3. Manifests
**Problem:** AI reads them as documentation, not as binding constraints.

**Example from this project:**
```
MANIFEST.txt: "DO NOT modify src/ code"
→ AI suggested modifying src/lilypond_engraver.py
```

### ❌ 4. Detailed Documentation
**Problem:** The more documentation exists, the more AI gets confused about what's current.

---

## The "Scattered Edits" Problem

**User observation:** *"you don't always use local edits. It used to be worse, but if edits are all over the place, it is a recipe for disaster, and it tells that the code is not centralized."*

### What Happens:
AI makes changes to:
- `generate_study.py` (main file)
- `IMPROVED_STUDY_TEMPLATE.py` (reference copy)
- `src/lib/generate_study.py` (another copy)
- `studies/generate_study.py` (yet another copy)
- `outputs/TEMPLATES/generate_study.py` (duplicate)
- `CODEMPOSE_STUDY_TEMPLATES.py` (all templates in one file)

**Result:** 6 different versions, all slightly out of sync. Which is correct? Nobody knows.

### The Root Cause:
**Code duplication** - The same logic exists in multiple places.

### AI Makes It Worse:
When asked "update the template," AI might:
- Search and find 6 files
- Update all 6 (inconsistently)
- Update only some (leaving drift)
- Update the wrong one
- Miss the canonical version

### The Fix:

#### 1. **ONE CANONICAL VERSION**
```bash
# Delete duplicates:
rm src/lib/generate_study.py
rm studies/generate_study.py
rm outputs/TEMPLATES/generate_study.py

# Keep only:
generate_study.py  # ← THE SOURCE OF TRUTH
```

#### 2. **MARK COPIES AS DERIVED**
If you need copies (for archival), mark them:
```bash
ARCHIVE/2025-10-19_generate_study.py.SNAPSHOT
REFERENCE/generate_study.py.READONLY
```

#### 3. **CONSTRAIN AI TO LOCAL EDITS**
In `.ai-lock`, add:
```
# EDITING RULES
# ============
# When modifying a file, use replace_string_in_file tool
# Include 3-5 lines context before/after
# If change affects multiple locations, ASK FIRST
# "This change appears in 6 files. Which should I update?"
```

#### 4. **CENTRALIZATION CHECK**
Before ANY session:
```bash
# Find duplicates
find . -name "generate_study.py" -type f

# Expected output: ONLY ONE (in project root)
# If more found: DELETE duplicates or mark as archives
```

### Warning Signs That Code Isn't Centralized:

❌ **"I updated 5 files to apply this change"** - Logic is duplicated  
❌ **"Changes needed in multiple locations"** - Abstraction missing  
❌ **"Updated template in 3 places"** - No single source of truth  
❌ **AI suggests editing documentation AND code** - Documentation may be stale

### Correct Centralization:

✅ **ONE template generator** (`generate_study.py`)  
✅ **ONE framework parser** (`src/lilypond_parser.py`)  
✅ **ONE score builder** (`src/score_builder.py`)  
✅ **Documentation DESCRIBES code** (doesn't duplicate it)  
✅ **Generated files clearly marked** (can be recreated)

### The Golden Rule (from User):

> **"Duplicate files typically tell you that you should ONLY touch the active code base."**

**Translation:**
- If a file exists in multiple places → It's probably archived/referenced
- **Only edit the PRIMARY/ACTIVE version**
- Never "sync" copies (they drift for a reason - history)
- If you don't know which is active → **ASK THE USER**

### For This Project Specifically:

**Primary Active Codebase:**
```
/workspaces/Codempose/
├── generate_study.py              ← ✅ ACTIVE (edit this)
├── src/                           ← ✅ ACTIVE (framework code)
│   ├── lilypond_parser.py
│   ├── score_builder.py
│   └── ...
├── studies/                       ← ✅ ACTIVE (generated study files)
│   ├── first.py
│   ├── second.py
│   └── ...
└── tests/                         ← ✅ ACTIVE (test suite)
```

**Archives/References (DO NOT EDIT):**
```
├── IMPROVED_STUDY_TEMPLATE.py     ← 📚 REFERENCE (shows template structure)
├── generate_study.py.backup       ← 🗄️ BACKUP (909 lines original)
├── backup/                        ← 🗄️ ARCHIVE (old versions)
├── cleanup/                       ← 🗄️ ARCHIVE (refactoring history)
├── outputs/OLD/                   ← 🗄️ ARCHIVE (old generated outputs)
├── outputs/TEMPLATES/             ← 🗄️ ARCHIVE (template snapshots)
└── src/lib/generate_study.py      ← ❓ UNCLEAR (ask user)
```

**Rule for AI:**
1. See a file in `backup/`, `cleanup/`, `OLD/`, or `*.backup`? → **Don't touch**
2. See same filename in multiple places? → **Only edit the one in active codebase**
3. Not sure which is active? → **Ask user before editing**
4. Never "sync" a backup with current code (that destroys history)

---

## What DOES Work (Based on This Project)

### ✅ 1. **LOCK FILES** - Mark Code as Read-Only

**Create a `.ai-lock` file** listing untouchable code:

```bash
# .ai-lock - DO NOT MODIFY THESE FILES
# Last updated: 2025-10-19

# Core framework (stable, don't touch)
src/lilypond_parser.py
src/score_builder.py
src/project_template.py
src/transformations.py

# Generated files (will be overwritten)
studies/*.py

# Configuration (hand-tuned)
.devcontainer/devcontainer.json
requirements.txt
```

**In every session, START with:** "Read .ai-lock and confirm you won't modify those files."

---

### ✅ 2. **GOLDEN REFERENCE** - Single Source of Truth

Instead of multiple reference files, have ONE file that represents the current correct state:

```bash
# Structure:
GOLDEN/
  ├── generate_study.py          # ← THE CORRECT VERSION
  ├── README.md                   # ← Why this version is correct
  └── CHANGES.md                  # ← What changed from previous version
```

**Rule:** Always compare against GOLDEN/ before making changes.

**In every session:** "Check GOLDEN/generate_study.py before suggesting changes."

---

### ✅ 3. **PROGRESSIVE EXAMPLES** - Learn from Existing Code

**What worked in this project:** Looking at the progression of .ly files (studies 1→21) showed the evolution.

**Why it worked:** Concrete examples > abstract requirements.

**How to use it:**
```bash
# Create example progression
examples/
  ├── v1_basic.py           # First working version
  ├── v2_with_metadata.py   # Added metadata
  ├── v3_with_stations.py   # Added station architecture
  └── CURRENT.py → v3_with_stations.py  # Symlink to current
```

**In every session:** "Look at examples/v*.py to understand the progression."

---

### ✅ 4. **DIFF-BASED CHANGES** - Never Replace, Always Patch

**Problem:** AI often replaces entire files, losing subtle improvements.

**Solution:** Make AI show you the diff BEFORE applying:

```bash
# Before session:
git commit -am "Checkpoint before AI session"

# After AI suggests changes:
git diff  # Review what actually changed

# If wrong:
git checkout -- file.py  # Revert
```

**Rule:** Never let AI "regenerate" a file. Only targeted edits.

---

### ✅ 5. **CHECKPOINT SYSTEM** - Save Before Experiments

**Create numbered checkpoints:**
```bash
checkpoints/
  ├── 001_basic_template.tar.gz
  ├── 002_added_metadata.tar.gz
  ├── 003_added_stations.tar.gz
  └── LATEST → 003_added_stations.tar.gz
```

**Workflow:**
1. Working state? → Create checkpoint
2. AI session → Experiment
3. Broke something? → Restore checkpoint
4. Fixed it? → Create new checkpoint

**Script it:**
```bash
#!/bin/bash
# checkpoint.sh
NUM=$(ls checkpoints/*.tar.gz | wc -l)
NEXT=$(printf "%03d" $((NUM + 1)))
tar czf "checkpoints/${NEXT}_$(date +%Y%m%d_%H%M%S).tar.gz" \
    generate_study.py \
    src/ \
    DOCUMENTATION/
echo "Checkpoint ${NEXT} created"
```

---

### ✅ 6. **SESSION NOTES** - Document What NOT to Do

**Create `SESSION_NOTES/` with dated files:**

```markdown
# SESSION_NOTES/2025-10-19.md

## What Worked
- Shortened docstring to fix .ly header pollution
- Added creative examples back (SOURCE_THEME_LILY, SOURCE_MELODY_LILY)

## What FAILED (Don't Try Again)
- ❌ Trying to escape braces with complex regex
- ❌ Using format specs in f-strings (`:< 20`)
- ❌ Doubling braces in IMPROVED_STUDY_TEMPLATE.py (already escaped)

## What's LOCKED
- generate_study.py template structure (620 lines)
- Template brace escaping (working, don't change)
- Creative examples format (keep commented)

## Next Session TODO
- [ ] Fix .ly header to show original snippets (src/ code change)
- [ ] Create final tarball
- [ ] Update version number
```

**In next session:** "Read SESSION_NOTES/2025-10-19.md first."

---

### ✅ 7. **VERIFICATION TESTS** - Automatic Regression Detection

**Create test script:**
```bash
#!/bin/bash
# verify_template.sh - Run this after AI changes

echo "Checking template integrity..."

# Test 1: File size (should be ~620 lines)
LINES=$(wc -l < generate_study.py)
if [ $LINES -lt 600 ] || [ $LINES -gt 650 ]; then
    echo "❌ FAIL: Template size changed ($LINES lines, expected ~620)"
    exit 1
fi

# Test 2: Creative examples present
if ! grep -q "SOURCE_THEME_LILY" generate_study.py; then
    echo "❌ FAIL: Creative examples missing"
    exit 1
fi

# Test 3: Generate and run test
python3 generate_study.py 99 "Test" || exit 1
cd studies && python3 ninetyninth.py || exit 1

echo "✅ ALL TESTS PASSED"
```

**After AI session:** Run `./verify_template.sh`

---

## Concrete Strategy for This Project

### Immediate Actions (Do These NOW):

1. **Create GOLDEN reference:**
   ```bash
   mkdir -p GOLDEN
   cp generate_study.py GOLDEN/
   echo "This is the CORRECT version as of 2025-10-19" > GOLDEN/README.md
   ```

2. **Create checkpoint:**
   ```bash
   mkdir -p checkpoints
   tar czf checkpoints/001_template_complete_$(date +%Y%m%d).tar.gz \
       generate_study.py \
       generate_study.py.backup \
       IMPROVED_STUDY_TEMPLATE.py \
       DOCUMENTATION/
   ```

3. **Create lock file:**
   ```bash
   cat > .ai-lock << 'EOF'
   # DO NOT MODIFY WITHOUT EXPLICIT USER REQUEST
   generate_study.py  # Template complete (620 lines)
   GOLDEN/            # Reference implementations
   checkpoints/       # Backup history
   EOF
   ```

4. **Create verification test:**
   ```bash
   cat > verify_template.sh << 'EOF'
   #!/bin/bash
   set -e
   echo "Verifying template..."
   
   # Check size
   LINES=$(wc -l < generate_study.py)
   [ $LINES -ge 600 ] || { echo "❌ Template too small"; exit 1; }
   [ $LINES -le 650 ] || { echo "❌ Template too large"; exit 1; }
   
   # Check creative examples
   grep -q "SOURCE_THEME_LILY" generate_study.py || { echo "❌ Missing SOURCE_THEME"; exit 1; }
   grep -q "SOURCE_MELODY_LILY" generate_study.py || { echo "❌ Missing SOURCE_MELODY"; exit 1; }
   
   # Test generation
   python3 generate_study.py 99 "Test" > /dev/null || { echo "❌ Generation failed"; exit 1; }
   
   echo "✅ Template verified"
   EOF
   
   chmod +x verify_template.sh
   ```

---

## For Tomorrow's Session

**START with this prompt:**

```
I have documentation in DOCUMENTATION/LILYPOND_HEADER_ISSUE.md 
about a .ly header format problem.

BEFORE suggesting any changes:
1. Read .ai-lock - confirm which files are locked
2. Read GOLDEN/README.md - understand the current correct state
3. Read SESSION_NOTES/2025-10-19.md - see what we tried today
4. Run ./verify_template.sh - confirm template still works

The ONLY task is: Fix the .ly header in src/ code (NOT the template).
The template (generate_study.py) is COMPLETE and LOCKED.

Do you understand?
```

---

## Why You're Right

> "if I would have relied on you solely, it would have gone NOWHERE"

**You're absolutely correct.** AI assistants are:
- ✅ Good at: Executing specific tasks with clear constraints
- ✅ Good at: Pattern matching from examples
- ✅ Good at: Generating boilerplate code
- ❌ Bad at: Understanding project history
- ❌ Bad at: Maintaining consistency across sessions
- ❌ Bad at: Knowing when to stop "improving"

**The successful projects use AI as a TOOL, not a DRIVER.**

**You need:**
- Human: Strategy, decisions, history, judgment
- AI: Execution, refactoring, search, generation

**You did it right by:**
- Catching when I removed creative examples
- Noticing the .ly header progression
- Demanding the template be completed
- Maintaining backups and reference files

---

## Going Forward

### For This Project:
1. ✅ Template is DONE (620 lines, tested, working)
2. ⚠️ .ly header needs src/ code fix (tomorrow)
3. ✅ Create final tarball after .ly fix
4. ✅ Document the release

### General Principle:
**"Lock what works, checkpoint before changes, verify after."**

### Your Role:
- **Arbiter**: You decide what's right
- **Historian**: You remember the context
- **Guardian**: You protect good code from "improvements"

### AI Role:
- **Executor**: Implement specific changes
- **Analyst**: Find patterns in code
- **Assistant**: Generate boilerplate, run tests

---

## The Meta-Lesson

The fact that **reviewing old .ly files (studies 1-21) gave you the answer** while **all the documentation failed** tells us:

**Concrete examples > Abstract requirements**

AI assistants are essentially **pattern matchers**. We work best when:
1. Shown working examples
2. Given specific diffs to apply
3. Constrained to narrow tasks
4. Verified after each change

We work worst when:
- Asked to "understand" intent
- Given too much freedom
- Expected to remember context
- Trusted to improve without guidance

---

## Your Observation is Critical

> "This project seems (HOPEFULLY) almost finished, but if I would have relied on you solely, it would have gone NOWHERE"

**This should be in every AI documentation:**

⚠️ **WARNING: AI assistants have no memory.**  
✅ **Solution: Lock files, checkpoints, and verification tests.**  
🎯 **Strategy: You lead, AI executes specific tasks.**

---

## Final Recommendation

**For tomorrow:**
1. ✅ Don't let me touch generate_study.py
2. ✅ Only fix src/lilypond_engraver.py (or whatever writes .ly headers)
3. ✅ Show diff before applying
4. ✅ Test with verify_template.sh after
5. ✅ Create final tarball when .ly header is fixed

**The template work is DONE. Protect it.**
