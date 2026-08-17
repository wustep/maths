#!/usr/bin/env python3
"""Rank unused lattice / ρ-rotated points by exact unit-degree into G.

Uses a float prefilter then exact squared-distance == 1.  Writes a JSON
table.  Coordinates come only from Parts' (a,b,c,d)/12 lattice and ρ.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from lattice import generate_disk, rotate_rho
from udg import F, load_vtx, sqdist


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--r-max", type=float, default=2.55)
    ap.add_argument("--min-deg", type=int, default=4)
    ap.add_argument("--out", type=Path, default=Path("candidates.json"))
    args = ap.parse_args()

    t0 = time.perf_counter()
    pts = load_vtx(args.vtx)
    have = set(pts)
    floats = [(p[0].to_float(), p[1].to_float()) for p in pts]
    n = len(pts)
    print(f"G n={n} r_max={args.r_max}", flush=True)

    disk = generate_disk(args.r_max)
    disk_pts = [p for _, p in disk]
    print(f"disk {len(disk_pts)} in {time.perf_counter()-t0:.1f}s", flush=True)

    # unique candidates: unrotated then rotated, skip those already in G
    cands: list[tuple[str, tuple[F, F]]] = []
    seen = set(have)
    for p in disk_pts:
        if p not in seen:
            seen.add(p)
            cands.append(("lattice", p))
    for p in disk_pts:
        q = rotate_rho(p)
        if q not in seen:
            seen.add(q)
            cands.append(("rho", q))
    print(f"new candidates {len(cands)}", flush=True)

    one = F.from_int(1)
    ranked = []
    t1 = time.perf_counter()
    for k, (kind, p) in enumerate(cands):
        xf, yf = p[0].to_float(), p[1].to_float()
        neigh = []
        for i, (xi, yi) in enumerate(floats):
            dx = xf - xi
            dy = yf - yi
            d2 = dx * dx + dy * dy
            if abs(d2 - 1.0) < 1e-8:
                if sqdist(p, pts[i]) == one:
                    neigh.append(i)
        deg = len(neigh)
        if deg >= args.min_deg:
            ranked.append(
                {
                    "kind": kind,
                    "deg": deg,
                    "neighbors": neigh,
                    "x": p[0].to_float(),
                    "y": p[1].to_float(),
                    "x_repr": repr(p[0]),
                    "y_repr": repr(p[1]),
                    "r": math.hypot(xf, yf),
                }
            )
        if (k + 1) % 20000 == 0:
            print(f"  scanned {k+1}/{len(cands)} kept {len(ranked)}", flush=True)

    ranked.sort(key=lambda r: (-r["deg"], r["r"]))
    summary = {
        "vtx": str(args.vtx),
        "n": n,
        "r_max": args.r_max,
        "n_candidates": len(cands),
        "n_kept": len(ranked),
        "min_deg": args.min_deg,
        "seconds": time.perf_counter() - t0,
        "scan_seconds": time.perf_counter() - t1,
        "degree_of_kept_max": ranked[0]["deg"] if ranked else None,
        "top": ranked[:50],
        "all": ranked,
    }
    args.out.write_text(json.dumps(summary, indent=2) + "\n")
    print(
        f"kept {len(ranked)} with deg>={args.min_deg}; "
        f"maxdeg={summary['degree_of_kept_max']} in {summary['seconds']:.1f}s"
    )
    for rec in ranked[:15]:
        print(f"  deg={rec['deg']:2d} {rec['kind']:7s} r={rec['r']:.4f} {rec['x_repr']}, {rec['y_repr']}")


if __name__ == "__main__":
    main()
