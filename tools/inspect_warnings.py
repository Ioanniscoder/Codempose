import importlib.util
from pathlib import Path
import sys

# Ensure the workspace root is on sys.path so imports like 'music_data'
# and other local modules inside lilypond_parser resolve correctly.
workspace_root = str(Path(__file__).resolve().parents[1])
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

lp_path = Path(__file__).resolve().parents[1] / 'lilypond_parser.py'
spec = importlib.util.spec_from_file_location('lilypond_parser', str(lp_path))
lp = importlib.util.module_from_spec(spec)
sys.modules['lilypond_parser'] = lp
spec.loader.exec_module(lp)

from pathlib import Path
import re

# Read the study file to find the primary snippet constant
first_py = Path(workspace_root) / 'first.py'
txt = first_py.read_text(encoding='utf8')
m = re.search(r"SOURCE_MELODY_LILY\s*=\s*r?([\"'])(.*?)\1", txt, re.S)
if m:
    snippet = m.group(2)
else:
    # fallback: use the small default that many studies include
    snippet = r"\relative e { e2 }"

sd = lp.parse_lilypond_to_data(snippet, part_name='Main Melody')
parts = sd.get('parts', {})
for pname, events in parts.items():
    print(f"Part: {pname}")
    for i, e in enumerate(events):
        print(i, e)
