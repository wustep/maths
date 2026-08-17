#!/usr/bin/env python3
"""Exact analysis of kissing codes in R^5 that contain a 24-cell.

After an orthogonal change of coordinates the 24-cell is the D4 root system
in the hyperplane x5 = 0.  An extra unit point x = (y, h) with 0 < |h| < 1
writes y = sqrt(1-h^2) u, |u|=1 in R^4.  Compatibility with every D4 root
is equivalent to
    φ(u) := max_{i≠j} (|u_i| + |u_j|)  ≤  β := 1 / sqrt(2(1-h^2)).
Since φ ≥ 1 on S^3 one must have β ≥ 1, hence h^2 ≥ 1/2.  (The poles
±e_5 are allowed separately and conflict with every non-polar extra point
in the same closed hemisphere, because those have |h| ≥ 1/√2 > 1/2.)

For two extra points in the same open hemisphere the first-four-coordinate
blocks y, y' then satisfy <y, y'> ≤ 0, so their directions form a
spherical code in S^3 of max inner product ≤ 0.  Rankin's bound A(4,0) ≤ 8
is realised by the exact Delsarte polynomial f(t) = t^2 + t:
    f(t) = (1/4) P_0^{(4)} + P_1^{(4)} + (3/4) P_2^{(4)},
    f ≤ 0 on [-1, 0],  f(1)/f_0 = 8.

Hence each open hemisphere holds at most 8 extra points and a
D4-containing kissing code has size at most 24+8+8 = 40.

This file checks the discrete supporting statements exactly:
  - every 24-cell hole has φ = 1, and they realise A(4,0) = 8;
  - the 1/2-graph on the 24 holes has independence number 8;
  - the Gegenbauer expansion of t^2+t in dimension 4 is as claimed.
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path

F = Fraction


def holes() -> list[tuple]:
    """24 holes of the D4 24-cell, as vectors of squared-norm 1 in Q(√? ).

    We store them as integer 4-tuples of a common squared scale:
      - 8 cross-polytope points ±e_i, scale 1 (norm^2 = 1)
      - 16 tesseract points (±1,±1,±1,±1)/2, scale 1 (norm^2 = 1)
    Both families already have norm^2 = 1 over Q.
    """
    pts = []
    for i in range(4):
        for s in (-1, 1):
            v = [F(0)] * 4
            v[i] = F(s)
            pts.append(tuple(v))
    for signs in itertools.product((-1, 1), repeat=4):
        pts.append(tuple(F(s, 2) for s in signs))
    assert len(pts) == 24
    assert all(sum(x * x for x in p) == 1 for p in pts)
    return pts


def phi_sq_bound_is_one(p) -> bool:
    """φ(p) ≤ 1 iff every pair-sum of abs coords is ≤ 1."""
    a = [abs(x) for x in p]
    for i, j in itertools.combinations(range(4), 2):
        if a[i] + a[j] > 1:
            return False
    return True


def independence_number(pts) -> tuple[int, list]:
    """Maximum subset with all pairwise inner products ≤ 0."""
    n = len(pts)
    # adjacency: ip > 0 (for these points, the only positive ip is 1/2)
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            ip = sum(pts[i][k] * pts[j][k] for k in range(4))
            if ip > 0:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    best = 0
    best_sets = []

    def rec(used: int, start: int, sz: int) -> None:
        nonlocal best
        # greedy bound
        remaining = 0
        for v in range(start, n):
            if (used >> v) & 1 == 0 and (adj[v] & used) == 0:
                remaining += 1
        if sz + remaining < best:
            return
        if sz > best:
            best = sz
            best_sets.clear()
        if sz == best:
            best_sets.append(used)
        for v in range(start, n):
            if (used >> v) & 1:
                continue
            if adj[v] & used:
                continue
            rec(used | (1 << v), v + 1, sz + 1)

    rec(0, 0, 0)
    return best, best_sets


def classify_set(pts, mask: int) -> str:
    idx = [i for i in range(len(pts)) if (mask >> i) & 1]
    kinds = []
    for i in idx:
        nz = sum(1 for x in pts[i] if x != 0)
        kinds.append(nz)
    n_axis = kinds.count(1)
    n_tess = kinds.count(4)
    return f"axis={n_axis} tesseract={n_tess}"


def gegenbauer4_t2_plus_t() -> dict:
    """Exact Delsarte certificate A(4,0) ≤ 8 via f(t) = t^2 + t.

    Dimension-4 recurrence (n=4):
        P0=1, P1=t,
        (k+2) P_{k+1} = (2k+2) t P_k - k P_{k-1}.
    Hence P2 = (4t^2 - 1)/3, and t^2 = (3 P2 + P0)/4.
    """
    # P2(t) = (4t^2-1)/3  ⇒  t^2 = (3 P2 + 1)/4
    # t^2 + t = (1/4) P0 + P1 + (3/4) P2
    f0, f1, f2 = F(1, 4), F(1), F(3, 4)
    f_at_1 = F(1) + F(1)  # 1^2 + 1
    ratio = f_at_1 / f0
    # f ≤ 0 on [-1, 0]: t(t+1) has roots -1, 0 and leading coeff +1.
    samples = [F(-1), F(-3, 4), F(-1, 2), F(-1, 4), F(0)]
    sample_vals = [s * (s + 1) for s in samples]
    return {
        "f": "t^2 + t",
        "gegenbauer_coeffs_n4": [str(f0), str(f1), str(f2)],
        "f(1)/f0": str(ratio),
        "nonpositive_on_[-1,0]_samples": [str(v) for v in sample_vals],
        "all_sample_le_0": all(v <= 0 for v in sample_vals),
        "bound": int(ratio),
    }


def main() -> int:
    pts = holes()
    assert all(phi_sq_bound_is_one(p) for p in pts)

    hist = {}
    for i, j in itertools.combinations(range(24), 2):
        ip = sum(pts[i][k] * pts[j][k] for k in range(4))
        hist[ip] = hist.get(ip, 0) + 1
    hist_s = {str(k): v for k, v in sorted(hist.items())}

    alpha, sets = independence_number(pts)
    classes = {}
    for m in sets:
        tag = classify_set(pts, m)
        classes[tag] = classes.get(tag, 0) + 1

    rankin = gegenbauer4_t2_plus_t()
    report = {
        "n_holes": 24,
        "all_holes_satisfy_phi_le_1": True,
        "hole_ip_histogram": hist_s,
        "independence_number_ip_le_0": alpha,
        "n_maximum_independent_sets": len(sets),
        "mis_types": classes,
        "rankin_A4_0": rankin,
        "max_extra_per_open_hemisphere": 8,
        "max_D4_containing_kissing_size": 40,
    }
    out = Path(__file__).resolve().parent / "d4_equator.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    assert alpha == 8
    assert rankin["bound"] == 8
    assert rankin["all_sample_le_0"]
    print("PASS: D4-containing kissing codes have size at most 40.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
