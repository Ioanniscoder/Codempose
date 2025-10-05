# Codempose Architecture

## Design Philosophy

Codempose implements a **two-tiered hybrid architecture** that separates simple declarative operations from complex programmatic transformations. This design choice emerged from careful consideration of Domain-Specific Language (DSL) design principles and the inherent complexity of musical composition.

## The Hybrid Model

### Tier 1: Composition Shorthand (`composition_shorthand.py`)

**Purpose**: Declarative functions for common musical operations

**Characteristics**:
- Simple argument types (strings, numbers, basic lists)
- Direct, readable function calls
- Context-independent transformations
- Minimal parsing complexity

**Example Operations**:
```python
from_roman_numerals("I-V-vi-IV", "C", "w-w-w-w")
from_scale_degrees("1-3-5-3-1", "C", "q-q-q-q-h")
augment(theme, 2.0)
```

**Design Rationale**:
- 80% of musical operations are simple and repetitive
- Readable code improves maintainability
- No complex parser needed
- Easy to test and debug

### Tier 2: Advanced Transformations (`advanced_transformations.py`)

**Purpose**: Complex, music-theory-aware transformations

**Characteristics**:
- Complex argument types (lists, dictionaries, multiple parameters)
- Full access to music21 API
- Context-aware operations
- Sophisticated algorithms

**Example Operations**:
```python
create_melodic_sequence(theme, interval_pattern=[-2, -2, 2])
realize_figured_bass(bass_line, figures="6 6 5 6/4 3")
apply_modal_mixture(melody, key='C major', borrow_from='parallel_minor')
```

**Design Rationale**:
- 20% of operations require sophisticated logic
- Direct Python code is clearer than complex string parsing
- Type hints enable IDE support
- Easy to extend with new algorithms

## Why Not a Unified Shorthand?

### The Parser Complexity Problem

Attempting to handle complex operations in shorthand leads to:

```python
# This would require a full expression parser:
'sequence(THEME, intervals=[-2, -2, 2], rhythm="augment")'
'canon(THEME, interval=7, delay=2.0, key="C major", strict_counterpoint=True)'

# Problems:
- List parsing: [-2, -2, 2]
- Keyword arguments: intervals=...
- String literals: "augment"
- Nested structures
- Type validation
```

**Result**: The parser becomes as complex as Python itself, duplicating functionality while adding fragility.

### The Leaky Abstraction Problem

Advanced transformations need context:

```python
borrow_from_minor(THEME)  # Needs: current key signature
tonicize(THEME, degree=5)  # Needs: tonal context, scale
voice_lead(SOPRANO, ALTO)  # Needs: both voices simultaneously
```

**Result**: Shorthand can't provide this context without becoming as complex as the code it's trying to simplify.

## Event Dictionary Format

All functions communicate through a canonical event dictionary format:

```python
# Note
{
    'type': 'note',
    'step': 'C',
    'octave': 4,
    'alter': 0,
    'ql': 1.0
}

# Rest
{
    'type': 'rest',
    'ql': 1.0
}

# Chord
{
    'type': 'chord',
    'ql': 1.0,
    'pitches': [
        {'step': 'C', 'octave': 4, 'alter': 0},
        ...
    ]
}
```

**Benefits**:
- Language-agnostic representation
- Easy to serialize/deserialize
- Decouples composition from engraving
- Testable in isolation

## Data Flow

```
┌──────────────────────────────────────────┐
│ User Code (build_score_data)            │
│                                          │
│ - Uses composition_shorthand functions  │
│ - Uses advanced_transformations         │
│ - Combines results                       │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│ Event Dictionaries                       │
│                                          │
│ - Canonical representation               │
│ - JSON-serializable                      │
│ - Framework-agnostic                     │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│ Engraving Layer (engrave_with_abjad)    │
│                                          │
│ - Converts to music21/Abjad             │
│ - Generates LilyPond                     │
│ - Produces PDF                           │
└──────────────────────────────────────────┘
```

## Extension Guidelines

### Adding a Shorthand Function

**When to add to `composition_shorthand.py`**:
- ✅ Arguments are simple (strings, numbers)
- ✅ Operation is context-independent
- ✅ Common enough to warrant shorthand
- ✅ Clear, unambiguous semantics

**Template**:
```python
def my_shorthand_function(param1: str, param2: int) -> List[Dict[str, Any]]:
    """
    Clear description.
    
    Args:
        param1: Simple description
        param2: Simple description
    
    Returns:
        List of event dictionaries
    
    Example:
        >>> events = my_shorthand_function("arg", 5)
    """
    # Implementation
    return events
```

### Adding an Advanced Function

**When to add to `advanced_transformations.py`**:
- ✅ Complex arguments needed (lists, dicts, multiple kwargs)
- ✅ Requires music theory knowledge
- ✅ Needs full music21 API access
- ✅ Context-dependent operation

**Template**:
```python
def my_advanced_function(
    events: List[Dict[str, Any]],
    complex_param: List[int],
    key: str = 'C major',
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Detailed description of the transformation.
    
    This function implements [music theory concept] by [algorithm].
    
    Args:
        events: The input events to transform
        complex_param: Description of complex parameter
        key: Musical key context (default: 'C major')
        **kwargs: Additional options
    
    Returns:
        Transformed event list
    
    Example:
        >>> result = my_advanced_function(
        ...     events=theme,
        ...     complex_param=[1, 2, 3],
        ...     key='D major'
        ... )
    
    Note:
        Additional implementation details, limitations, or theory references.
    """
    # Implementation with full Python power
    return transformed_events
```

## Benefits of This Architecture

### 1. Clarity of Intent

**Shorthand**:
```python
theme = from_scale_degrees("1-3-5", "C", "q-q-q")
```
Clear, readable, instantly understandable.

**Programmatic**:
```python
sequence = create_melodic_sequence(theme, interval_pattern=[-2, -2, 2])
```
Explicit parameters, type safety, IDE support.

### 2. Easy to Test

Each layer can be tested independently:
- Shorthand functions: Simple input/output tests
- Advanced functions: Complex scenario tests
- Integration: Combine both in realistic compositions

### 3. Scalable

- Add new shorthand functions without affecting advanced ones
- Add new advanced functions without changing shorthand
- Both can evolve independently

### 4. Gradual Learning Curve

Users can:
1. Start with simple shorthand functions
2. Gradually learn advanced functions
3. Eventually contribute new transformations

### 5. Best of Both Worlds

- **Shorthand**: Elegance and readability for common operations
- **Programmatic**: Unlimited power for complex transformations
- **Hybrid**: Use the right tool for each task

## Comparison with Alternatives

### Alternative 1: Everything in Shorthand

**Problems**:
- Parser becomes extremely complex
- Error messages become cryptic
- Hard to extend
- Debugging is difficult

### Alternative 2: Everything Programmatic

**Problems**:
- Verbose for simple operations
- Repetitive code
- Harder to read
- Steeper learning curve

### Alternative 3: Hybrid Model (Our Choice)

**Advantages**:
- Simple things are simple
- Complex things are possible
- Clear separation of concerns
- Easy to maintain and extend

## Conclusion

The hybrid architecture is not a compromise—it's the optimal design. It recognizes that:

1. **Simple operations should be simple**: Shorthand provides elegance
2. **Complex operations need power**: Programmatic code provides flexibility
3. **Both are valuable**: Use the right tool for each task

This architecture enables Codempose to be both **approachable for beginners** and **powerful for experts**, while maintaining **clean, maintainable code** throughout.
