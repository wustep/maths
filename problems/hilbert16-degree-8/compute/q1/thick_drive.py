#!/usr/bin/env python3
"""Finish the leftover whole-stratum thicken, cheap ranks first.

Parent thick_drive.py ordered M-certificate triangulations first and
died after 4 of 164 (all rank 16).  This driver walks every census
triangulation of twist-rank <= maxrank in increasing rank, so a
partial run is a finished prefix rather than four special cases.

Covers every sign vector within Hamming distance `radius` of the
entire Haas maximal stratum eta + span{delta_S}.

usage: python3 q1/thick_drive.py <worker> <nworkers> <maxrank> <outdir> [radius] [seconds]
"""
import glob
import json
import os
import subprocess
import sys
import tarfile
import time

from common import boot, census_schemes

boot()

import haas
from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "thicken")


def main():
    w, nw, maxrank, outdir = (int(sys.argv[1]), int(sys.argv[2]),
                              int(sys.argv[3]), sys.argv[4])
    radius = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    secs = sys.argv[6] if len(sys.argv) > 6 else None
    if not os.path.isabs(outdir):
        outdir = os.path.join(HERE, outdir)
    os.makedirs(outdir, exist_ok=True)
    census = census_schemes()
    splits = haas.all_splits()
    tasks = [d for d in json.load(open("span_tasks.json"))
             if d["rank"] <= maxrank]
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
    print(f"worker {w}/{nw} radius={radius} assigned {len(mine)} "
          f"already-done {sum(1 for _, d in mine if (d['cert'], radius) in done)}",
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
        task = f"/tmp/q1_thick_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        wit = f"/tmp/q1_thick_w{w}.jsonl"
        cmd = [BIN, task, "0", "1", wit, str(radius)]
        if secs:
            cmd.append(secs)
        subprocess.run(cmd, check=True)
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
