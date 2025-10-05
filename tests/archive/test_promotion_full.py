"""Test promotion with full metadata: time, key, and tempo"""

# Enable promotion toggle
# PROMOTE_TO_TINYNOTATION = False  # Promotion completed, toggle disabled

# Primary LilyPond snippet with complete metadata
# SOURCE_MELODY_LILY = r"\relative e { \time 6/4 \key c \major \tempo 4=90 e2 bmol4 c2 r4 | e2 f#4 e2 r4 }"  # Promoted to TinyNotation

# Promoted from LilyPond to TinyNotation
SOURCE_MELODY_TINY = "time=6/4 key=Cmajor tempo=90 E2 B-4 c2 r4 e2 f#4 e2 r4"

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/workspaces/Codempose')
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
