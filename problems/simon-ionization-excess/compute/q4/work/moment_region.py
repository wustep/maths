#!/usr/bin/env python3
"""Moment-feasible (Q,D) region for endpoint mass-stationary measures.

Given R and endpoint mass-stationarity (identities from q3/aspect_identities.py),
scan (Q,D) pairs that satisfy:
  - Positivity of M_{-1}, M_3 (endpoint moment signs)
  - Support [1,R] linear moment inequalities (Markov, Chebyshev, Hölder)
  - Existence of a 3-atom measure on {1,t,R} matching (M_{-1},1,D,M_3)

Also probes whether one extra interior stationarity radius t tightens the region.

Not a lower bound. Writes moment_region.json in this directory.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

# q2 compact gammas (beta3_compact.json)
GAMMA = {
    4: 0.901924285641075,
    6: 0.9017598208006703,
    8: 0.9005000199382865,
    12: 0.8995260524666927,
}


def endpoint_moments(Q: float, D: float, R: float) -> tuple[float, float]:
    """M_{-1}, M_3 from endpoint mass-stationarity."""
    m1 = Q + (Q - 1.0) * D
    m3 = (Q - 1.0) * R**3 + Q * D * R
    return m1, m3


def positivity_interval(Q: float, R: float) -> tuple[float, float] | None:
    """Open D-interval from M_{-1}>0 and M_3>0; None if Q outside (0,1)."""
    if not (0.0 < Q < 1.0):
        return None
    lo = ((1.0 - Q) / Q) * R * R
    hi = Q / (1.0 - Q)
    if lo >= hi:
        return None
    return lo, hi


def support_bounds(Q: float, D: float, R: float) -> dict:
    """Linear and elementary inequalities from supp subset [1,R], M_0=1."""
    m1, m3 = endpoint_moments(Q, D, R)
    ok = True
    reasons: list[str] = []

    if not (1.0 / R <= m1 <= 1.0):
        ok = False
        reasons.append("M_{-1} not in [1/R,1]")
    if not (1.0 <= m3 <= R**3):
        ok = False
        reasons.append("M_3 not in [1,R^3]")
    if not (1.0 <= D <= R * R):
        ok = False
        reasons.append("D not in [1,R^2]")

    m1_lo = max(1.0, 1.0 / m1) if m1 > 0 else math.inf
    m1_hi = min(R, math.sqrt(D))
    holder = m1_lo <= m1_hi + 1e-12 and m1 * m1_lo >= 1.0 - 1e-12
    if not holder:
        ok = False
        reasons.append("Hölder/Cauchy M_1 interval empty")

    cheb = m1_hi >= m1_lo and (D - 2.0 * m1_lo + 1.0) >= -1e-12
    if not cheb:
        ok = False
        reasons.append("Chebyshev (r-1)^2")

    return {"ok": ok, "reasons": reasons, "M_minus1": m1, "M_3": m3}


def solve_masses_at_t(
    t: float, R: float, m_minus1: float, D: float, m3: float
) -> tuple[float, float, float] | None:
    """Masses at radii (1,t,R) for k=0,-1,2; check k=3."""
    if not (1.0 < t < R):
        return None
    a, b, c = 1.0, t, R
    mat = [
        [1.0, 1.0, 1.0],
        [1.0 / a, 1.0 / t, 1.0 / b],
        [a * a, t * t, b * b],
    ]
    rhs = [1.0, m_minus1, D]
    det = (
        mat[0][0] * (mat[1][1] * mat[2][2] - mat[1][2] * mat[2][1])
        - mat[0][1] * (mat[1][0] * mat[2][2] - mat[1][2] * mat[2][0])
        + mat[0][2] * (mat[1][0] * mat[2][1] - mat[1][1] * mat[2][0])
    )
    if abs(det) < 1e-14:
        return None
    masses = []
    for col in range(3):
        repl = [[mat[i][j] if j != col else rhs[i] for j in range(3)] for i in range(3)]
        detc = (
            repl[0][0] * (repl[1][1] * repl[2][2] - repl[1][2] * repl[2][1])
            - repl[0][1] * (repl[1][0] * repl[2][2] - repl[1][2] * repl[2][0])
            + repl[0][2] * (repl[1][0] * repl[2][1] - repl[1][1] * repl[2][0])
        )
        masses.append(detc / det)
    if min(masses) < -1e-9:
        return None
    m3_check = masses[0] * a**3 + masses[1] * t**3 + masses[2] * b**3
    if abs(m3_check - m3) > 1e-5 * max(1.0, abs(m3)):
        return None
    return tuple(masses)


def two_atom_feasible(m_minus1: float, D: float, m3: float, R: float) -> bool:
    """Check 2-atom measure on [1,R]."""
    for a in (1.0,):
        for b in (R,):
            if abs(a - b) < 1e-14:
                continue
            p = (D - b * b) / (a * a - b * b)
            if not (0.0 <= p <= 1.0):
                continue
            m1c = p / a + (1.0 - p) / b
            m3c = p * a**3 + (1.0 - p) * b**3
            if abs(m1c - m_minus1) < 1e-8 and abs(m3c - m3) < 1e-6 * max(1.0, abs(m3)):
                return True
    return False


def three_atom_feasible(m_minus1: float, D: float, m3: float, R: float) -> bool:
    """Some 3-atom measure on {1,t,R} reproduces the moments."""
    if two_atom_feasible(m_minus1, D, m3, R):
        return True
    n = 120
    for k in range(1, n):
        t = 1.0 + (R - 1.0) * k / n
        if solve_masses_at_t(t, R, m_minus1, D, m3) is not None:
            return True
    return False


def scan_layer(
    R: float,
    gamma: float,
    *,
    q_hi: float,
    n_q: int,
    n_d: int,
) -> dict:
    cut = R / (R + 1.0)
    q_min = max(cut + 1e-6, 0.5)
    q_max = min(q_hi, 0.999)
    pos_below = support_below = measure_below = 0
    best_pos = best_support = best_measure = None

    for iq in range(n_q):
        Q = q_min + (q_max - q_min) * iq / max(n_q - 1, 1)
        if Q >= gamma:
            continue
        interval = positivity_interval(Q, R)
        if interval is None:
            continue
        lo, hi = interval
        for jd in range(n_d):
            D = lo + (hi - lo) * (jd + 0.5) / n_d
            pos_below += 1
            rec = {"Q": Q, "D": D}
            if best_pos is None or Q < best_pos["Q"]:
                best_pos = rec
            sb = support_bounds(Q, D, R)
            if not sb["ok"]:
                continue
            support_below += 1
            rec = {**rec, "M_minus1": sb["M_minus1"], "M_3": sb["M_3"]}
            if best_support is None or Q < best_support["Q"]:
                best_support = rec
            if not three_atom_feasible(sb["M_minus1"], D, sb["M_3"], R):
                continue
            measure_below += 1
            if best_measure is None or Q < best_measure["Q"]:
                best_measure = rec

    return {
        "positivity_below_gamma_count": pos_below,
        "support_below_gamma_count": support_below,
        "measure_below_gamma_count": measure_below,
        "best_positivity_only": best_pos,
        "best_with_support": best_support,
        "best_with_measure": best_measure,
    }


def scan_region(R: float, gamma: float) -> dict:
    cut = R / (R + 1.0)
    layer = scan_layer(R, gamma, q_hi=gamma, n_q=600, n_d=160)
    return {
        "R": R,
        "gamma": gamma,
        "cut": cut,
        "cut_beats_gamma": cut > gamma,
        "positivity_only_nonempty_below_gamma": layer[
            "positivity_below_gamma_count"
        ]
        > 0,
        "support_only_nonempty_below_gamma": layer["support_below_gamma_count"]
        > 0,
        "full_moment_nonempty_below_gamma": layer["measure_below_gamma_count"]
        > 0,
        **layer,
    }


def g_kernel(r: float, u: float) -> float:
    m = r if r >= u else u
    return (r**3 + u**3) / (2.0 * m)


def interior_stationarity_feasible(R: float, Q: float, D: float, t: float) -> bool:
    """Masses at {1,t,R} satisfy stationarity at all three radii."""
    targets = [
        0.5 * Q * (1.0 + D),
        0.5 * Q * (t * t + D),
        0.5 * Q * (R * R + D),
    ]
    radii = (1.0, t, R)
    mat = [[g_kernel(ri, rj) for rj in radii] for ri in radii]
    det = (
        mat[0][0] * (mat[1][1] * mat[2][2] - mat[1][2] * mat[2][1])
        - mat[0][1] * (mat[1][0] * mat[2][2] - mat[1][2] * mat[2][0])
        + mat[0][2] * (mat[1][0] * mat[2][1] - mat[1][1] * mat[2][0])
    )
    if abs(det) < 1e-12:
        return False
    masses = []
    for col in range(3):
        repl = [[mat[i][j] if j != col else targets[i] for j in range(3)] for i in range(3)]
        detc = (
            repl[0][0] * (repl[1][1] * repl[2][2] - repl[1][2] * repl[2][1])
            - repl[0][1] * (repl[1][0] * repl[2][2] - repl[1][2] * repl[2][0])
            + repl[0][2] * (repl[1][0] * repl[2][1] - repl[1][1] * repl[2][0])
        )
        masses.append(detc / det)
    if min(masses) < -1e-8:
        return False
    D_check = masses[0] + masses[1] * t * t + masses[2] * R * R
    return abs(D_check - D) < 1e-5 * max(1.0, D)


def scan_interior(R: float, gamma: float) -> dict:
    """Does one extra interior stationarity point eliminate Q < gamma?"""
    cut = R / (R + 1.0)
    survivors = []
    for iq in range(250):
        Q = cut + (0.999 - cut) * iq / 249
        if Q >= gamma:
            continue
        interval = positivity_interval(Q, R)
        if interval is None:
            continue
        lo, hi = interval
        for jd in range(80):
            D = lo + (hi - lo) * (jd + 0.5) / 80
            sb = support_bounds(Q, D, R)
            if not sb["ok"]:
                continue
            if not three_atom_feasible(sb["M_minus1"], D, sb["M_3"], R):
                continue
            ok_any = False
            for kt in range(1, 80):
                t = 1.0 + (R - 1.0) * kt / 80
                if interior_stationarity_feasible(R, Q, D, t):
                    ok_any = True
                    break
            if ok_any:
                survivors.append({"Q": Q, "D": D})
    return {
        "R": R,
        "gamma": gamma,
        "moment_feasible_below_gamma_with_3_stationarity": len(survivors) > 0,
        "count": len(survivors),
        "sample": survivors[:3],
    }


def gamma_at_R(R: int) -> float:
    if R in GAMMA:
        return GAMMA[R]
    keys = sorted(GAMMA)
    if R <= keys[0]:
        return GAMMA[keys[0]]
    if R >= keys[-1]:
        return GAMMA[keys[-1]]
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        if a <= R <= b:
            wa = (b - R) / (b - a)
            wb = (R - a) / (b - a)
            return wa * GAMMA[a] + wb * GAMMA[b]
    raise RuntimeError("unreachable")


def positivity_only_witness(R: float, Q: float, D: float) -> dict:
    m1, m3 = endpoint_moments(Q, D, R)
    interval = positivity_interval(Q, R)
    in_interval = interval is not None and interval[0] < D < interval[1]
    return {
        "R": R,
        "Q": Q,
        "D": D,
        "M_minus1": m1,
        "M_3": m3,
        "positivity_interval": interval,
        "D_in_positivity_interval": in_interval,
        "support_ok": support_bounds(Q, D, R)["ok"],
        "three_atom_ok": three_atom_feasible(m1, D, m3, R) if in_interval else False,
    }


def main() -> None:
    targets = [4, 8, 9]
    rows = [scan_region(R, gamma_at_R(R)) for R in targets]
    interior = [scan_interior(R, gamma_at_R(R)) for R in targets]

    witnesses = [
        positivity_only_witness(4.0, 0.801, 4.0),
        positivity_only_witness(4.0, 0.8942672775378222, 2.691982118274256),
    ]

    out = {
        "not_a_lower_bound": True,
        "method": (
            "Endpoint identities M_{-1}=Q+(Q-1)D, M_3=(Q-1)R^3+QDR; "
            "support [1,R] linear ineqs; 2/3-atom moment reconstruction."
        ),
        "regions": rows,
        "interior_stationarity_scan": interior,
        "positivity_only_witnesses": witnesses,
        "summary": {
            str(R): {
                "gamma": gamma_at_R(R),
                "cut": R / (R + 1),
                "cut_beats_gamma": (R / (R + 1)) > gamma_at_R(R),
                "positivity_only_below_gamma": rows[targets.index(R)][
                    "positivity_only_nonempty_below_gamma"
                ],
                "support_only_below_gamma": rows[targets.index(R)][
                    "support_only_nonempty_below_gamma"
                ],
                "full_moment_below_gamma": rows[targets.index(R)][
                    "full_moment_nonempty_below_gamma"
                ],
                "rigorous_R_lift_from_moments_alone": False,
            }
            for R in targets
        },
    }
    path = HERE / "moment_region.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    for r in rows:
        print(
            f"R={r['R']}  γ={r['gamma']:.6f}  cut={r['cut']:.6f}  "
            f"pos<Q<γ={r['positivity_only_nonempty_below_gamma']}  "
            f"support<Q<γ={r['support_only_nonempty_below_gamma']}  "
            f"measure<Q<γ={r['full_moment_nonempty_below_gamma']}"
        )
    print("wrote", path)


if __name__ == "__main__":
    main()
