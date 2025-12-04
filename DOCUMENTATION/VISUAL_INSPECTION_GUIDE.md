# Visual Inspection Guide - Smart Stripping Results

**Files to Inspect:**
- `outputs/ninetyninth.pdf` - Study 99 (comprehensive)
- `outputs/test_regression_baseline.pdf` - Regression test (simple)
- `outputs/ninetyninth.ly` - LilyPond source for study 99
- `outputs/test_regression_baseline.ly` - LilyPond source for test

---

## What to Look For

### 1. Smart Stripping (No Duplicate Metadata)

**Location:** Section 4 in `ninetyninth.pdf` or Section 2 in `test_regression_baseline.pdf`

**What you should see:**
```lilypond
# ✅ CORRECT (with smart stripping):
d4-.\p( fis8 g) a4~ | ... d4-.\p( fis8 g) a4~ | ...
# Musical content repeated, NO \key, \time, \tempo between repetitions

# ❌ WRONG (without smart stripping):
\key g \major \time 3/4 d4... \key g \major \time 3/4 d4...
# Duplicate metadata directives (would confuse LilyPond)
```

**How to verify in PDF:**
- Both repetitions render correctly
- No visual artifacts or layout issues
- Tempo/key/time only appear at staff start, not between repetitions

---

### 2. Measure Bar Generation

**Location:** Section 3 in both PDFs (Bass staff)

**In `test_regression_baseline.ly`:**
```lilypond
% Bass staff, Section 3:
r1 \bar "|" r1 \bar "||"
      ^^^^^ Measure bar between rests!
```

**In `ninetyninth.ly`:**
```lilypond
% Bass staff, Section 3 (THEME_B & r):
r2. \bar "|" r2. \bar "|" r2. \bar "|" r2. \bar "||"
      ^^^^^       ^^^^^       ^^^^^ Three measure bars for 4 rests!
```

**How to verify in PDF:**
- Look at Bass staff in rest sections
- Should see vertical bar lines between rest symbols
- Visual alignment with active Melody staff above

---

### 3. Section vs Measure Barline Distinction

**Location:** All sections in both PDFs

**In LilyPond source:**
```lilypond
# ✅ CORRECT:
r2. \bar "|" r2. \bar "|" r2. \bar "||" \break
                                  ^^^^^^^^^^^^
                            Break only after section barline!

# ❌ WRONG (old behavior):
r2. \bar "|" \break r2. \bar "|" \break r2. \bar "||"
             ^^^^^^             ^^^^^^
        Unwanted breaks after measure bars!
```

**How to verify in PDF:**
- System breaks should occur at logical section boundaries
- Measures within sections stay together on same system
- No awkward mid-section page breaks

---

## PDF Visual Inspection Checklist

### ninetyninth.pdf:

- [ ] **Section 1** (THEME_A & bass_figure):
  - Both staves render
  - Clean notation, no duplicate metadata
  
- [ ] **Section 2** (transpose(THEME_A) & bass_figure):
  - Both staves render
  - Transformation shows different notes (transposed up)
  - Bass staff original (correct durations)
  
- [ ] **Section 3** (THEME_B & r):
  - Melody shows THEME_B (4 measures)
  - Bass shows 4 rest measures WITH bar lines between them
  - Visual alignment maintained
  
- [ ] **Section 4** (THEME_A * 2 & bass_figure * 2):
  - Melody shows THEME_A twice (no duplicate metadata)
  - Bass shows bass_figure twice (no duplicate metadata)
  - Both staves render throughout entire section
  - NO missing Bass staff (previous bug fixed!)

### test_regression_baseline.pdf:

- [ ] **Section 1** (MELODY & BASS):
  - Simple 2-bar melody (c d e f | g2 a2)
  - Simple 2-bar bass (c2 g2 | f2 c2)
  
- [ ] **Section 2** (MELODY * 2 & BASS * 2):
  - Melody repeated twice (4 bars total)
  - Bass repeated twice (4 bars total)
  - Clean, no metadata clutter
  
- [ ] **Section 3** (MELODY & r):
  - Melody shows 2 bars
  - Bass shows 2 whole rests WITH bar line between them

---

## LilyPond Source Inspection

### Key Sections to Check:

#### 1. Staff Header (should only appear once):
```lilypond
\new Staff {
    \clef treble
    \time 3/4 \key g \major  ← Only here, at staff start
    # Music content...
}
```

#### 2. Injected Content (should be clean):
```lilypond
# ✅ Good (smart stripping):
d4-.\p( fis8 g) a4~ |
a4 g4->( fis) |
# Pure musical content, no directives

# ❌ Bad (naive approach):
\key g \major \time 3/4 \tempo "Andante" 4=90
d4-.\p( fis8 g) a4~ |
# Duplicate metadata cluttering the content
```

#### 3. Rest Sections (should have measure bars):
```lilypond
# ✅ Good (with measure bars):
r2. \bar "|" r2. \bar "|" r2. \bar "|" r2.

# ❌ Bad (without measure bars):
r2. r2. r2. r2.
# No visual separation between measures
```

#### 4. Break Positions (should be strategic):
```lilypond
# ✅ Good (after section barlines):
b'4\f c4 d4 \bar "||" \break
                ^^^^^^^^^^^^
              Section boundary

# ❌ Bad (after measure barlines):
r2. \bar "|" \break
          ^^^^^^^^^ Don't break mid-section!
```

---

## Quick Verification Commands

```bash
# Count metadata directives
grep -o '\\tempo' outputs/ninetyninth.ly | wc -l
# Should be 0 (all stripped from injected content)

# Count measure bars
grep -o '\bar "|"' outputs/ninetyninth.ly | wc -l
# Should be 3 (from Section 3 rests)

# Count section bars
grep -o '\bar "||"' outputs/ninetyninth.ly | wc -l
# Should be 8 (4 sections × 2 staves)

# Verify no breaks after measure bars
grep -E '\bar "\|".*\\break' outputs/ninetyninth.ly | wc -l
# Should be 0 (no breaks after measure bars)

# Show break contexts
grep -B1 '\\break' outputs/ninetyninth.ly
# All breaks should follow \bar "||"
```

---

## Expected Visual Appearance

### Section Boundaries:
- Clear double barlines (`||`) at section ends
- System breaks at logical positions
- Professional spacing between systems

### Repetitions:
- Content appears multiple times
- No visual clutter from metadata
- Identical notation for each repetition

### Rest Sections:
- Vertical bar lines visible between rest symbols
- Alignment with active staves above/below
- Clear measure structure

### Overall Layout:
- Both staves present throughout
- No missing sections
- No awkward pagination
- Professional music engraving appearance

---

## Comparison: Before vs After

### Before Smart Stripping:
```lilypond
% Repetition with metadata duplication:
\key g \major \time 3/4 \tempo "Andante" 4=90 d4 e f | g2 a2
\key g \major \time 3/4 \tempo "Andante" 4=90 d4 e f | g2 a2
                                              ^^^^^^^^^^^^^^
                                         Duplicate! Confuses LilyPond
```

### After Smart Stripping:
```lilypond
% Clean repetition:
d4 e f | g2 a2
d4 e f | g2 a2
     ^^^^^^^ Perfect! Just music, no metadata
```

---

## Files to Open for Inspection

1. **Primary:** `outputs/ninetyninth.pdf`
   - Most comprehensive
   - Shows all features
   - 4 sections with various transformations

2. **Secondary:** `outputs/test_regression_baseline.pdf`
   - Simpler, clearer example
   - Easier to see patterns
   - 3 sections with specific tests

3. **Source:** `outputs/ninetyninth.ly`
   - See actual LilyPond code
   - Verify clean content injection
   - Check bar line placement

4. **Source:** `outputs/test_regression_baseline.ly`
   - Simpler source for learning
   - Clear structure
   - Good reference example

---

## Summary: What Success Looks Like

✅ **No duplicate metadata** in repetitions  
✅ **Measure bars visible** in rest sections  
✅ **System breaks** only at section boundaries  
✅ **Both staves render** throughout entire composition  
✅ **Professional appearance** with proper engraving  
✅ **No layout corruption** or visual artifacts

All of these should be visible in the PDF files!
