#!/usr/bin/env python3
"""Continue L-BFGS from a saved q1 float candidate."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import (  # noqa: E402
    CAND,
    evaluate,
    half_logits_from_kernel,
    kernel_from_half_logits,
    lbfgs,
    mix_from_logits,
    mix_logits_from_lam,
    save_candidate,
)

PARENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PARENT))
from vector_smoothing import solve_boundary_qp  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate", nargs="?", default=str(CAND / "joint-lbfgs-hz8-L6.json"))
    ap.add_argument("--maxiter", type=int, default=80)
    ap.add_argument("--L", type=int, default=0, help="0 = keep candidate L")
    args = ap.parse_args()

    import json

    cand = json.loads(Path(args.candidate).read_text())
    ker = np.array(cand["kernels"], dtype=float)
    lam = np.array(cand["lambdas"], dtype=float)
    L = int(args.L) if args.L else int(cand["L"])
    R, m = ker.shape
    half = m // 2

    def unpack(x):
        mix = mix_from_logits(x[: R - 1])
        ps = [
            kernel_from_half_logits(x[R - 1 + r * half : R - 1 + (r + 1) * half])
            for r in range(R)
        ]
        return np.vstack(ps), mix

    def obj(x):
        ks, mix = unpack(x)
        _, _, _, _, g = solve_boundary_qp(ks, mix, L)
        return g

    x0 = np.concatenate(
        [mix_logits_from_lam(lam)] + [half_logits_from_kernel(p) for p in ker]
    )
    rec0, *_ = evaluate(ker, lam, L, tag="refine-start")
    res = lbfgs(obj, x0, maxiter=args.maxiter)
    ks, mix = unpack(res.x)
    rec, wL, wR, ks, mix = evaluate(ks, mix, L, tag="refine-lbfgs")
    print(
        "refine",
        rec0["gamma"],
        "->",
        rec["gamma"],
        "nfev",
        res.nfev,
        "success",
        res.success,
    )
    save_candidate("refine-lbfgs", rec, ks, mix, wL, wR)


if __name__ == "__main__":
    main()
