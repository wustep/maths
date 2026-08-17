#!/usr/bin/env python3
"""Start from a Bose/Singer Sidon-like set and add a short repair set.

A dent requires an infinite family, so we look for a *rule* (interval of
relative length α, a second dilate, a geometric progression) that
completes every prime-power instance.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bases import cover_stats, uncovered, is_sum_cover
from constructions import bose_set, two_ap
from singer import singer_difference_set, is_prime

BEL = math.sqrt(8 / 3)


def add_interval(A, n, start, length):
    S = set(A)
    for i in range(length):
        S.add((start + i) % n)
    return S


def try_interval_repairs(A, n, max_extra: int):
    """Try A ∪ (s + [0, L)) for L <= max_extra, various s."""
    base_miss = uncovered(A, n)
    if not base_miss:
        return cover_stats(A, n)
    # candidate starts: 0, missed points, and a few A-elements
    starts = [0, n // 2]
    starts.extend(base_miss[:8])
    starts.extend(list(A)[:4])
    best = None
    for L in range(1, max_extra + 1):
        for s in starts:
            B = add_interval(A, n, s, L)
            st = cover_stats(B, n)
            if st["ok"]:
                if best is None or st["m"] < best["m"]:
                    best = st
                    best["repair"] = f"interval start={s} L={L}"
                    return best  # first (shortest L, some s)
    return best


def try_second_dilate(A, n, max_extra: int):
    """A ∪ (g + d·[0,L))."""
    starts = [0]
    starts.extend(uncovered(A, n)[:6])
    ds = [2, 3, n // 2, max(1, int(math.sqrt(n)))]
    for L in range(1, max_extra + 1):
        for d in ds:
            for s in starts:
                B = set(A)
                for i in range(L):
                    B.add((s + d * i) % n)
                st = cover_stats(B, n)
                if st["ok"]:
                    st["repair"] = f"AP s={s} d={d} L={L}"
                    return st
    return None


def run_singer(qs):
    rows = []
    for q in qs:
        if not is_prime(q):
            continue
        v, D = singer_difference_set(q)
        st0 = cover_stats(D, v)
        extra_budget = max(1, int(1.05 * (BEL * math.sqrt(v) - len(D))))
        extra_budget = min(extra_budget, v - len(D))
        repair = try_interval_repairs(D, v, extra_budget)
        if repair is None:
            repair = try_second_dilate(D, v, extra_budget)
        row = {
            "kind": "singer",
            "q": q,
            "n": v,
            "sidon_m": st0["m"],
            "sidon_covered": st0["covered"],
            "sidon_ratio": st0["ratio"],
            "repair": None if repair is None else repair.get("repair"),
            "repaired_m": None if repair is None else repair["m"],
            "repaired_ratio": None if repair is None else repair["ratio"],
            "repaired_ok": False if repair is None else repair["ok"],
            "bel": BEL,
            "beat_bel": bool(repair and repair["ok"] and repair["ratio"] < BEL),
        }
        print(row, flush=True)
        rows.append(row)
    return rows


def run_bose(qs):
    rows = []
    for q in qs:
        got = bose_set(q)
        if got is None:
            print(f"bose failed q={q}", flush=True)
            continue
        n, A = got
        st0 = cover_stats(A, n)
        extra_budget = max(1, int(1.05 * (BEL * math.sqrt(n) - len(A))))
        extra_budget = min(extra_budget, n - len(A))
        repair = try_interval_repairs(A, n, extra_budget)
        if repair is None:
            repair = try_second_dilate(A, n, extra_budget)
        row = {
            "kind": "bose",
            "q": q,
            "n": n,
            "sidon_m": st0["m"],
            "sidon_covered": st0["covered"],
            "sidon_ratio": st0["ratio"],
            "repair": None if repair is None else repair.get("repair"),
            "repaired_m": None if repair is None else repair["m"],
            "repaired_ratio": None if repair is None else repair["ratio"],
            "repaired_ok": False if repair is None else repair["ok"],
            "beat_bel": bool(repair and repair["ok"] and repair["ratio"] < BEL),
        }
        print(row, flush=True)
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qs", default="3,5,7,11,13")
    ap.add_argument("--out", default="compute/sidon_repair.json")
    args = ap.parse_args()
    qs = [int(x) for x in args.qs.split(",") if x]
    rows = []
    rows.extend(run_singer(qs))
    rows.extend(run_bose(qs))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
