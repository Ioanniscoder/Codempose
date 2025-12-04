"""
REGRESSION TEST: Simple Two-Staff Baseline
===========================================

Minimal test to verify smart stripping and measure bar generation work correctly.
Based on ninetyninth.py structure but simplified.

Tests:
1. Two-staff layout (Melody & Bass)
2. Original snippets with bypass
3. Repetition syntax (no duplicate metadata)
4. Auto-rest with measure bars
"""

import _study_path  # Auto-path setup

from typing import Dict
from src.score_builder import build_score_from_blueprint
from src.project_template import run_pipeline_from_file

# ============================================================================
# METADATA
# ============================================================================

TITLE = "Regression Test: Simple Baseline"
COMPOSER = "Codempose Test Suite"

# ============================================================================
# SNIPPETS
# ============================================================================

MELODY = r"""
\relative c'' {
    \key c \major
    \time 4/4
    c4 d e f |
    g2 a2
}
""".strip()

BASS = r"""
\relative c {
    \clef bass
    \key c \major
    \time 4/4
    c2 g2 |
    f2 c2
}
""".strip()

# ============================================================================
# BLUEPRINT DEFINITION
# ============================================================================

VOICE_STAVE_DEF = "Melody & Bass"

VOICE_STAVE_DATA = """
    # Section 1: Original snippets
    MELODY & BASS;
    
    # Section 2: Repetition (test smart stripping)
    MELODY * 2 & BASS * 2;
    
    # Section 3: Auto-rest (test measure bar generation)
    MELODY & r
"""

# ============================================================================
# SCORE ASSEMBLY
# ============================================================================

def build_score_data() -> Dict:
    """Assemble score using Blueprint Strings."""
    
    metadata = {
        'title': TITLE,
        'composer': COMPOSER,
        'opus_number': 'REGRESSION-01',
        'instrumentation': 'Piano',
        'key_signature': {'tonic': 'c', 'mode': 'major'},
        'time_signature': '4/4',
        'tempo': 'Allegro, quarter note = 120',
        'original_snippets': {
            'MELODY': MELODY,
            'BASS': BASS,
        },
        'blueprint_structure': {
            'voice_stave_def': VOICE_STAVE_DEF,
            'voice_stave_data': VOICE_STAVE_DATA,
        }
    }
    
    return build_score_from_blueprint(
        VOICE_STAVE_DEF,
        VOICE_STAVE_DATA,
        {},  # Empty - uses metadata['original_snippets']
        metadata
    )

# ============================================================================
# PIPELINE EXECUTION
# ============================================================================

if __name__ == '__main__':
    run_pipeline_from_file(__file__)
