# Metadata-Preserving TinyNotation Format

## 🎯 Overview

The Codempose system now embeds musical metadata directly into TinyNotation strings, making promoted files complete and self-contained.

## 📝 Format Specification

### TinyNotation with Metadata Header

```
time=<time_sig> key=<key_sig> tempo=<bpm> <notes...>
```

### Examples

```python
# Simple example
SOURCE_MELODY_TINY = "time=4/4 c4 d4 e4 f4"

# With key signature
SOURCE_MELODY_TINY = "time=3/4 key=Gmajor d4 e4 f#4"

# Complete metadata
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4 e2 f#4"
```

### Header Format Rules

1. **Position**: Metadata header MUST be at the start of the string
2. **Separator**: Space-separated key=value pairs
3. **Order**: Any order is accepted (time, key, tempo)
4. **Optional**: Any or all metadata fields can be omitted

### Supported Metadata Fields

| Field | Format | Example | Description |
|-------|--------|---------|-------------|
| `time` | `time=<numerator>/<denominator>` | `time=6/4` | Time signature |
| `key` | `key=<Tonic><mode>` | `key=Cmajor`<br>`key=Dminor` | Key signature (tonic capitalized, mode lowercase) |
| `tempo` | `tempo=<bpm>` | `tempo=90` | Tempo in beats per minute |

### Key Signature Format Details

- **Tonic**: Single uppercase letter with optional accidental
  - `C`, `D`, `E`, `F`, `G`, `A`, `B`
  - `C#`, `Db`, `F#`, `Bb`, etc.
- **Mode**: Lowercase mode name (no space)
  - `major`, `minor`
- **Combined**: `Cmajor`, `Dminor`, `F#major`, `Bbminor`

---

## 🔄 Promotion Workflow

### Before Promotion

```python
# In your study file (e.g., first.py)
PROMOTE_TO_TINYNOTATION = True
SOURCE_MELODY_LILY = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 }"
```

### Run Promotion

```bash
python3 first.py
```

### After Promotion

```python
# PROMOTE_TO_TINYNOTATION = False  # Promotion completed, toggle disabled
# SOURCE_MELODY_LILY = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 }"  # Promoted to TinyNotation

# Promoted from LilyPond to TinyNotation
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2 B-4 c2"
```

### Run Again to Process

```bash
python3 first.py
```

### Result

Generated `.ly` file includes complete metadata:

```lilypond
\version "2.24.1"
\header { title = "first" }
\score {
  \new Staff {
    \clef treble
    \time 6/4
    \key c \major
    \tempo 4 = 90
    e,2 bes,4 c2
  }
  \layout { }
  \midi { }
}
```

---

## 🔧 Implementation Details

### Generator: `lily_to_tiny.py`

The `lily_to_tiny_notation()` function now:

1. **Extracts directives** from LilyPond input
2. **Builds metadata header** with key=value pairs
3. **Prepends header** to the note sequence
4. **Returns complete string** with embedded metadata

```python
# Header building logic
header_parts = []
if 'time' in directives:
    header_parts.append(f"time={directives['time']}")
if 'key' in directives:
    # Convert "c \\major" to "Cmajor"
    header_parts.append(f"key={tonic}{mode}")
if 'tempo' in directives:
    # Extract BPM from "4 = 90"
    header_parts.append(f"tempo={bpm}")

header = " ".join(header_parts)
tiny_notation = f"{header} {notes_sequence}"
```

### Consumer: `project_template.py`

The `run_pipeline_from_file()` function now:

1. **Detects metadata header** using regex pattern
2. **Parses key=value pairs** into metadata dictionary
3. **Removes header** from notes string
4. **Passes clean notes** to music21
5. **Populates score_data** with extracted metadata

```python
# Header extraction regex
header_pattern = r'^((?:\w+=[\w/]+\s+)*)'
header_match = re.match(header_pattern, tiny_string)

# Parse key=value pairs
for pair in header_str.split():
    if '=' in pair:
        key, value = pair.split('=', 1)
        # Process each metadata field...

# Remove header from notes
notes_string = tiny_string[len(header):].strip()
```

---

## ✅ Verification

### Test Case: Complete Round-Trip

**Input (LilyPond)**:
```lilypond
\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 }
```

**After Promotion (TinyNotation)**:
```python
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4"
```

**Pipeline Output**:
```
Detected metadata header: time=6/4 key=Cmajor tempo=90
Metadata: {
    'time_signature': '6/4',
    'key_signature': {'tonic': 'c', 'mode': 'major'},
    'tempo': {'beat_duration': 4, 'bpm': 90}
}
```

**Generated LilyPond**:
```lilypond
\time 6/4 \key c \major \tempo 4 = 90
e,2 bes,4 c2 r4
```

✅ **All metadata preserved through the complete cycle!**

---

## 🎓 Benefits

1. **Self-Contained**: TinyNotation files include all necessary musical context
2. **Human-Readable**: Clear key=value format is easy to understand
3. **No Data Loss**: Promotion preserves all metadata from LilyPond
4. **Backward Compatible**: Files without headers still work
5. **Extensible**: Easy to add new metadata fields in the future

---

## 📊 Metadata Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ LILYPOND INPUT                                              │
│ \relative e { \time 6/4 \key c \major \tempo 4=90 e2 ... } │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ lily_to_tiny_notation()                                     │
│ - Extract directives: time=6/4, key=c \major, tempo=4=90   │
│ - Build header: "time=6/4 key=Cmajor tempo=90"             │
│ - Convert notes: "E2 B-4 c2 r4"                            │
│ - Combine: "time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4"    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ PROMOTED FILE                                               │
│ SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2..." │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ run_pipeline_from_file()                                    │
│ - Detect header: "time=6/4 key=Cmajor tempo=90"            │
│ - Parse metadata: time_signature, key_signature, tempo     │
│ - Extract notes: "6/4 E2 B-4 c2 r4" (with time for m21)   │
│ - Build score_data with complete metadata                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ engrave_with_abjad()                                        │
│ - Write \time 6/4                                           │
│ - Write \key c \major                                       │
│ - Write \tempo 4 = 90                                       │
│ - Write notes: e,2 bes,4 c2 r4                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ LILYPOND OUTPUT                                             │
│ \time 6/4 \key c \major \tempo 4 = 90                      │
│ e,2 bes,4 c2 r4                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

Run the test suite:

```bash
# Test metadata embedding
python3 test_lily_to_tiny_debug.py

# Test promotion with metadata
python3 test_promotion_full.py

# Verify first.py still works
python3 first.py
```

All tests passing! ✅
