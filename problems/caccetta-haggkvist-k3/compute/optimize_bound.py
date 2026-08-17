#!/usr/bin/env python3
"""Search for an F₄ flag-algebra certificate beating HKN's 0.3465.

Matrices AC, AR, BR, IndT, IndV, Fork were independently recomputed in
flags4.py / ind_fork.py and agree with Hladký–Král'–Norin (Combinatorica
2017) Tables 1–2 and (4.14)–(4.15)/fork.  The published aᵢ are two-decimal
display values and do not reproduce (4.22); we treat Q ≽ 0 as free and
re-optimise.

Certificate for a number c: a PSD 8×8 matrix Q, a vector b ∈ ℝ¹⁴, and
scalars cT,cV,d ≥ 0 such that every coordinate of

    F(c,r)_k = ⟨Q, M_k⟩ + b·(BR−c AR)_k + cT IndT_k(c) + cV IndV_k(c) + d Fork_k(c)

is strictly negative.  Then F(c,r) < 0 on the simplex, so R(c)=∅, so
δα < c in every triangle-free oriented graph.

Uses scipy.optimize.linprog (HiGHS) on the linear multipliers for a
Cholesky parameterisation of Q.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

# Reuse the independently checked pieces from hkn_replay (AC/AR/BR/Ind/Fork
# match the paper; aᵢ are not used except as a warm start).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hkn_replay import (  # noqa: E402
    AR,
    BR,
    A_VECS,
    CT,
    CV,
    D_FORK,
    ac_slices,
    fork_coeffs,
    indT_coeffs,
    indV_coeffs,
    quad_form,
)

OUT = Path(__file__).resolve().parent / "certs"
OUT.mkdir(exist_ok=True)

MS = [np.array(M, dtype=float) for M in ac_slices()]  # 32 of 8×8
AR_A = np.array(AR, dtype=float)  # 14×32
BR_A = np.array(BR, dtype=float)


def pack_chol(L_flat: np.ndarray) -> np.ndarray:
    """36 lower-triangular entries → 8×8 L (row-major lower)."""
    L = np.zeros((8, 8))
    idx = 0
    for i in range(8):
        for j in range(i + 1):
            L[i, j] = L_flat[idx]
            idx += 1
    return L


def unpack_chol(L: np.ndarray) -> np.ndarray:
    out = []
    for i in range(8):
        for j in range(i + 1):
            out.append(L[i, j])
    return np.array(out)


def Q_from_as(avecs) -> np.ndarray:
    Q = np.zeros((8, 8))
    for a in avecs:
        aa = np.array(a, dtype=float)
        Q += np.outer(aa, aa)
    return Q


def sos_from_Q(Q: np.ndarray) -> np.ndarray:
    return np.array([float(np.sum(Q * Mk)) for Mk in MS])


def try_lp(c: float, Q: np.ndarray, eps: float = 1e-6):
    """Fix Q, minimise t s.t. F_k ≤ t.  Success if t < 0.

    Variables: t, b[14], cT, cV, d   (17 vars).  b free, rest ≥ 0 except t free.
    """
    sos = sos_from_Q(Q)
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c))
    # F_k = sos_k + sum_i b_i (BR_ik - c AR_ik) + cT it_k + cV iv_k + d fk_k
    # F_k - t ≤ 0
    # vars: [t, b0..b13, cT, cV, d]
    nvar = 1 + 14 + 3
    A_ub = np.zeros((32, nvar))
    b_ub = np.zeros(32)
    for k in range(32):
        A_ub[k, 0] = -1.0  # -t
        for i in range(14):
            A_ub[k, 1 + i] = BR_A[i, k] - c * AR_A[i, k]
        A_ub[k, 15] = it[k]
        A_ub[k, 16] = iv[k]
        A_ub[k, 17] = fk[k]
        b_ub[k] = -sos[k]  # move sos to RHS: linear ≤ -sos  i.e. sos+linear-t ≤ 0
    bounds = [(None, None)]  # t
    bounds += [(None, None)] * 14  # b
    bounds += [(0, None)] * 3  # cT,cV,d
    cobj = np.zeros(nvar)
    cobj[0] = 1.0
    res = linprog(cobj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not res.success:
        return None
    t = float(res.x[0])
    return {
        "t": t,
        "b": res.x[1:15].tolist(),
        "cT": float(res.x[15]),
        "cV": float(res.x[16]),
        "d": float(res.x[17]),
        "success": res.success,
        "ok": t < -eps,
    }


def F_coords(c, Q, b, cT, cV, d):
    sos = sos_from_Q(Q)
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c))
    b = np.array(b)
    out = sos + (b @ (BR_A - c * AR_A)) + cT * it + cV * iv + d * fk
    return out


def linear_only_empty(c: float):
    """Is R'(c) empty?  r≥0, 1ᵀr=1, (BR-cAR)r=0, IndT,IndV,Fork ≥ 0."""
    # feasibility LP: max 0 s.t. those
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c))
    # vars r[32]
    A_eq = BR_A - c * AR_A  # 14 × 32
    b_eq = np.zeros(14)
    # also 1ᵀr = 1
    A_eq = np.vstack([A_eq, np.ones((1, 32))])
    b_eq = np.append(b_eq, 1.0)
    # IndT ≥ 0, IndV ≥ 0, Fork ≥ 0  →  -Ind · r ≤ 0
    A_ub = np.vstack([-it, -iv, -fk])
    b_ub = np.zeros(3)
    bounds = [(0, None)] * 32
    res = linprog(np.zeros(32), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")
    return (not res.success), res


def chol_of_psd(Q: np.ndarray) -> np.ndarray:
    # jitter for numerical PSD
    w, V = np.linalg.eigh(0.5 * (Q + Q.T))
    w = np.clip(w, 0, None)
    Qp = (V * w) @ V.T
    try:
        return np.linalg.cholesky(Qp + 1e-12 * np.eye(8))
    except np.linalg.LinAlgError:
        return np.linalg.cholesky(Qp + 1e-8 * np.eye(8))


def random_search(c: float, n_try: int = 80, seed: int = 0):
    """Random PSD Q around HKN warm-start; keep the best t."""
    rng = np.random.default_rng(seed)
    Q0 = Q_from_as(A_VECS)
    best = None
    # include the exact HKN Q
    candidates = [Q0]
    for _ in range(n_try):
        # Q = A A^T for A 8×r, r=1..8, plus noise on Q0
        rnk = int(rng.integers(1, 9))
        A = rng.normal(scale=30.0, size=(8, rnk))
        Q = A @ A.T
        # also a convex combo with Q0
        lam = float(rng.random())
        Q = lam * Q0 + (1 - lam) * Q
        candidates.append(Q)
        # scaled Q0
        candidates.append((0.3 + 3 * rng.random()) * Q0)
    for Q in candidates:
        got = try_lp(c, Q)
        if got is None:
            continue
        if best is None or got["t"] < best["t"]:
            best = {**got, "Q": Q.tolist()}
    return best


def refine_chol(c: float, Q: np.ndarray, steps: int = 40):
    """Coordinate-descent on Cholesky of Q, calling the LP at each step."""
    L = chol_of_psd(np.array(Q))
    x = unpack_chol(L)
    best_Q = np.array(Q)
    best = try_lp(c, best_Q)
    if best is None:
        return None
    scale = 3.0
    rng = np.random.default_rng(1)
    for step in range(steps):
        improved = False
        order = rng.permutation(len(x))
        for j in order:
            for sgn in (+1.0, -1.0):
                trial = x.copy()
                trial[j] += sgn * scale
                Lt = pack_chol(trial)
                Qt = Lt @ Lt.T
                got = try_lp(c, Qt)
                if got is not None and got["t"] < best["t"] - 1e-9:
                    x = trial
                    best = {**got, "Q": Qt.tolist()}
                    best_Q = Qt
                    improved = True
                    break
        if not improved:
            scale *= 0.5
            if scale < 1e-3:
                break
    return best


def binary_search_threshold(c_lo=1 / 3 + 1e-6, c_hi=0.36, seed=0):
    """Smallest c where some Q we try certifies F < 0."""
    log = []
    best_cert = None
    # coarse grid first
    grid = list(np.linspace(c_hi, c_lo, 12))
    for c in grid:
        lin_empty, _ = linear_only_empty(float(c))
        rnd = random_search(float(c), n_try=40, seed=seed)
        rec = {
            "c": float(c),
            "linear_only_empty": bool(lin_empty),
            "t": None if rnd is None else rnd["t"],
            "ok": False if rnd is None else bool(rnd["ok"]),
        }
        log.append(rec)
        print(f"  c={c:.6f}  linear_empty={lin_empty}  t={rec['t']}", flush=True)
        if rnd is not None and rnd["ok"]:
            refined = refine_chol(float(c), np.array(rnd["Q"]), steps=20)
            use = refined if refined is not None and refined["t"] < rnd["t"] else rnd
            if use["ok"]:
                best_cert = {**use, "c": float(c)}
                c_hi = float(c)
    # binary search below the best certified c
    if best_cert is None:
        return None, log
    lo, hi = c_lo, best_cert["c"]
    Qw = np.array(best_cert["Q"])
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        got = try_lp(mid, Qw)
        if got is not None and got["ok"]:
            hi = mid
            best_cert = {**got, "Q": Qw.tolist(), "c": mid}
        else:
            rnd = random_search(mid, n_try=30, seed=seed + 7)
            if rnd is not None and rnd["ok"]:
                Qw = np.array(rnd["Q"])
                hi = mid
                best_cert = {**rnd, "c": mid}
            else:
                # try refine from current Q
                ref = refine_chol(mid, Qw, steps=15)
                if ref is not None and ref["ok"]:
                    Qw = np.array(ref["Q"])
                    hi = mid
                    best_cert = {**ref, "c": mid}
                else:
                    lo = mid
        print(f"  bin c in ({lo:.6f},{hi:.6f}) best_c={best_cert['c']:.6f} t={best_cert['t']:.6f}", flush=True)
    return best_cert, log


def main():
    print("Checking linear-only emptiness (no SOS) ...")
    for c in (0.40, 0.38, 0.36, 0.3543, 0.3532, 0.3465, 0.34, 1 / 3 + 0.001):
        empty, res = linear_only_empty(c)
        print(f"  R'(c={c:.4f}) empty={empty}  success={res.success}  msg={res.message}")

    print("\nHKN rounded-aᵢ warm start at 0.3465:")
    Q0 = Q_from_as(A_VECS)
    got = try_lp(0.3465, Q0)
    print("  ", None if got is None else {k: got[k] for k in ("t", "ok", "cT", "cV", "d")})

    print("\nSearching certificates ...")
    cert, log = binary_search_threshold()
    payload = {
        "published_hkn": 0.3465,
        "personal_communication_3388": 0.3388,
        "linear_scan": log,
        "certificate": None,
    }
    if cert is None:
        print("No c < 0.36 certified.")
    else:
        Q = np.array(cert["Q"])
        coords = F_coords(cert["c"], Q, cert["b"], cert["cT"], cert["cV"], cert["d"])
        w = float(np.max(coords))
        ev = np.linalg.eigvalsh(0.5 * (Q + Q.T))
        payload["certificate"] = {
            "c": cert["c"],
            "t": cert["t"],
            "worst_F": w,
            "all_negative": bool(np.all(coords < 0)),
            "Q_eigs": ev.tolist(),
            "Q_min_eig": float(ev.min()),
            "b": cert["b"],
            "cT": cert["cT"],
            "cV": cert["cV"],
            "d": cert["d"],
            "Q": cert["Q"],
            "F_coords": coords.tolist(),
        }
        print(f"\nCERTIFIED c = {cert['c']:.8f}  worst F = {w:.8f}  min_eig(Q)={ev.min():.4g}")
        print("beats HKN 0.3465?", cert["c"] < 0.3465 - 1e-8)
        print("beats 0.3388 communication?", cert["c"] < 0.3388 - 1e-8)

    path = OUT / "optimize_bound.json"
    path.write_text(json.dumps(payload, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
