#!/usr/bin/env python3
"""Targeted annealing at the two algebraically open deep-nest
M-schemes  <4 u 1<2 u 1<14>>>  and  <14 u 1<2 u 1<4>>>  ((p,n)=(19,3);
the only two of Orevkov's six that Theorem 21 of arXiv:2602.06888v3
does not exclude as T-curves).

Seeds: the five published (p,n)=(19,3) census certificates (their
triangulations were designed for deep nests; annealing starts from
their SIGNS), plus random certified triangulations.  Energy rewards
22 components and structural closeness to the target profile
(a, 2, c): a empty outer ovals, one oval containing 2 empties and one
oval with c empties.  Output format matches search_m8.py so
verify_found.py aggregates it.

Usage: python3 search_target.py <seed> <minutes> <outfile.jsonl>
"""

import json
import random
import sys
import tarfile
import time

from fractions import Fraction

from gen_triang import random_certified_triangulation
from fastcx import Complex
from notation import parse as parse_scheme
from replay_census import parse_pcom, ARCHIVE

D = 8
TARGETS = [(4, 2, 14), (14, 2, 4)]


def profile(scheme):
    """(ncomp-agnostic) structural read of a scheme: (a, b, c, junk)
    where a = empty outer ovals, b = empties in the largest outer
    nest, c = empties in its largest child, junk = everything that
    does not fit the <a u 1<b u 1<c>>> shape."""
    forest, _ = parse_scheme(scheme)
    a = sum(1 for t in forest if t == ())
    nests = [t for t in forest if t != ()]
    if not nests:
        return a, 0, 0, 0
    big = max(nests, key=lambda t: sum(1 + len(x) for x in t))
    junk = sum(sum(1 + _size(x) for x in t) for t in nests if t is not big)
    b = sum(1 for x in big if x == ())
    inner = [x for x in big if x != ()]
    if not inner:
        return a, b, 0, junk
    ibig = max(inner, key=_size)
    junk += sum(_size(x) + 1 for x in inner if x is not ibig)
    c = sum(1 for y in ibig if y == ())
    junk += sum(_size(y) + 1 for y in ibig if y != ())
    return a, b, c, junk


def _size(t):
    return sum(1 + _size(x) for x in t)


def shape_dist(scheme):
    a, b, c, junk = profile(scheme)
    return min(abs(a - ta) + abs(b - tb) + abs(c - tc)
               for (ta, tb, tc) in TARGETS) + 2 * junk


def seeds_from_census():
    tar = tarfile.open(ARCHIVE)
    out = []
    for name in sorted(tar.getnames()):
        if "/o22-p19-n03/" in name and name.endswith(".pcom"):
            raw = tar.extractfile(name).read().decode()
            tris, heights, signs, claimed = parse_pcom(raw)
            out.append((name.split("/")[-1], tris, heights, signs))
    return out


def main():
    seed = int(sys.argv[1])
    minutes = float(sys.argv[2])
    outpath = sys.argv[3]
    rng = random.Random(seed)
    deadline = time.time() + minutes * 60
    seeds = seeds_from_census()

    out = open(outpath, "w")
    seen = {}
    nstats = {"triangulations": 0, "evals": 0, "best_dist": 99}

    while time.time() < deadline:
        use_seed = rng.random() < 0.7
        if use_seed:
            name, tris, hts, s0 = seeds[rng.randrange(len(seeds))]
        else:
            r = random_certified_triangulation(
                D, rng, 1, rng.choice([50, 10, 4, 2]))
            if r is None:
                continue
            tris, hts = r
            s0 = None
        nstats["triangulations"] += 1
        cx = Complex(D, tris)
        tri_ser = [[list(v) for v in t] for t in tris]
        hts_ser = {f"{p[0]},{p[1]}": str(hts[p]) for p in hts}
        tri_id = nstats["triangulations"]
        wrote_tri = False

        def record(scheme, signs):
            nonlocal wrote_tri
            if scheme is None or scheme in seen:
                return
            seen[scheme] = True
            if not wrote_tri:
                out.write(json.dumps({"kind": "tri", "id": tri_id,
                                      "triangles": tri_ser,
                                      "heights": hts_ser}) + "\n")
                wrote_tri = True
            sd = {f"{p[0]},{p[1]}": s for p, s in zip(cx.base_pts, signs)}
            out.write(json.dumps({"kind": "scheme", "scheme": scheme,
                                  "tri": tri_id, "signs": sd}) + "\n")
            out.flush()

        if s0 is not None:
            signs = [s0[p] for p in cx.base_pts]
            # kick a few signs so chains explore
            for _ in range(rng.randrange(0, 4)):
                signs[rng.randrange(len(signs))] *= -1
        else:
            signs = [rng.choice((1, -1)) for _ in range(len(cx.base_pts))]

        ncomp, scheme = cx.eval(signs)

        def energy(nc, s):
            e = 3.0 * (22 - nc)
            if s is not None:
                d = shape_dist(s)
                e += d
                if nc == 22 and d < nstats["best_dist"]:
                    nstats["best_dist"] = d
            return e

        e = energy(ncomp, scheme)
        record(scheme, signs)
        steps = 4000
        t_hi, t_lo = 1.5, 0.05
        for step in range(steps):
            if step % 512 == 0 and time.time() > deadline:
                break
            T = t_hi * (t_lo / t_hi) ** (step / steps)
            k = rng.randrange(len(signs))
            signs[k] = -signs[k]
            nc2, s2 = cx.eval(signs)
            e2 = energy(nc2, s2)
            nstats["evals"] += 1
            if e2 <= e or rng.random() < pow(2.718281828, (e - e2) / T):
                e, ncomp, scheme = e2, nc2, s2
                record(scheme, signs)
            else:
                signs[k] = -signs[k]

    out.write(json.dumps({"kind": "summary", "seed": seed,
                          "mode": "target",
                          "distinct_schemes": len(seen), **nstats}) + "\n")
    out.close()
    print(f"target seed {seed}: {len(seen)} distinct schemes, "
          f"best 22-oval shape distance {nstats['best_dist']}, "
          f"{nstats['evals']} evals")


if __name__ == "__main__":
    main()
