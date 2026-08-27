#!/usr/bin/env python3
"""Build the dump that Rust must match, from the three JSON certificates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", type=Path, required=True)
    args = ap.parse_args()

    l1 = json.loads((HERE / "l1_polynomial.json").read_text())
    tests = json.loads((HERE / "center_family_tests.json").read_text())
    bez = json.loads((HERE / "bezout_samples.json").read_text())
    pull = json.loads((HERE / "pullback_degree.json").read_text())

    lines = []
    for mon in l1["L1_monomials"]:
        lines.append(f"L1 {mon['term']} {mon['coeff']}")
    for t in tests["tests"]:
        lines.append(f"center {t['name']} L1={t['L1']}")

    wanted = {
        ("chebyshev", 2): "chebyshev_m2",
        ("chebyshev", 3): "chebyshev_m3",
        ("chebyshev", 4): "chebyshev_m4",
        ("two_quadrics", 2): "two_quadrics",
        ("complex_square", 2): "complex_square",
    }
    seen = set()
    for rec in bez["samples"]:
        key = (rec["kind"], rec["m"])
        if key in wanted and key not in seen:
            lines.append(f"preimages {wanted[key]} {rec['count']}")
            seen.add(key)

    for name in ("chebyshev_n2_m3", "nonsep_um_plus_v_n2_m3"):
        rec = next(e for e in pull["examples"] if e["name"] == name)
        lines.append(f"deg {name} {rec['deg_Y']} bound {rec['bound']}")

    args.dump.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
