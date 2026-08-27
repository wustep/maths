#!/usr/bin/env python3
"""Perturb every published 22-oval lifting, then zonec-sweep new tris.

nest_walk.py only shook the five (19,3) certificates.  A nearby regular
triangulation of any of the 38 might still carry a new non-maximal
scheme (the M-question on a census triangulation is already closed).

usage: python3 q1/nest_broad.py <worker> <seed> <ntrials> <outdir>
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

from common import boot, census_schemes, resolve_out

boot()

import haas
from fastcx import Complex
from gen_fast import lower_hull_triangles
from tcurve import lattice_points, validate_triangulation, check_convexity
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span

K = 10 ** 6
OPEN = {"<4 u 1<2 u 1<14>>>", "<14 u 1<2 u 1<4>>>"}


def sig(tris):
    return hashlib.sha1(json.dumps(
        sorted(sorted(map(tuple, t)) for t in tris)).encode()).hexdigest()[:16]


def main():
    w, seed, ntrials, outdir = (int(sys.argv[1]), int(sys.argv[2]),
                                int(sys.argv[3]), sys.argv[4])
    minrank = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    outdir = resolve_out(outdir)
    os.makedirs(outdir, exist_ok=True)
    census = census_schemes()
    splits = haas.all_splits()
    PTS = lattice_points(D8)
    tar = tarfile.open(ARCHIVE)
    names = sorted(n for n in tar.getnames()
                   if n.startswith("deg8/o22-") and n.endswith(".pcom"))
    bases, census_sigs = [], set()
    for name in names:
        t0, h0, _s, _c = parse_pcom(tar.extractfile(name).read().decode())
        bases.append((name, {p: int(v) * K for p, v in h0.items()}))
        census_sigs.add(sig(t0))
    rng = random.Random(seed + 31 * w)
    res = open(f"{outdir}/b{w}.jsonl", "a")
    nov = open(f"{outdir}/b{w}_novel.jsonl", "a")
    seen = set()
    t0 = time.time()
    tried = swept = 0
    for it in range(ntrials):
        cert, base = rng.choice(bases)
        amp = rng.choice([K // 80, K // 30, K // 10, K // 4, K])
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
        task = f"/tmp/q1_nbroad_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        wit = f"/tmp/q1_nbroad_w{w}.jsonl"
        subprocess.run(["./zonec", task, "0", "1", wit], check=True)
        schemes, summ = {}, None
        for line in open(wit):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("kind") == "summary":
                summ = r
                continue
            if "signs" not in r:
                continue
            nc, sch = cx.eval(r["signs"])
            if sch is None:
                continue
            schemes.setdefault(sch, (nc, r))
        swept += 1
        novel = sorted(x for x in schemes if x not in census)
        hits = sorted(x for x in schemes if x in OPEN)
        rec = {"kind": "tri_done", "src": cert, "sig": s,
               "rank": len(basis), "nsplits": len(S),
               "evals": summ["evals"] if summ else 0,
               "complete": True if summ else False,
               "schemes": sorted(schemes), "novel": novel, "hits": hits,
               "seconds": round(time.time() - t0, 1)}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for x in novel:
            nc, r = schemes[x]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": x, "ncomp": nc,
                "source": f"zonec sweep of a perturbation of {cert}",
                "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(h[p]) for p in PTS},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        print(json.dumps({"tried": tried, "swept": swept, "rank": len(basis),
                          "n_schemes": len(schemes), "novel": novel,
                          "hits": hits}), flush=True)
    print(json.dumps({"worker": w, "tried": tried, "accepted": len(seen),
                      "swept": swept, "seconds": round(time.time() - t0, 1)}),
          flush=True)


if __name__ == "__main__":
    main()
