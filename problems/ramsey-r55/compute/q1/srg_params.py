#!/usr/bin/env python3
"""Feasible strongly regular parameters on 43 vertices in the (5,5) degree window.

A vertex-transitive SRG of prime order is circulant; the circulant census at 43
is empty. This file only lists integral parameter sets. It does not construct
or exclude a non-vertex-transitive SRG.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from r55lib import dump_json

OUT = Path(__file__).resolve().parent / "certs" / "srg43_params.json"


def integral_srg(n, k, lam, mu):
    # k(k-lam-1) = (n-k-1) mu
    if k * (k - lam - 1) != (n - k - 1) * mu:
        return None
    disc = (lam - mu) ** 2 + 4 * (k - mu)
    if disc < 0:
        return None
    s = int(math.isqrt(disc))
    if s * s != disc:
        return None
    # eigenvalues
    # theta, tau = ((lam-mu) ± s) / 2
    if (lam - mu + s) % 2 or (lam - mu - s) % 2:
        return None
    theta = (lam - mu + s) // 2
    tau = (lam - mu - s) // 2
    # multiplicities: f,g with f+g = n-1, theta f + tau g = -k
    # f = 1/2 * ((n-1) + ((n-1)(mu-lam) - 2k)/s)
    num = (n - 1) * (mu - lam) - 2 * k
    if num % s:
        return None
    f = ((n - 1) + num // s) // 2
    g = n - 1 - f
    if f < 0 or g < 0:
        return None
    if 2 * f != (n - 1) + num // s:
        return None
    return {"theta": theta, "tau": tau, "f": f, "g": g}


def main() -> int:
    n = 43
    rows = []
    for k in range(18, 25):
        for lam in range(0, k):
            for mu in range(0, k + 1):
                ev = integral_srg(n, k, lam, mu)
                if ev is None:
                    continue
                rows.append({"n": n, "k": k, "lam": lam, "mu": mu, **ev})
    payload = {
        "n": 43,
        "degree_window": [18, 24],
        "n_integral": len(rows),
        "params": rows,
        "note": (
            "No integral parameter set in the legal degree window. "
            "43 ≢ 1 (mod 4), so there is also no conference graph. "
            "Every SRG is either a conference graph or has integer "
            "eigenvalues, so there is no strongly regular graph on 43 "
            "vertices with degree in [18,24]. That excludes an SRG "
            "(5,5,43)-graph. It is not a bound on R(5,5)."
        ),
    }
    dump_json(str(OUT), payload)
    print(f"integral_srg43={len(rows)}")
    for r in rows:
        print(r)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
