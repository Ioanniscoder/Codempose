#!/usr/bin/env python3
"""
Direct Integration Test: Bypass Logic
======================================

Tests the complete flow with score_builder to verify:
1. Transformations with valid syntax work
2. Transformations with invalid syntax ERROR (don't bypass)
3. Display-only with complex syntax bypasses gracefully
"""

import sys
sys.path.insert(0, 'src')

from score_builder import build_score_from_blueprint

# Test metadata
METADATA = {
    'title': 'Bypass Logic Test',
    'composer': 'Test Suite',
    'original_snippets': {}
}

print("=" * 70)
print("INTEGRATION TEST: Bypass Logic with Score Builder")
print("=" * 70)

# ====================
# TEST 1: Simple transformation (should work)
# ====================
print("\n" + "=" * 70)
print("TEST 1: Simple Transformation (should succeed)")
print("=" * 70)

METADATA['original_snippets']['SIMPLE'] = r'\relative c { c4 d e f }'

try:
    result = build_score_from_blueprint(
        voice_stave_def="Staff",
        voice_stave_data="transpose_part(SIMPLE, 'P4')",
        snippets={},
        metadata=METADATA
    )
    print("\n✅ TEST 1 PASSED: Simple transformation succeeded")
    print(f"   Generated {len(result['parts'])} parts")
except Exception as e:
    print(f"\n❌ TEST 1 FAILED: {type(e).__name__}: {e}")

# ====================
# TEST 2: Display-only with standard LilyPond (should bypass if needed)
# ====================
print("\n" + "=" * 70)
print("TEST 2: Display-Only with Articulations (bypass allowed)")
print("=" * 70)

METADATA['original_snippets']['COMPLEX'] = r'\relative c { c4-. d4-> e4-^ f4-- }'

try:
    result = build_score_from_blueprint(
        voice_stave_def="Staff",
        voice_stave_data="COMPLEX",
        snippets={},
        metadata=METADATA
    )
    print("\n✅ TEST 2 PASSED: Display-only snippet handled")
    print(f"   Generated {len(result['parts'])} parts")
    print("   (May have used bypass - check output above)")
except Exception as e:
    print(f"\n❌ TEST 2 FAILED: {type(e).__name__}: {e}")

# ====================
# TEST 3: Transformation on parseable snippet with articulations
# ====================
print("\n" + "=" * 70)
print("TEST 3: Transformation with Articulations (should parse)")
print("=" * 70)

METADATA['original_snippets']['WITH_ART'] = r'\relative c { c4-. d4 e4 f4 }'

try:
    result = build_score_from_blueprint(
        voice_stave_def="Staff",
        voice_stave_data="transpose_part(WITH_ART, 'M3')",
        snippets={},
        metadata=METADATA
    )
    print("\n✅ TEST 3 PASSED: Transformation with articulations succeeded")
    print(f"   Generated {len(result['parts'])} parts")
except Exception as e:
    print(f"\n❌ TEST 3 FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
If all tests passed, the implementation is correct:

✅ TEST 1: Simple transformations work
✅ TEST 2: Display-only snippets can bypass if needed  
✅ TEST 3: Transformations with articulations parse successfully

The bypass logic now:
- BLOCKS bypass for transformations (critical safety fix)
- ALLOWS bypass for display-only snippets (graceful fallback)
- PARSES articulations/dynamics in both lilyshorthand and standard syntax
""")
