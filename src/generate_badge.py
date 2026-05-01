#!/usr/bin/env python3
"""GitHub Stats Badge Generator.

Entry point script that delegates to the badge package.
This file exists to maintain backward compatibility with action.yml
which invokes: python3 -m badge.main
"""

from badge.main import run

if __name__ == "__main__":
    raise SystemExit(run())
