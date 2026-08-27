#!/usr/bin/env python3
"""q2 search: grow free histograms from the q1 mix, not a joint refine.

q1 leftover refine / dropped-symmetry never logged a finished evaluation.
This file does not continue those two phases. Route:

  leftover   confirm q1 search.jsonl is incomplete (not a bound)
  lift       re-solve the q1 kernels at L=7,8,10 (L is free in Lemma 2.1)
  blocks     coordinate descent, one mix or one histogram at a time
  grow       add free-histogram kernels to the q1 mix (not 12-mode cosine
             on the published mix)
  resample   piecewise-constant resample of the current best to m=48,
             then another block cycle

A floating γ is not a bound. The published record to beat is 0.9435.
The folder record to beat is the q1 exact √(ab) = 0.9432425309706136.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

PARENT = Path(__file__).resolve().parents[1]
Q1 = PARENT / "q1"
sys.path.insert(0, str(PARENT))
from vector_smoothing import solve_boundary_qp, softmax  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "search.jsonl"
CAND = HERE / "candidates"
Q1_CERT_GAMMA = 0.9432425309706136
Q1_FLOAT = 0.9432425303235829
PUBLISHED = 0.9435


def dump(rec: dict) -> None:
    rec = {"t": time.time(), **rec}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    printable = {k: rec[k] for k in rec if k != "t"}
    print(json.dumps(printable), flush=True)


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


def lbfgs(obj, x0, maxiter: int, ftol: float = 1e-14):
    return minimize(
        obj,
        np.asarray(x0, dtype=float),
        method="L-BFGS-B",
        options={"maxiter": maxiter, "ftol": ftol, "gtol": 1e-10, "maxls": 20},
    )


def resample_kernel(p: np.ndarray, m_new: int) -> np.ndarray:
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


def load_q1_candidate():
    path = Q1 / "candidates" / "joint-lbfgs-hz8-L6.json"
    cand = json.loads(path.read_text())
    ker = np.array(cand["kernels"], dtype=float)
    lam = np.array(cand["lambdas"], dtype=float)
    L = int(cand["L"])
    return ker, lam, L, cand


def evaluate(kernels, lambdas, L, tag=""):
    kernels = np.asarray(kernels, dtype=float)
    lambdas = np.asarray(lambdas, dtype=float)
    lambdas = np.maximum(lambdas, 0.0)
    lambdas = lambdas / lambdas.sum()
    wL, wR, a, b, gamma = solve_boundary_qp(kernels, lambdas, L)
    rec = {
        "tag": tag,
        "R": int(kernels.shape[0]),
        "m": int(kernels.shape[1]),
        "L": int(L),
        "gamma": gamma,
        "a": a,
        "b": b,
        "beats_0.9435": bool(gamma < PUBLISHED - 1e-8),
        "beats_q1_float": bool(gamma < Q1_FLOAT - 1e-12),
        "beats_q1_cert": bool(gamma < Q1_CERT_GAMMA - 1e-12),
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
                "asymmetric": False,
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


def phase_leftover():
    """q1 refine / nosym never wrote a finished row. Confirm from the log."""
    log = (Q1 / "search.jsonl").read_text().splitlines()
    tags = []
    for line in log:
        rec = json.loads(line)
        tags.append(rec.get("tag"))
    needed_start = {"nosym-start", "refine-start"}
    finished = {"nosym-lbfgs-L6", "nosym-meta", "refine-lbfgs"}
    present_start = needed_start & set(tags)
    present_fin = finished & set(tags)
    rec = {
        "tag": "leftover-q1-check",
        "n_rows": len(tags),
        "starts_present": sorted(present_start),
        "finished_present": sorted(present_fin),
        "incomplete": present_start == needed_start and not present_fin,
        "has_finer": any(t and t.startswith("finer") for t in tags),
        "has_widths": any(t and str(t).startswith("widths") for t in tags),
    }
    dump(rec)
    if not rec["incomplete"]:
        raise SystemExit("FAIL expected q1 refine/nosym to be incomplete")
    if rec["has_finer"] or rec["has_widths"]:
        raise SystemExit("FAIL unexpected finished finer/widths rows in q1 log")
    return rec


def phase_lift():
    ker, lam, _, _ = load_q1_candidate()
    rec0, wL, wR, ker, lam = evaluate(ker, lam, 6, tag="lift-start-q1-L6")
    best = rec0
    best_pack = (ker, lam, wL, wR, 6)
    for L in (7, 8, 10):
        rec, wL, wR, ker, lam = evaluate(ker, lam, L, tag=f"lift-q1-L{L}")
        save_candidate(f"lift-q1-L{L}", rec, ker, lam, wL, wR)
        if rec["gamma"] < best["gamma"]:
            best = rec
            best_pack = (ker, lam, wL, wR, L)
    dump(
        {
            "tag": "lift-meta",
            "best_L": best["L"],
            "best_gamma": best["gamma"],
            "delta_vs_q1_float": Q1_FLOAT - best["gamma"],
        }
    )
    return best, best_pack


def _optimize_mix(ker, lam, L, maxiter: int, tag: str):
    R = ker.shape[0]

    def obj(x):
        mix = mix_from_logits(x)
        _, _, _, _, g = solve_boundary_qp(ker, mix, L)
        return g

    res = lbfgs(obj, mix_logits_from_lam(lam), maxiter=maxiter)
    mix = mix_from_logits(res.x)
    rec, wL, wR, ker, mix = evaluate(ker, mix, L, tag=tag)
    dump(
        {
            "tag": tag + "-meta",
            "success": bool(res.success),
            "nfev": int(res.nfev),
            "nit": int(getattr(res, "nit", -1)),
            "gamma": rec["gamma"],
        }
    )
    return rec, wL, wR, ker, mix


def _optimize_one_kernel(ker, lam, L, r: int, maxiter: int, tag: str):
    half = ker.shape[1] // 2
    ks = ker.copy()

    def obj(x):
        ks[r] = kernel_from_half_logits(x)
        _, _, _, _, g = solve_boundary_qp(ks, lam, L)
        return g

    res = lbfgs(obj, half_logits_from_kernel(ker[r]), maxiter=maxiter)
    ks[r] = kernel_from_half_logits(res.x)
    rec, wL, wR, ks, lam = evaluate(ks, lam, L, tag=tag)
    dump(
        {
            "tag": tag + "-meta",
            "r": r,
            "success": bool(res.success),
            "nfev": int(res.nfev),
            "nit": int(getattr(res, "nit", -1)),
            "gamma": rec["gamma"],
        }
    )
    return rec, wL, wR, ks, lam


def phase_blocks(
    ker, lam, L, cycles: int = 4, maxiter: int = 25, prefix: str = "blocks"
):
    rec, wL, wR, ker, lam = evaluate(ker, lam, L, tag=f"{prefix}-start")
    best = rec
    best_pack = (ker, lam, wL, wR)
    for cyc in range(cycles):
        rec, wL, wR, ker, lam = _optimize_mix(
            ker, lam, L, maxiter, tag=f"{prefix}-c{cyc}-mix"
        )
        if rec["gamma"] < best["gamma"]:
            best, best_pack = rec, (ker, lam, wL, wR)
        for r in range(ker.shape[0]):
            rec, wL, wR, ker, lam = _optimize_one_kernel(
                ker, lam, L, r, maxiter, tag=f"{prefix}-c{cyc}-k{r}"
            )
            if rec["gamma"] < best["gamma"]:
                best, best_pack = rec, (ker, lam, wL, wR)
    save_candidate(f"{prefix}-best", best, *best_pack[:4])
    dump(
        {
            "tag": f"{prefix}-meta",
            "cycles": cycles,
            "best_gamma": best["gamma"],
            "delta_vs_q1_float": Q1_FLOAT - best["gamma"],
        }
    )
    return best, best_pack


def phase_grow(ker, lam, L, max_R: int = 11, seeds: int = 5, maxiter: int = 30):
    rec, wL, wR, ker, lam = evaluate(ker, lam, L, tag="grow-start")
    best = rec
    best_pack = (ker, lam, wL, wR)
    rng = np.random.default_rng(20260827)
    half = ker.shape[1] // 2

    while ker.shape[0] < max_R:
        R = ker.shape[0]
        local_best = None
        local_x = None
        starts = [half_logits_from_kernel(ker[i % R]) for i in range(min(2, R))]
        starts.append(np.zeros(half))
        while len(starts) < seeds:
            starts.append(rng.normal(scale=0.4, size=half))

        def pack_from(x):
            newp = kernel_from_half_logits(x[:half])
            mix = mix_from_logits(x[half:])
            return np.vstack([ker, newp]), mix

        def obj(x):
            ks, mix = pack_from(x)
            _, _, _, _, g = solve_boundary_qp(ks, mix, L)
            return g

        for i, z0 in enumerate(starts):
            mix0 = np.concatenate([lam, [0.03]])
            mix0 = mix0 / mix0.sum()
            x0 = np.concatenate([z0, mix_logits_from_lam(mix0)])
            g0 = obj(x0)
            dump({"tag": f"grow-R{R + 1}-seed{i}-start", "gamma": g0})
            res = lbfgs(obj, x0, maxiter=maxiter)
            g = float(res.fun)
            dump(
                {
                    "tag": f"grow-R{R + 1}-seed{i}",
                    "gamma": g,
                    "nfev": int(res.nfev),
                    "success": bool(res.success),
                }
            )
            if local_best is None or g < local_best:
                local_best, local_x = g, res.x

        ks, mix = pack_from(local_x)
        rec, wL, wR, ker, lam = evaluate(ks, mix, L, tag=f"grow-R{R + 1}-newonly")
        # One cheap mix + new-kernel polish after the seed hunt, then one
        # pass over the old kernels so they can react to the new mass.
        rec, wL, wR, ker, lam = _optimize_mix(
            ker, lam, L, maxiter=max(10, maxiter // 2), tag=f"grow-R{R + 1}-mix"
        )
        rec, wL, wR, ker, lam = _optimize_one_kernel(
            ker, lam, L, ker.shape[0] - 1, maxiter, tag=f"grow-R{R + 1}-newk"
        )
        for r in range(ker.shape[0] - 1):
            rec, wL, wR, ker, lam = _optimize_one_kernel(
                ker, lam, L, r, maxiter=max(12, maxiter // 2), tag=f"grow-R{R + 1}-k{r}"
            )
        save_candidate(f"grow-R{ker.shape[0]}-L{L}", rec, ker, lam, wL, wR)
        if rec["gamma"] < best["gamma"]:
            best, best_pack = rec, (ker, lam, wL, wR)

    dump(
        {
            "tag": "grow-meta",
            "best_R": best["R"],
            "best_gamma": best["gamma"],
            "delta_vs_q1_float": Q1_FLOAT - best["gamma"],
        }
    )
    return best, best_pack


def phase_resample(ker, lam, L, m_new: int = 48, cycles: int = 2, maxiter: int = 20):
    ker_f = np.vstack([resample_kernel(p, m_new) for p in ker])
    rec0, wL, wR, ker_f, lam = evaluate(ker_f, lam, L, tag=f"resample-m{m_new}-start")
    save_candidate(f"resample-m{m_new}-start", rec0, ker_f, lam, wL, wR)
    best, pack = phase_blocks(
        ker_f, lam, L, cycles=cycles, maxiter=maxiter, prefix=f"resample-m{m_new}"
    )
    save_candidate(f"resample-m{m_new}-blocks", best, *pack[:4])
    dump(
        {
            "tag": "resample-meta",
            "m": m_new,
            "best_gamma": best["gamma"],
            "delta_vs_q1_float": Q1_FLOAT - best["gamma"],
        }
    )
    return best, pack


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--phase",
        choices=["leftover", "lift", "blocks", "grow", "resample", "all"],
        default="all",
    )
    ap.add_argument("--cycles", type=int, default=4)
    ap.add_argument("--maxiter", type=int, default=25)
    ap.add_argument("--max-R", type=int, default=11)
    ap.add_argument("--seeds", type=int, default=5)
    args = ap.parse_args()

    t0 = time.time()
    dump({"tag": "q2-start", "phase": args.phase})
    ker, lam, L, _ = load_q1_candidate()
    best = None
    pack = (ker, lam, None, None)

    if args.phase in ("leftover", "all"):
        phase_leftover()
    if args.phase in ("lift", "all"):
        rec, packL = phase_lift()
        # Keep the original L=6 kernels as the working mix. An L-lift of a
        # fixed shape is recorded; later phases reshape at L=6.
        if best is None or rec["gamma"] < best["gamma"]:
            best = rec
    if args.phase in ("blocks", "all"):
        rec, pack = phase_blocks(ker, lam, L, cycles=args.cycles, maxiter=args.maxiter)
        ker, lam = pack[0], pack[1]
        if best is None or rec["gamma"] < best["gamma"]:
            best = rec
    if args.phase in ("grow", "all"):
        rec, pack = phase_grow(
            ker, lam, L, max_R=args.max_R, seeds=args.seeds, maxiter=args.maxiter
        )
        ker, lam = pack[0], pack[1]
        if best is None or rec["gamma"] < best["gamma"]:
            best = rec
    if args.phase in ("resample", "all"):
        rec, pack = phase_resample(ker, lam, L)
        if best is None or rec["gamma"] < best["gamma"]:
            best = rec
    dump(
        {
            "tag": "q2-done",
            "phase": args.phase,
            "seconds": time.time() - t0,
            "best_gamma": None if best is None else best["gamma"],
            "best_tag": None if best is None else best["tag"],
        }
    )


if __name__ == "__main__":
    main()
