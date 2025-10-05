"""Test promotion feature: LilyPond to TinyNotation"""

# Enable promotion toggle
# PROMOTE_TO_TINYNOTATION = False  # Promotion completed, toggle disabled

# Primary LilyPond snippet that will be promoted
# SOURCE_MELODY_LILY = r"\relative c' { \time 4/4 c4 d e f | g a b c }"  # Promoted to TinyNotation

# Promoted from LilyPond to TinyNotation
SOURCE_MELODY_TINY = "4/4 c4 d4 e4 f4 g4 a4 b4 c'4"

# When you run this file, it will:
# 1. Convert SOURCE_MELODY_LILY to TinyNotation
# 2. Create a backup (.bak file)
# 3. Rewrite this file with SOURCE_MELODY_TINY
# 4. Disable the PROMOTE_TO_TINYNOTATION toggle

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/workspaces/Codempose')
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(__file__)
