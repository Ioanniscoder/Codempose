# Quick Reference: MusicXML Export & Shorthand Promotion

## MusicXML Export

### Automatic Generation
```bash
python3 your_file.py
# → outputs/your_file.musicxml created automatically
```

### Open in MuseScore
```bash
musescore outputs/your_file.musicxml
# Or in dev container:
$BROWSER outputs/your_file.musicxml
```

### What's Exported
- ✅ All parts and voices
- ✅ Pitches and durations
- ✅ Metadata (title, composer)
- ✅ Time/key signatures

---

## Shorthand Promotion

### Step 1: Write Shorthand
```python
VOICE_ASSIGNMENTS = {
    'Soprano': 'THEME + transpose(THEME, 7)',
    'Bass': 'BASS * 4',
}
```

### Step 2: Trigger Promotion
```python
PROMOTE_TO_PROGRAMMATIC = True
```

```bash
python3 your_file.py
# → Generates programmatic code
```

### Step 3: Review Generated Code
```python
PROGRAMMATIC_VOICE_GENERATION = '''
def build_score_data_programmatic():
    soprano_events = (
        voice_lookup["THEME"] +
        transpose_events(voice_lookup["THEME"], 7)
    )
    bass_events = voice_lookup["BASS"] * 4
    # ...
'''
```

### Step 4: Modify and Use
1. Copy code out of triple-quoted string
2. Modify as needed
3. Replace `build_score_data()`
4. Run again!

---

## Conversion Cheat Sheet

| Shorthand | Programmatic |
|-----------|--------------|
| `'THEME'` | `voice_lookup["THEME"]` |
| `'THEME * 3'` | `voice_lookup["THEME"] * 3` |
| `'V1 + V2'` | `voice_lookup["V1"] + voice_lookup["V2"]` |
| `'transpose(V, 7)'` | `transpose_events(voice_lookup["V"], 7)` |
| `'invert(V)'` | `invert_events(voice_lookup["V"])` |
| `'retrograde(V)'` | `retrograde_events(voice_lookup["V"])` |

---

## Toggle Reference

| Toggle | Default | When True |
|--------|---------|-----------|
| `PROMOTE_TO_TINYNOTATION` | False | Convert LILY → TINY |
| `PROMOTE_TO_PROGRAMMATIC` | False | Convert Shorthand → Python |

---

## File Outputs

### Standard Run
```
outputs/
├── your_file.ly        # LilyPond source
├── your_file.pdf       # PDF score
├── your_file.midi      # MIDI audio
└── your_file.musicxml  # MusicXML (MuseScore)
```

### After Promotion
```
outputs/
├── your_file.YYYYMMDD_HHMMSS.bak  # Backup
└── your_file.py                    # Copy of modified file
```

---

## Common Workflows

### Workflow 1: Quick Composition
```bash
1. Write shorthand
2. python3 file.py
3. Open outputs/file.pdf or file.musicxml
```

### Workflow 2: Complex Composition
```bash
1. Write shorthand
2. Set PROMOTE_TO_PROGRAMMATIC = True
3. python3 file.py  (generates code)
4. Edit generated code
5. python3 file.py  (use modified code)
6. Open outputs/file.musicxml in MuseScore
```

### Workflow 3: Iterative Development
```bash
1. Write shorthand → test
2. Promote to programmatic
3. Add custom logic
4. Test → export to MuseScore
5. Make final edits in MuseScore
6. Export to PNG/MP3/etc.
```

---

## Documentation

- **Full Guide:** `outputs/DOCUMENTATION/MUSICXML_AND_PROMOTION_GUIDE.md`
- **Implementation:** `outputs/DOCUMENTATION/IMPLEMENTATION_SUMMARY_OCT5.md`
- **This Card:** Quick reference for daily use

---

## Troubleshooting

### MusicXML Issues
**Q:** File not generated?  
**A:** Check console for errors, verify `score_data` is valid

**Q:** MuseScore can't open?  
**A:** Check file size > 0, verify XML well-formed

### Promotion Issues
**Q:** No code generated?  
**A:** Ensure `VOICE_ASSIGNMENTS` exists in file

**Q:** Generated code has errors?  
**A:** Review VOICE_ASSIGNMENTS syntax

---

**Need Help?** Check the full documentation in `outputs/DOCUMENTATION/`
