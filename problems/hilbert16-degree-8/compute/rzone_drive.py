#!/usr/bin/env python3
"""Exhaustive maximal-stratum sweeps on regular triangulations OUTSIDE the census.

Same product as zonec_drive, but the triangulations are drawn by
gen_fast.random_certified_triangulation: random integer heights, brute-force
lower hull, then exact Fraction certification that those heights induce the
triangulation.  So every triangulation swept here is regular -- Viro applies --
and every 22-oval witness is an honest M-curve of a degree-8 T-curve.

Because every maximal sign distribution on a fixed triangulation lies in
eta + span{delta_S}, each finished triangulation is an exhaustive
classification of the M-curves IT supports.  Across triangulations this is a
sample, not an enumeration.

usage: rzone_drive.py <worker> <seed> <ntri> <outdir> [maxrank]
"""
import json
import os
import random
import subprocess
import sys
import time

import haas
from fastcx import Complex
from gen_fast import random_certified_triangulation
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span


def main():
    w, seed, ntri, outdir = (int(sys.argv[1]), int(sys.argv[2]),
                             int(sys.argv[3]), sys.argv[4])
    maxrank = int(sys.argv[5]) if len(sys.argv) > 5 else 27
    os.makedirs(outdir, exist_ok=True)
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    known = set()
    if os.path.exists("census_tri_schemes.txt"):
        known = {l.strip() for l in open("census_tri_schemes.txt") if l.strip()}
    splits = haas.all_splits()
    rng = random.Random(seed)
    res = open(f"{outdir}/r{w}.jsonl", "a")
    nov = open(f"{outdir}/r{w}_novel.jsonl", "a")
    seen_tri, allsch = set(), set()
    t0 = time.time()
    ntried = nswept = 0
    for i in range(ntri):
        got = random_certified_triangulation(
            D8, rng, noise_num=rng.choice([1, 1, 2, 3, 5, 8, 13]),
            noise_den=rng.choice([50, 20, 10, 5, 3]))
        ntried += 1
        if got is None:
            continue
        tris, hfrac = got
        tris = [tuple(tuple(v) for v in t) for t in tris]
        sig = tuple(sorted(tuple(sorted(t)) for t in tris))
        if sig in seen_tri:
            continue
        seen_tri.add(sig)
        cx = Complex(D8, tris)
        pts = cx.base_pts
        E = edgeset(tris)
        S = [s for s in splits if s.edges <= E]
        basis = f2_basis([delta_bits(s, pts) for s in S])
        if len(basis) > maxrank:
            continue
        task = f"/tmp/rzone_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        wit = f"/tmp/rzone_w{w}.jsonl"
        subprocess.run(["./zonec", task, "0", "1", wit], check=True)
        schemes, summ = {}, None
        for line in open(wit):
            r = json.loads(line)
            if r["kind"] == "summary":
                summ = r
                continue
            nc, sch = cx.eval(r["signs"])
            if sch is None:
                continue
            schemes.setdefault(sch, (nc, r))
        nswept += 1
        allsch |= set(schemes)
        novel = sorted(s for s in schemes if s not in census)
        fresh = sorted(s for s in schemes if s not in known)
        rec = {"kind": "tri_done", "src": f"rand-{seed}-{i}",
               "rank": len(basis), "nsplits": len(S),
               "evals": summ["evals"], "maximal": summ["maximal"],
               "exhaustive": True, "distinct_schemes": len(schemes),
               "schemes": sorted(schemes), "novel": novel,
               "outside_census_tri_sweeps": fresh}
        res.write(json.dumps(rec) + "\n")
        for s in novel:
            nc, r = schemes[s]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": s, "ncomp": nc,
                "src": f"rand-{seed}-{i}", "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(v)
                            for p, v in hfrac.items()},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        if nswept % 25 == 0:
            res.flush()
            print(json.dumps({"swept": nswept, "tried": ntried,
                              "distinct_total": len(allsch),
                              "seconds": round(time.time() - t0, 1)}),
                  flush=True)
    res.write(json.dumps({"kind": "summary", "swept": nswept,
                          "tried": ntried, "distinct_total": len(allsch),
                          "schemes": sorted(allsch),
                          "seconds": round(time.time() - t0, 1)}) + "\n")
    res.close()
    nov.close()


if __name__ == "__main__":
    main()
