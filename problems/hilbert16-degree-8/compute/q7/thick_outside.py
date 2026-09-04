#!/usr/bin/env python3
"""Radius-1 thicken of fresh regular triangulations, one at a time.

Census triangulations are already finished through rank 26. This draws
certified regular triangulations (gen_fast) that are not among the
census edge-sets, keeps those of twist-rank at most 16, and runs the
existing thickc enumerator. No queue pickle: one triangulation's task
file at a time.

usage: python3 q7/thick_outside.py <ntris> <maxrank> <out.jsonl> [seed]
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT))
os.chdir(ROOT)

import even_walk as ew
import export_span
import gen_fast
import haas
from fastcx import Complex
from notation import canon
from zone_search import D8, edgeset, delta_bits, f2_basis


def census_edges():
    seen = set()
    if os.path.exists("span_tasks.json"):
        for d in json.load(open("span_tasks.json")):
            seen.add(d.get("edges_key"))
    return {x for x in seen if x}


def edges_key(tris):
    return tuple(sorted(frozenset(e) for t in tris
                        for e in ((t[0], t[1]), (t[0], t[2]), (t[1], t[2]))))


def main():
    ntris = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    maxrank = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    out = Path(ew.resolve_out(sys.argv[3] if len(sys.argv) > 3
                              else "even_out/thick_outside.jsonl"))
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    rng = random.Random(seed)
    known = ew.known_schemes()
    splits = haas.all_splits()
    bin_path = ROOT / "thickc"
    if not bin_path.exists():
        subprocess.check_call(["gcc", "-O3", "-o", str(bin_path),
                               str(ROOT / "thickc.c")])
    out.parent.mkdir(exist_ok=True)
    drawn = kept = evals = 0
    schemes = {}
    novel = []
    with out.open("w") as log:
        while kept < ntris:
            drawn += 1
            rec = gen_fast.random_certified_triangulation(8, rng)
            if rec is None:
                continue
            tris, frac = rec
            tris = [tuple(tuple(v) for v in t) for t in tris]
            cx = Complex(D8, tris)
            pts = cx.base_pts
            E = edgeset(tris)
            S = [s for s in splits if s.edges <= E]
            basis = f2_basis([delta_bits(s, pts) for s in S])
            rank = len(basis)
            if rank > maxrank or rank < 6:
                continue
            kept += 1
            task = HERE / "work" / "thick_outside.task"
            wit = HERE / "work" / "thick_outside.jsonl"
            export_span.emit(cx, pts, basis, str(task))
            subprocess.check_call(
                [str(bin_path), str(task), "0", "1", str(wit)])
            tri_evals = 0
            complete = False
            for line in open(wit):
                r = json.loads(line)
                if r.get("kind") == "summary":
                    tri_evals = r.get("evals", 0)
                    complete = bool(r.get("complete"))
                    continue
                if "signs" not in r:
                    continue
                nc, sch = cx.eval(r["signs"])
                if sch is None:
                    continue
                sch = canon(sch)
                if sch in schemes:
                    continue
                schemes[sch] = True
                if sch not in known:
                    recn = {
                        "kind": "NEW",
                        "scheme": sch,
                        "ncomp": nc,
                        "rank": rank,
                        "triangles": [[list(v) for v in t] for t in tris],
                        "heights": {f"{p[0]},{p[1]}": int(frac[p])
                                    for p in frac},
                        "signs": {f"{p[0]},{p[1]}": int(s)
                                  for p, s in zip(pts, r["signs"])},
                        "source": "q7 thick_outside",
                    }
                    novel.append(recn)
                    log.write(json.dumps(recn) + "\n")
                    log.flush()
                    print(f"  NEW {sch} rank={rank}", flush=True)
            evals += tri_evals
            print(f"  tri {kept}/{ntris} rank={rank} evals={tri_evals} "
                  f"complete={complete} schemes={len(schemes)}", flush=True)
            log.write(json.dumps({
                "kind": "tri_done", "rank": rank, "evals": tri_evals,
                "complete": complete, "drawn": drawn, "kept": kept,
            }) + "\n")
            log.flush()
        summary = {
            "kind": "summary",
            "drawn": drawn,
            "kept": kept,
            "maxrank": maxrank,
            "evals": evals,
            "distinct": len(schemes),
            "new": len(novel),
            "complete": kept >= ntris,
            "schemes": sorted(schemes),
            "novel": [r["scheme"] for r in novel],
        }
        log.write(json.dumps(summary) + "\n")
    dest = HERE / "certs" / "thick_outside.json"
    dest.write_text(json.dumps(summary, indent=2) + "\n")
    if novel:
        (HERE / "certs" / "new_schemes.json").write_text(
            json.dumps(novel, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print("wrote", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
