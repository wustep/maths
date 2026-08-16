#!/usr/bin/env python3
"""CEGAR cyclic 2-colorings for n just above 617."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import monotonic

from pysat.solvers import Cadical195

from vdw import first_mono_ap, format_ab

HERE = Path(__file__).resolve().parent


def add_ap(solver: Cadical195, ap: tuple[int, ...]) -> None:
    solver.add_clause([-(p + 1) for p in ap])
    solver.add_clause([p + 1 for p in ap])


def violations(colors: list[int], n: int) -> list[tuple[int, ...]]:
    hits = []
    seen: set[frozenset[int]] = set()
    for d in range(1, n):
        for a in range(n):
            pts = tuple((a + i * d) % n for i in range(7))
            key = frozenset(pts)
            if len(key) < 7 or key in seen:
                continue
            seen.add(key)
            c0 = colors[pts[0]]
            if all(colors[p] == c0 for p in pts[1:]):
                hits.append(pts)
    return hits


def solve_n(n: int, seconds: float) -> dict:
    started = monotonic()
    solver = Cadical195()
    solver.add_clause([-1])
    for a in range(n):
        add_ap(solver, tuple((a + i) % n for i in range(7)))
    colors = None
    rounds = 0
    last_v = None
    while monotonic() - started < seconds:
        rounds += 1
        if not solver.solve():
            solver.delete()
            return {"n": n, "sat": False, "rounds": rounds, "elapsed": round(monotonic() - started, 3)}
        model = solver.get_model()
        colors = [
            1 if lit > 0 else 0
            for lit in sorted(model, key=abs)
            if 1 <= abs(lit) <= n
        ]
        hits = violations(colors, n)
        last_v = len(hits)
        if not hits:
            solver.delete()
            return {
                "n": n,
                "sat": True,
                "rounds": rounds,
                "elapsed": round(monotonic() - started, 3),
                "colors": colors,
            }
        for pts in hits[:200]:
            add_ap(solver, pts)
    solver.delete()
    return {"n": n, "sat": False, "timeout": True, "rounds": rounds, "last_violations": last_v}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=618)
    parser.add_argument("--n-max", type=int, default=628)
    parser.add_argument("--seconds", type=float, default=12.0)
    args = parser.parse_args()
    rows = []
    for n in range(args.n_min, args.n_max + 1):
        rec = solve_n(n, args.seconds)
        slim = {k: v for k, v in rec.items() if k != "colors"}
        rows.append(slim)
        print(slim, flush=True)
        if rec.get("sat"):
            (HERE / f"cycle_{n}.txt").write_text(format_ab(rec["colors"]) + "\n")
            (HERE / f"coloring_{6 * n}.txt").write_text(format_ab(rec["colors"] * 6) + "\n")
            break
    (HERE / "cyclic_cegar.json").write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
