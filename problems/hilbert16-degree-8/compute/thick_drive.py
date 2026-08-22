#!/usr/bin/env python3
"""Drive thickc over census triangulations, M-certificate ones first.

Covers every sign vector within Hamming distance 1 of the WHOLE maximal
stratum of a triangulation, rather than of the single representative the
paper published.  Triangulations are taken in order: those carrying a
22-oval certificate first, then the rest by increasing twist rank, since
cost is 46 * 2^rank.

usage: thick_drive.py <worker> <nworkers> <maxrank> <outdir> [seconds-per-tri]
"""
import glob
import json
import os
import subprocess
import sys
import tarfile
import time

import haas
from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span


def main():
    w, nw, maxrank, outdir = (int(sys.argv[1]), int(sys.argv[2]),
                              int(sys.argv[3]), sys.argv[4])
    secs = sys.argv[5] if len(sys.argv) > 5 else None
    os.makedirs(outdir, exist_ok=True)
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    splits = haas.all_splits()
    tasks = [d for d in json.load(open("span_tasks.json"))
             if d["rank"] <= maxrank]
    tasks.sort(key=lambda d: (0 if "/o22-" in d["cert"] else 1, d["rank"]))
    tar = tarfile.open(ARCHIVE)
    res = open(f"{outdir}/h{w}.jsonl", "a")
    nov = open(f"{outdir}/h{w}_novel.jsonl", "a")
    done = set()
    for fn in sorted(glob.glob(f"{outdir}/h*.jsonl")):
        if fn.endswith("_novel.jsonl"):
            continue
        for l in open(fn):
            try:
                done.add(json.loads(l)["cert"])
            except Exception:
                pass
    for i, d in enumerate(tasks):
        if i % nw != w or d["cert"] in done:
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
        task = f"/tmp/thick_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        wit = f"/tmp/thick_w{w}.jsonl"
        cmd = ["./thickc", task, "0", "1", wit] + ([secs] if secs else [])
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
               "evals": summ["evals"], "complete": bool(summ["complete"]),
               "distinct_schemes": len(schemes), "novel": novel,
               "seconds": round(time.time() - t0, 1)}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for s in novel:
            nc, r = schemes[s]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": s, "ncomp": nc, "cert": d["cert"],
                "source": f"radius-1 thickening of the maximal stratum of "
                          f"{d['cert']}",
                "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(v) for p, v in hfrac.items()},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        print(json.dumps({k: rec[k] for k in
                          ("cert", "rank", "evals", "distinct_schemes",
                           "novel", "complete", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
