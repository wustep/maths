#!/usr/bin/env python3
"""Drive ballc over the census, grouped by triangulation, one worker's share.

The previous Hamming-ball phase ran in Python on a hand-picked seed set and
finished 11 of 24 task files.  This covers *every* certificate in the
replayed census: certs are grouped by their triangulation (184 distinct), the
complex is built once per group, and every cert on it is a ball centre.

usage: ball_drive.py <worker> <nworkers> <radius> <outdir> [seconds-per-tri]
"""
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import time

from fastcx import Complex
from replay_census import parse_pcom, ARCHIVE
import export_span
import haas
from zone_search import D8, edgeset, delta_bits, f2_basis

GROUPS = "ball_groups.json"


def build_groups():
    tar = tarfile.open(ARCHIVE)
    names = sorted(n for n in tar.getnames() if n.endswith(".pcom"))
    groups = {}
    for n in names:
        tris, _h, signs, claimed = parse_pcom(
            tar.extractfile(n).read().decode())
        k = hashlib.sha1(json.dumps(
            sorted(sorted(map(tuple, tr)) for tr in tris)).encode()
        ).hexdigest()[:12]
        groups.setdefault(k, {"rep": n, "certs": []})
        groups[k]["certs"].append(n)
    json.dump(groups, open(GROUPS, "w"))
    return groups


def main():
    w, nw, radius, outdir = (int(sys.argv[1]), int(sys.argv[2]),
                             int(sys.argv[3]), sys.argv[4])
    secs = sys.argv[5] if len(sys.argv) > 5 else None
    os.makedirs(outdir, exist_ok=True)
    groups = (json.load(open(GROUPS)) if os.path.exists(GROUPS)
              else build_groups())
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    splits = haas.all_splits()
    tar = tarfile.open(ARCHIVE)
    # chunk the seed lists so the 849-certificate triangulation does not
    # pin one worker for the whole run
    CH = 48
    chunks = []
    for k in sorted(groups, key=lambda k: -len(groups[k]["certs"])):
        cs = groups[k]["certs"]
        for i in range(0, len(cs), CH):
            chunks.append((k, i, cs[i:i + CH]))
    load = [0] * nw
    keys = []
    for ch in chunks:
        j = load.index(min(load))
        load[j] += len(ch[2])
        if j == w:
            keys.append(ch)
    res = open(f"{outdir}/bw{w}.jsonl", "a")
    nov = open(f"{outdir}/bw{w}_novel.jsonl", "a")
    # every worker skips chunks any worker has already finished
    done = set()
    for fn in sorted(__import__("glob").glob(f"{outdir}/bw*.jsonl")):
        if fn.endswith("_novel.jsonl"):
            continue
        for l in open(fn):
            try:
                done.add(json.loads(l)["group"])
            except Exception:
                pass
    for (k, off, certs) in keys:
        tag = f"{k}:{off}"
        if tag in done:
            continue
        g = groups[k]
        t0 = time.time()
        tris, hfrac, _s, _c = parse_pcom(
            tar.extractfile(g["rep"]).read().decode())
        tris = [tuple(tuple(v) for v in t) for t in tris]
        cx = Complex(D8, tris)
        pts = cx.base_pts
        E = edgeset(tris)
        S = [s for s in splits if s.edges <= E]
        basis = f2_basis([delta_bits(s, pts) for s in S])
        task = f"/tmp/ballc_w{w}.task"
        export_span.emit(cx, pts, basis, task)
        seeds = []
        for n in certs:
            _t, _h, signs, _c = parse_pcom(
                tar.extractfile(n).read().decode())
            seeds.append([signs[p] for p in pts])
        with open(task, "a") as fh:
            fh.write(f"SEEDS {len(seeds)}\n")
            for s in seeds:
                fh.write(" ".join(map(str, s)) + "\n")
        wit = f"/tmp/ballc_w{w}.jsonl"
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
            assert nc == r["ncomp"]
            schemes.setdefault(sch, (nc, r))
        novel = sorted(s for s in schemes if s not in census)
        rec = {"kind": "group_done", "group": tag, "tri": k, "rep": g["rep"],
               "ncerts": len(certs), "radius": radius,
               "rank": len(basis), "evals": summ["evals"],
               "complete": bool(summ["complete"]),
               "distinct_schemes": len(schemes),
               "schemes": sorted(schemes), "novel": novel,
               "seconds": round(time.time() - t0, 1)}
        res.write(json.dumps(rec) + "\n")
        res.flush()
        for s in novel:
            nc, r = schemes[s]
            nov.write(json.dumps({
                "kind": "NOVEL", "scheme": s, "ncomp": nc,
                "cert": certs[r["seed"]], "group": tag, "regular": True,
                "triangles": [[list(v) for v in t] for t in tris],
                "heights": {f"{p[0]},{p[1]}": int(v)
                            for p, v in hfrac.items()},
                "signs": {f"{pts[j][0]},{pts[j][1]}": r["signs"][j]
                          for j in range(len(pts))}}) + "\n")
            nov.flush()
        print(json.dumps({kk: rec[kk] for kk in
                          ("rep", "ncerts", "evals", "distinct_schemes",
                           "novel", "seconds", "complete")}), flush=True)


if __name__ == "__main__":
    main()
