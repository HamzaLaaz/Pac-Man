#!/usr/bin/env python3
"""Root entry point required by the subject: python3 pac-man.py config.json

This just makes `src/` importable and delegates to `src/main.py`, so the
game can be launched exactly as the subject specifies, directly from the
repository root.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from main import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
