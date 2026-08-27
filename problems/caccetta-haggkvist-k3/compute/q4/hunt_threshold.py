#!/usr/bin/env python3
"""Hunt a flag-algebra c < 0.34645 on the rebuilt F₄ system plus extras.

HKN's 8×8 SOS is on β-flags. q3 added the order-2 non-edge type (9×9).
This run also samples mixed β/η SOS, random rank-1 sums, and a longer
HiGHS loop. A certificate needs every F-coordinate strictly negative.
Saturation at the old threshold is leftover, not a numerical dent.
Do not treat 0.3388 as published.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

PARENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PARENT))
from flags4 import induced, type_of, enumerate_labeled  # noqa: E402
from hkn_replay import AR, BR, ac_slices, fork_coeffs, indT_coeffs, indV_coeffs  # noqa: E402
from optimize_bound import Q_from_as  # noqa: E402
from hkn_replay import A_VECS  # noqa: E402

HERE = Path(__file__).resolve().parent
KEEP = HERE / "certs" / "keep"

ETA_FLAGS = [(a, b) for a in (0, 1, 2) for b in (0, 1, 2)]


def eta_id(arcs3) -> int | None:
    if (0, 1) in arcs3 or (1, 0) in arcs3:
        return None

    def code(u, v):
        if (u, v) in arcs3:
            return 1
        if (v, u) in arcs3:
            return 2
        return 0

    return ETA_FLAGS.index((code(0, 2), code(1, 2)))


def compute_AC_eta():
    n_type = [0] * 32
    acc = np.zeros((9, 9, 32))
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        for perm in __import__("itertools").permutations(range(4)):
            x, y, z, w = perm
            if (x, y) in arcs or (y, x) in arcs:
                continue
            ki = eta_id(induced(arcs, (x, y, z)))
            kj = eta_id(induced(arcs, (x, y, w)))
            if ki is None or kj is None:
                continue
            acc[ki, kj, t] += 1
    AC = np.zeros((9, 9, 32))
    for t in range(32):
        if n_type[t]:
            AC[:, :, t] = acc[:, :, t] / n_type[t]
    return AC, n_type


def sos_eta(Qe, AC):
    return np.einsum("ij,ijk->k", Qe, AC)


def try_lp(c, sos):
    AR_A = np.array(AR, dtype=float)
    BR_A = np.array(BR, dtype=float)
    it = np.array(indT_coeffs(c))
    iv = np.array(indV_coeffs(c))
    fk = np.array(fork_coeffs(c))
    nvar = 1 + 14 + 3
    A_ub = np.zeros((32, nvar))
    b_ub = np.zeros(32)
    for k in range(32):
        A_ub[k, 0] = -1.0
        for i in range(14):
            A_ub[k, 1 + i] = BR_A[i, k] - c * AR_A[i, k]
        A_ub[k, 15] = it[k]
        A_ub[k, 16] = iv[k]
        A_ub[k, 17] = fk[k]
        b_ub[k] = -sos[k]
    bounds = [(None, None)] + [(None, None)] * 14 + [(0, None)] * 3
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
        "ok": t < -1e-6,
    }


def rand_psd(rng, dim, scale=20.0):
    rnk = int(rng.integers(1, dim + 1))
    A = rng.normal(scale=scale, size=(dim, rnk))
    return A @ A.T


def main():
    AC, n_type = compute_AC_eta()
    Qb0 = Q_from_as(A_VECS)
    MS = [np.array(M, dtype=float) for M in ac_slices()]
    rng = np.random.default_rng(4)
    targets = [0.34645, 0.34640, 0.3460, 0.340, 0.3388, 0.335]
    best = {}
    n_try = 80
    for c in targets:
        hit = None
        sos0 = np.array([float(np.sum(Qb0 * Mk)) for Mk in MS])
        got = try_lp(c, sos0)
        if got is not None:
            hit = {**got, "kind": "hkn-Q"}
        for i in range(n_try):
            Qb = 0.35 * Qb0 + 0.65 * rand_psd(rng, 8, 40.0)
            Qe = rand_psd(rng, 9, 25.0) if i % 2 == 0 else np.zeros((9, 9))
            sos = np.array([float(np.sum(Qb * Mk)) for Mk in MS]) + sos_eta(Qe, AC)
            got = try_lp(c, sos)
            if got is None:
                continue
            if hit is None or got["t"] < hit["t"]:
                hit = {**got, "kind": "mixed" if i % 2 == 0 else "beta-only"}
        best[str(c)] = None if hit is None else {k: hit[k] for k in hit}
        print(f"c={c} t={None if hit is None else hit['t']} kind={None if hit is None else hit.get('kind')}", flush=True)
    rec = {
        "n_labeled_by_type": n_type,
        "eta_flags": 9,
        "n_try": n_try,
        "best_t_by_c": best,
        "note": (
            "t<0 certifies emptiness at that c. "
            "If the best t at c<0.34645 stays nonnegative, the extra SOS "
            "did not move the F4 threshold. 0.3388 is a personal communication."
        ),
    }
    KEEP.mkdir(exist_ok=True)
    path = KEEP / "hunt_threshold.json"
    path.write_text(json.dumps(rec, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
