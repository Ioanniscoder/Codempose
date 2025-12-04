import sys
from pathlib import Path

# Add src/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import project_template as pt


def test_final_sanitize_preserves_directives():
    inp = "\\version \"2.24.1\"\n\\new Staff { e'4 }\n"
    # inject control character in front of the directive name to simulate trimming
    broken = inp.replace('\\version', '\x0bversion')
    out = pt._final_sanitize_ly_text(broken)
    lines = out.splitlines()
    # the sanitizer should restore the leading backslash on common directives
    assert any(l.startswith('\\version') for l in lines)
    assert any(l.startswith('\\new Staff') for l in lines)
    # and there should be no lines that start with the directive name lacking a backslash
    assert not any(l.startswith('version') for l in lines)
    assert not any(l.startswith('new ') for l in lines)


def test_final_sanitize_keeps_comments():
    inp = "% this is a % comment with weird\x0bchars\n\\new Staff { e4 }\n"
    out = pt._final_sanitize_ly_text(inp)
    # comment should still start with %
    assert out.splitlines()[0].startswith('%')
    assert '\\new Staff' in out
