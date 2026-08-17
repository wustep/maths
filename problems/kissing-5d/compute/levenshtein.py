#!/usr/bin/env python3
"""Exact Levenshtein number L_5(5, 1/2) = 48, independently computed."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from delsarte import levenshtein_n5_s_half


def main() -> int:
    val = levenshtein_n5_s_half()
    report = {
        "L_5(5,1/2)": str(val),
        "equals_48": val == 48,
    }
    out = Path(__file__).resolve().parent / "levenshtein.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(report)
    assert val == 48
    print("PASS: L_5(5, 1/2) = 48 exactly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
