#!/usr/bin/env python3
"""Compact status of the C searches: units, evaluations, novelty."""
import json
import glob
import sys

SETS = [("census span (runs4)", "runs4/w?.jsonl", "tri_done"),
        ("walk: non-census regular tris", "runs5/k?.jsonl", "tri_done"),
        ("random regular tris", "runs5/r?.jsonl", "tri_done"),
        ("balls r4, all census certs", "runs5/bw?.jsonl", "group_done"),
        ("balls r7, the two productive certs", "runs5/t?.jsonl", "seed_done"),
        ("balls r6, deep-nest certs", "runs5/d?.jsonl", "seed_done"),
        ("balls r6, all 38 M-certs", "runs5/m?.jsonl", "seed_done"),
        ("balls r7, the 5 remaining productive", "runs5/p?.jsonl", "seed_done"),
        ("balls r6, (M-1)-certificates", "runs5/n?.jsonl", "seed_done")]


def main():
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    prev = {x["scheme"] for x in json.load(open("certs/new_schemes.json"))}
    grand = 0
    allnov = set()
    for label, pat, kind in SETS:
        rs = []
        for f in sorted(glob.glob(pat)):
            for l in open(f):
                d = json.loads(l)
                if d.get("kind") == kind:
                    rs.append(d)
        if not rs:
            continue
        ev = sum(r["evals"] for r in rs)
        grand += ev
        nov = {s for r in rs for s in r.get("novel", [])}
        allnov |= nov
        print(f"{label:38s} units={len(rs):5d}  evals={ev:12,d}  "
              f"outside-census={len(nov)}")
    print(f"{'TOTAL evaluations performed':38s} {'':11s}  evals={grand:12,d}")
    print("(balls are nested -- a radius-7 ball contains the radius-6 and "
          "radius-4 balls\n of the same seed -- so this counts evaluations "
          "done, not distinct sign vectors.)")
    fresh = sorted(allnov - prev)
    print(f"\nschemes outside the published 2,367: {len(allnov)} "
          f"({len(allnov & prev)} already certified)")
    print(f"NEW beyond the certified eight: {fresh if fresh else 'none'}")


if __name__ == "__main__":
    main()
