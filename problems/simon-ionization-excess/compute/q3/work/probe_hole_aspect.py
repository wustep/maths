#!/usr/bin/env python3
"""Adversarial probe of the proposed q3 aspect lift for β_3.

Writes a JSON summary next to this script. Does not touch q2 certs.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
Q2 = HERE.parents[1] / "q2"

FMIN = 0.8941074569749823
GAMMA12 = 0.8995260524666927
QHI = 0.921
ASPECT_CLAIM = QHI / (1.0 - QHI)  # ≈11.658
T0 = (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0) - (1.0 + math.sqrt(2.0)) ** (-1.0 / 3.0)


def g_kernel(r: float, u: float) -> float:
    m = r if r >= u else u
    return (r**3 + u**3) / (2.0 * m)


def atomic_ID(radii, masses):
    r = np.asarray(radii, dtype=float)
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    D = float(np.dot(m, r**2))
    I = 0.0
    for i in range(len(r)):
        for j in range(len(r)):
            I += m[i] * m[j] * g_kernel(r[i], r[j])
    return I, D, I / D


def V_atomic(x, radii, masses):
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    return float(sum(mu * g_kernel(x, float(u)) for u, mu in zip(radii, m)))


def moments(radii, masses):
    r = np.asarray(radii, dtype=float)
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    return {
        "M_m1": float(np.dot(m, 1.0 / r)),
        "M3": float(np.dot(m, r**3)),
        "D": float(np.dot(m, r**2)),
        "m": m,
        "r": r,
    }


def check_VR_formulas(radii, masses):
    """V(1) and V(R) identities that claim to hold whenever supp ⊆ [1,R]."""
    mo = moments(radii, masses)
    r = mo["r"] / mo["r"].min()
    m = mo["m"]
    R = float(r.max())
    D = float(np.dot(m, r**2))
    Mm1 = float(np.dot(m, 1.0 / r))
    M3 = float(np.dot(m, r**3))
    V1 = V_atomic(1.0, r, m)
    VR = V_atomic(R, r, m)
    V1_pred = D / 2.0 + Mm1 / 2.0
    VR_pred = R**2 / 2.0 + M3 / (2.0 * R)
    return {
        "R": R,
        "D": D,
        "V1": V1,
        "V1_pred": V1_pred,
        "V1_abs_err": abs(V1 - V1_pred),
        "VR": VR,
        "VR_pred": VR_pred,
        "VR_abs_err": abs(VR - VR_pred),
    }


def equilibrium_residual(radii, masses):
    I, D, Q = atomic_ID(radii, masses)
    r = np.asarray(radii, dtype=float)
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    rels = []
    for ri in r:
        V = V_atomic(float(ri), r, m)
        rhs = 0.5 * Q * (ri**2 + D)
        rels.append(abs(V - rhs) / max(abs(rhs), 1e-30))
    return I, D, Q, max(rels), rels


def two_atomic_mass_stationary(R: float):
    """Solve V(1)=(Q/2)(1+D) for mass p at 1, 1-p at R."""

    def pack(p):
        p = float(np.clip(p, 1e-12, 1 - 1e-12))
        return np.array([1.0, R]), np.array([p, 1.0 - p])

    def gap(p):
        r, m = pack(p[0])
        I, D, Q = atomic_ID(r, m)
        V1 = V_atomic(1.0, r, m)
        return (V1 - 0.5 * Q * (1.0 + D)) ** 2

    best = None
    for p0 in (0.1, 0.3, 0.5, 0.64, 0.8, 0.95):
        res = minimize(gap, [p0], bounds=[(1e-9, 1 - 1e-9)], method="L-BFGS-B")
        r, m = pack(res.x[0])
        I, D, Q, mx, _ = equilibrium_residual(r, m)
        rec = {
            "R": R,
            "p": float(m[0]),
            "Q": Q,
            "D": D,
            "max_rel_err": mx,
            "Q_over_1mQ": Q / (1.0 - Q) if Q < 1 else None,
            "bound_holds": (Q / (1.0 - Q) > R) if Q < 1 else False,
            "Q_le_Qhi": Q <= QHI,
            "aspect_ge_12": R >= 12,
        }
        if best is None or rec["max_rel_err"] < best["max_rel_err"]:
            best = rec
    return best


def power_law_ID(alpha: float, n: float) -> float:
    if n <= 1.0 + 1e-12:
        return 1.0
    if abs(alpha + 1.0) < 1e-14:
        C = 1.0 / math.log(n)
    else:
        C = (alpha + 1.0) / (n ** (alpha + 1.0) - 1.0)
    if abs(alpha + 3.0) < 1e-14:
        D = C * math.log(n)
    else:
        D = C * (n ** (alpha + 3.0) - 1.0) / (alpha + 3.0)

    def inner(u: float) -> float:
        if abs(alpha + 4.0) < 1e-14:
            a = math.log(u)
        else:
            a = (u ** (alpha + 4.0) - 1.0) / (alpha + 4.0)
        if abs(alpha + 1.0) < 1e-14:
            b = math.log(u)
        else:
            b = (u ** (alpha + 1.0) - 1.0) / (alpha + 1.0)
        return u ** (alpha - 1.0) * (a + (u**3) * b)

    L = math.log(n)
    nodes, weights = np.polynomial.legendre.leggauss(96)
    acc = 0.0
    for x, w in zip(nodes, weights):
        s = 0.5 * L * (x + 1.0)
        u = math.exp(s)
        acc += w * inner(u) * u
    I = C * C * acc * (0.5 * L)
    return I / D


def optimize_k_atomic(k: int, aspect_min: float | None = None, seed: int = 0):
    def unpack(x):
        logs = x[:k]
        raw = x[k:]
        radii = np.exp(logs - logs.min())
        if aspect_min is not None:
            # force last (after sort) to be at least aspect_min
            radii = np.sort(radii)
            if radii[-1] < aspect_min:
                radii[-1] = aspect_min
        masses = np.exp(raw)
        masses = masses / masses.sum()
        return radii, masses

    def fun(x):
        r, m = unpack(x)
        return atomic_ID(r, m)[2]

    best = 1.0
    best_x = None
    rng = np.random.default_rng(3 + k + seed)
    starts = []
    logs = np.array([-i * math.log(T0) for i in range(k)])
    starts.append(np.concatenate([logs, np.zeros(k)]))
    hi = math.log(aspect_min) if aspect_min else math.log(3.5)
    starts.append(np.concatenate([np.linspace(0.0, hi, k), np.zeros(k)]))
    for _ in range(10):
        starts.append(rng.normal(0.0, 1.0, size=2 * k))
    for z0 in starts:
        res = minimize(fun, z0, method="Nelder-Mead", options={"maxiter": 2500})
        if res.fun < best:
            best = float(res.fun)
            best_x = res.x
    r, m = unpack(best_x)
    I, D, Q, mx, _ = equilibrium_residual(r, m)
    return {
        "k": k,
        "Q": Q,
        "aspect": float(r.max() / r.min()),
        "D": D,
        "max_rel_err": mx,
        "Q_over_1mQ": Q / (1.0 - Q) if Q < 1 else None,
        "radii": r.tolist(),
        "masses": m.tolist(),
    }


def two_clump(R_far: float, p_far: float, n_each: int = 6):
    """Near clump on [1, 3.5] power-like + far clump around R_far."""
    near_r = np.geomspace(1.0, 3.5, n_each)
    far_r = np.geomspace(R_far / 1.2, R_far, n_each)
    r = np.concatenate([near_r, far_r])
    # equal-m within clump
    m = np.concatenate(
        [np.full(n_each, (1.0 - p_far) / n_each), np.full(n_each, p_far / n_each)]
    )
    I, D, Q = atomic_ID(r, m)
    return {"R_far": R_far, "p_far": p_far, "Q": Q, "aspect": float(r.max()), "D": D}


def random_search(n_trials: int = 400, seed: int = 11):
    rng = np.random.default_rng(seed)
    best = 1.0
    hits_below_gamma = []
    crit_hits = []
    for _ in range(n_trials):
        k = int(rng.integers(2, 16))
        hi = rng.choice([3.5, 8.0, 12.0, 20.0, 50.0, 200.0])
        logs = np.sort(rng.uniform(0.0, math.log(hi), size=k))
        logs[0] = 0.0
        masses = rng.dirichlet(np.ones(k))
        r = np.exp(logs)
        Q = atomic_ID(r, masses)[2]
        best = min(best, Q)
        if Q < GAMMA12:
            hits_below_gamma.append({"k": k, "Q": Q, "aspect": float(r.max())})
        _, _, Q2, mx, _ = equilibrium_residual(r, masses)
        if mx < 1e-3 and Q2 <= QHI and r.max() >= 12:
            crit_hits.append({"k": k, "Q": Q2, "aspect": float(r.max()), "err": mx})
    return best, hits_below_gamma, crit_hits


def analyze_singular_faces(masks: list[int]):
    mat = Q2 / "certs" / "beta3_mid_R12_n22.txt"
    lines = mat.read_text().splitlines()
    n, gam = lines[0].split()
    n = int(n)
    gam = float(gam)
    c = np.array([float(x) for x in lines[1].split()])
    A = np.array([[float(x) for x in lines[2 + i].split()] for i in range(n)])
    M = A - 0.5 * gam * (c[:, None] + c[None, :])
    rows = []
    for mask in masks:
        idx = [b for b in range(n) if mask & (1 << b)]
        MS = M[np.ix_(idx, idx)]
        AS = A[np.ix_(idx, idx)]
        cS = c[idx]
        ev = np.linalg.eigvalsh(MS)
        # least-squares M x = 1
        ones = np.ones(len(idx))
        x, *_ = np.linalg.lstsq(MS, ones, rcond=None)
        resid = float(np.linalg.norm(MS @ x - ones))
        s = float(np.sum(x))
        npos = int(np.sum(x > 1e-12))
        nneg = int(np.sum(x < -1e-12))
        same_sign = (npos == len(idx)) or (nneg == len(idx))
        val = None
        phi = None
        if abs(s) > 1e-14:
            m = x / s
            val = float(m @ MS @ m)
            den = float(cS @ m)
            if den > 0:
                phi = float(m @ AS @ m / den)
        # min of quadratic on this face via SLSQP
        k = len(idx)

        def qfun(z):
            return float(z @ MS @ z)

        cons = {"type": "eq", "fun": lambda z: np.sum(z) - 1.0}
        bounds = [(0.0, 1.0)] * k
        qmin = 1e9
        for z0 in (np.ones(k) / k, np.clip(np.abs(x), 1e-12, None)):
            z0 = z0 / z0.sum()
            res = minimize(
                qfun,
                z0,
                bounds=bounds,
                constraints=cons,
                method="SLSQP",
                options={"maxiter": 400, "ftol": 1e-14},
            )
            if res.success:
                qmin = min(qmin, float(res.fun))
        # vertices
        qmin = min(qmin, float(np.min(np.diag(MS))))
        rows.append(
            {
                "mask": mask,
                "k": k,
                "idx": idx,
                "eig_min": float(ev[0]),
                "eig_max": float(ev[-1]),
                "n_near0": int(np.sum(np.abs(ev) < 1e-10)),
                "lstsq_resid": resid,
                "same_sign_lstsq": same_sign,
                "mMm_lstsq": val,
                "phi_lstsq": phi,
                "slsqp_min_mMm": qmin if qmin < 1e8 else None,
                "neg_interior_critical": bool(
                    same_sign and val is not None and val < -1e-12
                ),
            }
        )
    return rows


def main():
    out = {
        "fmin": FMIN,
        "gamma12": GAMMA12,
        "Qhi": QHI,
        "Qhi_over_1mQhi": ASPECT_CLAIM,
        "twelve_over_thirteen": 12.0 / 13.0,
    }

    # --- V(1), V(R) always-true formulas ---
    rng = np.random.default_rng(0)
    form_errs = []
    for _ in range(80):
        k = int(rng.integers(2, 10))
        r = np.sort(np.exp(rng.uniform(0.0, math.log(30.0), size=k)))
        r[0] = 1.0
        m = rng.dirichlet(np.ones(k))
        form_errs.append(check_VR_formulas(r, m))
    # include a point with mass near 0-ish (r=1e-3 before scale → after scale it's 1)
    form_errs.append(check_VR_formulas([1.0, 2.0, 12.0], [0.2, 0.3, 0.5]))
    out["VR_formula_max_abs_err"] = max(
        max(e["V1_abs_err"], e["VR_abs_err"]) for e in form_errs
    )
    out["VR_formula_samples"] = form_errs[:5] + [form_errs[-1]]

    # --- 2-atomic mass-stationary curve ---
    two_stat = [
        two_atomic_mass_stationary(R)
        for R in (1.78, 2.0, 4.0, 8.0, 11.7, 12.0, 12.5, 16.0, 20.0, 40.0)
    ]
    out["two_atomic_stationary"] = two_stat
    out["two_atomic_R12"] = two_stat[5]
    out["any_stat_QleQhi_aspect_ge12"] = any(
        r["Q_le_Qhi"] and r["aspect_ge_12"] and r["max_rel_err"] < 1e-6 for r in two_stat
    )

    # --- known 6-atomic local min vs aspect bound ---
    r6 = np.array(
        [
            1.0,
            1.2557746075059502,
            1.543824249248174,
            1.8871052268055883,
            2.319961557207525,
            2.913359871416808,
        ]
    )
    m6 = np.array(
        [
            0.2522610362609393,
            0.21585235829528895,
            0.1806624028716379,
            0.14779821618584926,
            0.11683721548862015,
            0.08658877089766435,
        ]
    )
    I, D, Q, mx, _ = equilibrium_residual(r6, m6)
    mo = moments(r6, m6)
    Mm1_id = Q + (Q - 1.0) * D
    M3_id = (Q - 1.0) * r6.max() ** 3 + Q * D * r6.max()
    out["six_atomic_check"] = {
        "Q": Q,
        "D": D,
        "aspect": float(r6.max()),
        "eq_max_rel": mx,
        "M_m1": mo["M_m1"],
        "M_m1_from_criticality": Mm1_id,
        "M_m1_err": abs(mo["M_m1"] - Mm1_id),
        "M3": mo["M3"],
        "M3_from_criticality": M3_id,
        "M3_err": abs(mo["M3"] - M3_id),
        "Q_over_1mQ": Q / (1.0 - Q),
    }

    # --- power-law / heavy tail ---
    pl = []
    for alpha, n in [
        (-2.0, 3.5),
        (-2.0, 12.0),
        (-2.0, 80.0),
        (-3.5, 20.0),
        (-3.5, 200.0),
        (-4.0, 50.0),
        (-4.0, 1.0e3),
        (-2.5, 10.0),
        (-1.5, 5.0),
        (0.0, 4.0),
    ]:
        pl.append({"alpha": alpha, "n": n, "Q": power_law_ID(alpha, n)})
    out["power_law"] = pl
    out["power_law_min_Q"] = min(p["Q"] for p in pl)

    # 64-atom quadrature of the HPS trial
    edges = np.geomspace(1.0, 3.50, 65)
    radii = np.sqrt(edges[:-1] * edges[1:])
    masses = np.log(edges[1:] / edges[:-1])  # α=-2
    I, D, Q64 = atomic_ID(radii, masses)
    out["power_law_64atom"] = {
        "Q": Q64,
        "D": D,
        "aspect": float(radii.max() / radii.min()),
        "Q_over_1mQ": Q64 / (1.0 - Q64),
        "below_12_13": Q64 < 12.0 / 13.0,
    }

    # --- two-clump scan ---
    clumps = []
    for Rf in (12.0, 20.0, 50.0, 200.0):
        for p in (0.01, 0.05, 0.2, 0.5, 0.8, 0.95):
            clumps.append(two_clump(Rf, p))
    out["two_clump_min_Q"] = min(c["Q"] for c in clumps)
    out["two_clump_best"] = min(clumps, key=lambda c: c["Q"])
    out["two_clump_below_gamma"] = [c for c in clumps if c["Q"] < GAMMA12]

    # --- random atomic ---
    rnd_min, rnd_hits, rnd_crit = random_search(500)
    out["random_min_Q"] = rnd_min
    out["random_below_gamma"] = rnd_hits
    out["random_crit_QleQhi_aspect12"] = rnd_crit

    # --- optimize at forced aspect ≥ 12 ---
    forced = [optimize_k_atomic(k, aspect_min=12.0, seed=1) for k in (2, 3, 4, 6, 8)]
    out["forced_aspect12"] = [
        {k: v for k, v in rec.items() if k not in ("radii", "masses")} | {"n_radii": rec["k"]}
        for rec in forced
    ]
    out["forced_aspect12_min_Q"] = min(r["Q"] for r in forced)
    out["forced_aspect12_any_below_gamma"] = any(r["Q"] < GAMMA12 for r in forced)
    out["forced_aspect12_crit_QleQhi"] = [
        r for r in forced if r["max_rel_err"] < 1e-3 and r["Q"] <= QHI
    ]

    # unconstrained small-k (sanity)
    uncon = [optimize_k_atomic(k, aspect_min=None, seed=2) for k in (2, 3, 4)]
    out["unconstrained_smallk"] = [
        {k: v for k, v in rec.items() if k not in ("radii", "masses")} for rec in uncon
    ]

    # --- mass near 0 (before scaling: atom at eps) ---
    near0 = []
    for eps in (1e-6, 1e-3, 0.05, 0.2):
        for p0 in (0.01, 0.2, 0.5):
            r = np.array([eps, 1.0, 3.5])
            m = np.array([p0, 0.5 * (1 - p0), 0.5 * (1 - p0)])
            I, D, Q = atomic_ID(r, m)
            near0.append({"eps": eps, "p0": p0, "Q": Q, "aspect": float(r.max() / r.min())})
    out["near0_min_Q"] = min(x["Q"] for x in near0)
    out["near0_best"] = min(near0, key=lambda x: x["Q"])

    # --- F(r)=2V/(r^2+D) at large r for the 64-atom trial ---
    def F_of(x, r, m, D):
        return 2.0 * V_atomic(x, r, m) / (x**2 + D)

    rpl, mpl = radii, masses / masses.sum()
    _, Dpl, Qpl = atomic_ID(rpl, mpl)
    out["F_large_r"] = {
        "Q": Qpl,
        "F_at_R": F_of(float(rpl.max()), rpl, mpl, Dpl),
        "F_at_20": F_of(20.0, rpl, mpl, Dpl),
        "F_at_200": F_of(200.0, rpl, mpl, Dpl),
        "V_minus_rhs_at_200": V_atomic(200.0, rpl, mpl)
        - 0.5 * Qpl * (200.0**2 + Dpl),
        "note": "V-rhs ~ (1-Q)r^2/2 > 0, not negative",
    }

    # --- Q_hi / (1-Q_hi) for several trials ---
    trials = {
        "power64": Q64,
        "explore_power": 0.9206549282371305,
        "k6": 0.9232307844581592,
        "k2": 0.9432997272187643,
        "Qhi_claimed": QHI,
    }
    out["aspect_caps"] = {
        name: {"Q": q, "Q_over_1mQ": q / (1.0 - q), "lt12": q / (1.0 - q) < 12}
        for name, q in trials.items()
    }

    # singular faces: filled later if dump exists
    dump = HERE / "R12_singular_masks.txt"
    if dump.exists():
        masks = []
        for line in dump.read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            masks.append(int(line.split()[0]))
        out["R12_singular"] = analyze_singular_faces(masks)
        out["R12_singular_neg_interior"] = any(
            r["neg_interior_critical"] for r in out["R12_singular"]
        )
        out["R12_singular_slsqp_neg"] = [
            r for r in out["R12_singular"] if (r["slsqp_min_mMm"] or 0) < -1e-12
        ]
    else:
        out["R12_singular"] = None

    out["any_Q_below_gamma"] = bool(
        out["power_law_min_Q"] < GAMMA12
        or out["two_clump_min_Q"] < GAMMA12
        or out["random_min_Q"] < GAMMA12
        or out["forced_aspect12_min_Q"] < GAMMA12
        or out["near0_min_Q"] < GAMMA12
        or rnd_hits
    )
    dest = HERE / "probe_hole_aspect.json"

    def _jsonable(o):
        if isinstance(o, dict):
            return {str(k): _jsonable(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_jsonable(v) for v in o]
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return _jsonable(o.tolist())
        return o

    dest.write_text(json.dumps(_jsonable(out), indent=2) + "\n")
    print("wrote", dest)
    print("VR formula max abs err", out["VR_formula_max_abs_err"])
    print("power64 Q", Q64, "cap", Q64 / (1 - Q64))
    print("two-atomic R=12", two_stat[5])
    print("forced aspect12 min Q", out["forced_aspect12_min_Q"])
    print("random min Q", rnd_min)
    print("any Q below gamma12", out["any_Q_below_gamma"])
    print("any stat Q<=Qhi aspect>=12", out["any_stat_QleQhi_aspect_ge12"])


if __name__ == "__main__":
    main()
