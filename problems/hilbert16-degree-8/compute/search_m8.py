#!/usr/bin/env python3
"""Annealing search for degree-8 T-curve schemes.

Worker model: each process generates random certified convex primitive
triangulations of T_8 (gen_triang), then runs simulated-annealing
chains over sign distributions with the fast evaluator (fastcx).

Two objectives:
  * mode "m": maximize the number of components (target: 22-oval
    M-curves), recording every scheme seen along the way;
  * mode "nest": maximize components + bonus for nesting depth
    (target: the two algebraically open deep-nest M-schemes
    <4 u 1<2 u 1<14>>> and <14 u 1<2 u 1<4>>>, and generally schemes
    with a depth-3 nest).

Every distinct scheme is recorded with a witness (triangulation
heights + signs).  Witnesses are re-verified EXACTLY afterwards by
verify_found.py; nothing from this file is a claim by itself.

Usage: python3 search_m8.py <seed> <minutes> <outfile.jsonl> [mode]
"""

import json
import random
import sys
import time

from gen_triang import random_certified_triangulation
from standard import standard_triangulation, standard_heights
from fastcx import Complex
from notation import parse as parse_scheme

D = 8

NOISE = [(1, 1000), (1, 50), (1, 10), (1, 4), (1, 2), (1, 1), (2, 1)]


def depth_bonus(scheme):
    """Rough nesting score: an oval at depth k contributes min(k, 3)."""
    if scheme is None:
        return 0
    forest, _ = parse_scheme(scheme)

    def walk(forest, depth):
        b = 0
        for oval in forest:
            b += min(depth, 3)
            b += walk(oval, depth + 1)
        return b
    return walk(forest, 0)


def anneal(cx, rng, steps, mode, record):
    n = len(cx.base_pts)
    signs = [rng.choice((1, -1)) for _ in range(n)]
    ncomp, scheme = cx.eval(signs)

    def energy(ncomp, scheme):
        e = -ncomp
        if mode == "nest" and scheme is not None:
            e -= 0.25 * depth_bonus(scheme)
        return e

    e = energy(ncomp, scheme)
    record(scheme, signs)
    best = e
    t_hi, t_lo = 2.0, 0.05
    for step in range(steps):
        T = t_hi * (t_lo / t_hi) ** (step / steps)
        k = rng.randrange(n)
        signs[k] = -signs[k]
        nc2, s2 = cx.eval(signs)
        e2 = energy(nc2, s2)
        if e2 <= e or rng.random() < pow(2.718281828, (e - e2) / T):
            e, ncomp, scheme = e2, nc2, s2
            record(scheme, signs)
            if e < best:
                best = e
        else:
            signs[k] = -signs[k]
    return best


def main():
    seed = int(sys.argv[1])
    minutes = float(sys.argv[2])
    outpath = sys.argv[3]
    mode = sys.argv[4] if len(sys.argv) > 4 else "m"
    rng = random.Random(seed)
    deadline = time.time() + minutes * 60

    out = open(outpath, "w")
    seen = {}
    stats_n = {"triangulations": 0, "evals": 0}

    def flush_summary():
        out.flush()

    while time.time() < deadline:
        # triangulation: mostly random, sometimes the standard one
        if rng.random() < 0.1:
            tris = standard_triangulation(D)
            hts = standard_heights(D)
        else:
            nn, nd = NOISE[rng.randrange(len(NOISE))]
            r = random_certified_triangulation(D, rng, nn, nd)
            if r is None:
                continue
            tris, hts = r
        stats_n["triangulations"] += 1
        cx = Complex(D, tris)
        tri_ser = [[list(v) for v in t] for t in tris]
        hts_ser = {f"{p[0]},{p[1]}": str(hts[p]) for p in hts}
        tri_id = stats_n["triangulations"]
        wrote_tri = False

        def record(scheme, signs):
            nonlocal wrote_tri
            stats_n["evals"] += 1
            if scheme is None or scheme in seen:
                return
            seen[scheme] = True
            if not wrote_tri:
                out.write(json.dumps({"kind": "tri", "id": tri_id,
                                      "triangles": tri_ser,
                                      "heights": hts_ser}) + "\n")
                wrote_tri = True
            sd = {f"{p[0]},{p[1]}": s
                  for p, s in zip(cx.base_pts, signs)}
            out.write(json.dumps({"kind": "scheme", "scheme": scheme,
                                  "tri": tri_id, "signs": sd}) + "\n")
            out.flush()

        # a few chains per triangulation
        for _ in range(3):
            if time.time() > deadline:
                break
            anneal(cx, rng, 4000, mode, record)

    out.write(json.dumps({"kind": "summary", "seed": seed, "mode": mode,
                          "distinct_schemes": len(seen), **stats_n})
              + "\n")
    out.close()
    print(f"seed {seed} mode {mode}: {len(seen)} distinct schemes, "
          f"{stats_n['triangulations']} triangulations, "
          f"{stats_n['evals']} evals")


if __name__ == "__main__":
    main()
