import sys
from pathlib import Path

# Add src/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from project_template import engrave_with_abjad


def test_hybrid_attempt_when_no_relative():
    sd = {
        'metadata': {'title': 'no-relative-hybrid', 'original_input': 'c d e f'},
        'parts': {
            'M': [
                {'type': 'note', 'step': 'c', 'alter': 0, 'octave': 4, 'ql': 1.0},
                {'type': 'note', 'step': 'd', 'alter': 0, 'octave': 4, 'ql': 1.0}
            ]
        }
    }
    # Should not raise
    engrave_with_abjad(sd, 'test_no_relative')
