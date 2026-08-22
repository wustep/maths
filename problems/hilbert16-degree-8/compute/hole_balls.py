#!/usr/bin/env python3
"""Hamming balls centred on OUR certificates, not the paper's.

Every published exhaustion so far was centred on a census certificate:
radius 4 around all 2,367, radius 6 around the 38 M- and 78 (M-1)-
certificates, radius 7 around the seven productive M-certificates.  The
seventeen schemes certified in `certs/new_schemes.json` sit at Hamming
distance 1-6 from their source certificate, so a radius-6 ball around
ONE OF OURS reaches distance up to 12 from the census certificate --
ground no previous sweep touched (a seed at distance d contributes new
points as soon as d + radius > 7).

Each of our certificates carries its own triangulation and its own
integer lifting, already certified exactly by verify_new.py, so every
witness found here is a regular T-curve on a certified triangulation.

usage: hole_balls.py <radius> <outdir> <worker> <nworkers> [maxseconds]
       (seed order is set by SEED_ORDER below: novelty of the ball first)
"""
import glob
import json
import os
import subprocess
import sys
import time

import export_span
import haas
from fastcx import Complex
from zone_search import D8, edgeset, delta_bits, f2_basis

CERTS = "certs/new_schemes.json"


def load_seeds():
    """Our 17 certificates, with the Hamming distance to their source."""
    import tarfile
    from replay_census import parse_pcom, ARCHIVE
    tar = tarfile.open(ARCHIVE)
    cache = {}
    out = []
    for c in json.load(open(CERTS)):
        nm = [w for w in c["source"].replace(":", " ").split()
              if w.endswith(".pcom")][0]
        if nm not in cache:
            cache[nm] = parse_pcom(tar.extractfile(nm).read().decode())
        _t, _h, csigns, _c = cache[nm]
        sg = {tuple(int(x) for x in k.split(",")): int(v)
              for k, v in c["signs"].items()}
        d = sum(1 for p in csigns if csigns[p] != sg[p])
        out.append({"scheme": c["scheme"], "src": nm, "dist": d, "cert": c})
    return out


def main():
    radius, outdir = int(sys.argv[1]), sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    nw = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    secs = sys.argv[5] if len(sys.argv) > 5 else None
    os.makedirs(outdir, exist_ok=True)
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    ours = {x["scheme"] for x in json.load(open(CERTS))}
    known = census | ours
    splits = haas.all_splits()

    seeds = load_seeds()
    # only seeds whose ball leaves the swept region are worth the time
    seeds = [s for s in seeds if s["dist"] + radius > 7]
    seeds.sort(key=lambda s: -s["dist"])
    print(f"{len(seeds)} seeds at radius {radius}", flush=True)

    tag = os.environ.get("HB_TAG", "b")
    res = open(f"{outdir}/{tag}{w}.jsonl", "a")
    nov = open(f"{outdir}/{tag}{w}_novel.jsonl", "a")
    done = set()
    for fn in sorted(glob.glob(f"{outdir}/{tag}*.jsonl")):
        if fn.endswith("_novel.jsonl"):
            continue
        for l in open(fn):
            try:
                r = json.loads(l)
                done.add((r["seed_scheme"], r["radius"]))
            except Exception:
                pass
    for i, s in enumerate(seeds):
        if i % nw != w or (s["scheme"], radius) in done:
            continue
        t0 = time.time()
        c = s["cert"]
        tris = [tuple(tuple(v) for v in t) for t in c["triangles"]]
        cx = Complex(D8, tris)
        pts = cx.base_pts
        E = edgeset(tris)
        S = [sp for sp in splits if sp.edges <= E]
        basis = f2_basis([delta_bits(sp, pts) for sp in S])
        task = f"/tmp/hb_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        sg = {tuple(int(x) for x in k.split(",")): int(v)
              for k, v in c["signs"].items()}
        with open(task, "a") as fh:
            fh.write("SEEDS 1\n")
            fh.write(" ".join(str(sg[p]) for p in pts) + "\n")
        wit = f"/tmp/hb_w{w}.jsonl"
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
        novel = sorted(x for x in schemes if x not in known)
        rec = {"kind": "seed_done", "seed_scheme": s["scheme"],
               "src_cert": s["src"], "seed_dist_to_src": s["dist"],
               "radius": radius, "evals": summ["evals"],
               "complete": bool(summ["complete"]),
               "distinct_schemes": len(schemes),
               "outside_census": sorted(x for x in schemes
                                        if x not in census),
               "novel": novel, "seconds": round(time.time() - t0, 1)}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for x in novel:
            nc, r = schemes[x]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": x, "ncomp": nc,
                "source": f"radius-{radius} ball around our certificate "
                          f"for {s['scheme']} (itself at distance "
                          f"{s['dist']} from {s['src']})",
                "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": c["heights"],
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        print(json.dumps({k: rec[k] for k in
                          ("seed_scheme", "radius", "evals",
                           "distinct_schemes", "novel", "complete",
                           "seconds")}), flush=True)


if __name__ == "__main__":
    main()
