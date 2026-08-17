#!/usr/bin/env python3
"""Recompute max_d g for every SAT witness. Independent of sat_exact."""

from __future__ import annotations

import json
from pathlib import Path

from gaplib import max_gap_dilates, shakan_lower, uniq_mod


def main():
    rows = []
    for line in Path("compute/certs/sat_G.jsonl").read_text().splitlines():
        rec = json.loads(line)
        p, n, A = rec["p"], rec["n"], rec["witness"]
        A2 = uniq_mod(A, p)
        assert len(A2) == n, (p, n, A)
        g, d = max_gap_dilates(A2, p)
        sh = shakan_lower(p, n)
        ok = g == rec["witness_g"] == rec["G"] and g + 1e-12 >= sh
        rows.append(
            {
                "p": p,
                "n": n,
                "G_claimed": rec["G"],
                "g_recomputed": g,
                "d": d,
                "shakan": sh,
                "ratio_mean": g * n / p,
                "ratio_sqrt": g / (p**0.5),
                "extra": g - sh,
                "ok": ok,
            }
        )
        print(
            f"p={p:3d} n={n:2d} G={g:3d} sh={sh:6.2f} extra={g-sh:5.2f} "
            f"G/mean={g*n/p:.3f} G/sqrt={g/(p**0.5):.3f} ok={ok}"
        )
    bad = [r for r in rows if not r["ok"]]
    Path("compute/certs/sat_G_verified.json").write_text(json.dumps(rows, indent=2))
    print("failures", len(bad))
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
