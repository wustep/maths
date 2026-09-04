#!/usr/bin/env python3
"""Radius-1 thicken of collection-space refinements.

Census triangulations already have a finished radius-1 thicken of the
whole Haas maximal stratum. Collection-space greedy refinements are
usually not those triangulations. For every C witness of a distinct
odd size-5 scheme, evaluate the 45 single-coordinate sign flips on
that refinement and try to regularize anything outside census+17.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT))
os.chdir(ROOT)

import deepnest as dn
import even_walk as ew
import haas
from fastcx import Complex
from notation import canon
from tcurve import check_convexity, validate_triangulation

D8 = 8


def rows(path):
    with open(path) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    known = ew.known_schemes()
    sp = dn.splits()
    pts = None
    novel = {}
    evals = 0
    witnesses = 0
    for path in sorted(glob.glob(str(HERE / "even_out" / "odd5c_*.jsonl"))):
        for row in rows(path):
            if row.get("kind") != "WITNESS":
                continue
            ids = row["collection"]
            coll = [sp[i] for i in ids]
            try:
                tris = dn.fast_refine(coll)
            except ValueError:
                continue
            if len(tris) != 64:
                continue
            tris = [tuple(tuple(v) for v in t) for t in tris]
            cx = Complex(D8, tris)
            if pts is None:
                pts = cx.base_pts
            signs = haas.signs_of(coll)
            base = [signs[p] for p in pts]
            witnesses += 1
            for k in range(len(pts)):
                sg = list(base)
                sg[k] = -sg[k]
                evals += 1
                nc, sch = cx.eval(sg)
                if sch is None:
                    continue
                sch = canon(sch)
                if sch in known or sch in novel:
                    continue
                rec = {
                    "kind": "NEW",
                    "scheme": sch,
                    "ncomp": nc,
                    "flip": k,
                    "collection": ids,
                    "source": "q7 thicken of an odd size-5 refinement",
                }
                frac = None
                if not validate_triangulation(D8, tris):
                    h = haas.regularize(tris, iters=80000, seed=k)
                    if h is not None:
                        frac = {p: Fraction(int(h[p])) for p in h}
                        if check_convexity(D8, tris, frac):
                            frac = None
                if frac is not None:
                    rec["triangles"] = [[list(v) for v in t] for t in tris]
                    rec["heights"] = {f"{p[0]},{p[1]}": int(v)
                                      for p, v in frac.items()}
                    rec["signs"] = {f"{p[0]},{p[1]}": int(s)
                                    for p, s in zip(pts, sg)}
                    rec["regular"] = True
                else:
                    rec["regular"] = False
                novel[sch] = rec
                print(f"  NEW {sch} regular={rec['regular']}", flush=True)

    certs = [r for r in novel.values() if r.get("regular") and "triangles" in r]
    if certs:
        dest = HERE / "certs" / "new_schemes.json"
        dest.write_text(json.dumps(certs, indent=2) + "\n")
    summary = {
        "what": ("Radius-1 sign flips on greedy refinements of distinct "
                 "odd size-5 collections."),
        "witnesses": witnesses,
        "evals": evals,
        "novel": sorted(novel),
        "regular": [r["scheme"] for r in certs],
        "complete": True,
    }
    out = HERE / "certs" / "thicken_witnesses.json"
    out.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
