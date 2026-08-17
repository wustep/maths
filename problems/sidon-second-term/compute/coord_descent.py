#!/usr/bin/env python3
"""Coordinate descent on the published 8 kernels (equal m).

Each sweep re-optimizes one kernel's cosine modes and the mixing weights,
holding the other kernels fixed. Goal: a floating γ strictly below 0.94349259.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vector_smoothing import solve_boundary_qp, softmax, symmetric_kernel_from_logits  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_results.jsonl"


def dump(rec):
    with OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)


def load_r8():
    ns: dict = {}
    exec((ROOT / "refs" / "sidon_numerical_search.py").read_text(), ns)
    ker, lam = ns["stored_candidates"]()[8]
    return [np.asarray(p, dtype=float).copy() for p in ker], np.asarray(lam, dtype=float).copy()


def gamma_of(kers, lam, L):
    _, _, _, _, g = solve_boundary_qp(np.vstack(kers), lam, L)
    return g


def main():
    L = 6
    kers, lam = load_r8()
    m = kers[0].size
    g0 = gamma_of(kers, lam, L)
    dump({"tag": "cd-start", "L": L, "gamma": g0})
    best = g0
    rng = np.random.default_rng(21)

    for sweep in range(4):
        for r in range(len(kers)):
            others = [p for i, p in enumerate(kers) if i != r]

            def unpack(x):
                theta = x[:8]
                logits = x[8:]
                mix = softmax(logits)
                newp = symmetric_kernel_from_logits(theta, m)
                allk = others[:r] + [newp] + others[r:]
                return allk, mix

            def obj(x):
                ks, mix = unpack(x)
                return gamma_of(ks, mix, L)

            x0 = np.zeros(8 + len(kers))
            x0[8:] = np.log(np.clip(lam, 1e-12, None))
            x0[:8] += rng.normal(scale=0.05, size=8)
            res = minimize(
                obj, x0, method="Powell", options={"maxiter": 18, "xtol": 4e-4, "ftol": 1e-9}
            )
            ks, mix = unpack(res.x)
            g = gamma_of(ks, mix, L)
            dump({"tag": f"cd-sweep{sweep}-k{r}", "gamma": g, "improved": g < best - 1e-10})
            if g < best:
                best = g
                kers, lam = ks, mix
                # persist best candidate
                _, wL, a, b, _ = None, None, None, None, None
                wL, wR, a, b, g2 = solve_boundary_qp(np.vstack(kers), lam, L)
                Path(ROOT / "certs" / "best_float.json").write_text(
                    json.dumps(
                        {
                            "tag": f"cd-sweep{sweep}-k{r}",
                            "m": m,
                            "L": L,
                            "asymmetric": False,
                            "gamma_float": g2,
                            "a_float": a,
                            "b_float": b,
                            "lambdas": lam.tolist(),
                            "kernels": [p.tolist() for p in kers],
                            "weights_left": wL.tolist(),
                            "weights_right": wR.tolist(),
                        },
                        indent=2,
                    )
                )
        dump({"tag": f"cd-sweep{sweep}-end", "gamma": best})
    dump({"tag": "cd-final", "gamma": best, "beats_hz_gamma0": best < 0.94349259})


if __name__ == "__main__":
    main()
