#!/usr/bin/env python3
"""Radius-1 thicken of triangulations obtained by perturbing M-certificate liftings.

The uniform sampler saturates at low twist-rank. High-rank regular
triangulations sit near the census liftings: scale an M-certificate
MIN_WEIGHTS by 10^6, add integer noise, take the lower hull, re-certify
exactly, skip census signatures, and thicken.

usage: python3 q7/thick_walk.py <nkept> <maxrank> <out.jsonl> [seed]
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import subprocess
import sys
import tarfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(ROOT))
os.chdir(ROOT)

import even_walk as ew
import export_span
import haas
from fastcx import Complex
from gen_fast import lower_hull_triangles
from notation import canon
from replay_census import ARCHIVE, URL, parse_pcom
from tcurve import lattice_points, validate_triangulation, check_convexity
from zone_search import D8, edgeset, delta_bits, f2_basis

K = 10 ** 6


def sig(tris):
    return hashlib.sha1(json.dumps(
        sorted(sorted(map(tuple, t)) for t in tris)).encode()).hexdigest()[:16]


def ensure_archive():
    if os.path.exists(ARCHIVE):
        return
    os.makedirs("data", exist_ok=True)
    subprocess.check_call(["curl", "-fsSL", "-o", ARCHIVE, URL])


def main():
    nkept = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    maxrank = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    out = Path(ew.resolve_out(sys.argv[3] if len(sys.argv) > 3
                              else "even_out/thick_walk.jsonl"))
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 11
    ensure_archive()
    tar = tarfile.open(ARCHIVE)
    recs = json.load(open("certs/mcert_collections.json"))
    bases = []
    census_sigs = set()
    for rec in recs.values():
        cert = rec["cert"]
        tris0, h0, _s, _c = parse_pcom(tar.extractfile(cert).read().decode())
        bases.append({p: int(v) * K for p, v in h0.items()})
        census_sigs.add(sig(tris0))
    rng = random.Random(seed)
    lat = lattice_points(D8)
    splits = haas.all_splits()
    known = ew.known_schemes()
    bin_path = ROOT / "thickc"
    if not bin_path.exists():
        subprocess.check_call(["gcc", "-O3", "-o", str(bin_path),
                               str(ROOT / "thickc.c")])
    out.parent.mkdir(exist_ok=True)
    drawn = kept = evals = tried = 0
    schemes = {}
    novel = []
    with out.open("w") as log:
        while kept < nkept and tried < nkept * 200:
            tried += 1
            base = rng.choice(bases)
            amp = rng.choice([K // 100, K // 30, K // 10, K // 3, K])
            h = {p: base[p] + rng.randint(-amp, amp) for p in lat}
            tris = lower_hull_triangles(lat, [float(h[p]) for p in lat])
            if validate_triangulation(D8, tris):
                continue
            hf = {p: Fraction(h[p]) for p in lat}
            if check_convexity(D8, tris, hf):
                continue
            drawn += 1
            if sig(tris) in census_sigs:
                continue
            tris = [tuple(tuple(v) for v in t) for t in tris]
            cx = Complex(D8, tris)
            pts = cx.base_pts
            E = edgeset(tris)
            S = [s for s in splits if s.edges <= E]
            basis = f2_basis([delta_bits(s, pts) for s in S])
            rank = len(basis)
            if rank < 8 or rank > maxrank:
                continue
            kept += 1
            task = HERE / "work" / "thick_walk.task"
            wit = HERE / "work" / "thick_walk.jsonl"
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
                        "heights": {f"{p[0]},{p[1]}": int(hf[p])
                                    for p in hf},
                        "signs": {f"{p[0]},{p[1]}": int(s)
                                  for p, s in zip(pts, r["signs"])},
                        "source": "q7 thick_walk",
                    }
                    novel.append(recn)
                    log.write(json.dumps(recn) + "\n")
                    log.flush()
                    print(f"  NEW {sch} rank={rank}", flush=True)
            evals += tri_evals
            print(f"  tri {kept}/{nkept} rank={rank} evals={tri_evals} "
                  f"complete={complete} schemes={len(schemes)} tried={tried}",
                  flush=True)
            log.write(json.dumps({
                "kind": "tri_done", "rank": rank, "evals": tri_evals,
                "complete": complete, "kept": kept, "tried": tried,
            }) + "\n")
            log.flush()
        summary = {
            "kind": "summary",
            "tried": tried,
            "drawn": drawn,
            "kept": kept,
            "maxrank": maxrank,
            "evals": evals,
            "distinct": len(schemes),
            "new": len(novel),
            "complete": kept >= nkept,
            "schemes": sorted(schemes),
            "novel": [r["scheme"] for r in novel],
        }
        log.write(json.dumps(summary) + "\n")
    dest = HERE / "certs" / "thick_walk.json"
    dest.write_text(json.dumps(summary, indent=2) + "\n")
    if novel:
        (HERE / "certs" / "new_schemes.json").write_text(
            json.dumps(novel, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print("wrote", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
