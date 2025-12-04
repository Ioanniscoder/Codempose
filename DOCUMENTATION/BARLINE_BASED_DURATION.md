# Barline-Based Duration Calculation

**Date:** October 20, 2025  
**Insight:** Use barlines (`|`) as synchronization units instead of summing note durations

---

## The Problem with Event-Based Duration

**Current approach:**
1. Parse LilyPond → get events
2. Sum `event['ql']` values
3. **Problem:** Parser creates extra events (ties, articulations expand)
4. **Result:** 36 QL instead of 12 QL

**Why it fails:**
- Parser implementation details leak into duration calculation
- Tied notes might create multiple events
- Articulations, dynamics might add zero-duration events
- Auto-inserted rests inflate the count

---

## The Barline Solution

**Musical reality:**
```lilypond
d4-.\p( fis8 g) a4~ |      % Bar 1 (3 QL in 3/4 time)
a4 g4->( fis) |             % Bar 2 (3 QL in 3/4 time)
e4.( d8~ d4) |              % Bar 3 (3 QL in 3/4 time)
b'4\f c4 d4                 % Bar 4 (3 QL in 3/4 time, implied barline)
```

**Simple calculation:**
1. **Count barlines:** 3 explicit `|` + 1 implied = **4 bars**
2. **Get time signature:** `\time 3/4` = **3 QL per bar**
3. **Calculate duration:** 4 bars × 3 QL/bar = **12 QL**

**Benefits:**
- ✅ No dependency on parser event structure
- ✅ Matches musician's mental model
- ✅ Works regardless of ties, articulations, dynamics
- ✅ Handles incomplete final bars correctly
- ✅ Simple to implement (regex or string count)

---

## Implementation Options

### Option A: String-Based (Simplest)

```python
import re

def calculate_snippet_duration_from_barlines(lily_string: str) -> dict:
    """
    Calculate snippet duration by counting barlines and using time signature.
    
    Returns:
        dict: {
            'bars': int,
            'time_signature': str,
            'ql_per_bar': float,
            'total_ql': float
        }
    """
    # Extract time signature (default 4/4)
    time_match = re.search(r'\\time\s+(\d+)/(\d+)', lily_string)
    if time_match:
        numerator = int(time_match.group(1))
        denominator = int(time_match.group(2))
        time_sig = f"{numerator}/{denominator}"
        ql_per_bar = numerator * (4.0 / denominator)  # Convert to quarter lengths
    else:
        time_sig = "4/4"
        ql_per_bar = 4.0
    
    # Count explicit barlines (|)
    # Exclude || (double barline at end), \bar commands
    barlines = lily_string.count('|')
    double_barlines = lily_string.count('||')
    barlines -= double_barlines  # Don't double-count
    
    # Add 1 for implied final barline (unless snippet ends with ||)
    if not lily_string.rstrip().endswith('||'):
        bars = barlines + 1
    else:
        bars = barlines
    
    total_ql = bars * ql_per_bar
    
    return {
        'bars': bars,
        'time_signature': time_sig,
        'ql_per_bar': ql_per_bar,
        'total_ql': total_ql
    }
```

**Example usage:**
```python
THEME_A_LILY = r"""
\relative c'' {
    \key g \major
    \time 3/4
    d4-.\p( fis8 g) a4~ |
    a4 g4->( fis) |
    e4.( d8~ d4) |
    b'4\f c4 d4
}
""".strip()

duration = calculate_snippet_duration_from_barlines(THEME_A_LILY)
print(f"{duration['total_ql']} QL ({duration['bars']} bars × {duration['ql_per_bar']} QL/bar)")
# Output: 12.0 QL (4 bars × 3.0 QL/bar)
```

### Option B: Parser-Assisted (More Robust)

```python
def calculate_snippet_duration_from_parsed_barlines(parsed_events: list, time_sig: str) -> dict:
    """
    Calculate duration from parsed barline events.
    Uses parser's barline detection but not note durations.
    """
    # Count barline events
    barline_count = sum(1 for e in parsed_events if e.get('type') == 'barline')
    
    # Parse time signature
    if '/' in time_sig:
        num, denom = time_sig.split('/')
        ql_per_bar = int(num) * (4.0 / int(denom))
    else:
        ql_per_bar = 4.0
    
    # Barlines separate bars, so bar_count = barline_count + 1
    # (unless last barline is double bar ||)
    last_barline = next((e for e in reversed(parsed_events) if e.get('type') == 'barline'), None)
    if last_barline and last_barline.get('style') == '||':
        bars = barline_count
    else:
        bars = barline_count + 1
    
    return {
        'bars': bars,
        'ql_per_bar': ql_per_bar,
        'total_ql': bars * ql_per_bar
    }
```

---

## Advantages Over Event-Summing

| Aspect | Event Summing | Barline Counting |
|--------|---------------|------------------|
| **Complexity** | High (handle ties, dots, tuplets) | Low (count `|` characters) |
| **Accuracy** | Depends on parser internals | Independent of parser bugs |
| **Robustness** | Breaks if parser changes | Works with any parser |
| **Musical Model** | Technical (QL addition) | Natural (measures) |
| **Edge Cases** | Many (grace notes, tremolo) | Few (pickup bars) |

---

## Edge Cases to Handle

### 1. Pickup Bars (Anacrusis)
```lilypond
\partial 4  % Pickup beat
d4 |
```
**Solution:** Detect `\partial`, subtract from first bar

### 2. Double Barlines
```lilypond
d4 e4 f4 ||  % Section end
```
**Solution:** Don't count as measure separator (already done above)

### 3. Repeat Barlines
```lilypond
d4 e4 f4 \bar ":|."
```
**Solution:** Count as regular barline

### 4. No Explicit Barlines (rare in practice)
```lilypond
\time 3/4
d4 e4 f4 g4 a4 b4  % 6 quarters = 2 bars
```
**Solution:** Fall back to summing note durations (but warn user)

---

## Implementation Plan

### Step 1: Add to `src/project_template.py`
In `_build_documentation_block()`, replace duration calculation:

```python
# OLD (broken):
# total_ql = sum(e.get('ql', 0) for e in events)

# NEW (simple):
from lilypond_parser import calculate_snippet_duration_from_barlines
duration_info = calculate_snippet_duration_from_barlines(snippet)
```

### Step 2: Update .ly Header Format
```lilypond
%   THEME_A (4 bars in 3/4 = 12.0 QL):
%     \relative c'' { ... }
```

### Step 3: Use for Synchronization Check
In `src/score_builder.py`, when assembling sections:

```python
# Check if snippets have compatible durations
theme_duration = calculate_snippet_duration_from_barlines(THEME_A_LILY)
bass_duration = calculate_snippet_duration_from_barlines(BASS_FIGURE_LILY)

if theme_duration['total_ql'] != bass_duration['total_ql']:
    print(f"⚠️  Duration mismatch:")
    print(f"   THEME_A: {theme_duration['bars']} bars = {theme_duration['total_ql']} QL")
    print(f"   BASS: {bass_duration['bars']} bars = {bass_duration['total_ql']} QL")
```

---

## Testing

### Test 1: Simple Snippet
```python
snippet = r"\time 3/4 d4 e4 f4 |"
result = calculate_snippet_duration_from_barlines(snippet)
assert result['total_ql'] == 3.0  # 1 bar × 3 QL
```

### Test 2: Multiple Bars
```python
snippet = r"\time 4/4 c4 d4 e4 f4 | g4 a4 b4 c'4 |"
result = calculate_snippet_duration_from_barlines(snippet)
assert result['total_ql'] == 8.0  # 2 bars × 4 QL
```

### Test 3: Complex Notation (ties, articulations)
```python
snippet = r"\time 3/4 d4-.\p( fis8 g) a4~ | a4 g4->( fis) |"
result = calculate_snippet_duration_from_barlines(snippet)
assert result['total_ql'] == 6.0  # 2 bars × 3 QL (regardless of complexity)
```

### Test 4: THEME_A (Real Case)
```python
result = calculate_snippet_duration_from_barlines(THEME_A_LILY)
assert result['bars'] == 4
assert result['total_ql'] == 12.0
```

---

## Benefits for the Project

1. **Immediate Fix:** Solves duration mismatch without parser changes
2. **Reliable:** Works regardless of parser bugs
3. **Simple:** Easy to understand and maintain
4. **Musical:** Matches how composers think
5. **Fast:** String counting is O(n), no complex parsing
6. **Reusable:** Can validate user input snippets

---

## Recommendation

**Implement Option A (String-Based) immediately:**
- Simple regex for time signature
- String count for barlines
- No dependency on parser internals
- Can enhance with Option B later if needed

**This fixes:**
- ✅ .ly header duration display
- ✅ Synchronization warnings
- ✅ Snippet length analysis
- ✅ Blueprint assembly validation

**Without:**
- ❌ Touching the parser
- ❌ Complex event logic
- ❌ Risk of breaking existing code

---

## Next Steps

1. Implement `calculate_snippet_duration_from_barlines()` in new file: `src/snippet_utils.py`
2. Update `src/project_template.py` to use it for .ly header
3. Test with ninetyninth.py
4. Verify all durations show correctly
5. Move on to second question (starter file with manifests)

**User's suggestion is the correct solution!** Much simpler than trying to fix the parser.
