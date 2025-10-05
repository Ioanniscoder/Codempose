# LilyPond Shorthand → TinyNotation Parser

## Overview

This isolated parser project converts a custom LilyPond-inspired shorthand notation into music21's TinyNotation format, with rich metadata tracking for review and debugging.

## Architecture

```
LilyPond Shorthand → lily_to_tiny_notation() → ParseResult
                                                    ├─ tiny_notation (string for music21)
                                                    ├─ tokens[] (detailed metadata)
                                                    ├─ directives{} (time/key/tempo)
                                                    └─ warnings[] (global issues)
```

## Supported Syntax

### Note Tokens
- **Basic notes**: `c`, `d`, `e`, `f`, `g`, `a`, `b`
- **Octave markers**: `c'` (up), `c''` (2 up), `c,` (down), `c,,` (2 down)
- **Accidentals**: `fis`/`f#` (sharp), `bes`/`bmol`/`bemol` (flat)
- **Durations**: `4` (quarter), `8` (eighth), `2` (half), `2.` (dotted)
- **Rests**: `r4`, `r2`, etc.

### Directives
- **Time signature**: `\time 6/4`
- **Key signature**: `\key c \major`
- **Tempo**: `\tempo 4=90`
- **Relative mode**: `\relative c' { ... }`

### Example
```lilypond
\relative e { \time 6/4 \key c \major e2 bmol4 c2 r4 | e2 f#4 e2 r4 }
```

Converts to:
```
6/4 E2 Bb4 C2 r4 E2 F#4 E2 r4
```

## Modules

- **`data_structures.py`**: `ParseResult` and `TokenInfo` dataclasses
- **`lily_tokenizer.py`**: Regex-based tokenization
- **`lily_token_parser.py`**: Individual token parsing with relative logic
- **`lily_to_tiny.py`**: Main conversion function

## Usage

```python
from lily_to_tiny import lily_to_tiny_notation

result = lily_to_tiny_notation(r"\relative c' { c4 d e f }")

# Use the TinyNotation output
print(result.tiny_notation)  # "4/4 C4 D4 E4 F4"

# Review warnings
if result.has_warnings():
    print(result.format_review())

# Get flagged tokens
for token in result.flagged_tokens():
    print(f"{token.original} → {token.converted}: {token.warnings}")
```

## Testing

Run all tests:
```bash
cd parser_project
python -m unittest discover -v
```

Run specific test file:
```bash
python -m unittest test_data_structures.py -v
```

## Development Status

✅ **COMPLETE - ALL PHASES IMPLEMENTED AND TESTED**

- [x] Phase 1: Data structures (`ParseResult`, `TokenInfo`) - 11 tests passing
- [x] Phase 2: Tokenizer (regex extraction) - Fully functional
- [x] Phase 3: Token parser (pitch/duration/accidentals) - Fully functional
- [x] Phase 4: Relative octave logic - Fully functional
- [x] Phase 5: Main converter function - Fully functional
- [x] Phase 6: Comprehensive test suite - **28/28 tests passing ✅**

**Status**: Production-ready. Ready for integration with main project.

See `COMPLETION_REPORT.md` for detailed implementation summary.

## Design Principles

1. **Single Responsibility**: Each module has one clear job
2. **Test-Driven**: Write tests first, then implementation
3. **Metadata Preservation**: Never lose diagnostic information
4. **Clean Separation**: TinyNotation output is pure (no embedded warnings)
5. **Human-Readable**: All warnings and reviews are clear English
