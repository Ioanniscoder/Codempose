#!/usr/bin/env bash
set -euo pipefail

# Create venv if missing
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run the generator forcing verbatim emission
python main.py --input first.py --force-verbatim

echo "Generated outputs/first.ly (verbatim)"
