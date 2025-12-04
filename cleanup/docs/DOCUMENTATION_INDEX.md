# Codempose Documentation Index

## Latest Updates (October 5, 2025)

### Promotion System Update ✨ 
- **PROMOTION_WORKFLOW.md** - Complete guide with quick reference (READ FIRST!)
- Study files now include both LilyPond and TinyNotation formats by default
- Toggle controls which format is dominant (gets processed)
- Generated .ly files show both original snippets in comments

### Staff Order & Octave Fixes ✨
- **FIX_COMPLETE.md** - Summary of fixes
- Added `reverse=True` to sorted() for correct staff order
- Changed `\relative e` to `\relative e'` for correct melody octave

---

## Core Documentation

### Getting Started
1. **README_DOCUMENTATION.md** - Project overview and quick start
2. **PROMOTION_WORKFLOW.md** - Dual-format system guide (includes quick reference)

### System Architecture
1. **COMPLETE_SUMMARY.md** - System architecture
2. **RESTRUCTURE_SUMMARY.md** - Pipeline processing
3. **METADATA_TINYNOTATION_FORMAT.md** - TinyNotation format

### Fixes & History
1. **FIX_COMPLETE.md** - Staff order & octave fixes
2. **DIAGNOSIS_STAFF_ISSUES.md** - Technical analysis
3. **OPTIONS_STAFF_FIX.md** - Solution approaches

### Development
1. **DEVELOPMENT.md** - Contribution guide
2. **DEVELOPER_CHANGES.md** - Changelog

---

## Quick Navigation

### "I want to..."

#### Create a new composition
→ Use **first.py** as template  
→ Run `python3 first.py`  

#### Understand the promotion system
→ Read **PROMOTION_WORKFLOW.md** (includes quick reference)  

#### Debug staff ordering or octave issues
→ **FIX_COMPLETE.md** (solutions)  
→ **DIAGNOSIS_STAFF_ISSUES.md** (technical details)  

#### Understand the pipeline
→ **RESTRUCTURE_SUMMARY.md** (pipeline flow)  
→ **COMPLETE_SUMMARY.md** (architecture)  

#### Contribute
→ **DEVELOPMENT.md** (guidelines)  
→ **DEVELOPER_CHANGES.md** (recent changes)  

---

## File Organization

### Root Directory
```
first.py                    ← Two-stave composition template
second.py                   ← Additional study file
third.py                    ← Additional study file
fourth.py                   ← Additional study file
fifth.py                    ← Additional study file

project_template.py         ← Pipeline orchestrator
music_data.py               ← Data structure conversions
lilypond_parser.py          ← LilyPond → score_data parser
lily_to_tiny.py             ← LilyPond → TinyNotation converter
relative_octave_logic.py    ← Octave calculation logic

PROMOTION_WORKFLOW.md       ← Promotion guide (⭐ START HERE)
PROMOTION_QUICK_REFERENCE.md← Quick cheat sheet
FIX_COMPLETE.md             ← Staff/octave fixes summary
README_DOCUMENTATION.md     ← Project overview
```

### outputs/ Directory
```
first.py                    ← Study file copy (inspection)
first.ly                    ← Generated LilyPond source
first.pdf                   ← Musical score (PDF)
first.midi                  ← Audio playback
first.TIMESTAMP.bak         ← Backup (if promoted)

[All documentation also copied here]
```

---

## Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| PROMOTION_WORKFLOW.md | ✅ Current | Oct 4, 2025 |
| PROMOTION_UPDATE.md | ✅ Current | Oct 4, 2025 |
| PROMOTION_VERIFICATION.md | ✅ Current | Oct 4, 2025 |
| PROMOTION_QUICK_REFERENCE.md | ✅ Current | Oct 4, 2025 |
| FIX_COMPLETE.md | ✅ Current | Oct 4, 2025 |
| DIAGNOSIS_STAFF_ISSUES.md | ✅ Current | Oct 4, 2025 |
| OPTIONS_STAFF_FIX.md | ✅ Current | Oct 4, 2025 |
| README_DOCUMENTATION.md | ✅ Current | Oct 4, 2025 |
| FIRST_PY_DOCUMENTATION.md | ✅ Current | Oct 4, 2025 |
| COMPLETE_SUMMARY.md | ✅ Current | Oct 4, 2025 |
| RESTRUCTURE_SUMMARY.md | ✅ Current | Oct 4, 2025 |
| METADATA_TINYNOTATION_FORMAT.md | ✅ Current | Oct 4, 2025 |

---

## Reading Order (Recommended)

### For New Users:
1. **README_DOCUMENTATION.md** - Start here
2. **PROMOTION_WORKFLOW.md** - Dual-format system

### For Developers:
1. **COMPLETE_SUMMARY.md** - Architecture
2. **RESTRUCTURE_SUMMARY.md** - Pipeline
3. **DEVELOPMENT.md** - Guidelines

### For Troubleshooting:
1. **PROMOTION_WORKFLOW.md** - Quick reference at end
2. **FIX_COMPLETE.md** - Common issues

---

## Version History

### v2.0 (October 4, 2025) - Dual-Format Workflow
- ✅ Both LilyPond and TinyNotation present from the start
- ✅ Toggle controls dominance (not generation)
- ✅ Improved file management (backups in outputs/)
- ✅ Enhanced documentation suite (4 new guides)

### v1.5 (October 4, 2025) - Staff Order & Octave Fixes
- ✅ Fixed staff ordering (Melody top, Harmony bottom)
- ✅ Fixed melody octave (E4 instead of E3)
- ✅ Minimal code changes (2 lines total)
- ✅ Universal benefit for all compositions

### v1.0 - Initial System
- Parser with metadata extraction
- Promotion system (original version)
- Two-stave output support
- Music21 transformations

---

## Support & Feedback

For questions or issues:
1. Check **PROMOTION_QUICK_REFERENCE.md** for quick answers
2. Review **PROMOTION_WORKFLOW.md** for detailed guidance
3. See **DIAGNOSIS_STAFF_ISSUES.md** for technical details
4. Consult **PROMOTION_VERIFICATION.md** for test results

---

## License & Attribution

**Project**: Codempose  
**Repository**: Ioanniscoder/Codempose  
**Branch**: experimental/project_template_sanitizer_fix  
**Last Updated**: October 4, 2025

---

**Quick Start**: Open `first.py`, run `python3 first.py`, check `outputs/` directory! 🎵
