#!/usr/bin/env python3
"""Print Python sidecar import status. Run from repo root with the venv active."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from maths.envcheck import main

if __name__ == "__main__":
    raise SystemExit(main())
