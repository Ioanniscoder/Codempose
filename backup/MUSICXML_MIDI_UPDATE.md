# MusicXML and MIDI Output Update Summary

**Date:** October 22, 2025  
**Status:** Code updated, requires music21 environment for testing

## Problem Statement

After implementing barline validation for LilyPond parsing, the MusicXML and MIDI outputs were not reflecting the corrected barline structure. Issues:

1. **MusicXML**: Only 2 barlines total, wrong measure count
2. **Time signature**: Showing 4/4 instead of 3/4
3. **Measure structure**: Not respecting validated barlines

## Root Cause

The `data_to_part()` function in `music_data.py` was ignoring barline events:
- Line 101-103: Barline events returned `None`
- Comment said "Barlines are typically handled at the measure level"
- music21 was auto-generating measures, not using our validated barlines

## Solution

### 1. LilyPond Documentation Output

**File:** `src/lily_converter.py` (lines 20-24)

Added barline handling to `events_to_lily()`:
```python
# Handle barlines
if ev.get('type') == 'barline':
    barline_style = ev.get('style', '|')
    lily_tokens.append(barline_style)
    continue
```

**Purpose:** When programmatic voices are documented, barlines now appear in the LilyPond snippets.

**Impact:** Low - only affects documentation output, doesn't touch main .ly generation.

### 2. MusicXML/MIDI Measure Creation

**File:** `src/music_data.py` (lines 116-159)

Complete rewrite of `data_to_part()` to create measures from barlines:

**Before:**
```python
def data_to_part(events: list, metadata: dict = None):
    part = music21.stream.Part()
    for ev in events:
        # ... process notes/rests
        if ev.get('type') == 'barline':
            return None  # Ignored!
```

**After:**
```python
def data_to_part(events: list, metadata: dict = None):
    part = music21.stream.Part()
    
    # Detect if events include barlines
    has_barlines = any(ev.get('type') == 'barline' for ev in events)
    
    if has_barlines:
        # Create explicit measures based on barline positions
        current_measure = music21.stream.Measure()
        measure_number = 1
        
        # Add metadata to first measure
        if metadata:
            if 'time_signature' in metadata:
                # Parse "3/4" → TimeSignature(3/4)
                num, denom = map(int, time_sig.split('/'))
                current_measure.timeSignature = music21.meter.TimeSignature(f'{num}/{denom}')
            
            if 'key_signature' in metadata:
                # Parse {'tonic': 'g', 'mode': 'major'} → Key('g', 'major')
                current_measure.keySignature = music21.key.Key(tonic, mode)
        
        for ev in events:
            if ev.get('type') == 'barline':
                # Finalize current measure
                current_measure.number = measure_number
                part.append(current_measure)
                
                # Start new measure
                current_measure = music21.stream.Measure()
                measure_number += 1
            else:
                # Add note/rest/chord to current measure
                element = _event_to_music21(ev)
                if element:
                    current_measure.append(element)
        
        # Append final measure if it has content
        if len(current_measure) > 0:
            current_measure.number = measure_number
            part.append(current_measure)
        
        return part
    
    # Fallback: original behavior for backward compatibility
    # (for events without barlines)
```

**Key Features:**
- ✅ Detects barline events automatically
- ✅ Creates explicit music21.Measure objects
- ✅ Adds time signature to first measure
- ✅ Adds key signature to first measure
- ✅ Numbers measures correctly
- ✅ Handles final incomplete measure
- ✅ Backward compatible (fallback to old behavior if no barlines)

## Expected Results

### Before Changes:
```
MusicXML: 6 measures total (auto-generated, incorrect boundaries)
Barlines: 2 explicit barline tags
Time signature: 4/4 (default)
```

### After Changes:
```
MusicXML: ~20+ measures (one per barline from validated structure)
Barlines: Implicit in measure boundaries
Time signature: 3/4 (from metadata)
Key signature: G major (from metadata)
Measures: Aligned with validated barlines from token-level parsing
```

## Impact on MIDI

MIDI files automatically inherit timing from music21 Measure objects:
- ✅ Correct measure boundaries
- ✅ Proper time signature
- ✅ Accurate note timing
- ✅ Better playback synchronization

## Testing Required

Since music21 is not available in this environment, testing requires:

1. **Regenerate Study 100:**
   ```bash
   python3 generate_study.py 100
   ```

2. **Verify MusicXML measure count:**
   ```bash
   grep '<measure' outputs/100th.musicxml | wc -l
   # Expected: ~40 (20 per staff × 2 staves)
   ```

3. **Check time signature:**
   ```bash
   grep '<beats>' outputs/100th.musicxml | head -2
   # Expected: <beats>3</beats>
   ```

4. **Verify key signature:**
   ```bash
   grep '<key>' outputs/100th.musicxml -A 3 | head -6
   # Expected: G major (1 sharp)
   ```

5. **Test MIDI playback:**
   - Open `outputs/100th.midi` in a MIDI player
   - Verify 3/4 time signature
   - Check bar divisions align with score

## Files Modified

1. **src/lily_converter.py**
   - Lines 20-24: Added barline handling to `events_to_lily()`
   - Purpose: Documentation of programmatic voices

2. **src/music_data.py**
   - Lines 116-159: Complete rewrite of `data_to_part()` barline handling
   - Lines 127-145: Added metadata extraction (time/key signature)
   - Purpose: Proper MusicXML/MIDI export with measures

3. **test_musicxml_output.py** (NEW)
   - Test script explaining the changes
   - Shows expected behavior without requiring music21

## Backward Compatibility

✅ **Fully backward compatible:**
- Events without barlines use original behavior
- Old code paths preserved via fallback
- No breaking changes to existing functionality

## Integration with Barline Validation

This completes the barline validation feature:

1. **Tokenizer**: Extracts barlines from LilyPond (`src/lily_tokenizer.py`)
2. **Parser**: Validates barlines at token level (`src/lilypond_parser.py`)
3. **LilyPond Export**: Barlines preserved in .ly output (via bypass)
4. **Documentation**: Barlines shown in programmatic voice docs (`src/lily_converter.py`) ✅ NEW
5. **MusicXML/MIDI**: Measures created from validated barlines (`src/music_data.py`) ✅ NEW

## Next Steps

1. Test in environment with music21 installed
2. Verify MusicXML structure matches LilyPond output
3. Confirm MIDI playback timing is correct
4. Update main tarball with these changes
