#!/usr/bin/env python3
"""Deep Hamming balls around the deep-nest census certificates.

The previous session's ball phase reached radius 4 around eleven key
deep-nest certificates and that is where all eight new schemes came from.
In C the same eleven seeds are cheap enough to go two radii further, which
is a strict superset of that search: radius 6 is ~9.5 million sign vectors
per seed against 164 thousand at radius 4.

usage: ball_deep.py <radius> <outdir> [worker] [nworkers] [seconds-per-group]
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
from ball_drive import build_groups, GROUPS

KEY = os.environ["BALL_KEYS"].split(",") if os.environ.get("BALL_KEYS") else [
       "(10v1(2v1(8)))", "(9v1(2v1(8)))", "(10v1(2v1(7)))",
       "(16v1(2v1(1)))", "(15v1(2v1(2)))", "(17v1(2v1(1)))",
       "(1v1(2v1(15)))", "(2v1(1v1(15)))", "(16v3(1))",
       "(17v1(1)v1(2))", "(18v1(3))"]


def main():
    radius, outdir = int(sys.argv[1]), sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    nw = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    secs = sys.argv[5] if len(sys.argv) > 5 else None
    os.makedirs(outdir, exist_ok=True)
    groups = (json.load(open(GROUPS)) if os.path.exists(GROUPS)
              else build_groups())
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    splits = haas.all_splits()
    tar = tarfile.open(ARCHIVE)
    want = {}
    for k, g in groups.items():
        for n in g["certs"]:
            if n.split("/")[-1][:-5] in KEY:
                want.setdefault(k, []).append(n)
    items = [(k, n) for k in sorted(want) for n in sorted(want[k])]
    print(f"{len(items)} key certificates on {len(want)} triangulations",
          flush=True)
    tag = os.environ.get("BALL_TAG", "d")
    res = open(f"{outdir}/{tag}{w}.jsonl", "a")
    nov = open(f"{outdir}/{tag}{w}_novel.jsonl", "a")
    # every worker skips seeds any worker has already finished
    done = set()
    for fn in sorted(__import__("glob").glob(f"{outdir}/{tag}*.jsonl")):
        if fn.endswith("_novel.jsonl"):
            continue
        for l in open(fn):
            try:
                done.add(json.loads(l)["seed_cert"])
            except Exception:
                pass
    for i, (k, cert) in enumerate(items):
        if i % nw != w or cert in done:
            continue
        t0 = time.time()
        tris, hfrac, signs, _c = parse_pcom(
            tar.extractfile(cert).read().decode())
        tris = [tuple(tuple(v) for v in t) for t in tris]
        cx = Complex(D8, tris)
        pts = cx.base_pts
        E = edgeset(tris)
        S = [s for s in splits if s.edges <= E]
        basis = f2_basis([delta_bits(s, pts) for s in S])
        task = f"/tmp/deep_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        with open(task, "a") as fh:
            fh.write("SEEDS 1\n")
            fh.write(" ".join(str(signs[p]) for p in pts) + "\n")
        wit = f"/tmp/deep_w{w}.jsonl"
        cmd = ["./ballc", task, str(radius), wit] + ([secs] if secs else [])
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
        rec = {"kind": "seed_done", "seed_cert": cert, "radius": radius,
               "evals": summ["evals"], "complete": bool(summ["complete"]),
               "distinct_schemes": len(schemes),
               "schemes": sorted(schemes), "novel": novel,
               "seconds": round(time.time() - t0, 1)}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for s in novel:
            nc, r = schemes[s]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": s, "ncomp": nc, "cert": cert,
                "source": f"radius-{radius} ball around {cert}",
                "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(v)
                            for p, v in hfrac.items()},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
