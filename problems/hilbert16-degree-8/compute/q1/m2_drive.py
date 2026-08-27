#!/usr/bin/env python3
"""Radius-r Hamming balls around every 20-oval census certificate.

The seventeen schemes outside the published 2,367 all sit next to an
M-curve.  The 78 twenty-one-oval certificates have no hole within
radius 6.  The next ring is the 237 twenty-oval certificates; a
radius-4 ball around each is cheap and was never run as a family.

usage: python3 q1/m2_drive.py <radius> <outdir> <worker> <nworkers>
"""
import glob
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
    seeds = sorted(n for n in tar.getnames()
                   if n.endswith(".pcom") and "/o20-" in n)
    print(f"{len(seeds)} twenty-oval certificates, worker {w}/{nw}",
          flush=True)
    res = open(f"{outdir}/m{w}.jsonl", "a")
    nov = open(f"{outdir}/m{w}_novel.jsonl", "a")
    done = set()
    for fn in sorted(glob.glob(f"{outdir}/m*.jsonl")):
        if fn.endswith("_novel.jsonl"):
            continue
        for l in open(fn):
            try:
                r = json.loads(l)
                done.add((r["seed_cert"], r["radius"]))
            except Exception:
                pass
    for i, cert in enumerate(seeds):
        if i % nw != w or (cert, radius) in done:
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
        task = f"/tmp/q1_m2_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        with open(task, "a") as fh:
            fh.write("SEEDS 1\n")
            fh.write(" ".join(str(signs[p]) for p in pts) + "\n")
        wit = f"/tmp/q1_m2_w{w}.jsonl"
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
                          ("seed_cert", "evals", "distinct_schemes",
                           "novel", "complete", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
