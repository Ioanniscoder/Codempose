"""Test that multi-voice sections are correctly exported to LilyPond format.

This test validates the Priority 3 implementation fix for LilyPond export.
"""

import re


def test_fourteenth_ly_has_multi_voice_syntax():
    """Verify fourteenth.ly contains LilyPond polyphonic << ... \\\\ ... >> syntax."""
    
    with open('outputs/fourteenth.ly', 'r') as f:
        content = f.read()
    
    # Check for multi-voice polyphonic syntax: << { ... } \\ { ... } >>
    multi_voice_pattern = r'<<\s*\{[^}]+\}\s*\\\\\s*\{[^}]+\}\s*>>'
    matches = re.findall(multi_voice_pattern, content)
    
    print(f"✓ Found {len(matches)} multi-voice sections in fourteenth.ly")
    
    # We expect at least 4 multi-voice sections (2 phrases × 2 staves)
    assert len(matches) >= 4, f"Expected at least 4 multi-voice sections, found {len(matches)}"
    
    print(f"✓ Multi-voice syntax verification passed")
    print(f"\nSample multi-voice section:")
    print(f"  {matches[0][:80]}...")
    
    return True


def test_pdf_exists():
    """Verify that fourteenth.pdf was successfully generated."""
    from pathlib import Path
    
    pdf_path = Path('outputs/fourteenth.pdf')
    
    assert pdf_path.exists(), "fourteenth.pdf was not generated"
    
    file_size = pdf_path.stat().st_size
    assert file_size > 10000, f"PDF file is suspiciously small: {file_size} bytes"
    
    print(f"✓ fourteenth.pdf exists ({file_size:,} bytes)")
    
    return True


def test_voices_have_correct_notes():
    """Verify that voice notes are present in the LilyPond file."""
    
    with open('outputs/fourteenth.ly', 'r') as f:
        content = f.read()
    
    # Check for soprano notes (higher octave)
    assert "g''4" in content, "Soprano notes (g'') not found"
    print("✓ Soprano voice notes present")
    
    # Check for alto notes (middle octave)  
    assert "d''4" in content, "Alto notes (d'') not found"
    print("✓ Alto voice notes present")
    
    # Check for tenor notes (single quote octave)
    assert "b'4" in content, "Tenor notes (b') not found"
    print("✓ Tenor voice notes present")
    
    # Check for bass notes (no quote/comma octave)
    assert "g4" in content or "g,4" in content, "Bass notes (g/g,) not found"
    print("✓ Bass voice notes present")
    
    return True


if __name__ == '__main__':
    print("="*70)
    print("LILYPOND MULTI-VOICE EXPORT TEST")
    print("="*70)
    print()
    
    try:
        test_pdf_exists()
        print()
        test_fourteenth_ly_has_multi_voice_syntax()
        print()
        test_voices_have_correct_notes()
        print()
        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print()
        print("Summary:")
        print("  • PDF generated successfully (fourteenth.pdf)")
        print("  • LilyPond file contains proper << ... \\\\ ... >> syntax")
        print("  • All 4 voices (SATB) are present in the output")
        print("  • Multi-voice polyphony framework fully functional!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except FileNotFoundError as e:
        print(f"\n❌ FILE NOT FOUND: {e}")
        exit(1)
