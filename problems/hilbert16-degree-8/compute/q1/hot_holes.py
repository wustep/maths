#!/usr/bin/env python3
"""Hamming balls aimed at the four hole-map targets with both
b-neighbours already realised.

    <5 u 1<6> u 1<9>>     22 ovals, T-undecided M-scheme (Orevkov 89)
    <4 u 1<6> u 1<9>>     21 ovals
    <1<2> u 1<16>>        20 ovals
    <3 u 1<3> u 1<12>>    20 ovals

The M-scheme cannot live on a census triangulation (those 184 were
classified exhaustively).  The three non-maximal holes might still sit
a short Hamming distance from a neighbouring census certificate that
was never taken past radius 6.

usage: python3 q1/hot_holes.py <radius> <outdir> <worker> <nworkers>
"""
import json
import os
import subprocess
import sys
import tarfile
import time

from common import HERE, boot, known_schemes, resolve_out

boot()

import haas
from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span

# neighbouring published certificates for each hole
SEEDS = [
    "deg8/o22-p07-n15/(5v1(5)v1(10)).pcom",   # neighbour of <5 u 1<6> u 1<9>>
    "deg8/o22-p07-n15/(5v1(7)v1(8)).pcom",
    "deg8/o21-p06-n15/(4v1(5)v1(10)).pcom",   # may not exist; filtered
    "deg8/o21-p12-n09/(4v1(7)v1(8)).pcom",
    "deg8/o20-p03-n17/(1(1)v1(16)).pcom",
    "deg8/o20-p03-n17/(1(3)v1(15)).pcom",
    "deg8/o20-p11-n09/(3v1(2)v1(13)).pcom",
    "deg8/o20-p11-n09/(3v1(4)v1(11)).pcom",
]


def main():
    radius, outdir = int(sys.argv[1]), sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    nw = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    outdir = resolve_out(outdir)
    os.makedirs(outdir, exist_ok=True)
    known = known_schemes()
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    splits = haas.all_splits()
    tar = tarfile.open(ARCHIVE)
    names = set(tar.getnames())
    seeds = [s for s in SEEDS if s in names]
    print(f"{len(seeds)} of {len(SEEDS)} seed certificates present",
          flush=True)
    res = open(f"{outdir}/t{w}.jsonl", "a")
    nov = open(f"{outdir}/t{w}_novel.jsonl", "a")
    for i, cert in enumerate(seeds):
        if i % nw != w:
            continue
        t0 = time.time()
        tris, hfrac, signs, claimed = parse_pcom(
            tar.extractfile(cert).read().decode())
        tris = [tuple(tuple(v) for v in t) for t in tris]
        cx = Complex(D8, tris)
        pts = cx.base_pts
        E = edgeset(tris)
        S = [s for s in splits if s.edges <= E]
        basis = f2_basis([delta_bits(s, pts) for s in S])
        task = f"/tmp/q1_hot_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        with open(task, "a") as fh:
            fh.write("SEEDS 1\n")
            fh.write(" ".join(str(signs[p]) for p in pts) + "\n")
        wit = f"/tmp/q1_hot_w{w}.jsonl"
        subprocess.run(["./ballc", task, str(radius), wit], check=True)
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
        novel = sorted(x for x in schemes if x not in known)
        rec = {"kind": "seed_done", "seed_cert": cert, "claimed": claimed,
               "radius": radius, "evals": summ["evals"] if summ else 0,
               "complete": bool(summ["complete"]) if summ else False,
               "distinct_schemes": len(schemes),
               "outside_census": sorted(x for x in schemes if x not in census),
               "novel": novel, "seconds": round(time.time() - t0, 1)}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for x in novel:
            nc, r = schemes[x]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": x, "ncomp": nc,
                "source": f"radius-{radius} ball around {cert}",
                "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(v) for p, v in hfrac.items()},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        print(json.dumps({k: rec[k] for k in
                          ("seed_cert", "radius", "evals",
                           "distinct_schemes", "novel", "complete",
                           "seconds")}), flush=True)


if __name__ == "__main__":
    main()
