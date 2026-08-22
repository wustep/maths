#!/usr/bin/env python3
"""Exhaustive maximal-stratum sweeps on certified regular triangulations
obtained by perturbing the census liftings.

The uniform random generator (rzone_drive) lands on near-Delaunay
triangulations: short edges, few Harnack splits, twist-rank 6-16, and it
saturates at two M-schemes.  The high-rank part of the space sits near the
census liftings, so this walks outward from them instead: scale a census
certificate's integer MIN_WEIGHTS by K, add integer noise, and take the lower
hull.  Anything produced this way is regular *by construction*; it is then
re-certified exactly (validate_triangulation + Fraction check_convexity)
before a single sign vector is evaluated, and triangulations that coincide
with a census one are skipped.

Each accepted triangulation is swept exhaustively over
eta + span{delta_S} by zonec, so it is a complete classification of the
M-curves that triangulation supports.

usage: walk_drive.py <worker> <seed> <ntrials> <outdir> [minrank]
"""
import hashlib
import json
import os
import random
import subprocess
import sys
import tarfile
import time
from fractions import Fraction

import haas
from fastcx import Complex
from gen_fast import lower_hull_triangles
from tcurve import lattice_points, validate_triangulation, check_convexity
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span

K = 10 ** 6


def sig(tris):
    return hashlib.sha1(json.dumps(
        sorted(sorted(map(tuple, t)) for t in tris)).encode()).hexdigest()[:16]


def main():
    w, seed, ntrials, outdir = (int(sys.argv[1]), int(sys.argv[2]),
                                int(sys.argv[3]), sys.argv[4])
    minrank = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    os.makedirs(outdir, exist_ok=True)
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    known = {l.strip() for l in open("census_tri_schemes.txt") if l.strip()}
    splits = haas.all_splits()
    PTS = lattice_points(D8)
    tar = tarfile.open(ARCHIVE)
    tasks = json.load(open("span_tasks.json"))
    bases = []
    census_sigs = set()
    for d in tasks:
        t0, h0, _s, _c = parse_pcom(tar.extractfile(d["cert"]).read().decode())
        bases.append((d["cert"], {p: int(v) * K for p, v in h0.items()}))
        census_sigs.add(sig(t0))
    rng = random.Random(seed)
    res = open(f"{outdir}/k{w}.jsonl", "a")
    nov = open(f"{outdir}/k{w}_novel.jsonl", "a")
    seen, allsch = set(), set()
    t0 = time.time()
    tried = swept = 0
    for it in range(ntrials):
        cert, base = rng.choice(bases)
        amp = rng.choice([K // 100, K // 30, K // 10, K // 3, K])
        h = {p: base[p] + rng.randint(-amp, amp) for p in PTS}
        tried += 1
        tris = lower_hull_triangles(PTS, [float(h[p]) for p in PTS])
        if validate_triangulation(D8, tris):
            continue
        hf = {p: Fraction(h[p]) for p in PTS}
        if check_convexity(D8, tris, hf):
            continue
        s = sig(tris)
        if s in seen or s in census_sigs:
            continue
        seen.add(s)
        tris = [tuple(tuple(v) for v in t) for t in tris]
        cx = Complex(D8, tris)
        pts = cx.base_pts
        E = edgeset(tris)
        S = [sp for sp in splits if sp.edges <= E]
        basis = f2_basis([delta_bits(sp, pts) for sp in S])
        if len(basis) < minrank:
            continue
        task = f"/tmp/walk_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        wit = f"/tmp/walk_w{w}.jsonl"
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
        swept += 1
        allsch |= set(schemes)
        novel = sorted(x for x in schemes if x not in census)
        fresh = sorted(x for x in schemes if x not in known)
        rec = {"kind": "tri_done", "sig": s, "from": cert, "amp": amp,
               "rank": len(basis), "nsplits": len(S),
               "evals": summ["evals"], "maximal": summ["maximal"],
               "exhaustive": True, "distinct_schemes": len(schemes),
               "schemes": sorted(schemes), "novel": novel,
               "outside_census_tri_schemes": fresh}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for x in novel:
            nc, r = schemes[x]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": x, "ncomp": nc,
                "source": f"walk from {cert} amp={amp}", "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(h[p]) for p in PTS},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        if swept % 20 == 0:
            print(json.dumps({"swept": swept, "tried": tried,
                              "distinct_total": len(allsch),
                              "fresh": sorted(allsch - known),
                              "seconds": round(time.time() - t0, 1)}),
                  flush=True)
    res.write(json.dumps({"kind": "summary", "swept": swept, "tried": tried,
                          "distinct_total": len(allsch),
                          "schemes": sorted(allsch),
                          "outside_census_tri_schemes": sorted(allsch - known),
                          "seconds": round(time.time() - t0, 1)}) + "\n")
    res.close()
    nov.close()


if __name__ == "__main__":
    main()
