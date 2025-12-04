# BLUEPRINT STRING IMPLEMENTATION ANALYSIS
Date: October 15, 2025

---

## CRITICAL DESIGN DECISIONS

### 1. **Parser Architecture: Three-Function Design**

```
parse_voice_stave_def(def_string)
    → Returns layout structure

parse_voice_stave_data(data_string, layout)
    → Returns sections structure

build_score_from_blueprint(def_string, data_string, snippets, metadata)
    → Orchestrates parsing + assembly
```

**Why separate functions?**
- **Testability:** Each parser function can be unit tested independently
- **Reusability:** `parse_voice_stave_def()` can be used for validation tools
- **Clarity:** Single responsibility principle
- **Debugging:** Easier to trace issues to specific parsing stages

---

### 2. **Data Structure Design**

**Option A: Nested Dictionaries (Proposed)**
```python
{
    'layout': [['Soprano', 'Alto'], ['Tenor', 'Bass']],
    'sections': [
        {
            'staff_0': {'Soprano': ['SOP_A'], 'Alto': ['ALT_A']},
            'staff_1': {'Tenor': ['TEN_A'], 'Bass': ['BAS_A']}
        }
    ]
}
```

**Option B: Flat Lists (Simpler)**
```python
{
    'layout': [['UpperStaff'], ['LowerStaff']],
    'sections': [
        [
            ['MELODY_A', 'MELODY_B'],  # Staff 0 content
            ['r']                       # Staff 1 content
        ]
    ]
}
```

**RECOMMENDATION: Option B (Flat Lists)**

**Rationale:**
- Most study files use single-voice-per-staff (simpler case)
- Multi-voice can be handled by voice count in layout
- Less nesting = easier debugging
- Cleaner assembly loop logic

**When multi-voice is needed:**
```python
# Layout: [['Soprano', 'Alto'], ['Bass']]
# Section: [[['SOP_A'], ['ALT_A']], [['BASS_A']]]
#           ↑ Staff 0 (2 voices)   ↑ Staff 1 (1 voice)
```

---

### 3. **Rest Generation Strategy**

**Challenge:** How to calculate rest duration when `'r'` is encountered?

**Option A: Look-ahead (Calculate before building)**
```python
# Parse all sections first
# Calculate max duration per section
# Generate rests to match
```

**Option B: Two-pass (Build active parts, then fill rests)**
```python
# First pass: Build all non-rest parts
# Second pass: Generate rests to match each section's duration
```

**Option C: Lazy evaluation (Generate during assembly)**
```python
# As you build each section, check for 'r'
# Calculate duration from already-built parts
# Generate rest on-the-fly
```

**RECOMMENDATION: Option B (Two-Pass)**

**Rationale:**
- Clean separation of concerns
- All active parts built first (can validate durations)
- Rest generation happens with full context
- Easier to debug duration mismatches

---

### 4. **Error Handling Philosophy**

**Fail Fast vs. Graceful Degradation**

**Proposed: FAIL FAST with clear messages**

```python
# Check 1: Staff count mismatch
if len(staff_contents) != len(layout):
    raise ValueError(
        f"Section {i+1} has {len(staff_contents)} staves "
        f"but layout defines {len(layout)} staves.\n"
        f"Data: '{section_data}'"
    )

# Check 2: Voice count mismatch
if len(voice_snippets) != len(voice_names):
    raise ValueError(
        f"Staff {i} has {len(voice_names)} voices "
        f"but section provides {len(voice_snippets)} snippet groups.\n"
        f"Expected: {voice_names}, Got: {voice_snippets}"
    )

# Check 3: Missing snippet
if snippet_name not in snippets and snippet_name != 'r':
    raise KeyError(
        f"Snippet '{snippet_name}' not found in SNIPPETS dictionary.\n"
        f"Available snippets: {list(snippets.keys())}"
    )
```

**Why fail fast?**
- Blueprint errors indicate fundamental composition issues
- Better to catch at parse time than generate invalid scores
- Clear error messages guide composers to fix

---

### 5. **Whitespace & Comment Handling**

**Strategy:**
```python
# Strip comments and normalize whitespace BEFORE parsing

def normalize_blueprint_string(data_string):
    """Clean up blueprint string for parsing."""
    lines = []
    for line in data_string.split('\n'):
        # Remove comments
        line = re.sub(r'#.*$', '', line)
        # Strip whitespace
        line = line.strip()
        # Skip empty lines
        if line:
            lines.append(line)
    return '\n'.join(lines)
```

**Then parse the cleaned string:**
```python
cleaned = normalize_blueprint_string(VOICE_STAVE_DATA)
sections = cleaned.split(';')
```

---

## IMPLEMENTATION ROADMAP

### Phase 1: Core Parser (1-2 hours)

**File:** `score_blueprint.py` (new)

**Functions:**
1. `normalize_blueprint_string(data)` - Clean whitespace/comments
2. `parse_voice_stave_def(def_string)` - Parse header
3. `parse_voice_stave_data(data_string, layout)` - Parse body
4. `build_score_from_blueprint(def_string, data_string, snippets, metadata)` - Orchestrate

**Testing:**
- Create `test_score_blueprint.py` with unit tests
- Test each delimiter level independently
- Test edge cases (empty sections, mismatches, etc.)

---

### Phase 2: Assembly Logic (1 hour)

**Update:** `project_template.py` or create `score_assembler.py`

**Functions:**
1. `assemble_section(section_data, snippets)` - Build one section
2. `generate_matching_rests(duration)` - Create rest events
3. `validate_section_durations(section)` - Check alignment

**Integration:**
- Hook into existing `build_score_data()` flow
- Ensure compatibility with voice metadata
- Preserve all existing transformation capabilities

---

### Phase 3: Refactor thirteenth.py (30 minutes)

**Changes:**
1. Add VOICE_STAVE_DEF constant
2. Add VOICE_STAVE_DATA constant
3. Replace Station 3 manual assembly (lines 320-395)
4. Keep SNIPPETS dictionary structure
5. Call `build_score_from_blueprint()`

**Validation:**
```bash
# Generate both versions
python3 thirteenth.py  # New version
diff outputs/thirteenth.ly outputs/thirteenth_old.ly
# Should be identical (or minimal formatting differences)
```

---

### Phase 4: Documentation & Migration (1 hour)

**Tasks:**
1. Update DEVELOPMENT.md with blueprint syntax
2. Create examples for each study pattern
3. Add migration guide for existing studies
4. Create blueprint validator tool

---

## DISCUSSION POINTS

### Question 1: Single-Staff Simplification

For single-staff scores, should we allow omitting `&`?

**Example:**
```python
# Option A: Require consistency (always use delimiters)
VOICE_STAVE_DEF = "Piano"
VOICE_STAVE_DATA = "INTRO | THEME; VARIATION; CODA"

# Option B: Auto-detect (no & or ; needed for single staff)
VOICE_STAVE_DATA = "INTRO | THEME | VARIATION | CODA"
```

**RECOMMENDATION: Option A (Require Delimiters)**
- Consistency across all score types
- Clear section boundaries
- Easier parsing logic

---

### Question 2: Multi-Voice Comma Placement

For multi-voice staves, where should the comma go?

**Example:**
```python
# Option A: Outside the pipe groups (voice-level separation)
VOICE_STAVE_DATA = "SOP_A | SOP_B, ALT_A | ALT_B & TEN_A, BAS_A"
#                  ↑ Soprano content  ↑ Alto content

# Option B: Inside with parentheses (clearer grouping)
VOICE_STAVE_DATA = "(SOP_A | SOP_B, ALT_A | ALT_B) & (TEN_A, BAS_A)"
```

**RECOMMENDATION: Option A (Comma Outside)**
- Simpler to parse (no need for parentheses in data string)
- Parentheses only in VOICE_STAVE_DEF (header)
- Clearer visual alignment with layout

---

### Question 3: Rest Duration Calculation

When multiple staves are active in a section, which duration should rests match?

**Example:**
```python
# Section with duration mismatch
VOICE_STAVE_DATA = "THEME_4_BARS & HARMONY_8_BARS; r & BASS_CONTINUED"
#                   ↑ 4 bars      ↑ 8 bars          ↑ How many bars?
```

**Options:**
- **A:** Match the longest active staff (8 bars)
- **B:** Require all active staves to have same duration (fail with error)
- **C:** Allow user to specify: `r(8)` for 8-bar rest

**RECOMMENDATION: Option B (Enforce Alignment)**
- Mismatched durations likely indicate composition error
- Forces conscious section design
- Prevents accidental misalignment
- Can relax later if needed

**Implementation:**
```python
def validate_section_durations(section):
    """Ensure all parts in a section have the same total duration."""
    durations = []
    for staff_parts in section:
        total_ql = sum(event['duration'] for part in staff_parts 
                       for event in part if event != 'r')
        durations.append(total_ql)
    
    if len(set(durations)) > 1:
        raise ValueError(
            f"Section has mismatched durations: {durations}\n"
            f"All staves must have equal total duration per section."
        )
    
    return durations[0]  # Return the common duration
```

---

### Question 4: Integration with Transformations

Should transformations happen before or after blueprint parsing?

**Current pattern (thirteenth.py):**
```python
SNIPPETS = {
    'THEME': theme_events,
    'THEME_TRANSPOSED': transpose_part(theme_events, 4),  # ← Transform in SNIPPETS
}
```

**Alternative:**
```python
VOICE_STAVE_DATA = "transpose(THEME, 4) & r"  # ← Transform in blueprint string
```

**RECOMMENDATION: Keep transformations in SNIPPETS (current pattern)**
- Blueprint string stays declarative (what to play, not how to modify)
- Transformations are reusable across sections
- Easier to debug (can inspect transformed snippets)
- Doesn't complicate parser

---

## PROPOSED IMPLEMENTATION ORDER

1. ✅ **Design finalized** (this document + BLUEPRINT_STRING_FRAMEWORK_V2.md)

2. ⏳ **Create `score_blueprint.py`** with core parser functions
   - Implement parser functions
   - Add comprehensive docstrings
   - Include inline examples

3. ⏳ **Create `test_score_blueprint.py`** with unit tests
   - Test each delimiter level
   - Test edge cases
   - Test error conditions

4. ⏳ **Update `project_template.py`** (or create `score_assembler.py`)
   - Add assembly functions
   - Integrate with existing build_score_data()
   - Preserve all metadata handling

5. ⏳ **Refactor `thirteenth.py`** as validation
   - Replace manual assembly
   - Verify identical output
   - Measure LOC reduction

6. ⏳ **Document** the system
   - Update DEVELOPMENT.md
   - Create migration guide
   - Add examples

---

## QUESTIONS FOR USER

Before proceeding with implementation, please confirm:

1. **Data Structure:** Accept recommendation for flat list structure (Option B)?

2. **Rest Duration:** Enforce equal duration per section (fail if mismatch)?

3. **Single-Staff:** Require `;` delimiters even for single-staff scores?

4. **Multi-Voice Comma:** Use comma outside pipe groups (no parens in data string)?

5. **Error Handling:** Fail fast with detailed error messages?

6. **File Organization:** Create new `score_blueprint.py` or add to existing file?

7. **Testing Priority:** Write tests first (TDD) or implement then test?

---

## ESTIMATED EFFORT

- **Parser Implementation:** 2 hours
- **Assembly Integration:** 1 hour  
- **thirteenth.py Refactor:** 30 minutes
- **Testing:** 1 hour
- **Documentation:** 1 hour

**Total:** ~5.5 hours of focused development

**Code Reduction:** ~70 lines per complex study file

---

## NEXT STEP

**Await user confirmation on design decisions, then proceed with:**

```bash
# Step 1: Create the parser
touch /workspaces/Codempose/score_blueprint.py

# Step 2: Create tests
touch /workspaces/Codempose/test_score_blueprint.py

# Step 3: Implement core functions
# Step 4: Refactor thirteenth.py
# Step 5: Validate output matches
```
