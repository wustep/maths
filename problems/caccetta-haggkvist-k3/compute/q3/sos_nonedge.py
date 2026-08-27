#!/usr/bin/env python3
"""Add a Cauchy–Schwarz block on the order-2 non-edge type.

HKN's 8×8 SOS is on β-flags (the directed-edge type).  The other order-2
type is two vertices with no arc.  Two 3-vertex flags of that type still
live on 4 vertices, so the block stays inside F₄.

If a PSD Qη makes the Farkas form strictly negative at some c < 0.34645,
that is a numerical dent.  Saturation at the old threshold is leftover.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

PARENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PARENT))
from flags4 import induced, type_of, enumerate_labeled  # noqa: E402
from hkn_replay import AR, BR, ac_slices, fork_coeffs, indT_coeffs, indV_coeffs  # noqa: E402
from optimize_bound import F_coords, Q_from_as, try_lp  # noqa: E402
from hkn_replay import A_VECS  # noqa: E402

HERE = Path(__file__).resolve().parent
KEEP = HERE / "certs" / "keep"

# η-flags: roots 0,1 with no arc 0–1; extra vertex 2.
# Encode the pair (0,2) and (1,2) as 0=none, 1=root→extra, 2=extra→root.
ETA_FLAGS = [(a, b) for a in (0, 1, 2) for b in (0, 1, 2)]  # 9


def eta_id(arcs3) -> int | None:
    if (0, 1) in arcs3 or (1, 0) in arcs3:
        return None
    def code(u, v):
        if (u, v) in arcs3:
            return 1
        if (v, u) in arcs3:
            return 2
        return 0
    pair = (code(0, 2), code(1, 2))
    return ETA_FLAGS.index(pair)


def compute_AC_eta():
    n_type = [0] * 32
    acc = np.zeros((9, 9, 32))
    for arcs in enumerate_labeled(4):
        t = type_of(arcs)
        n_type[t] += 1
        for perm in itertools.permutations(range(4)):
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


def try_lp_both(c, Qb, Qe, AC):
    MS = [np.array(M, dtype=float) for M in ac_slices()]
    sos_b = np.array([float(np.sum(Qb * Mk)) for Mk in MS])
    sos_e = sos_eta(Qe, AC)
    sos = sos_b + sos_e
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
    rng = np.random.default_rng(1)
    targets = [0.34645, 0.3460, 0.340, 0.3388, 0.335]
    best = {}
    for c in targets:
        hit = try_lp_both(c, Qb0, np.zeros((9, 9)), AC)
        for _ in range(40):
            Qb = 0.4 * Qb0 + 0.6 * rand_psd(rng, 8, 30.0)
            Qe = rand_psd(rng, 9, 20.0)
            got = try_lp_both(c, Qb, Qe, AC)
            if got is None:
                continue
            if hit is None or got["t"] < hit["t"]:
                hit = {**got, "Qb": Qb.tolist(), "Qe": Qe.tolist()}
        best[str(c)] = None if hit is None else {k: hit[k] for k in hit if k not in ("Qb", "Qe")}
        print(f"c={c} t={None if hit is None else hit['t']}", flush=True)
    rec = {
        "n_labeled_by_type": n_type,
        "eta_flags": 9,
        "best_t_by_c": best,
        "note": (
            "t<0 certifies emptiness at that c. "
            "If the best t at c<0.34645 stays nonnegative, the extra SOS "
            "did not move the F4 threshold."
        ),
    }
    KEEP.mkdir(exist_ok=True)
    path = KEEP / "sos_nonedge.json"
    path.write_text(json.dumps(rec, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
