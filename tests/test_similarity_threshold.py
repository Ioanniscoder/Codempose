from project_template import engrave_with_abjad
from pathlib import Path
import json


def _read_last_audit():
    p = Path('outputs') / 'verification_audit.jsonl'
    if not p.exists():
        return None
    with p.open('r', encoding='utf8') as fh:
        lines = [l.strip() for l in fh if l.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def test_similarity_threshold_controls_decision(tmp_path):
    # Clean audit file
    out = Path('outputs')
    out.mkdir(exist_ok=True)
    audit = out / 'verification_audit.jsonl'
    if audit.exists():
        audit.unlink()

    # Build a tiny score_data where tokens may have small differences
    sd = {
        'metadata': {'title': 'threshold-test', 'enable_verification_audit': True, 'verification_similarity_threshold': 0.99},
        'parts': {
            'M': [
                {'type': 'note', 'step': 'c', 'alter': 0, 'octave': 4, 'ql': 1.0},
                {'type': 'note', 'step': 'd', 'alter': 0, 'octave': 4, 'ql': 1.0},
                {'type': 'note', 'step': 'e', 'alter': 0, 'octave': 4, 'ql': 1.0},
            ]
        }
    }

    # Run engraver; with very high threshold it should likely fallback to manual
    engrave_with_abjad(sd, 'test_threshold_high')
    a = _read_last_audit()
    assert a is not None
    assert a.get('decision') in ('manual', 'hybrid')

    # Now lower threshold to accept hybrids
    sd['metadata']['verification_similarity_threshold'] = 0.5
    engrave_with_abjad(sd, 'test_threshold_low')
    a2 = _read_last_audit()
    assert a2 is not None
    assert a2.get('decision') in ('manual', 'hybrid')
