#!/usr/bin/env python3
"""Correct compact-support lower bound on β_3^{rad}.

Withdrawn: the h(D_L,D_R) lift in certify_beta3.py. h(0,1)≈0.991
exceeds the power-law I/D≈0.921, so that lift is not a global bound.

This file certifies Q=I/D on radial probabilities whose D-mass (the
measure z(dr)=r² m(dr)/D) is supported in some interval of aspect R,
after scaling inf(supp z)=1 so supp z ⊆ [1,R].

Mid-radius Rayleigh, s=3, HPS Newton form:
  I ≥ ∑_{ij} F_ij (c_i + c_j)/2 μ_i μ_j
  D  = ∑_i ρ_i ,  ρ_i / (c_i μ_i) ∈ [1/q, q]
  c_i = a_i b_i = r_i^{*2},  q = R^{1/n},
  F_ij = min f on the bin-pair t-range.

The discrete φ(μ)=(μ^T A μ)/(c·μ), A_ij=F_ij(c_i+c_j)/2, satisfies
  I/D ≥ φ(μ) − P (1−fmin)
with P ≤ (q−1)/(q+1). Proof: I/D is a reweighting of the F-average
λ_i=∑_j F_ij μ_j ∈ [fmin,1] by s_i∈[1/q,q]; the total-variation mass
on {s/S−1>0} is at most (q−1)/(q+1) (two-value s, direct calculus).

φ ≥ φ_target is certified by verify_beta3.c (exhaustive faces of
M = A − φ_target (c 1^T + 1 c^T)/2) and independently by SLSQP +
vertices + the PSD margin of M.

Writes certs/beta3_compact.json.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
from mpmath import iv, mp, mpf, nstr, power
from scipy.optimize import minimize

from beta3_kernel import (
    FMIN_MP,
    S,
    assemble_mid,
    f_mp,
    fmin_iv,
    iv_bounds,
)

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
mp.dps = 80
iv.dps = 60


def P_max_iv(q):
    """(q−1)/(q+1) as an interval."""
    return (q - 1) / (q + 1)


def slsqp_phi(A, c):
    n = A.shape[0]

    def fun(m):
        den = float(c @ m)
        if den <= 0:
            return 1e9
        return float(m @ A @ m) / den

    cons = {"type": "eq", "fun": lambda z: np.sum(z) - 1.0}
    bounds = [(0.0, 1.0)] * n
    best = 1e9
    rng = np.random.default_rng(1)
    starts = [np.ones(n) / n]
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1.0
        starts.append(e)
        best = min(best, fun(e))
    for _ in range(16):
        v = rng.random(n)
        starts.append(v / v.sum())
    for z0 in starts:
        res = minimize(
            fun,
            z0,
            bounds=bounds,
            constraints=cons,
            method="SLSQP",
            options={"maxiter": 500, "ftol": 1e-14},
        )
        if res.success:
            best = min(best, float(res.fun))
    return best


def eig_min_M(A, c, lam):
    n = A.shape[0]
    ones = np.ones(n)
    M = A - lam * 0.5 * (np.outer(c, ones) + np.outer(ones, c))
    M = 0.5 * (M + M.T)
    return float(np.linalg.eigvalsh(M).min())


def write_matrix(A, c, lam, path: Path):
    n = A.shape[0]
    lines = [f"{n} {lam:.16e}"]
    lines.append(" ".join(f"{c[i]:.16e}" for i in range(n)))
    for i in range(n):
        lines.append(" ".join(f"{A[i, j]:.16e}" for j in range(n)))
    path.write_text("\n".join(lines) + "\n")


def run_faces(mat: Path, fac: Path) -> dict:
    cbin = HERE / "verify_beta3"
    src = HERE / "verify_beta3.c"
    subprocess.check_call(["gcc", "-O3", "-o", str(cbin), str(src), "-lm"])
    subprocess.check_call([str(cbin), str(mat), str(fac)], cwd=str(HERE))
    out = {}
    for line in fac.read_text().splitlines():
        k, _, v = line.partition(" ")
        if k in {
            "n",
            "interior_critical",
            "singular_or_illconditioned",
            "n_faces",
            "copositive",
        }:
            out[k] = int(float(v))
        else:
            out[k] = float(v)
    return out


def f_small(t):
    return (1.0 + t**3) / (1.0 + t**2)


def main() -> None:
    import sys

    CERTS.mkdir(parents=True, exist_ok=True)
    fmin = mpf(FMIN_MP)
    configs = [
        # R covers the numerical power-law aspect ~3.5; n so 2^n is runnable
        (4, 18, 0.9060),
        (6, 20, 0.9065),
        (8, 20, 0.9060),
        (12, 22, 0.9055),
    ]
    quick = "--quick" in sys.argv
    if quick:
        configs = [(4, 18, 0.9060)]
    rows = []
    best_compact = fmin
    best = None

    for R, n, target in configs:
        print(f"==== R={R} n={n} target={target} ====")
        blob = assemble_mid(R, n)
        A = np.array([[float(blob["A_lo"][i][j]) for j in range(n)] for i in range(n)])
        c = np.array([float(blob["rmid2"][i]) for i in range(n)])
        phi_num = slsqp_phi(A, c)
        ev = eig_min_M(A, c, target)
        print(f"  SLSQP φ={phi_num:.8f}  λ_min(M({target}))={ev:.4e}")

        q = blob["q_iv"]
        P = P_max_iv(q)
        err = P * (1 - blob["fmin_iv"])
        err_hi = mpf(err.b)
        q_hi = mpf(q.b)
        P_hi = mpf(P.b)

        faces = None
        certified_phi = None
        if ev >= 1e-11:
            certified_phi = target
            print("  PSD certificate: M ⪰ 0")
        elif n <= 22:
            mat = CERTS / f"beta3_mid_R{R}_n{n}.txt"
            fac = CERTS / f"beta3_mid_faces_R{R}_n{n}.txt"
            write_matrix(A, c, target, mat)
            faces = run_faces(mat, fac)
            print(
                f"  faces copositive={faces.get('copositive')} "
                f"minM={faces.get('min_mMm')} minφ={faces.get('min_phi')} "
                f"singular={faces.get('singular_or_illconditioned')}"
            )
            if faces.get("copositive") and faces.get("min_mMm_safe", -1) >= 0:
                certified_phi = target

        if certified_phi is None:
            print("  no compact certificate at this target")
            compact = fmin
            used_phi = None
        else:
            used_phi = certified_phi
            compact = mpf(certified_phi) - err_hi
            if compact < fmin:
                print("  error ate the gap; compact < fmin")

        f_R = f_small(1.0 / R)
        # Separated-clump lower bound: no aspect-R window holds all D-mass,
        # so some pair-mass sits at t ≤ 1/R < t0, f ≥ f(1/R).
        # Worst two-mass split ε=1/2: Q ≥ (1/2) fmin + (1/2) f(1/R) is too
        # optimistic (pair mass on cross is 2ε(1-ε) of the *count*, not the
        # (r²+u²) weight). We only record the number, we do not use it as
        # a global lift.
        sep_half = 0.5 * float(fmin) + 0.5 * f_R

        row = {
            "R": R,
            "n": n,
            "phi_target": target,
            "slsqp_phi": phi_num,
            "eig_min_M": ev,
            "certified_phi": used_phi,
            "q_hi": S(q_hi),
            "P_max_hi": S(P_hi),
            "err_P_hi": S(err_hi),
            "compact_gamma": S(compact),
            "compact_inv": S(1 / compact),
            "beats_1.1185_on_aspect_le_R": bool(
                compact > fmin and (1 / compact) < mpf("1.1185")
            ),
            "f_at_1_over_R": f_R,
            "separated_half_record_only": sep_half,
            "faces": faces,
        }
        rows.append(row)
        if used_phi is not None and compact > best_compact:
            best_compact = compact
            best = row
        print(
            f"  compact γ≥{float(compact):.8f}  1/γ≤{float(1/compact):.6f}  "
            f"aspect≤{R} class_only={row['beats_1.1185_on_aspect_le_R']} "
            f"(not a Thm 2.2 dent)"
        )

    # Withdrawn global number from certify_beta3.py
    withdrawn_inv = mpf("1.116823910980300911670485397084439427267")
    status = (
        "dent"
        if best and best["beats_1.1185_on_aspect_le_R"]
        else "residue"
    )
    # Honest: this is a dent of the leading coefficient only after the
    # compact bound is lifted to every radial measure. We do NOT lift it
    # with the withdrawn h. So the published-record dent is still open
    # unless compact γ itself is used only as a restricted-class bound.
    # A restricted-class bound is a new remainder class / Z-range style
    # object only if it improves a published inequality. HPS Prop. 4.5
    # is for all measures, so a compact-only γ does not replace 1.1185
    # in Theorem 2.2.
    cert = {
        "arxiv": "2504.18487v1",
        "status": status if False else "residue",
        "is_new_bound": False,
        "beats_1.1185_in_HPS_theorem": False,
        "reason": (
            "Certified Q ≥ compact_gamma for D-measures of aspect ≤ R. "
            "HPS β_3 is an inf over all radial probabilities. The "
            "h(D_L,D_R) lift is withdrawn, so this does not replace "
            "b(3)<1.1185 in Theorem 2.2."
        ),
        "compact_best_gamma": S(best_compact) if best else None,
        "compact_best_inv": S(1 / best_compact) if best else None,
        "compact_best_row": best,
        "configs": rows,
        "P_max_formula": "(q-1)/(q+1)",
        "withdrawn": {
            "old_gamma_inv": S(withdrawn_inv),
            "why": (
                "h(0,1)=1-(1/12)(1-fmin)≈0.991 > power-law I/D≈0.921 "
                "on a measure that sits in a fixed-window tail."
            ),
        },
        "HPS_fmin": S(fmin),
        "HPS_b3": S(1 / fmin),
    }
    # overwrite status to residue explicitly
    cert["status"] = "residue"
    out = CERTS / ("beta3_compact_quick.json" if quick else "beta3_compact.json")
    out.write_text(json.dumps(cert, indent=2, default=str) + "\n")
    print("wrote", out)
    print("OVERALL status: residue (compact bound not lifted to all measures)")


if __name__ == "__main__":
    main()
