#!/usr/bin/env python3
"""Independent checks: Shakan on listed sets, SAT witnesses, construction tables.

Does not import sat_exact or search_local. Recomputes gaps from scratch.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from constructions import (
    equally_spaced,
    geometric,
    jittered_grid,
    nearest_subgroup,
    random_set,
    small_squares,
    subgroup,
)
from gaplib import gap, is_prime, max_gap_dilates, primes_upto, shakan_lower, uniq_mod


def check_shakan_on(A, p, tag):
    A = uniq_mod(A, p)
    n = len(A)
    g, d = max_gap_dilates(A, p)
    sh = shakan_lower(p, n)
    ok = g + 1e-12 >= sh
    return {
        "tag": tag,
        "p": p,
        "n": n,
        "g": g,
        "d": d,
        "shakan": sh,
        "ok": ok,
        "ratio": g / (p / n) if n else None,
    }


def check_equivalence_gap_vs_complement_ap(A, p):
    """max_d g(dA) equals the longest difference-1 gap among the dilates,
    which is the longest AP in A^c."""
    g, d = max_gap_dilates(A, p)
    # longest AP in complement: for each diff δ, gap of δ^{-1} A
    # already what max_gap_dilates computes
    S = set(uniq_mod(A, p))
    # independently: for each difference δ, longest run in complement along +δ
    best = 0
    for delta in range(1, p):
        # mark complement along the Hamilton cycle +delta
        run = 0
        # start at 0, walk p steps, then account for wrap
        seq_miss = []
        x = 0
        for _ in range(p):
            seq_miss.append(x not in S)
            x = (x + delta) % p
        # circular longest True run
        if all(seq_miss):
            best = p
            break
        doubled = seq_miss + seq_miss
        cur = 0
        local = 0
        for b in doubled:
            if b:
                cur += 1
                if cur > local:
                    local = cur
            else:
                cur = 0
        local = min(local, p)
        if local > best:
            best = local
    return g == best, g, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certs", type=str, default=None)
    args = ap.parse_args()
    failures = []
    reports = []

    # 1. tiny exhaustive Shakan check: every n-set for small p
    for p in [5, 7, 11, 13]:
        assert is_prime(p)
        # all nonempty proper subsets is 2^p; p=13 is 8k, fine if we skip n=1
        for mask in range(1, 1 << p):
            A = [i for i in range(p) if mask >> i & 1]
            if len(A) <= 1 or len(A) == p:
                continue
            rec = check_shakan_on(A, p, f"enum-{p}")
            if not rec["ok"]:
                failures.append(rec)
        reports.append({"enum_p": p, "ok": True})

    # 2. constructions on a list of primes
    import random

    rng = random.Random(0)
    for p in primes_upto(80):
        if p < 5:
            continue
        n = max(2, int(round(p**0.5)))
        families = {
            "squares": small_squares(p, n),
            "equal": equally_spaced(p, n),
            "geom": geometric(p, n),
            "sub": nearest_subgroup(p, n)[0],
            "rand": random_set(p, n, rng),
        }
        for tag, A in families.items():
            rec = check_shakan_on(A, p, tag)
            reports.append(rec)
            if not rec["ok"]:
                failures.append(rec)
            eq, g1, g2 = check_equivalence_gap_vs_complement_ap(A, p)
            if not eq:
                failures.append({"tag": f"equiv-{tag}", "p": p, "g_dil": g1, "g_ap": g2})

    # 3. optional certificate file
    if args.certs:
        data = json.loads(Path(args.certs).read_text())
        items = data if isinstance(data, list) else [data]
        for rec in items:
            p, A = rec["p"], rec["A"]
            g, d = max_gap_dilates(A, p)
            claimed = rec.get("g", rec.get("G", rec.get("g_upper")))
            if claimed is not None and g != claimed:
                failures.append({"tag": "cert-g", "p": p, "claimed": claimed, "got": g})
            sh = shakan_lower(p, len(uniq_mod(A, p)))
            if g + 1e-12 < sh:
                failures.append({"tag": "cert-shakan", "p": p, "g": g, "sh": sh})

    out = {"n_reports": len(reports), "n_failures": len(failures), "failures": failures[:20]}
    print(json.dumps(out, indent=2))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
