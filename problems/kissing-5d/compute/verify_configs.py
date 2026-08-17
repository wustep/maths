#!/usr/bin/env python3
"""Replay the four published 40-point codes and Cohn–Rajagopal Table 2.1."""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from configs import CONFIGS, _dot, _norm2, ip_histogram, is_kissing

# Cohn–Rajagopal arXiv:2412.00937v3, Table 2.1: unordered pair counts.
# Columns: -1, -4/5, -3/4, -1/2, -3/10, -1/4, 0, 1/5, 1/2
PUBLISHED = {
    "D5": {
        Fraction(-1): 20,
        Fraction(-1, 2): 240,
        Fraction(0): 280,
        Fraction(1, 2): 240,
    },
    "L5": {
        Fraction(-1): 12,
        Fraction(-3, 4): 32,
        Fraction(-1, 2): 192,
        Fraction(-1, 4): 32,
        Fraction(0): 272,
        Fraction(1, 2): 240,
    },
    "Q5": {
        Fraction(-1): 10,
        Fraction(-4, 5): 30,
        Fraction(-1, 2): 180,
        Fraction(-3, 10): 60,
        Fraction(0): 250,
        Fraction(1, 5): 10,
        Fraction(1, 2): 240,
    },
    "R5": {
        Fraction(-1): 6,
        Fraction(-4, 5): 30,
        Fraction(-3, 4): 20,
        Fraction(-1, 2): 144,
        Fraction(-3, 10): 60,
        Fraction(-1, 4): 28,
        Fraction(0): 242,
        Fraction(1, 5): 10,
        Fraction(1, 2): 240,
    },
}


def _fmt(h):
    return {f"{t.numerator}/{t.denominator}": c for t, c in h.items()}


def main() -> int:
    report = {}
    ok = True
    for name, builder in CONFIGS.items():
        pts = builder()
        norms = {_norm2(p) for p in pts}
        hist = ip_histogram(pts)
        kissing = is_kissing(pts)
        match = hist == PUBLISHED[name]
        n = len(pts)
        status = {
            "n": n,
            "squared_norms": [f"{x.numerator}/{x.denominator}" for x in sorted(norms)],
            "kissing": kissing,
            "histogram": _fmt(hist),
            "matches_CR_table_2_1": match,
        }
        report[name] = status
        print(f"{name}: n={n} kissing={kissing} table={match}")
        if n != 40 or not kissing or not match or norms != {2}:
            ok = False
            print("  FAIL", status)
    out = Path(__file__).resolve().parent / "verify_configs.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("wrote", out)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
