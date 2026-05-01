#!/usr/bin/env python3
"""GitHub Stats Badge Generator.

Entry point script that delegates to the badge package.
This file exists to maintain backward compatibility with action.yml
which invokes: python3 src/generate_badge.py
"""

import sys
from pathlib import Path

# Ensure the src/ directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from badge.main import run

if __name__ == "__main__":
    raise SystemExit(run())
