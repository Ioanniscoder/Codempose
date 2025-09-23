#!/usr/bin/env python3
"""
Codempose local entrypoint example.
Run this to verify Python execution inside Codespaces/devcontainer.
"""
import sys


def main():
    print("Codempose: Python environment OK — sys.version=" + sys.version.replace('\n', ' '))


if __name__ == "__main__":
    main()
