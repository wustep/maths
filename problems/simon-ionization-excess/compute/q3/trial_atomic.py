#!/usr/bin/env python3
"""Explicit atomic trial: an upper bound on β_3, not a lower bound.

64-atom geometric quadrature of m(dr)∝ r^{-2} dr on [1, 7/2].
Interval arithmetic on the finite double sum. Used only to show
β_3 ≤ Q_hi < 12/13, so a global minimizer (if it exists) cannot
be a mass-stationary measure of aspect ≥ 12.

Writes certs/trial_atomic.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import iv, mp, mpf, nstr

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
mp.dps = 80
iv.dps = 60


def S(x, d: int = 40) -> str:
    return nstr(x, d, strip_zeros=False)


def g_iv(r, u, r_ge_u: bool):
    mx = r if r_ge_u else u
    return (r**3 + u**3) / (2 * mx)


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    n_lo, n_hi = iv.mpf(1), iv.mpf(7) / 2
    k = 64
    # geometric edges and mid-radii, masses ∝ r^{-2} Δlog r (equal log-width)
    q = iv.exp(iv.log(n_hi / n_lo) / k)
    radii = [n_lo * q ** (iv.mpf(i) + iv.mpf("0.5")) for i in range(k)]
    # equal log-width, m_i ∝ r_i^{-2} * r_i * Δlog = r_i^{-1} Δlog; use r^{-2}
    # times midpoint rule on log grid: Δu = log q constant, m ∝ e^{α u} with α=-2
    # so m_i ∝ r_i^{-2} * r_i * log q = r_i^{-1} log q. Either choice is a trial.
    raw = [1 / r**2 for r in radii]
    tot = sum(raw)
    masses = [w / tot for w in raw]

    D = sum(m * r**2 for m, r in zip(masses, radii))
    I = iv.mpf(0)
    for i, (mi, ri) in enumerate(zip(masses, radii)):
        for j, (mj, uj) in enumerate(zip(masses, radii)):
            I += mi * mj * g_iv(ri, uj, i >= j)
    Q = I / D
    Q_hi = mpf(Q.b)
    cut = mpf(12) / 13
    blob = {
        "k": k,
        "n": "7/2",
        "alpha_mass": "m_i ∝ r_i^{-2}",
        "Q_interval": [S(mpf(Q.a)), S(mpf(Q.b))],
        "Q_hi": S(Q_hi),
        "D_interval": [S(mpf(D.a)), S(mpf(D.b))],
        "aspect_hi": S(mpf((radii[-1] / radii[0]).b)),
        "below_12_13": bool(Q_hi < cut),
        "inv_hi": S(1 / mpf(Q.a)),
        "note": (
            "Upper bound on β_3 only. Not used as a lower bound. "
            "Shows a trial with Q < 12/13, so the inf is not forced "
            "to live in the aspect-≥12 mass-stationary class."
        ),
    }
    out = CERTS / "trial_atomic.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("Q in", blob["Q_interval"], "Q_hi", float(Q_hi), "<12/13", Q_hi < cut)
    print("wrote", out)
    if not (Q_hi < cut):
        raise SystemExit("trial_atomic.py FAIL")
    print("trial_atomic.py PASS")


if __name__ == "__main__":
    main()
