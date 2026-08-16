#!/usr/bin/env python3
"""CEGAR: complementary 1234-coloring, add violated 7-APs until SAT or fail."""

from __future__ import annotations

import json
from pathlib import Path
from time import monotonic

from pysat.solvers import Cadical195

from vdw import first_mono_ap, format_ab, quadratic_residue_cycle

HERE = Path(__file__).resolve().parent
P = 617
N = 2 * P


def zip_turned() -> list[int]:
    cycle = quadratic_residue_cycle(P, 0)
    cycle_1 = [cycle[j % P] for j in range(1, P + 1)]
    odds = [0] * N
    for j in range(1, P + 1):
        odds[2 * j - 2] = cycle_1[j - 1]
    turned = [1 - c for c in odds]
    evens = [0] * N
    for j in range(1, P + 1):
        src = 2 * j - 1
        dest = (src - P) % N
        if dest == 0:
            dest = N
        evens[dest - 1] = turned[src - 1]
    return [odds[i] if (i + 1) % 2 == 1 else evens[i] for i in range(N)]


def add_ap(solver: Cadical195, ap: tuple[int, ...]) -> None:
    solver.add_clause([-(p + 1) for p in ap])
    solver.add_clause([p + 1 for p in ap])


def all_violations(colors: list[int]) -> list[tuple[int, int]]:
    """Return (start, d) for every mono 7-AP with distinct points, cyclic."""
    hits = []
    seen: set[frozenset[int]] = set()
    for d in range(1, N):
        for a in range(N):
            pts = tuple((a + i * d) % N for i in range(7))
            key = frozenset(pts)
            if len(key) < 7 or key in seen:
                continue
            seen.add(key)
            c0 = colors[pts[0]]
            if all(colors[p] == c0 for p in pts[1:]):
                hits.append((a, d))
    return hits


def main() -> None:
    started = monotonic()
    seed = zip_turned()
    solver = Cadical195()
    for i in range(P):
        solver.add_clause([i + 1, i + P + 1])
        solver.add_clause([-(i + 1), -(i + P + 1)])
    # forbid cyclic 7-strings
    for a in range(N):
        add_ap(solver, tuple((a + i) % N for i in range(7)))
    rounds = []
    colors = None
    for rnd in range(1, 40):
        if not solver.solve():
            rounds.append({"round": rnd, "result": "unsat"})
            break
        model = solver.get_model()
        colors = [
            1 if lit > 0 else 0
            for lit in sorted(model, key=abs)
            if 1 <= abs(lit) <= N
        ]
        hits = all_violations(colors)
        rounds.append({"round": rnd, "violations": len(hits), "elapsed": round(monotonic() - started, 3)})
        print(rounds[-1], flush=True)
        if not hits:
            break
        # add up to 200 new APs
        added = 0
        seen_ap: set[frozenset[int]] = set()
        for a, d in hits:
            pts = tuple((a + i * d) % N for i in range(7))
            key = frozenset(pts)
            if key in seen_ap:
                continue
            seen_ap.add(key)
            add_ap(solver, pts)
            added += 1
            if added >= 250:
                break
    rec = {
        "rounds": rounds,
        "sat": colors is not None and rounds and rounds[-1].get("violations") == 0,
        "elapsed": round(monotonic() - started, 3),
    }
    if rec["sat"]:
        assert first_mono_ap(colors, 7, True) is None
        (HERE / "cycle_1234_complement.txt").write_text(format_ab(colors) + "\n")
        (HERE / "coloring_7404.txt").write_text(format_ab(colors * 6) + "\n")
        rec["file"] = "coloring_7404.txt"
    print(json.dumps({k: v for k, v in rec.items() if k != "rounds"}, sort_keys=True), flush=True)
    (HERE / "zip_cegar.json").write_text(json.dumps(rec, indent=2) + "\n")
    solver.delete()


if __name__ == "__main__":
    main()
