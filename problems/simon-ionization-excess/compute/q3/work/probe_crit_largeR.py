#!/usr/bin/env python3
"""Hunt a mass-stationary k-atomic with Q<=0.921 and aspect>=12.

Also recompute the α=-2 64-atom trial with the correct bin masses,
and check 3-scale clumps.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
QHI = 0.921
GAMMA12 = 0.8995260524666927
T0 = (1.0 + math.sqrt(2.0)) ** (1.0 / 3.0) - (1.0 + math.sqrt(2.0)) ** (-1.0 / 3.0)


def g_kernel(r, u):
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
            I += m[i] * m[j] * g_kernel(float(r[i]), float(r[j]))
    return I, D, I / D


def V_atomic(x, radii, masses):
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    return float(sum(mu * g_kernel(x, float(u)) for u, mu in zip(radii, m)))


def eq_stats(radii, masses):
    I, D, Q = atomic_ID(radii, masses)
    r = np.asarray(radii, dtype=float)
    m = np.asarray(masses, dtype=float)
    m = m / m.sum()
    rels = []
    for ri in r:
        V = V_atomic(float(ri), r, m)
        rhs = 0.5 * Q * (float(ri) ** 2 + D)
        rels.append(abs(V - rhs) / max(abs(rhs), 1e-30))
    return {
        "Q": Q,
        "D": D,
        "aspect": float(r.max() / r.min()),
        "max_rel_err": max(rels),
        "Q_over_1mQ": Q / (1.0 - Q) if Q < 1 else None,
        "masses": m.tolist(),
        "radii": r.tolist(),
    }


def power64_correct():
    n, k, alpha = 3.50, 64, -2.0
    edges = np.geomspace(1.0, n, k + 1)
    radii = np.sqrt(edges[:-1] * edges[1:])
    masses = (edges[1:] ** (alpha + 1.0) - edges[:-1] ** (alpha + 1.0)) / (alpha + 1.0)
    st = eq_stats(radii, masses)
    st["tag"] = "power64_alpha-2"
    return st


def minimize_eq_at_aspect(k: int, R: float, seed: int = 0):
    """Min equilibrium residual with r_min=1, r_max=R fixed."""

    def unpack(x):
        # k-2 interior log-radii in (0, log R), k log-masses
        if k == 2:
            radii = np.array([1.0, R])
            masses = np.exp(x)
        else:
            logs = 1e-6 + (math.log(R) - 2e-6) * (1.0 / (1.0 + np.exp(-x[: k - 2])))
            interiors = np.sort(np.exp(logs))
            radii = np.concatenate([[1.0], interiors, [R]])
            masses = np.exp(x[k - 2 :])
        masses = masses / masses.sum()
        return radii, masses

    def fun(x):
        r, m = unpack(x)
        return eq_stats(r, m)["max_rel_err"]

    dim = (k - 2) + k
    rng = np.random.default_rng(seed + k)
    best = None
    starts = [np.zeros(dim)]
    # geometric interiors
    if k > 2:
        t = np.linspace(0, 1, k)[1:-1]
        logs = np.log(R) * t
        # inverse sigmoid
        z = np.log((logs / math.log(R)) / (1 - logs / math.log(R) + 1e-12))
        starts.append(np.concatenate([z, np.zeros(k)]))
    for _ in range(8):
        starts.append(rng.normal(0.0, 1.0, size=dim))
    for z0 in starts:
        res = minimize(fun, z0, method="Nelder-Mead", options={"maxiter": 3000})
        r, m = unpack(res.x)
        st = eq_stats(r, m)
        st["k"] = k
        st["R_forced"] = R
        if best is None or st["max_rel_err"] < best["max_rel_err"]:
            best = st
    return best


def three_scale_scan():
    rows = []
    for R in (12.0, 20.0, 50.0, 100.0):
        # near power-law clump + far atom
        edges = np.geomspace(1.0, 3.5, 9)
        r_near = np.sqrt(edges[:-1] * edges[1:])
        m_near = 1.0 / r_near  # rough
        for p in (1e-4, 1e-3, 0.01, 0.05, 0.2):
            r = np.concatenate([r_near, [R]])
            m = np.concatenate([(1 - p) * m_near / m_near.sum(), [p]])
            st = eq_stats(r, m)
            st["p_far"] = p
            st["R"] = R
            rows.append(st)
    return rows


def stretch_k6():
    """Take the q2 6-atomic min and move the outer atom, reopt masses."""
    r0 = np.array(
        [1.0, 1.2509485166627945, 1.5417709429109967, 1.8833334534910702, 2.317996232261877, 2.910379951332926]
    )
    m0 = np.array(
        [0.24895792377472611, 0.216344339384039, 0.18217225268302675, 0.14743454099397063, 0.11789791416729146, 0.087193028996946]
    )
    rows = []
    for R in (2.91, 4.0, 8.0, 12.0, 20.0, 50.0):
        r = r0.copy()
        r[-1] = R

        def fun(z):
            m = np.exp(z)
            return atomic_ID(r, m)[2]

        res = minimize(fun, np.log(m0), method="Nelder-Mead", options={"maxiter": 2000})
        m = np.exp(res.x)
        st = eq_stats(r, m)
        st["R"] = R
        rows.append(st)
    return rows


def main():
    out = {}
    out["power64_correct"] = {k: v for k, v in power64_correct().items() if k not in ("radii", "masses")}
    p64 = power64_correct()
    out["power64_Q"] = p64["Q"]
    out["power64_cap"] = p64["Q"] / (1.0 - p64["Q"])

    crit = []
    for k in (2, 3, 4, 5, 6, 8):
        for R in (12.0, 16.0):
            st = minimize_eq_at_aspect(k, R, seed=4)
            slim = {key: st[key] for key in ("k", "R_forced", "Q", "D", "aspect", "max_rel_err", "Q_over_1mQ")}
            slim["Q_le_Qhi"] = st["Q"] <= QHI
            slim["crit_1e-3"] = st["max_rel_err"] < 1e-3
            slim["kills"] = bool(st["Q"] <= QHI and st["max_rel_err"] < 1e-3 and st["aspect"] >= 12)
            crit.append(slim)
    out["crit_forced_R"] = crit
    out["any_kill"] = any(c["kills"] for c in crit)
    out["best_crit_at_12"] = min(
        (c for c in crit if c["R_forced"] == 12.0), key=lambda c: c["max_rel_err"]
    )

    three = three_scale_scan()
    out["three_scale_min_Q"] = min(t["Q"] for t in three)
    out["three_scale_best"] = min(
        ({k: v for k, v in t.items() if k not in ("radii", "masses")} for t in three),
        key=lambda t: t["Q"],
    )
    out["three_scale_below_gamma"] = [
        {k: v for k, v in t.items() if k not in ("radii", "masses")}
        for t in three
        if t["Q"] < GAMMA12
    ]

    out["stretch_k6"] = [{k: v for k, v in t.items() if k not in ("radii", "masses")} for t in stretch_k6()]

    dest = HERE / "probe_crit_largeR.json"

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
        return o

    dest.write_text(json.dumps(_jsonable(out), indent=2) + "\n")
    print("wrote", dest)
    print("power64 Q", out["power64_Q"], "cap", out["power64_cap"])
    print("any kill", out["any_kill"])
    print("best crit at 12", out["best_crit_at_12"])
    print("three-scale min Q", out["three_scale_min_Q"])
    print("stretch k6", [(t["R"], t["Q"], t["max_rel_err"]) for t in out["stretch_k6"]])


if __name__ == "__main__":
    main()
