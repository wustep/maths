#!/usr/bin/env python3
"""Radius-1 thicken of the leftover high-rank census triangulations.

q1 finished every census triangulation of twist-rank at most 20
(164/164).  This driver walks ranks ``minrank`` through ``maxrank``
in increasing rank.  The leftover named in the q1 wrap is ranks 21–26
(20 triangulations).

usage: python3 q2/thick_drive.py <worker> <nworkers> <minrank> <maxrank> <outdir> [radius] [seconds]
"""
import glob
import json
import os
import subprocess
import sys
import tarfile
import time

from common import boot, census_schemes, resolve_out

boot()

import haas
from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "thicken")


def main():
    w, nw, minrank, maxrank, outdir = (
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
        int(sys.argv[4]), sys.argv[5])
    radius = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    secs = sys.argv[7] if len(sys.argv) > 7 else None
    outdir = resolve_out(outdir)
    os.makedirs(outdir, exist_ok=True)
    census = census_schemes()
    splits = haas.all_splits()
    tasks = [d for d in json.load(open("span_tasks.json"))
             if minrank <= d["rank"] <= maxrank]
    tasks.sort(key=lambda d: (d["rank"], d["cert"]))
    tar = tarfile.open(ARCHIVE)
    res = open(f"{outdir}/h{w}.jsonl", "a")
    nov = open(f"{outdir}/h{w}_novel.jsonl", "a")
    done = set()
    for fn in sorted(glob.glob(f"{outdir}/h*.jsonl")):
        if fn.endswith("_novel.jsonl"):
            continue
        for l in open(fn):
            try:
                r = json.loads(l)
                if r.get("kind") == "tri_done" and r.get("complete"):
                    done.add((r["cert"], r.get("radius", 1)))
            except Exception:
                pass
    mine = [(i, d) for i, d in enumerate(tasks) if i % nw == w]
    print(f"worker {w}/{nw} ranks {minrank}-{maxrank} radius={radius} "
          f"assigned {len(mine)} already-done "
          f"{sum(1 for _, d in mine if (d['cert'], radius) in done)}",
          flush=True)
    for i, d in mine:
        if (d["cert"], radius) in done:
            continue
        t0 = time.time()
        tris, hfrac, _s, _c = parse_pcom(
            tar.extractfile(d["cert"]).read().decode())
        tris = [tuple(tuple(v) for v in t) for t in tris]
        cx = Complex(D8, tris)
        pts = cx.base_pts
        E = edgeset(tris)
        S = [s for s in splits if s.edges <= E]
        basis = f2_basis([delta_bits(s, pts) for s in S])
        task = f"/tmp/q2_thick_r{radius}_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        wit = f"/tmp/q2_thick_r{radius}_w{w}.jsonl"
        cmd = [BIN, task, "0", "1", wit, str(radius)]
        if secs:
            cmd.append(secs)
        subprocess.run(cmd, check=True)
        schemes, summ = {}, None
        for line in open(wit):
            line = line.strip()
            if not line:
                continue
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
        if summ is None:
            rec = {"kind": "tri_done", "cert": d["cert"], "rank": len(basis),
                   "radius": radius, "evals": 0, "complete": False,
                   "distinct_schemes": 0, "novel": [],
                   "seconds": round(time.time() - t0, 1),
                   "error": "no summary in walker output"}
            res.write(json.dumps(rec) + "\n")
            res.flush()
            print(json.dumps(rec), flush=True)
            continue
        novel = sorted(s for s in schemes if s not in census)
        rec = {"kind": "tri_done", "cert": d["cert"], "rank": len(basis),
               "radius": radius, "evals": summ["evals"],
               "complete": bool(summ["complete"]),
               "distinct_schemes": len(schemes), "novel": novel,
               "seconds": round(time.time() - t0, 1)}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for s in novel:
            nc, r = schemes[s]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": s, "ncomp": nc, "cert": d["cert"],
                "source": (f"radius-{radius} thickening of the maximal "
                           f"stratum of {d['cert']}"),
                "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(v) for p, v in hfrac.items()},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        print(json.dumps({k: rec[k] for k in
                          ("cert", "rank", "radius", "evals",
                           "distinct_schemes", "novel", "complete",
                           "seconds")}), flush=True)


if __name__ == "__main__":
    main()
