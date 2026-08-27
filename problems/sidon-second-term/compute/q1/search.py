#!/usr/bin/env python3
"""q1 search: re-optimize Hou–Zhao Lemma 2.1 beyond the published mix.

Phases (all exploratory; a float is not a bound):

  replay     published R=1..8 at L=4 and the L=6 plateau
  joint      L-BFGS on all eight free symmetric histograms at L=6
  continue   add kernels R=9,10,12 with 12 cosine modes at L=6
  nosym      drop kernel symmetry; independent left/right weights
  finer      resample published kernels to m=48 and re-shape
  widths     two-scale (m,L) pairs with L-BFGS, not Powell

The published record to beat is 0.9435. The folder already has an L=6
lift at ~0.9434925085; anything above that plateau is not new.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

PARENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PARENT))
from vector_smoothing import (  # noqa: E402
    check_program,
    general_kernel_from_logits,
    solve_boundary_qp,
    softmax,
    SmoothingProgram,
    symmetric_kernel_from_logits,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "search.jsonl"
CAND = HERE / "candidates"
PUBLISHED = 0.9435
L6_PLATEAU = 0.9434925085
HZ_GAMMA0 = 0.943492590713545


def dump(rec: dict) -> None:
    rec = {"t": time.time(), **rec}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec[k] for k in rec if k != "t"}), flush=True)


def load_r8():
    ns: dict = {}
    exec((PARENT / "refs" / "sidon_numerical_search.py").read_text(), ns)
    ker, lam = ns["stored_candidates"]()[8]
    return np.asarray(ker, dtype=float), np.asarray(lam, dtype=float)


def load_all():
    ns: dict = {}
    exec((PARENT / "refs" / "sidon_numerical_search.py").read_text(), ns)
    return ns["stored_candidates"]()


def evaluate(kernels, lambdas, L, asymmetric=False, tag=""):
    kernels = np.asarray(kernels, dtype=float)
    lambdas = np.asarray(lambdas, dtype=float)
    lambdas = np.maximum(lambdas, 0.0)
    lambdas = lambdas / lambdas.sum()
    wL, wR, a, b, gamma = solve_boundary_qp(
        kernels, lambdas, L, asymmetric=asymmetric
    )
    prog = SmoothingProgram(kernels.shape[1], L, lambdas, kernels, wL, wR)
    report = check_program(prog)
    rec = {
        "tag": tag,
        "R": int(kernels.shape[0]),
        "m": int(kernels.shape[1]),
        "L": int(L),
        "asymmetric": bool(asymmetric),
        "gamma": gamma,
        "a": a,
        "b": b,
        "feasible": report["feasible"],
        "min_cover_left": report["min_cover_left"],
        "min_cover_right": report["min_cover_right"],
        "beats_0.9435": bool(gamma < PUBLISHED - 1e-8),
        "beats_l6_plateau": bool(gamma < L6_PLATEAU - 1e-10),
        "beats_hz_gamma0": bool(gamma < HZ_GAMMA0 - 1e-12),
    }
    dump(rec)
    return rec, wL, wR, kernels, lambdas


def save_candidate(name: str, rec, kernels, lambdas, wL, wR) -> Path:
    CAND.mkdir(parents=True, exist_ok=True)
    path = CAND / f"{name}.json"
    path.write_text(
        json.dumps(
            {
                "tag": rec["tag"],
                "m": rec["m"],
                "L": rec["L"],
                "asymmetric": rec["asymmetric"],
                "gamma_float": rec["gamma"],
                "a_float": rec["a"],
                "b_float": rec["b"],
                "lambdas": np.asarray(lambdas).tolist(),
                "kernels": np.asarray(kernels).tolist(),
                "weights_left": np.asarray(wL).tolist(),
                "weights_right": np.asarray(wR).tolist(),
            },
            indent=2,
        )
        + "\n"
    )
    return path


def half_logits_from_kernel(p: np.ndarray) -> np.ndarray:
    half = np.clip(p[: p.size // 2], 1e-15, None)
    return np.log(half)


def kernel_from_half_logits(z: np.ndarray) -> np.ndarray:
    h = softmax(np.asarray(z, dtype=float)) * 0.5
    return np.concatenate([h, h[::-1]])


def mix_from_logits(z: np.ndarray) -> np.ndarray:
    return softmax(np.concatenate([np.asarray(z, dtype=float), [0.0]]))


def mix_logits_from_lam(lam: np.ndarray) -> np.ndarray:
    lam = np.clip(lam, 1e-15, None)
    lam = lam / lam.sum()
    return np.log(lam[:-1] / lam[-1])


def resample_kernel(p: np.ndarray, m_new: int) -> np.ndarray:
    """Piecewise-constant density on [0,1], resampled to m_new bins."""
    m = len(p)
    density = p * m
    edges_old = np.linspace(0.0, 1.0, m + 1)
    edges_new = np.linspace(0.0, 1.0, m_new + 1)
    out = np.zeros(m_new)
    i = 0
    for j in range(m_new):
        a, b = edges_new[j], edges_new[j + 1]
        mass = 0.0
        while i < m and edges_old[i + 1] <= a + 1e-15:
            i += 1
        k = i
        while k < m and edges_old[k] < b - 1e-15:
            lo = max(edges_old[k], a)
            hi = min(edges_old[k + 1], b)
            if hi > lo:
                mass += density[k] * (hi - lo)
            k += 1
        out[j] = mass
    out = 0.5 * (out + out[::-1])
    s = out.sum()
    return out / s if s > 0 else np.ones(m_new) / m_new


def lbfgs(obj, x0, maxiter: int, ftol: float = 1e-12):
    return minimize(
        obj,
        np.asarray(x0, dtype=float),
        method="L-BFGS-B",
        options={"maxiter": maxiter, "ftol": ftol, "gtol": 1e-8, "maxls": 20},
    )


def phase_replay():
    cands = load_all()
    for R in range(1, 9):
        ker, lam = cands[R]
        evaluate(ker, lam, 4, tag=f"replay-R{R}-L4")
    ker, lam = load_r8()
    for L in (5, 6, 8):
        evaluate(ker, lam, L, tag=f"replay-hz8-L{L}")
    evaluate(ker, lam, 6, asymmetric=True, tag="replay-hz8-L6-asym-weights")


def phase_joint(maxiter: int = 40):
    """Free symmetric histograms for all eight published kernels, L=6."""
    ker, lam = load_r8()
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
        _, _, _, _, g = solve_boundary_qp(ks, mix, 6)
        return g

    x0 = np.concatenate(
        [mix_logits_from_lam(lam)] + [half_logits_from_kernel(p) for p in ker]
    )
    rec0, *_ = evaluate(ker, lam, 6, tag="joint-start-hz8-L6")
    res = lbfgs(obj, x0, maxiter=maxiter)
    ks, mix = unpack(res.x)
    rec, wL, wR, ks, mix = evaluate(ks, mix, 6, tag="joint-lbfgs-hz8-L6")
    dump(
        {
            "tag": "joint-lbfgs-meta",
            "success": bool(res.success),
            "nfev": int(res.nfev),
            "nit": int(getattr(res, "nit", -1)),
            "gamma0": rec0["gamma"],
            "gamma": rec["gamma"],
            "delta": rec0["gamma"] - rec["gamma"],
        }
    )
    save_candidate("joint-lbfgs-hz8-L6", rec, ks, mix, wL, wR)
    return rec


def phase_continue(max_R: int = 12, nmodes: int = 12, maxiter: int = 25):
    """Add cosine-mode kernels on top of the published mix, at L=6."""
    ker, lam = load_r8()
    rng = np.random.default_rng(20260827)
    current_k, current_l = ker.copy(), lam.copy()
    rec, wL, wR, current_k, current_l = evaluate(
        current_k, current_l, 6, tag="cont-start-R8-L6"
    )
    best = rec["gamma"]

    for Rnew in range(9, max_R + 1):
        n_old = current_k.shape[0]

        def unpack(x):
            theta = x[:nmodes]
            mix = mix_from_logits(x[nmodes:])
            newp = symmetric_kernel_from_logits(theta, current_k.shape[1])
            return np.vstack([current_k, newp]), mix

        def obj(x):
            ks, mix = unpack(x)
            _, _, _, _, g = solve_boundary_qp(ks, mix, 6)
            return g

        best_local = None
        best_x = None
        seeds = [np.zeros(nmodes)]
        for _ in range(4):
            seeds.append(rng.normal(scale=0.35, size=nmodes))
        for i, theta0 in enumerate(seeds):
            mix0 = np.concatenate([current_l, [0.02]])
            mix0 = mix0 / mix0.sum()
            x0 = np.concatenate([theta0, mix_logits_from_lam(mix0)])
            g0 = obj(x0)
            dump({"tag": f"cont-R{Rnew}-seed{i}-start", "gamma": g0})
            res = lbfgs(obj, x0, maxiter=maxiter)
            g = obj(res.x)
            dump(
                {
                    "tag": f"cont-R{Rnew}-seed{i}",
                    "gamma": g,
                    "nfev": int(res.nfev),
                    "success": bool(res.success),
                }
            )
            if best_local is None or g < best_local:
                best_local, best_x = g, res.x

        ks, mix = unpack(best_x)
        rec, wL, wR, current_k, current_l = evaluate(
            ks, mix, 6, tag=f"cont-R{Rnew}-L6"
        )
        save_candidate(f"cont-R{Rnew}-L6", rec, current_k, current_l, wL, wR)
        if rec["gamma"] < best:
            best = rec["gamma"]
    return best


def phase_nosym(maxiter: int = 20):
    """Drop kernel symmetry at L=6, starting from the published mix."""
    ker, lam = load_r8()
    R, m = ker.shape

    def unpack(x):
        mix = mix_from_logits(x[: R - 1])
        ps = [
            general_kernel_from_logits(x[R - 1 + r * m : R - 1 + (r + 1) * m], m)
            for r in range(R)
        ]
        return np.vstack(ps), mix

    def obj(x):
        ks, mix = unpack(x)
        _, _, _, _, g = solve_boundary_qp(ks, mix, 6, asymmetric=True)
        return g

    x0 = np.concatenate(
        [mix_logits_from_lam(lam)]
        + [np.log(np.clip(p, 1e-15, None)) for p in ker]
    )
    rec0, *_ = evaluate(ker, lam, 6, asymmetric=True, tag="nosym-start")
    res = lbfgs(obj, x0, maxiter=maxiter)
    ks, mix = unpack(res.x)
    rec, wL, wR, ks, mix = evaluate(
        ks, mix, 6, asymmetric=True, tag="nosym-lbfgs-L6"
    )
    dump(
        {
            "tag": "nosym-meta",
            "success": bool(res.success),
            "nfev": int(res.nfev),
            "gamma0": rec0["gamma"],
            "gamma": rec["gamma"],
            "delta": rec0["gamma"] - rec["gamma"],
        }
    )
    save_candidate("nosym-lbfgs-L6", rec, ks, mix, wL, wR)
    return rec


def phase_finer(m_new: int = 48, maxiter: int = 25):
    """Resample published kernels to a finer grid and re-shape at L=6."""
    ker, lam = load_r8()
    ker_f = np.vstack([resample_kernel(p, m_new) for p in ker])
    rec0, *_ = evaluate(ker_f, lam, 6, tag=f"finer-resample-m{m_new}-L6")
    R, m = ker_f.shape
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
        _, _, _, _, g = solve_boundary_qp(ks, mix, 6)
        return g

    x0 = np.concatenate(
        [mix_logits_from_lam(lam)] + [half_logits_from_kernel(p) for p in ker_f]
    )
    res = lbfgs(obj, x0, maxiter=maxiter)
    ks, mix = unpack(res.x)
    rec, wL, wR, ks, mix = evaluate(ks, mix, 6, tag=f"finer-lbfgs-m{m_new}-L6")
    dump(
        {
            "tag": f"finer-m{m_new}-meta",
            "success": bool(res.success),
            "nfev": int(res.nfev),
            "gamma0": rec0["gamma"],
            "gamma": rec["gamma"],
            "delta": rec0["gamma"] - rec["gamma"],
        }
    )
    save_candidate(f"finer-lbfgs-m{m_new}-L6", rec, ks, mix, wL, wR)
    return rec


def phase_widths(maxiter: int = 20):
    """Two-width L-BFGS. Uses the parent multi-scale solver."""
    sys.path.insert(0, str(PARENT))
    from multiscale import solve_multiscale, sym_kernel  # noqa: WPS433

    rng = np.random.default_rng(27)
    pairs = [((16, 32), (6, 6)), ((24, 48), (4, 6)), ((32, 64), (6, 4))]
    best = None
    for (m1, m2), (L1, L2) in pairs:

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

        x0 = rng.normal(scale=0.2, size=17)
        res = lbfgs(obj, x0, maxiter=maxiter)
        lam, kers, Ls = unpack(res.x)
        sol = solve_multiscale(lam, kers, Ls)
        rec = {
            "tag": f"widths-m{m1}-{m2}-L{L1}-{L2}",
            "kind": "multiscale",
            "ms": [m1, m2],
            "Ls": [L1, L2],
            "gamma": sol["gamma"],
            "feasible": sol["feasible"],
            "min_cover": sol["min_cover"],
            "nfev": int(res.nfev),
            "beats_0.9435": bool(sol["gamma"] < PUBLISHED - 1e-8),
            "beats_l6_plateau": bool(sol["gamma"] < L6_PLATEAU - 1e-10),
        }
        dump(rec)
        if best is None or rec["gamma"] < best["gamma"]:
            best = rec
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--phase",
        choices=["replay", "joint", "continue", "nosym", "finer", "widths", "all"],
        default="all",
    )
    ap.add_argument("--maxiter-joint", type=int, default=40)
    ap.add_argument("--maxiter-cont", type=int, default=25)
    ap.add_argument("--max-R", type=int, default=12)
    args = ap.parse_args()

    t0 = time.time()
    dump({"tag": "q1-start", "phase": args.phase})
    if args.phase in ("replay", "all"):
        phase_replay()
    if args.phase in ("joint", "all"):
        phase_joint(maxiter=args.maxiter_joint)
    if args.phase in ("continue", "all"):
        phase_continue(max_R=args.max_R, maxiter=args.maxiter_cont)
    if args.phase in ("nosym", "all"):
        phase_nosym()
    if args.phase in ("finer", "all"):
        phase_finer(48)
    if args.phase in ("widths", "all"):
        phase_widths()
    dump({"tag": "q1-done", "phase": args.phase, "seconds": time.time() - t0})


if __name__ == "__main__":
    main()
