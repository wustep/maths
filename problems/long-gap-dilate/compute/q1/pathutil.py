"""Put the parent compute/ directory on sys.path."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

Q1 = Path(__file__).resolve().parent
CERTS = Q1 / "certs"
CERTS.mkdir(parents=True, exist_ok=True)
