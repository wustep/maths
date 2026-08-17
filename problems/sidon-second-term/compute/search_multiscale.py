#!/usr/bin/env python3
"""Search the multi-scale smoothing program.

Phase 1: sanity — equal-m Hou–Zhao R=8 must recover γ ≈ 0.94349259.
Phase 2: two and three widths, cosine-mode kernels + mix.
Phase 3: take the published 8 kernels as one scale and add a second scale.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multiscale import solve_multiscale, softmax, sym_kernel  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_results.jsonl"
PUBLISHED = 0.9435


def dump(rec):
    with OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)


def load_r8():
    ns: dict = {}
    exec((ROOT / "refs" / "sidon_numerical_search.py").read_text(), ns)
    ker, lam = ns["stored_candidates"]()[8]
    return [np.asarray(p, dtype=float) for p in ker], np.asarray(lam, dtype=float)


def eval_ms(lams, kers, Ls, tag):
    sol = solve_multiscale(lams, kers, Ls)
    rec = {
        "tag": tag,
        "kind": "multiscale",
        "ms": [len(p) for p in kers],
        "Ls": list(Ls),
        "R": len(kers),
        "gamma": sol["gamma"],
        "A": sol["A"],
        "B": sol["B"],
        "min_cover": sol["min_cover"],
        "feasible": sol["feasible"],
        "beats_published": bool(sol["gamma"] < PUBLISHED - 1e-8),
    }
    dump(rec)
    return rec, sol


def sanity():
    kers, lam = load_r8()
    eval_ms(lam, kers, [4] * 8, "ms-sanity-hz-r8-L4")
    eval_ms(lam, kers, [6] * 8, "ms-sanity-hz-r8-L6")


def search_two_widths():
    pairs = [(16, 32), (24, 48), (32, 64), (16, 48), (20, 40), (32, 48)]
    rng = np.random.default_rng(7)
    for m1, m2 in pairs:
        for L1, L2 in [(4, 4), (4, 6), (6, 4), (5, 5)]:

            def unpack(x):
                t1, t2 = x[:8], x[8:16]
                mix = 1.0 / (1.0 + math.exp(-x[16]))
                return (
                    np.array([mix, 1.0 - mix]),
                    [sym_kernel(t1, m1), sym_kernel(t2, m2)],
                    [L1, L2],
                )

            def obj(x):
                lam, kers, Ls = unpack(x)
                return solve_multiscale(lam, kers, Ls)["gamma"]

            best = None
            for seed in range(3):
                x0 = rng.normal(scale=0.25, size=17)
                res = minimize(
                    obj, x0, method="Powell", options={"maxiter": 40, "xtol": 2e-4, "ftol": 1e-9}
                )
                rec, _ = eval_ms(*unpack(res.x), tag=f"ms-2-m{m1}-{m2}-L{L1}-{L2}-s{seed}")
                if best is None or rec["gamma"] < best["gamma"]:
                    best = rec
            print("best pair", m1, m2, L1, L2, best["gamma"], flush=True)


def search_three_widths():
    rng = np.random.default_rng(11)
    triples = [((16, 32, 64), (4, 4, 4)), ((16, 32, 64), (4, 5, 6)), ((24, 32, 48), (4, 4, 4))]
    for ms, Ls in triples:

        def unpack(x):
            thetas = [x[8 * i : 8 * (i + 1)] for i in range(3)]
            mix = softmax(x[24:26])
            # 2 logits + implicit last
            mix = softmax(np.concatenate([x[24:26], [0.0]]))
            return mix, [sym_kernel(thetas[i], ms[i]) for i in range(3)], list(Ls)

        def obj(x):
            lam, kers, L = unpack(x)
            return solve_multiscale(lam, kers, L)["gamma"]

        x0 = rng.normal(scale=0.2, size=26)
        res = minimize(obj, x0, method="Powell", options={"maxiter": 35, "xtol": 3e-4, "ftol": 1e-9})
        eval_ms(*unpack(res.x), tag=f"ms-3-m{ms[0]}-{ms[1]}-{ms[2]}-L{Ls[0]}-{Ls[1]}-{Ls[2]}")


def hz_plus_new_scale():
    """Keep the 8 published kernels at m=32 and add one kernel at another m."""
    kers, lam8 = load_r8()
    rng = np.random.default_rng(13)
    for m_new, L_new, L_old in [(16, 4, 4), (48, 4, 4), (64, 4, 4), (16, 6, 4), (64, 6, 4)]:

        def unpack(x):
            theta = x[:8]
            logits = x[8:]  # 8 old + 1 new
            mix = softmax(logits)
            newp = sym_kernel(theta, m_new)
            return mix, kers + [newp], [L_old] * 8 + [L_new]

        def obj(x):
            lam, ks, Ls = unpack(x)
            return solve_multiscale(lam, ks, Ls)["gamma"]

        x0 = np.zeros(8 + 9)
        x0[8:16] = np.log(np.clip(lam8, 1e-12, None))
        x0[16] = np.log(0.02)
        x0[:8] = rng.normal(scale=0.2, size=8)
        res = minimize(obj, x0, method="Powell", options={"maxiter": 30, "xtol": 3e-4, "ftol": 1e-9})
        eval_ms(*unpack(res.x), tag=f"ms-hz8+m{m_new}-L{L_new}")


def main():
    print("=== sanity equal-m ===", flush=True)
    sanity()
    print("=== two widths ===", flush=True)
    search_two_widths()
    print("=== three widths ===", flush=True)
    search_three_widths()
    print("=== hz + new scale ===", flush=True)
    hz_plus_new_scale()
    print("done", flush=True)


if __name__ == "__main__":
    main()
