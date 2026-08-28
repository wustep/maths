#!/usr/bin/env python3
"""Radius-1 thicken of leftover census triangulations of ranks 22–26.

q1 finished ranks ≤ 20 (164/164). q2 finished rank 21 (5/5). The leftover
named in the q2 wrap is the fifteen census triangulations of ranks 22–26
and the two open (19,3) nests. The only leftover (19,3) certificate is
the rank-23 Harnack triangulation ``deg8/o22-p19-n03/(18v1(3)).pcom``.

usage:
  python3 q3/thick_drive.py <w> <nw> <minrank> <maxrank> <outdir> [radius] [seconds]
  python3 q3/thick_drive.py ... --only <cert>
  python3 q3/thick_drive.py ... --prefer-193
"""
import argparse
import glob
import json
import os
import subprocess
import tarfile
import time

from common import HERE, QNAME, boot, census_schemes, resolve_out

boot()

import haas
from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE
from zone_search import D8, edgeset, delta_bits, f2_basis
import export_span

BIN = os.path.join(HERE, "thicken")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("worker", type=int)
    p.add_argument("nworkers", type=int)
    p.add_argument("minrank", type=int)
    p.add_argument("maxrank", type=int)
    p.add_argument("outdir")
    p.add_argument("radius", nargs="?", type=int, default=1)
    p.add_argument("seconds", nargs="?", default=None)
    p.add_argument("--only", action="append", default=[])
    p.add_argument("--prefer-193", action="store_true")
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--nshards", type=int, default=1)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    w, nw = args.worker, args.nworkers
    radius = args.radius
    outdir = resolve_out(args.outdir)
    os.makedirs(outdir, exist_ok=True)
    census = census_schemes()
    splits = haas.all_splits()
    tasks = [d for d in json.load(open("span_tasks.json"))
             if args.minrank <= d["rank"] <= args.maxrank]
    if args.only:
        want = set(args.only)
        tasks = [d for d in tasks if d["cert"] in want]
    if args.prefer_193:
        tasks.sort(key=lambda d: (0 if "p19-n03" in d["cert"] else 1,
                                  d["rank"], d["cert"]))
    else:
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
    if args.only:
        mine = list(enumerate(tasks))
    else:
        mine = [(i, d) for i, d in enumerate(tasks) if i % nw == w]
    print(f"worker {w}/{nw} ranks {args.minrank}-{args.maxrank} "
          f"radius={radius} assigned {len(mine)} already-done "
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
        tag = f"w{w}" if args.nshards == 1 else f"w{w}_s{args.shard}"
        task = f"/tmp/{QNAME}_thick_r{radius}_{tag}.task"
        export_span.emit(cx, pts, basis, task)
        wit = f"/tmp/{QNAME}_thick_r{radius}_{tag}.jsonl"
        cmd = [BIN, task, str(args.shard), str(args.nshards), wit, str(radius)]
        if args.seconds:
            cmd.append(str(args.seconds))
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
                   "shard": args.shard, "nshards": args.nshards,
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
               "seconds": round(time.time() - t0, 1),
               "shard": args.shard, "nshards": args.nshards}
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
