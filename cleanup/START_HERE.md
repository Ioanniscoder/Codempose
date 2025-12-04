# START HERE - AI SESSION INITIALIZATION
**Last Updated:** October 19, 2025  
**MANDATORY:** Read this file at the start of EVERY session before doing anything else.

---

## 🔴 CRITICAL RULES (Violation = Session Failure)

### 1. **LOCKED FILES - DO NOT MODIFY**
```
generate_study.py (620 lines) - Template COMPLETE, tested, working
  ├─ Has: Creative examples, shortened docstring, station architecture
  └─ Other copies exist in backup/, cleanup/, src/lib/, outputs/TEMPLATES/
     → Those are ARCHIVES. Only edit root version IF user explicitly requests.
     → Currently: NO EDITS NEEDED. File is DONE.

backup/           - Historical snapshots, never touch
cleanup/          - Refactoring history, never touch  
outputs/OLD/      - Old generated files, never touch
*.backup files    - Backups, never touch
```

### 2. **REQUIRED OUTPUT FORMATS**

#### **.ly File Header Format (MANDATORY)**
User requirement: "I want to see the original snippets, for reference"

**CORRECT FORMAT (Phase 2 - Studies 6-12):**
```lilypond
% ========================================
% ORIGINAL LILYPOND INPUT (for reference)
% ========================================
% COMPOSITION STRUCTURE (from VOICE_STAVE_DATA):
% 
% Melody Staff:
%   Soprano: INTRO + THEME + VARIATION
% 
% VOICE SNIPPETS:
% 
% INTRO:
% LILYPOND FORMAT:
% \relative c'' {
%     \time 4/4
%     \key c \major
%     e4 b4 e'4 b4
% }
```

**WRONG FORMAT (Phase 3 - Studies 13+, do NOT use):**
```lilypond
% ========================================
% HOW TO USE
% ========================================
% - Copy any snippet above into a new study file
% - Use shorthand expressions as templates
```
❌ This is generic, provides no reference value

**Where to fix:** `src/lilypond_engraver.py` or `src/converter.py` (find file that writes .ly header comments)

---

## 📋 CURRENT PROJECT STATE

### ✅ COMPLETED (Do not revisit)
- [x] Template improvements (generate_study.py: 620 lines)
- [x] Brace escaping fixed (no format specs in f-strings)
- [x] Creative examples restored (SOURCE_THEME_LILY, SOURCE_MELODY_LILY)
- [x] Docstring shortened (3 lines, prevents .ly pollution)
- [x] Test generation verified (ninetyninth.py works)
- [x] All outputs created (PDF, MIDI, MusicXML)

### ⚠️ PENDING (Current task)
- [ ] Fix .ly header format in framework code
  - Location: `src/` directory (NOT template)
  - Files: `src/lilypond_engraver.py` or `src/converter.py`
  - Change: Phase 3 format → Phase 2 format
  - Action: Find where header comments are generated, modify to show original snippets

---

## 🎯 SESSION WORKFLOW (Follow this order)

### Step 1: VERIFY STATE
```bash
# Check template integrity
wc -l generate_study.py              # Should be ~620 lines
grep -q "SOURCE_THEME_LILY" generate_study.py && echo "✅ Template OK"

# Verify archives untouched
git status                           # Should not show changes in backup/, cleanup/
```

### Step 2: UNDERSTAND TASK
- Read user request carefully
- Check if task involves locked files → If yes, STOP and ask user
- Check if task is already complete → Reference documentation

### Step 3: PLAN BEFORE ACTING
- **DO NOT** make edits immediately
- **DO** show user your understanding first
- **DO** ask if target file is correct before modifying
- **DO** show diff before applying changes

### Step 4: EXECUTE WITH CONSTRAINTS
- Use `replace_string_in_file` (not regenerate entire files)
- Include 3-5 lines context before/after
- If change affects multiple files → ASK which to modify
- One focused edit at a time

### Step 5: VERIFY AFTER CHANGE
```bash
# Test generation still works
python3 generate_study.py 99 "Test"
cd studies && python3 ninetyninth.py

# Check outputs
ls -la outputs/ninetyninth.*         # Should have .ly, .pdf, .midi, .musicxml
head -20 outputs/ninetyninth.ly      # Check header format
```

---

## 🚫 ANTI-PATTERNS (Things that cause regressions)

### ❌ Taking Samples Instead of Complete Analysis
**Bad:** "I checked first.ly, fifth.ly, tenth.ly - they seem similar"  
**Good:** "I checked ALL .ly files (first through twentyfirst) and found 3 distinct phases"

**Why:** User says: *"Only if I press you you find the pattern that is actually found"*

**Solution:** When asked to analyze progression/pattern:
1. Check ALL examples (not samples)
2. Document the complete progression
3. Identify phase boundaries
4. Ask user to confirm pattern before making changes

### ❌ Creating Documentation Without Reading It Back
**Bad:** Write 500-line analysis, never reference it in next action  
**Good:** Write focused directives at top, reference specific sections when making decisions

**Why:** User says: *"You create extensive md documents, without actually reading it back, I don't either"*

**Solution:** 
- Put ACTION ITEMS at top of documents
- Use this START_HERE.md as single source of truth
- Reference specific sections: "Per LILYPOND_HEADER_ISSUE.md section 'Phase 2 Format'..."

### ❌ Editing Scattered Duplicates
**Bad:** "I updated generate_study.py in 5 locations"  
**Good:** "I found generate_study.py in 5 locations. Root version is active. Others are archives. Only editing root."

**Why:** User says: *"if edits are all over the place, it is a recipe for disaster, and it tells that the code is not centralized"*

**Solution:** 
- If file exists in multiple places → Only edit root/active version
- If unsure which is active → ASK USER
- Never "sync" archives with current code

### ❌ "Improving" Working Code
**Bad:** "I noticed generate_study.py could be simplified..."  
**Good:** "generate_study.py is locked as complete. Not modifying."

**Why:** User says: *"it is SO HARD to let you KEEP improvements. Before I know it, they are gone"*

**Solution:**
- If file is in .ai-lock → DON'T suggest improvements
- If user asks for improvement → Show diff first, get approval
- Working code > "better" code

---

## 📊 PATTERN ANALYSIS PROTOCOL

When user asks to "study the files" or "find the pattern":

### ✅ CORRECT APPROACH:
1. **Complete Enumeration:** Check ALL files in range
2. **Document Boundaries:** "Files 1-5 use format A, 6-12 use format B, 13+ use format C"
3. **Show Evidence:** Include examples from EACH phase
4. **Confirm Pattern:** Ask user if analysis is correct

### ❌ WRONG APPROACH:
1. ❌ Check 3 samples and extrapolate
2. ❌ Assume pattern without verification
3. ❌ Present tentative conclusion as fact
4. ❌ Skip phase boundaries

### Example from this project:
**User asked:** "Check the .ly files for progression"  
**Wrong:** Check first.ly, seventh.ly, fourteenth.ly  
**Right:** Check first through twentyfirst, found:
- Phase 1: Studies 1-5 (TINYNOTATION INSPECTOR)
- Phase 2: Studies 6-12 (ORIGINAL SNIPPETS) ← User wants this
- Phase 3: Studies 13+ (HOW TO USE) ← Current unwanted format

---

## 🔧 CURRENT TASK DETAILS

### Task: Fix .ly Header Format
**What:** Change from "HOW TO USE" (Phase 3) to "ORIGINAL SNIPPETS" (Phase 2)  
**Where:** Framework code in `src/` (NOT the template)  
**Why:** User wants to see original LilyPond snippets for reference  
**Priority:** Medium (cosmetic but valuable for documentation)

### Action Plan:
1. Find file that generates .ly header comments
   - Candidates: `src/lilypond_engraver.py`, `src/converter.py`
   - Search for: "HOW TO USE" string in src/
2. Analyze how studies 6-12 generated Phase 2 format
   - Compare old .ly files (outputs/OLD/sixth.ly through twelfth.ly)
   - Identify what data was available to generate that format
3. Modify header generation to:
   - Show VOICE_STAVE_DATA structure
   - Include original LilyPond snippet contents
   - Format like Phase 2 examples
4. Test with ninetyninth.py
5. Verify output matches desired format

### Success Criteria:
```bash
head -30 outputs/ninetyninth.ly
# Should show:
# - ORIGINAL LILYPOND INPUT header
# - COMPOSITION STRUCTURE with VOICE_STAVE_DATA
# - VOICE SNIPPETS with actual LilyPond code
# Should NOT show:
# - HOW TO USE generic instructions
```

---

## 💾 QUICK REFERENCE

### Files to Read First:
1. `START_HERE.md` (this file) - Session initialization
2. `.ai-lock` - Files that are off-limits
3. `DOCUMENTATION/LILYPOND_HEADER_ISSUE.md` - Current task details
4. `DOCUMENTATION/HOW_TO_WORK_WITH_AI_ASSISTANTS.md` - Meta-guidance

### Files to Never Touch:
- `generate_study.py` (COMPLETE - 620 lines)
- `backup/`, `cleanup/`, `outputs/OLD/`, `*.backup`
- `IMPROVED_STUDY_TEMPLATE.py` (reference only)

### Verification Commands:
```bash
# Template integrity
wc -l generate_study.py && grep -q "SOURCE_THEME_LILY" generate_study.py

# Test generation
python3 generate_study.py 99 "Test" && cd studies && python3 ninetyninth.py

# Check output format
head -30 outputs/ninetyninth.ly
```

---

## 📝 UPDATE THIS FILE

When task is complete:
1. Move task from PENDING to COMPLETED
2. Add newly modified file to .ai-lock
3. Update CURRENT TASK to next priority
4. Document any new patterns/rules discovered

**This file is the CONTRACT between user and AI for how sessions should work.**

---

**Last verified working state:** October 19, 2025, 11:00 PM
