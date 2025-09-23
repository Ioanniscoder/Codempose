#!/usr/bin/env bash
set -euo pipefail

echo "Running project_template.py -> generates relative_score.ly and relative_score.pdf"
python3 project_template.py

echo "Serving workspace on port 8888 (bind 0.0.0.0). Press Ctrl-C to stop."
python3 -m http.server 8888 --bind 0.0.0.0
