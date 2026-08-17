#!/usr/bin/env python3
"""Search the Hou–Zhao vector-smoothing program for a constant below 0.9435.

This is exploratory. A floating-point gamma is not a bound. Any claimed
improvement must go through rationalize_certificate.py and both verifiers.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vector_smoothing import (  # noqa: E402
    SmoothingProgram,
    check_program,
    gamma_of,
    general_kernel_from_logits,
    solve_boundary_qp,
    softmax,
    symmetric_kernel_from_logits,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "search_results.jsonl"
PUBLISHED = 0.9435
CHO = 0.98183


def dump(rec: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)


def evaluate(kernels, lambdas, L, asymmetric=False, tag=""):
    kernels = np.asarray(kernels, dtype=float)
    lambdas = np.asarray(lambdas, dtype=float)
    lambdas = np.maximum(lambdas, 0)
    lambdas = lambdas / lambdas.sum()
    wL, wR, a, b, gamma = solve_boundary_qp(kernels, lambdas, L, asymmetric=asymmetric)
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
        "beats_cho": bool(gamma < CHO),
        "beats_published": bool(gamma < PUBLISHED - 1e-8),
    }
    dump(rec)
    return rec, wL, wR, kernels, lambdas


def optimize_symmetric_one(m: int, L: int, nmodes: int = 12, restarts: int = 4):
    """1-kernel symmetric search via cosine-mode softmax."""
    best = None
    rng = np.random.default_rng(20260817 + 1000 * m + L)

    def obj(theta):
        p = symmetric_kernel_from_logits(theta, m)
        _, _, _, _, g = solve_boundary_qp(p[None, :], np.array([1.0]), L)
        return g

    seeds = [np.zeros(nmodes)]
    # peaked-in-the-middle seed (similar to Hou–Zhao R=1 shape)
    seeds.append(np.array([0.4, -0.3, 0.15, -0.08, 0.04, -0.02] + [0.0] * (nmodes - 6))[:nmodes])
    for _ in range(restarts):
        seeds.append(rng.normal(scale=0.35, size=nmodes))

    for i, x0 in enumerate(seeds):
        res = minimize(obj, x0, method="Powell", options={"maxiter": 80, "xtol": 3e-5, "ftol": 1e-10})
        rec, wL, wR, ker, lam = evaluate(
            symmetric_kernel_from_logits(res.x, m)[None, :],
            np.array([1.0]),
            L,
            tag=f"sym1-m{m}-L{L}-seed{i}",
        )
        if best is None or rec["gamma"] < best["gamma"]:
            best = {**rec, "theta": res.x.tolist(), "kernel": ker[0].tolist(), "wL": wL[0].tolist()}
    return best


def optimize_asymmetric_one(m: int, L: int, nmodes: int = 10):
    """1-kernel, drop symmetry, independent left/right weights."""

    def obj(z):
        p = general_kernel_from_logits(z, m)
        _, _, _, _, g = solve_boundary_qp(p[None, :], np.array([1.0]), L, asymmetric=True)
        return g

    # start from a symmetrized good shape
    x0 = np.log(np.clip(np.linspace(0.3, 1.7, m) * np.linspace(1.7, 0.3, m), 1e-6, None))
    res = minimize(obj, x0, method="Powell", options={"maxiter": 60, "xtol": 5e-5, "ftol": 1e-10})
    rec, wL, wR, ker, lam = evaluate(
        general_kernel_from_logits(res.x, m)[None, :],
        np.array([1.0]),
        L,
        asymmetric=True,
        tag=f"asym1-m{m}-L{L}",
    )
    return rec


def optimize_two(m: int, L: int, nmodes: int = 10):
    """Free symmetric histogram + uniform kernel."""

    def unpack(x):
        theta = x[:-1]
        t = 1.0 / (1.0 + math.exp(-x[-1]))
        p = symmetric_kernel_from_logits(theta, m)
        u = np.ones(m) / m
        return np.vstack([p, u]), np.array([t, 1.0 - t])

    def obj(x):
        ker, lam = unpack(x)
        _, _, _, _, g = solve_boundary_qp(ker, lam, L)
        return g

    x0 = np.zeros(nmodes + 1)
    x0[-1] = 0.0
    res = minimize(obj, x0, method="Powell", options={"maxiter": 80, "xtol": 3e-5, "ftol": 1e-10})
    ker, lam = unpack(res.x)
    rec, wL, wR, ker, lam = evaluate(ker, lam, L, tag=f"r2-m{m}-L{L}")
    return rec


def optimize_from_hz_plus_one(m: int = 32, L: int = 4):
    """Start at the published R=8 floating mix and try a 9th cosine kernel."""
    # Mixing weights from the paper (floats).
    lam8 = np.array(
        [39490874, 8624912, 135342, 12911860, 20451562, 2832639, 9217142, 6335669],
        dtype=float,
    )
    lam8 = lam8 / lam8.sum()
    # Rebuild the 8 kernels from the manuscript search script if present.
    search_py = ROOT / "refs" / "sidon_numerical_search.py"
    ns: dict = {}
    exec(search_py.read_text(), ns)
    cands = ns["stored_candidates"]()
    ker8, _ = cands[8]

    def obj(x):
        theta = x[:6]
        logits = x[6:]
        new_p = symmetric_kernel_from_logits(theta, m)
        mix = softmax(np.concatenate([logits, [0.0]]))
        ker = np.vstack([ker8, new_p])
        _, _, _, _, g = solve_boundary_qp(ker, mix, L)
        return g

    x0 = np.zeros(6 + 8)
    rec_base, *_ = evaluate(ker8, lam8, L, tag="hz-r8-float-replay")
    res = minimize(obj, x0, method="Powell", options={"maxiter": 40, "xtol": 1e-4, "ftol": 1e-9})
    theta = res.x[:6]
    mix = softmax(np.concatenate([res.x[6:], [0.0]]))
    ker = np.vstack([ker8, symmetric_kernel_from_logits(theta, m)])
    rec, *_ = evaluate(ker, mix, L, tag="r9-from-hz")
    return rec_base, rec


def replay_table1():
    search_py = ROOT / "refs" / "sidon_numerical_search.py"
    ns: dict = {}
    exec(search_py.read_text(), ns)
    cands = ns["stored_candidates"]()
    rows = []
    for R in range(1, 9):
        ker, lam = cands[R]
        rec, *_ = evaluate(ker, lam, 4, tag=f"table1-R{R}-replay")
        rows.append(rec)
    return rows


def save_candidate(path: Path, rec, kernels, lambdas, wL, wR):
    payload = {
        "tag": rec["tag"],
        "m": rec["m"],
        "L": rec["L"],
        "asymmetric": rec["asymmetric"],
        "gamma_float": rec["gamma"],
        "a_float": rec["a"],
        "b_float": rec["b"],
        "lambdas": lambdas.tolist(),
        "kernels": kernels.tolist(),
        "weights_left": wL.tolist(),
        "weights_right": wR.tolist(),
    }
    path.write_text(json.dumps(payload, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase",
        choices=["replay", "grid1", "asym", "r2", "r9", "all"],
        default="all",
    )
    args = parser.parse_args()

    if args.phase in ("replay", "all"):
        print("=== replay Hou–Zhao Table 1 with independent QP ===", flush=True)
        replay_table1()

    if args.phase in ("grid1", "all"):
        print("=== symmetric 1-kernel grid ===", flush=True)
        for m, L in [
            (16, 4),
            (24, 4),
            (32, 3),
            (32, 4),
            (32, 5),
            (32, 6),
            (48, 4),
            (48, 5),
            (64, 4),
            (64, 6),
        ]:
            optimize_symmetric_one(m, L)

    if args.phase in ("asym", "all"):
        print("=== asymmetric 1-kernel ===", flush=True)
        for m, L in [(32, 4), (32, 6), (48, 4), (64, 4)]:
            optimize_asymmetric_one(m, L)

    if args.phase in ("r2", "all"):
        print("=== two-kernel (free+uniform) ===", flush=True)
        for m, L in [(32, 4), (32, 6), (48, 4), (64, 4)]:
            optimize_two(m, L)

    if args.phase in ("r9", "all"):
        print("=== R=9 continuation from Hou–Zhao mix ===", flush=True)
        optimize_from_hz_plus_one()


if __name__ == "__main__":
    main()
