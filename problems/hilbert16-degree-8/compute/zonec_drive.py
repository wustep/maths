#!/usr/bin/env python3
"""Drive the C sweeper over census triangulations, one worker's share.

For each triangulation: export the prepared complex + twist basis, sweep the
entire affine subspace eta + span{delta_S} in C, then decode the witnesses
back to exact scheme strings in Python and diff against the census.

A finished triangulation here is an exhaustive classification of the maximal
T-curves it supports -- every maximal sign distribution on it lies in that
subspace, so nothing is sampled.

usage: zonec_drive.py <worker> <nworkers> <minrank> <outdir>
"""
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
    w, nw, minrank, outdir = (int(sys.argv[1]), int(sys.argv[2]),
                              int(sys.argv[3]), sys.argv[4])
    os.makedirs(outdir, exist_ok=True)
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    splits = haas.all_splits()
    tasks = [d for d in json.load(open("span_tasks.json"))
             if d["rank"] >= minrank]
    # longest-processing-time first, so the three workers finish together
    tasks.sort(key=lambda d: -d["rank"])
    mine, load = [], [0] * nw
    for d in tasks:
        k = load.index(min(load))
        load[k] += 1 << d["rank"]
        if k == w:
            mine.append(d)
    tar = tarfile.open(ARCHIVE)
    res = open(f"{outdir}/w{w}.jsonl", "a")
    nov = open(f"{outdir}/w{w}_novel.jsonl", "a")
    done = set()
    if os.path.exists(f"{outdir}/w{w}.jsonl"):
        for l in open(f"{outdir}/w{w}.jsonl"):
            try:
                done.add(json.loads(l)["cert"])
            except Exception:
                pass
    for d in mine:
        cert = d["cert"]
        if cert in done:
            continue
        t0 = time.time()
        tris, hfrac, _s, _c = parse_pcom(
            tar.extractfile(cert).read().decode())
        tris = [tuple(tuple(v) for v in t) for t in tris]
        cx = Complex(D8, tris)
        pts = cx.base_pts
        E = edgeset(tris)
        S = [s for s in splits if s.edges <= E]
        basis = f2_basis([delta_bits(s, pts) for s in S])
        task = f"/tmp/zonec_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        wit = f"/tmp/zonec_w{w}.jsonl"
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
            assert nc == r["ncomp"]
            if sch not in schemes:
                schemes[sch] = (nc, r)
        novel = sorted(s for s in schemes if s not in census)
        rec = {"kind": "tri_done", "cert": cert, "rank": len(basis),
               "nsplits": len(S), "evals": summ["evals"],
               "valid": summ["valid"], "maximal": summ["maximal"],
               "exhaustive": True, "distinct_schemes": len(schemes),
               "schemes": sorted(schemes), "novel": novel,
               "seconds": round(time.time() - t0, 1)}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for s in novel:
            nc, r = schemes[s]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": s, "ncomp": nc, "cert": cert,
                "rank": len(basis), "sweep_index": r["sweep_index"],
                "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(v)
                            for p, v in hfrac.items()},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        print(json.dumps({k: rec[k] for k in
                          ("cert", "rank", "evals", "distinct_schemes",
                           "novel", "seconds")}), flush=True)
    res.close()
    nov.close()


if __name__ == "__main__":
    main()
