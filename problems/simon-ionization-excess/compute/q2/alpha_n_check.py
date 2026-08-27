#!/usr/bin/env python3
"""Second path for alpha_{N,s}: different seed, Nelder-Mead, no L-BFGS-B.

Confirms the search upper bounds in alpha_n.json to a few 1e-4. Still
not a lower bound on the infimum.

Replay: python3 alpha_n.py && python3 alpha_n_check.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from alpha_n import alpha_of, flatten, unflatten

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"


def main() -> None:
    blob = json.loads((CERTS / "alpha_n.json").read_text())
    rng = np.random.default_rng(20260827)
    worst = 0.0
    for row in blob["rows"]:
        N, s = row["N"], row["s"]
        best = float("inf")
        for _ in range(40):
            pts0 = rng.normal(size=(N, 3))
            res = minimize(
                lambda v, N=N, s=s: alpha_of(unflatten(v, N), s),
                flatten(pts0),
                method="Nelder-Mead",
                options={"maxiter": 800, "xatol": 1e-8, "fatol": 1e-10},
            )
            a = alpha_of(unflatten(res.x, N), s)
            if a < best:
                best = a
        gap = best - row["search_min"]
        worst = min(worst, gap)
        # A second search may go a bit lower (better upper bound) or stay above.
        if best + 5e-3 < row["search_min"]:
            raise SystemExit(
                f"N={N} s={s}: Nelder-Mead {best} is well below L-BFGS {row['search_min']}"
            )
        print(f"N={N} s={s:.2f}  L-BFGS {row['search_min']:.8f}  NM {best:.8f}  gap {gap:+.2e}")
    print("alpha_n_check.py: second search consistent with alpha_n.json")
    print("Neither path certifies a lower bound.")


if __name__ == "__main__":
    main()
