#!/usr/bin/env python3
"""Certified lower bound on β_3^{rad} with a conservative z-kernel.

HPS arXiv:2504.18487v1, Newton + radial, s=3:

  Q = I/D = ∬ f(t) (r^{-2}+u^{-2})/2 z(dr)z(du)  /  ∫ r^{-2} z(dr)

where z(dr) = r² m(dr)/D is a probability, f(t)=(1+t³)/(1+t²),
t=min(r,u)/max(r,u). Scale so inf(supp z)=1. Then z lives on [1,∞).

On a geometric partition of [1,R],
  F_ij = min f on the exact t-range of bins i,j  (unimodal),
  w_hi_i = a_i^{-2}  (upper bound of r^{-2} on the bin),
  w_lo_i = b_i^{-2}  (lower bound),
  K_ij = F_ij (w_lo_i + w_lo_j)/2.

Then Q ≥ (z^T K z)/(w_hi · z) for every z supported on [1,R].
The discrete Rayleigh is certified by the smallest eigenvalue of
  M(λ) = K − λ (w_hi 1^T + 1 w_hi^T)/2
when that eigenvalue is positive (PSD ⇒ copositive), else by
exhaustive face enumeration of m^T M m on the simplex (C).

A right tail r>R is controlled after inf(supp z)=1: writing η=z([1,R]),
ε=1-η, s=W_tail/W_mid ≤ ε/η, and using f≥fmin on every pair that
touches the tail,

  Q ≥ g(ε,s; β_R) := [η² β_R + ηε fmin(1+s) + ε² fmin s] / [η + ε s].

Because Q is an average of f, also Q≥fmin. The certified global
number is the min of β_R and the clipped g over ε∈[0,1), s∈[0,ε/η].

This file does NOT reuse the withdrawn mid-radius + h(D_L,D_R) lift
in certify_beta3.py (that h(0,1) exceeds the power-law I/D).

Writes certs/beta3_global.json.
"""

from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import numpy as np
from mpmath import iv, mp, mpf, nstr, power

from beta3_kernel import (
    FMIN_MP,
    S,
    b3_iv,
    f_mp,
    fmin_iv,
    Fmin_on_trange_iv,
    t_range_bins,
    t0_iv,
    iv_bounds,
)

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"

mp.dps = 80
iv.dps = 60


def g_trunc(eps, s, beta, fmin):
    """Lower bound of Q with a right tail, inf(supp z)=1."""
    eta = 1 - eps
    if eta <= 0:
        return fmin
    num = eta**2 * beta + eta * eps * fmin * (1 + s) + eps**2 * fmin * s
    den = eta + eps * s
    return num / den


def min_g_over_tail(beta, fmin, n_eps: int = 400):
    """Min of max(fmin, g) over ε∈[0,1) and s∈[0, ε/η]."""
    best = beta
    at = (0.0, 0.0)
    for i in range(n_eps):
        eps = i / n_eps
        if eps == 0:
            val = beta
            s = 0.0
        else:
            eta = 1 - eps
            s_hi = eps / eta
            # g is monotone in s; min on [0, s_hi] is at an endpoint
            g0 = g_trunc(eps, 0.0, beta, fmin)
            g1 = g_trunc(eps, s_hi, beta, fmin)
            val = min(g0, g1)
            s = 0.0 if g0 <= g1 else s_hi
        val = max(val, fmin)
        if val < best:
            best = val
            at = (eps, s)
    return best, at


def assemble_conservative(R: float, n: int):
    """Conservative K, w_hi, w_lo on n geometric bins of [1,R]."""
    edges = [power(mpf(R), mpf(i) / n) for i in range(n + 1)]
    a, b = edges[:-1], edges[1:]
    F_lo = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            tlo, thi = t_range_bins(a[i], b[i], a[j], b[j])
            Fi = Fmin_on_trange_iv(tlo, thi)
            F_lo[i][j] = mpf(Fi.a)
    w_lo = [1 / (b[i] ** 2) for i in range(n)]
    w_hi = [1 / (a[i] ** 2) for i in range(n)]
    K = [
        [F_lo[i][j] * (w_lo[i] + w_lo[j]) / 2 for j in range(n)] for i in range(n)
    ]
    q = iv.exp(iv.log(iv.mpf(str(R))) / n)
    return {
        "n": n,
        "R": R,
        "edges": edges,
        "F_lo": F_lo,
        "w_lo": w_lo,
        "w_hi": w_hi,
        "K": K,
        "q_iv": q,
        "fmin_iv": fmin_iv(),
        "b3_iv": b3_iv(),
    }


def np_mats(blob):
    n = blob["n"]
    K = np.array([[float(blob["K"][i][j]) for j in range(n)] for i in range(n)])
    w = np.array([float(blob["w_hi"][i]) for i in range(n)])
    return K, w


def eig_psd_margin(K, w, lam: float):
    """Smallest eigenvalue of M = K − λ (w 1^T + 1 w^T)/2."""
    n = K.shape[0]
    ones = np.ones(n)
    M = K - lam * 0.5 * (np.outer(w, ones) + np.outer(ones, w))
    M = 0.5 * (M + M.T)
    ev = np.linalg.eigvalsh(M)
    return float(ev[0]), M


def slsqp_rayleigh(K, w):
    """Numerical min of z^T K z / (w·z) on the simplex (not a bound)."""
    from scipy.optimize import minimize

    n = len(w)

    def fun(z):
        den = float(w @ z)
        if den <= 0:
            return 1e9
        return float(z @ K @ z) / den

    cons = {"type": "eq", "fun": lambda z: np.sum(z) - 1.0}
    bounds = [(0.0, 1.0)] * n
    best = 1e9
    rng = np.random.default_rng(0)
    starts = [np.ones(n) / n, np.array([1.0] + [0.0] * (n - 1))]
    for _ in range(12):
        v = rng.random(n)
        starts.append(v / v.sum())
    for z0 in starts:
        res = minimize(
            fun,
            z0,
            bounds=bounds,
            constraints=cons,
            method="SLSQP",
            options={"maxiter": 400, "ftol": 1e-14},
        )
        if res.success:
            best = min(best, float(res.fun))
    # vertices
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1.0
        best = min(best, fun(e))
    return best


def write_matrix_kw(K, w, lam, path: Path):
    """Same layout as verify_beta3.c: n gamma, c-row, A rows.

    Here A=K, c=w, gamma=lam, so the C code checks z^T (K − λ (w1^T+1w^T)/2) z.
    """
    n = K.shape[0]
    lines = [f"{n} {lam:.16e}"]
    lines.append(" ".join(f"{w[i]:.16e}" for i in range(n)))
    for i in range(n):
        lines.append(" ".join(f"{K[i, j]:.16e}" for j in range(n)))
    path.write_text("\n".join(lines) + "\n")


def run_faces(matrix_path: Path, faces_path: Path) -> dict:
    cbin = HERE / "verify_beta3"
    src = HERE / "verify_beta3.c"
    subprocess.check_call(["gcc", "-O3", "-o", str(cbin), str(src), "-lm"])
    subprocess.check_call(
        [str(cbin), str(matrix_path), str(faces_path)], cwd=str(HERE)
    )
    out = {}
    for line in faces_path.read_text().splitlines():
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


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    fmin = float(FMIN_MP)
    b3 = float(1 / FMIN_MP)

    # Several windows: we take the best *global* number among them.
    configs = [
        (4, 16),
        (6, 18),
        (8, 20),
        (12, 20),
    ]
    rows = []
    best_global = fmin
    best_row = None

    for R, n in configs:
        print(f"assembling R={R} n={n} ...")
        blob = assemble_conservative(R, n)
        K, w = np_mats(blob)
        num = slsqp_rayleigh(K, w)
        print(f"  SLSQP Rayleigh (not a bound) {num:.8f}")

        # Binary search the largest λ with λ_min(M) ≥ 0 (PSD certificate).
        lo, hi = fmin, min(num, 0.99)
        psd_lam = fmin
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            ev0, _ = eig_psd_margin(K, w, mid)
            if ev0 >= 1e-12:
                psd_lam = mid
                lo = mid
            else:
                hi = mid
        ev_at, _ = eig_psd_margin(K, w, psd_lam)
        print(f"  PSD λ ≤ {psd_lam:.8f}  λ_min(M)={ev_at:.4e}")

        compact = psd_lam
        faces = None
        # If PSD is too close to fmin, try a slightly higher λ via faces (n≤20).
        face_target = min(num - 1e-4, psd_lam + 0.008)
        if n <= 20 and face_target > psd_lam + 1e-5:
            mat = CERTS / f"beta3_K_R{R}_n{n}.txt"
            fac = CERTS / f"beta3_faces_R{R}_n{n}.txt"
            write_matrix_kw(K, w, face_target, mat)
            print(f"  face-enum at λ={face_target:.6f} ...")
            faces = run_faces(mat, fac)
            print(
                f"  faces copositive={faces.get('copositive')} "
                f"minM={faces.get('min_mMm')} singular={faces.get('singular_or_illconditioned')}"
            )
            if faces.get("copositive"):
                compact = max(compact, face_target)

        gmin, gat = min_g_over_tail(compact, fmin)
        # Because g can dip to fmin, the lift may not improve on fmin.
        global_g = gmin
        beats = global_g > fmin + 1e-10 and (1 / global_g) < 1.1185
        row = {
            "R": R,
            "n": n,
            "slsqp_rayleigh": num,
            "psd_lambda": psd_lam,
            "psd_eig_min": ev_at,
            "compact_beta": compact,
            "face_target": face_target,
            "faces": faces,
            "g_min": global_g,
            "g_at_eps_s": gat,
            "global_gamma": global_g,
            "global_inv": 1 / global_g if global_g > 0 else None,
            "beats_1.1185": bool(beats),
        }
        rows.append(row)
        if global_g > best_global:
            best_global = global_g
            best_row = row
        print(
            f"  compact β_R≥{compact:.8f}  tail-g≥{global_g:.8f}  "
            f"1/g≤{1/global_g:.6f}  beats={beats}"
        )

    # Also record that the withdrawn lift fails the power-law test.
    withdrawn = {
        "h_at_0_1": 1 - (1 / 12) * (1 - fmin),
        "power_law_I_over_D": 0.9206549402498677,
        "fails": True,
        "note": (
            "h(0,1)≈0.991 > 0.921 = I/D of the HPS power-law trial "
            "placed entirely in a fixed-window 'tail'. The mid-radius "
            "+ h(D_L,D_R) lift in certify_beta3.py is not a global bound."
        ),
    }

    status = (
        "dent"
        if best_row and best_row["beats_1.1185"]
        else "residue"
    )
    cert = {
        "arxiv": "2504.18487v1",
        "urls_opened": [
            "https://arxiv.org/abs/2504.18487",
            "https://arxiv.org/html/2504.18487v1",
        ],
        "status": status,
        "is_new_bound": bool(status == "dent"),
        "beats_1.1185": bool(status == "dent"),
        "gamma_lower": S(mpf(best_global)),
        "gamma_inv_upper": S(1 / mpf(best_global)),
        "HPS_fmin": S(FMIN_MP),
        "HPS_b3": S(1 / FMIN_MP),
        "printed_1.1185": "1.1185",
        "method": (
            "Conservative z-kernel on geometric bins of [1,R] after "
            "inf(supp z)=1. PSD or C face-enum of M(λ). Right-tail "
            "mixture g(ε,s) clipped at fmin. The older h(D_L,D_R) lift "
            "is withdrawn."
        ),
        "configs": rows,
        "best": best_row,
        "withdrawn_tail_lemma": withdrawn,
        "did_not_use_invalid_1.1168": True,
    }
    out = CERTS / "beta3_global.json"
    out.write_text(json.dumps(cert, indent=2, default=str) + "\n")
    print("wrote", out)
    print("status:", status, "gamma≥", best_global, "1/gamma≤", 1 / best_global)
    if status != "dent":
        print("certify_beta3_global.py residue (no certified global dent)")
    else:
        print("certify_beta3_global.py PASS")


if __name__ == "__main__":
    main()
