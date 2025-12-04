#!/usr/bin/env python3
"""
Test script to demonstrate enhanced parser debug output
"""

import sys
sys.path.insert(0, '/workspaces/Codempose/src')

# Create a test study with an intentionally problematic snippet
test_study = """
from src.score_builder import build_score_from_blueprint

# Define metadata
metadata = {
    'title': 'Parser Debug Test',
    'composer': 'Test',
    'original_snippets': {
        # This snippet has problematic syntax that should trigger debug output
        'BROKEN_SNIPPET': r'''
\\relative c'' {
    \\tempo "Allegro"
    \\time 4/4
    c4 d e f
    % This has weird characters: ♪ ♫ ♬
    g4 a b c
    % Missing duration here might break things
    d e f g
}
''',
        'GOOD_SNIPPET': r'''
\\relative c' {
    c4 d e f
}
'''
    }
}

# Test 1: Good snippet (should work)
print("\\n" + "="*70)
print("TEST 1: Good snippet (should parse successfully)")
print("="*70)

layout_good = ['Piano']
sections_good = [
    {'Piano': ['GOOD_SNIPPET']}
]

try:
    result = build_score_from_blueprint(layout_good, sections_good, metadata)
    print("✓ Test 1 PASSED: Good snippet parsed successfully")
except Exception as e:
    print(f"✗ Test 1 FAILED: {e}")

# Test 2: Broken snippet (should trigger debug output)
print("\\n" + "="*70)
print("TEST 2: Broken snippet (should trigger debug output)")
print("="*70)

layout_broken = ['Piano']
sections_broken = [
    {'Piano': ['BROKEN_SNIPPET']}
]

try:
    result = build_score_from_blueprint(layout_broken, sections_broken, metadata)
    print("Note: If you see comprehensive debug output above, the system is working!")
    print("✓ Test 2: Debug output generated (check output above)")
except Exception as e:
    print(f"Test 2: Exception raised - {type(e).__name__}: {e}")
    print("✓ Debug output should have been generated above")

print("\\n" + "="*70)
print("TESTS COMPLETE")
print("="*70)
print("Expected behavior:")
print("1. Good snippet should parse without errors")
print("2. Broken snippet should trigger comprehensive debug output showing:")
print("   - Snippet name and type")
print("   - Error type and message")
print("   - Original LilyPond input")
print("   - Tokenization attempt (success/failure)")
print("   - Full traceback")
print("   - Bypass attempt result")
print("="*70)
"""
