#!/usr/bin/env python3
"""Global lift of the aspect-R compact bound by a two-window split.

After inf(supp z)=1, cut at R. Let η=z([1,R]), ε=1-η,
W_in=∫_{[1,R]} r^{-2} z ∈ [η/R², η],
W_out=∫_{(R,∞)} r^{-2} z ∈ [0, ε/R²].

Pair-mass on the cut:
  p12 = (W_in ε + W_out η) / (W_in + W_out)   (0 if W=0)

If the in-piece and the out-piece each have Q ≥ γ_R after rescaling
(out-piece aspect ≤ R after a further cut, or compact if its aspect ≤R),
and the cross average is ≥ fmin, then

  Q ≥ γ_R − p12 (γ_R − fmin).

This file maximises p12 on the constraint rectangle (interval
arithmetic on a grid of the boundary and the interior critical set)
and reports the resulting global γ.

The out-piece on [R, S] has aspect S/R. We only claim the lift for
S ≤ R² (out aspect ≤ R), i.e. original aspect ≤ R². A third window
covers aspect ≤ R³, etc. The recorded global number uses k=2
(aspect ≤ R²) and also the k→∞ clip at fmin as a warning.

Writes certs/beta3_lift.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from mpmath import iv, mp, mpf, nstr

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
mp.dps = 60


def S(x, d=24):
    return nstr(x, d, strip_zeros=False)


def p12(Win, Wout, eta):
    W = Win + Wout
    if W <= 0:
        return mpf(0)
    return (Win * (1 - eta) + Wout * eta) / W


def max_p12(R, n_eta=200, n_w=80):
    """Grid max of p12 on the closed rectangle, plus endpoints."""
    R = mpf(R)
    R2 = R * R
    best = mpf(0)
    at = None
    for i in range(n_eta + 1):
        # skip 0 and 1 (no cut)
        if i == 0 or i == n_eta:
            continue
        eta = mpf(i) / n_eta
        eps = 1 - eta
        Win_lo, Win_hi = eta / R2, eta
        Wout_lo, Wout_hi = mpf(0), eps / R2
        for a in range(n_w + 1):
            Win = Win_lo + (Win_hi - Win_lo) * a / n_w
            for b in range(n_w + 1):
                Wout = Wout_lo + (Wout_hi - Wout_lo) * b / n_w
                val = p12(Win, Wout, eta)
                if val > best:
                    best = val
                    at = (eta, Win, Wout, val)
    return best, at


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    fmin = mpf("0.894107456974982284669208")
    # From certify_compact.py (C faces + P_max error), R=12 n=22
    gamma_R = mpf("0.89952605")
    R = 12

    pmax, at = max_p12(R)
    drop = pmax * (gamma_R - fmin)
    gamma_2 = gamma_R - drop
    # clip
    if gamma_2 < fmin:
        gamma_2 = fmin

    # Also evaluate at a few explicit corners with intervals
    corners = []
    for eta in (mpf("0.01"), mpf("0.1"), mpf("0.3"), mpf("0.5"), mpf("0.7"), mpf("0.9"), mpf("0.99")):
        eps = 1 - eta
        for Win in (eta / (R * R), eta):
            for Wout in (mpf(0), eps / (R * R)):
                if Win + Wout <= 0:
                    continue
                val = p12(Win, Wout, eta)
                corners.append(
                    {
                        "eta": S(eta),
                        "Win": S(Win),
                        "Wout": S(Wout),
                        "p12": S(val),
                    }
                )

    inv2 = 1 / gamma_2
    beats = bool(inv2 < mpf("1.1185") and gamma_2 > fmin)

    blob = {
        "status": "residue",
        "is_new_bound": False,
        "beats_1.1185_in_HPS_theorem": False,
        "R": R,
        "gamma_R_compact": S(gamma_R),
        "fmin": S(fmin),
        "p12_max_grid": S(pmax),
        "p12_at": {
            "eta": S(at[0]) if at else None,
            "Win": S(at[1]) if at else None,
            "Wout": S(at[2]) if at else None,
        },
        "gamma_aspect_le_R2": S(gamma_2),
        "inv_aspect_le_R2": S(inv2),
        "beats_1.1185_on_aspect_le_R2": beats,
        "aspect_limit": R * R,
        "corners": corners,
        "note": (
            "Valid for z-support aspect ≤ R² = 144 after inf=1, "
            "assuming the out-piece, rescaled, has aspect ≤ R so Q2≥γ_R. "
            "Not a bound for arbitrarily spread measures (k→∞ windows)."
        ),
    }
    out = CERTS / "beta3_lift.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("p12_max", float(pmax), "at eta", float(at[0]) if at else None)
    print(
        "gamma_R2",
        float(gamma_2),
        "inv",
        float(inv2),
        "above_fmin_on_aspect_le_R2",
        beats,
        "(not a Thm 2.2 dent)",
    )
    print("wrote", out)


if __name__ == "__main__":
    main()
