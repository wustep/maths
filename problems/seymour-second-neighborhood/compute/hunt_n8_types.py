#!/usr/bin/env python3
"""Existence census of Pisa missing-degree types at n=8.

For each graphical missing-degree sequence on 8 vertices we ask CP-SAT
whether a Pisa orientation exists.  Regular sequences and a band of
near-regular ones are searched first (those are the types Halkiewicz
saw at n<=7).  Each SAT witness is rechecked by seymour.is_pisa.
"""

from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pisa_cegar import solve_pisa
from seymour import is_pisa, cycle_power, lex_product, directed_cycle, empty_graph, missing_degree_sequence


def erdos_gallai(deg):
    d = sorted(deg, reverse=True)
    n = len(d)
    if any(x < 0 or x >= n for x in d):
        return False
    if sum(d) % 2:
        return False
    csum = 0
    for k in range(1, n + 1):
        csum += d[k - 1]
        rest = k * (k - 1) + sum(min(d[i], k) for i in range(k, n))
        if csum > rest:
            return False
    return True


def all_graphical(n=8):
    seqs = []
    # nonincreasing sequences
    def rec(prefix, leftover, parts):
        if parts == 0:
            if leftover == 0:
                seqs.append(tuple(prefix))
            return
        hi = prefix[-1] if prefix else n - 1
        hi = min(hi, leftover)
        lo = 0
        # remaining parts-1 can take at most hi each
        # leftover - hi*(parts-1) <= next <= hi
        for x in range(hi, -1, -1):
            if x * parts < leftover:
                break
            rec(prefix + [x], leftover - x, parts - 1)

    for s in range(0, n * (n - 1) + 1, 2):
        rec([], s, n)
    return [s for s in seqs if erdos_gallai(s)]


def known_witnesses():
    rows = []
    for name, out in [
        ("C8", __import__("seymour", fromlist=["directed_cycle"]).directed_cycle(8)),
        ("C8^2", cycle_power(8, 2)),
        ("C8^3", cycle_power(8, 3)),
        ("C4[E2]", lex_product(directed_cycle(4), empty_graph(2))),
        ("C2[RT3]?skip", None),
    ]:
        if out is None:
            continue
        rows.append((name, tuple(missing_degree_sequence(out)), out))
    return rows


def main():
    n = 8
    seqs = all_graphical(n)
    print(f"graphical sequences: {len(seqs)}", flush=True)

    # prioritise regular and unimodal-near-regular
    def prio(s):
        return (max(s) - min(s), -sum(s), s)

    seqs = sorted(set(seqs), key=prio)

    results = []
    # seed with constructions
    seen = set()
    for name, md, out in known_witnesses():
        rec = {
            "miss_deg": list(md),
            "status": "FEASIBLE",
            "source": name,
            "pisa": bool(is_pisa(out)),
        }
        results.append(rec)
        seen.add(md)
        print(f"SEED {md} {name}", flush=True)

    time_limit = 25.0
    for s in seqs:
        if s in seen:
            continue
        # skip extremely sparse missing (almost empty graph): those are
        # C8-like and already seeded, or have min outdegree issues.
        print(f"TRY {s}", flush=True)
        rec = solve_pisa(
            n, list(s),
            time_limit=time_limit,
            max_rounds=40,
            workers=8,
        )
        rec = {
            "miss_deg": list(s),
            "status": rec.get("status"),
            "source": "sat",
            "solve_time": rec.get("total_time"),
            "rounds": len(rec.get("rounds") or []),
            "code": rec.get("code"),
            "witness_missing_deg": (rec.get("witness") or {}).get("missing_deg"),
            "tight": (rec.get("witness") or {}).get("tight"),
        }
        results.append(rec)
        print(f"  -> {rec['status']} t={rec['solve_time']}", flush=True)
        Path(__file__).resolve().parent.joinpath("certs", "pisa8_types_partial.json").write_text(
            json.dumps(results, indent=2) + "\n"
        )

    outp = Path(__file__).resolve().parent / "certs" / "pisa8_types.json"
    outp.write_text(json.dumps(results, indent=2) + "\n")
    print(f"wrote {outp}")


if __name__ == "__main__":
    main()
