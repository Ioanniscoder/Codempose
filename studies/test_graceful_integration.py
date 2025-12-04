#!/usr/bin/env python3
"""
Integration Test Study: Graceful Degradation
=============================================

This study tests all four scenarios from the review feedback:
1. Transformation with valid syntax → Parse and transform
2. Transformation with potentially problematic syntax → Should still work or error gracefully
3. Display-only with complex syntax → Bypass with warning  
4. Display-only with simple syntax → Parse or bypass

"""

METADATA = {
    'title': 'Integration Test: Graceful Degradation',
    'composer': 'Test Suite',
    'opus': 'Test-2025'
}

# Snippet 1: Simple, always parses successfully
SIMPLE = r"""
\relative c' {
  c4 d e f
}
"""

# Snippet 2: With standard LilyPond articulations (should parse with new code)
WITH_ARTICULATIONS = r"""
\relative c' {
  c4-. d4-> e4-^ f4--
}
"""

# Snippet 3: With dynamics (should parse with new code)
WITH_DYNAMICS = r"""
\relative c' {
  c4\p d4\mp e4\mf f4\f
}
"""

# Snippet 4: Mixed standard + lilyshorthand (testing dual support)
MIXED = r"""
\relative c' {
  c4-. d4(.) e4\p f4(p)
}
"""

# Blueprint: Test transformation vs display-only
VOICE_STAVE_DEF = "UpperStaff"

VOICE_STAVE_DATA = r"""
transpose_part(SIMPLE, 'P5');
transpose_part(WITH_ARTICULATIONS, 'M3');
WITH_DYNAMICS;
MIXED
"""
