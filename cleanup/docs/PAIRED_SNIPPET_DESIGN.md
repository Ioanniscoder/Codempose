# PAIRED SNIPPET ARCHITECTURE DESIGN
Date: October 14, 2025

## CURRENT PROBLEM

In thirteenth.py, snippets are handled asymmetrically:

```python
# CURRENT APPROACH (CONFUSING):
THEME_A_LILY = r"""..."""      # Upper staff content
INTERMEZZO_LILY = r"""..."""   # Lower staff content

# Assembly mixes them:
upper_staff.extend(theme_a_events)
lower_staff.extend(create_bar_rests(theme_a_events))  # Generated rests

upper_staff.append({'type': 'rest', 'ql': intermezzo_duration})  # Generated rest
lower_staff.extend(intermezzo_events)
```

**Issues:**
1. Snippets defined separately without clear pairing
2. Rests generated in different sections of code
3. Hard to see which upper snippet pairs with which lower snippet
4. No validation that upper/lower have same duration

---

## PROPOSED ARCHITECTURE: PAIRED SNIPPETS

### Concept

Every musical section is defined as a **pair** of snippets:
```python
SECTION = {
    'name': 'Theme A Original',
    'upper': THEME_A_LILY,
    'lower': 'r',  # Special marker for "generate rests"
    'barline': '||'
}
```

### Complete Example

```python
# ============================================================================
# SNIPPET DEFINITIONS
# ============================================================================

THEME_A_LILY = r"""
\relative c' {
    \time 4/4
    \key c \major
    c4 [d e f]8 e4~ e4 |
    ~g16 a2(p) [b c d]8 c4~ c4 |
    [e f g]8 f4 e2 d4 |
    ~c16 e2~ e4 r2
}
"""

INTERMEZZO_LILY = r"""
\relative c, {
    \time 4/4
    \key c \major
    <c e g>2 <d f a>2 |
    <e g b>2 <f a c>2
}
"""

# ============================================================================
# SCORE STRUCTURE (PAIRED SNIPPETS)
# ============================================================================

SCORE_STRUCTURE = [
    {
        'name': 'Theme A Original',
        'upper': 'THEME_A',
        'lower': 'r',  # Generate matching rests
        'barline': '||'
    },
    {
        'name': 'Intermezzo 1',
        'upper': 'r',  # Generate matching rests
        'lower': 'INTERMEZZO',
        'barline': '||'
    },
    {
        'name': 'Theme A Transposed',
        'upper': 'transpose(THEME_A, P5)',
        'lower': 'r',
        'barline': '||'
    },
    {
        'name': 'Intermezzo 2',
        'upper': 'r',
        'lower': 'INTERMEZZO',
        'barline': '||'
    },
    {
        'name': 'Theme A Inverted',
        'upper': 'invert(THEME_A, C4)',
        'lower': 'r',
        'barline': '||'
    },
    {
        'name': 'Intermezzo 3',
        'upper': 'r',
        'lower': 'INTERMEZZO',
        'barline': '||'
    },
    {
        'name': 'Finale',
        'upper': 'chordify(THEME_A)',
        'lower': 'r',
        'barline': None  # No barline at end
    }
]
```

---

## IMPLEMENTATION

### New Library Function: composition_utils.py

```python
def generate_matching_rests(events: List[dict], time_sig: str = '4/4') -> List[dict]:
    """
    Generate whole-bar rests (r1) matching the duration and measure count of events.
    
    Args:
        events: List of musical events to match
        time_sig: Time signature (e.g., '4/4', '3/4', '6/8')
    
    Returns:
        List of rest events, one r1 per measure
    
    Example:
        >>> events = parse_lilypond("c4 d4 e4 f4 | g2 a2")
        >>> rests = generate_matching_rests(events, '4/4')
        >>> # Returns: [{'type': 'rest', 'ql': 4.0}, {'type': 'rest', 'ql': 4.0}]
    """
    # Parse time signature
    numerator, denominator = map(int, time_sig.split('/'))
    bar_duration = numerator * (4.0 / denominator)
    
    # Calculate total duration and number of measures
    total_ql = sum(e.get('ql', 0) for e in events if e.get('type') != 'barline')
    num_measures = int(round(total_ql / bar_duration))
    
    # Validate: total should be exact multiple of bar duration
    expected_duration = num_measures * bar_duration
    if abs(total_ql - expected_duration) > 0.01:
        print(f"⚠️  Warning: Events total {total_ql} QL, expected {expected_duration} QL "
              f"({num_measures} measures of {time_sig})")
    
    # Create one whole-bar rest per measure
    return [{'type': 'rest', 'ql': bar_duration} for _ in range(num_measures)]


def create_barline(style: str = "||") -> dict:
    """Create a barline event marker."""
    return {'type': 'barline', 'style': style, 'ql': 0.0}


def build_paired_score(
    structure: List[dict],
    snippets: dict,
    metadata: dict
) -> Tuple[List[dict], List[dict]]:
    """
    Build a two-stave score from paired snippet structure.
    
    Args:
        structure: List of section definitions with 'upper' and 'lower' keys
        snippets: Dict mapping snippet names to parsed events
        metadata: Score metadata (time signature, key, etc.)
    
    Returns:
        Tuple of (upper_staff_events, lower_staff_events)
    
    Example:
        >>> structure = [
        ...     {'name': 'Intro', 'upper': 'THEME_A', 'lower': 'r', 'barline': '||'}
        ... ]
        >>> upper, lower = build_paired_score(structure, snippets, metadata)
    """
    upper_staff = []
    lower_staff = []
    time_sig = metadata.get('time_signature', '4/4')
    
    for section in structure:
        section_name = section['name']
        upper_content = section['upper']
        lower_content = section['lower']
        barline_style = section.get('barline')
        
        print(f"  Building section: {section_name}")
        
        # Resolve upper staff
        if upper_content == 'r':
            # Generate rests matching lower staff
            lower_events = _resolve_snippet(lower_content, snippets)
            upper_events = generate_matching_rests(lower_events, time_sig)
        else:
            upper_events = _resolve_snippet(upper_content, snippets)
        
        # Resolve lower staff
        if lower_content == 'r':
            # Generate rests matching upper staff
            lower_events = generate_matching_rests(upper_events, time_sig)
        else:
            lower_events = _resolve_snippet(lower_content, snippets)
        
        # Validate durations match
        upper_ql = sum(e.get('ql', 0) for e in upper_events if e.get('type') != 'barline')
        lower_ql = sum(e.get('ql', 0) for e in lower_events if e.get('type') != 'barline')
        
        if abs(upper_ql - lower_ql) > 0.01:
            print(f"    ⚠️  Duration mismatch: upper={upper_ql} QL, lower={lower_ql} QL")
        else:
            print(f"    ✓ Duration match: {upper_ql} QL")
        
        # Add to staves
        upper_staff.extend(upper_events)
        lower_staff.extend(lower_events)
        
        # Add synchronized barlines
        if barline_style:
            barline = create_barline(barline_style)
            upper_staff.append(barline)
            lower_staff.append(barline)
    
    return upper_staff, lower_staff


def _resolve_snippet(content: str, snippets: dict) -> List[dict]:
    """
    Resolve a snippet reference to events.
    
    Supports:
    - Direct reference: 'THEME_A'
    - Transformation: 'transpose(THEME_A, P5)'
    - Rest marker: 'r' (handled by caller)
    """
    # Simple case: direct snippet reference
    if content in snippets:
        return snippets[content]
    
    # Transformation case: parse and apply
    # (This would use existing transformation parsing logic)
    # For now, simplified:
    return snippets.get(content, [])
```

---

## USAGE IN STUDY FILES

### thirteenth.py (Refactored)

```python
from composition_utils import build_paired_score

def build_score_data() -> Dict[str, Dict]:
    """Build complete feature showcase using paired snippet architecture."""
    
    # Parse all snippets
    theme_a_parsed = parse_lilypond_to_data(THEME_A_LILY, part_name='ThemeA')
    theme_a_events = theme_a_parsed['parts']['ThemeA']
    
    intermezzo_parsed = parse_lilypond_to_data(INTERMEZZO_LILY, part_name='Intermezzo')
    intermezzo_events = intermezzo_parsed['parts']['Intermezzo']
    
    # Generate transformations
    theme_a_part = data_to_part(theme_a_events, theme_a_parsed['metadata'])
    theme_a_transposed = extract_data_from_part(transpose_part(theme_a_part, 'P5'))
    theme_a_inverted = extract_data_from_part(invert_part(theme_a_part, 'C4'))
    theme_a_harmony = extract_data_from_part(chordify_part(theme_a_part))
    
    # Create snippet library
    snippets = {
        'THEME_A': theme_a_events,
        'THEME_A_P5': theme_a_transposed,
        'THEME_A_INV': theme_a_inverted,
        'THEME_A_HARM': theme_a_harmony,
        'INTERMEZZO': intermezzo_events
    }
    
    # Define structure (clear and declarative!)
    structure = [
        {'name': 'Theme A Original', 'upper': 'THEME_A', 'lower': 'r', 'barline': '||'},
        {'name': 'Intermezzo 1', 'upper': 'r', 'lower': 'INTERMEZZO', 'barline': '||'},
        {'name': 'Theme A Transposed', 'upper': 'THEME_A_P5', 'lower': 'r', 'barline': '||'},
        {'name': 'Intermezzo 2', 'upper': 'r', 'lower': 'INTERMEZZO', 'barline': '||'},
        {'name': 'Theme A Inverted', 'upper': 'THEME_A_INV', 'lower': 'r', 'barline': '||'},
        {'name': 'Intermezzo 3', 'upper': 'r', 'lower': 'INTERMEZZO', 'barline': '||'},
        {'name': 'Finale', 'upper': 'THEME_A_HARM', 'lower': 'r', 'barline': None}
    ]
    
    # Build score
    metadata = theme_a_parsed['metadata']
    upper_staff, lower_staff = build_paired_score(structure, snippets, metadata)
    
    # Return as score data
    return {
        'parts': {
            'UpperStaff': upper_staff,
            'LowerStaff': lower_staff
        },
        'metadata': {
            'title': 'Thirteenth Study',
            'time_signature': '4/4',
            'staff_info': {
                'UpperStaff': {'clef': 'treble', 'role': 'melody'},
                'LowerStaff': {'clef': 'bass', 'role': 'harmony'}
            }
        }
    }
```

---

## BENEFITS

1. **Clear Structure**
   - Section order visible at a glance
   - Upper/lower pairing explicit
   - Easy to reorder or add sections

2. **Consistent Rest Generation**
   - Rests generated by single function
   - Always match duration of paired staff
   - Validation catches mismatches

3. **No Scattered Logic**
   - All assembly in one function
   - No manual barline insertion
   - Transformations applied before assembly

4. **Easy to Extend**
   - Add new section: append to structure list
   - Add new transformation: add to snippets dict
   - Change order: reorder structure list

5. **Validated**
   - Duration matching enforced
   - Warnings for mismatches
   - Clear error messages

---

## MIGRATION PATH

1. **Create composition_utils.py** with:
   - `generate_matching_rests()`
   - `create_barline()`
   - `build_paired_score()`

2. **Update thirteenth.py** to use new architecture

3. **Test thoroughly**

4. **Migrate other studies** incrementally

5. **Deprecate old manual assembly pattern**

---

## NEXT STEPS

Ready to implement?

1. Create composition_utils.py
2. Refactor thirteenth.py to use it
3. Verify output matches current version
4. Document new pattern
