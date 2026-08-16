#!/usr/bin/env python3
"""Cadical: 3703 residue seed, at most F flips, free color at 3704."""

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

from vdw import first_mono_ap, format_ab, load_coloring

HERE = Path(__file__).resolve().parent


def build(seed: list[int], max_flips: int, target: int) -> Cadical195:
    n = target
    solver = Cadical195()
    max_d = (n - 1) // 6
    for d in range(1, max_d + 1):
        for a in range(n - 6 * d):
            ap = [a + i * d for i in range(7)]
            solver.add_clause([-(p + 1) for p in ap])
            solver.add_clause([p + 1 for p in ap])
    flip_vars = []
    for i, bit in enumerate(seed):
        x = i + 1
        f = n + i + 1
        flip_vars.append(f)
        if bit == 0:
            solver.add_clause([-f, x])
            solver.add_clause([f, -x])
        else:
            solver.add_clause([-f, -x])
            solver.add_clause([f, x])
    card = CardEnc.atmost(
        lits=flip_vars,
        bound=max_flips,
        encoding=EncType.seqcounter,
        top_id=n + len(seed) + 1,
    )
    for clause in card.clauses:
        solver.add_clause(clause)
    return solver


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flips", type=int, default=2)
    parser.add_argument("--target", type=int, default=3704)
    parser.add_argument("--seconds", type=float, default=45.0)
    args = parser.parse_args()
    seed = load_coloring(str(HERE / "coloring_3703.txt"))
    solver = build(seed, args.flips, args.target)
    box: dict = {"colors": None}

    def _run() -> None:
        if solver.solve():
            model = solver.get_model()
            box["colors"] = [
                1 if lit > 0 else 0
                for lit in sorted(model, key=abs)
                if 1 <= abs(lit) <= args.target
            ]

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=args.seconds)
    timed_out = thread.is_alive()
    if timed_out:
        try:
            solver.interrupt()
        except Exception:
            pass
        thread.join(timeout=3)
    colors = box["colors"]
    rec = {
        "flips": args.flips,
        "target": args.target,
        "sat": colors is not None,
        "timeout": timed_out and colors is None,
    }
    if colors is not None:
        assert first_mono_ap(colors, 7) is None
        path = HERE / f"coloring_{args.target}.txt"
        path.write_text(format_ab(colors) + "\n", encoding="ascii")
        rec["file"] = path.name
        rec["n_flips"] = sum(colors[i] != seed[i] for i in range(len(seed)))
    print(json.dumps(rec, sort_keys=True), flush=True)
    with (HERE / "flip_sat.jsonl").open("a", encoding="ascii") as handle:
        handle.write(json.dumps(rec, sort_keys=True) + "\n")
    solver.delete()


if __name__ == "__main__":
    main()
