#!/usr/bin/env python3
"""Independent unit-distance checker for a published .vtx file.

Rebuilds every edge by exact squared-distance == 1 in Q(√3,√5,√11).
Writes an edge list, degree histogram, and a JSON summary.  Does not
trust any precomputed edge file.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

from udg import (
    F,
    classify_parts,
    degrees,
    load_vtx,
    sqdist,
    unit_edges,
    write_edge_list,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("vtx", type=Path)
    ap.add_argument("--edges-out", type=Path, default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--expect-n", type=int, default=None)
    ap.add_argument("--expect-m", type=int, default=None)
    args = ap.parse_args()

    t0 = time.perf_counter()
    pts = load_vtx(args.vtx)
    t_parse = time.perf_counter() - t0
    n = len(pts)

    # Sanity: float uniqueness and no NaNs
    floats = [(p[0].to_float(), p[1].to_float()) for p in pts]
    if any(abs(x) > 20 or abs(y) > 20 for x, y in floats):
        print("warning: some coordinates have |coord| > 20")
    # near-duplicate float check
    rounded = [(round(x, 12), round(y, 12)) for x, y in floats]
    if len(set(rounded)) != n:
        raise SystemExit("float-rounded coordinates are not unique")

    t1 = time.perf_counter()
    edges = unit_edges(pts)
    t_edges = time.perf_counter() - t1
    m = len(edges)
    deg = degrees(n, edges)
    hist = dict(sorted(Counter(deg).items()))

    # Near-unit float pairs that failed exact test: report as a sanity residue.
    near = 0
    for i in range(n):
        xi, yi = floats[i]
        for j in range(i + 1, n):
            dx = xi - floats[j][0]
            dy = yi - floats[j][1]
            d2 = dx * dx + dy * dy
            if abs(d2 - 1.0) < 1e-9:
                if sqdist(pts[i], pts[j]) != F.from_int(1):
                    near += 1

    parts = classify_parts(pts)
    summary = {
        "vtx": str(args.vtx),
        "n": n,
        "m": m,
        "min_degree": min(deg) if deg else None,
        "max_degree": max(deg) if deg else None,
        "degree_histogram": {str(k): v for k, v in hist.items()},
        "n_large_no_sqrt5": len(parts["large"]),
        "n_rotated_has_sqrt5": len(parts["small_rotated"]),
        "near_unit_float_not_exact": near,
        "parse_seconds": t_parse,
        "edge_seconds": t_edges,
        "origin_present": any(p[0].is_zero() and p[1].is_zero() for p in pts),
    }
    print(json.dumps(summary, indent=2))

    if args.expect_n is not None and n != args.expect_n:
        raise SystemExit(f"expected n={args.expect_n}, got {n}")
    if args.expect_m is not None and m != args.expect_m:
        raise SystemExit(f"expected m={args.expect_m}, got {m}")

    if args.edges_out:
        write_edge_list(args.edges_out, n, edges)
        print(f"wrote {args.edges_out}")
    if args.json_out:
        args.json_out.write_text(json.dumps(summary, indent=2) + "\n")
        print(f"wrote {args.json_out}")


if __name__ == "__main__":
    main()
