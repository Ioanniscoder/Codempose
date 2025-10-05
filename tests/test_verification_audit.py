import json
import os
from project_template import engrave_with_abjad


def test_verification_audit_written(tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    out_file = str(out_dir / "audit_test")
    sd = {
        'metadata': {'title': 'audit-test', 'enable_verification_audit': True},
        'parts': {
            'M': [
                {'type': 'note', 'step': 'c', 'alter': 0, 'octave': 4, 'ql': 1.0},
            ]
        }
    }

    # Run engraver; it should write a verification_audit.jsonl into out_dir
    engrave_with_abjad(sd, out_file)

    audit_path = out_dir / 'verification_audit.jsonl'
    assert audit_path.exists(), f"audit file not created: {audit_path}"

    # Parse last line and check fields
    with open(audit_path, 'r', encoding='utf8') as fh:
        lines = [l for l in fh.read().splitlines() if l.strip()]
    assert lines, 'audit file is empty'
    j = json.loads(lines[-1])
    assert 'timestamp' in j and 'decision' in j and 'similarity' in j and 'output_file' in j
    assert j['output_file'].endswith('audit_test')
