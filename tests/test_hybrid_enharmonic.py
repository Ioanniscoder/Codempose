import sys
from pathlib import Path

# Add src/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from project_template import engrave_with_abjad


def test_enharmonic_csharp_vs_db():
    sd = {
        'metadata': {'title': 'enharmonic'},
        'parts': {
            'E': [
                {'type': 'note', 'step': 'c', 'alter': 1, 'octave': 4, 'ql': 1.0},
                {'type': 'note', 'step': 'd', 'alter': -1, 'octave': 4, 'ql': 1.0}
            ]
        }
    }
    # Should not raise and should either accept hybrid or fallback gracefully
    engrave_with_abjad(sd, 'test_enharmonic')
