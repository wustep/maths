#!/usr/bin/env python3
"""Try to stretch the 3703 residue coloring past the published bound.

Encodings:
  --mode tail     free the last W colors, keep the prefix
  --mode flips    allow at most F flips of the 3703 seed, plus a free 3704th bit
  --mode window   free a window of width W ending at N
"""

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

from vdw import first_mono_ap, format_ab, load_coloring

HERE = Path(__file__).resolve().parent


def aps_in(n: int, k: int = 7) -> list[tuple[int, ...]]:
    out = []
    max_d = (n - 1) // (k - 1)
    for d in range(1, max_d + 1):
        for a in range(n - (k - 1) * d):
            out.append(tuple(a + i * d for i in range(k)))
    return out


def solve_with_timeout(solver: Cadical195, n: int, seconds: float) -> list[int] | None:
    result: dict[str, list[int] | None] = {"colors": None}

    def _run() -> None:
        if solver.solve():
            model = solver.get_model()
            result["colors"] = [
                1 if lit > 0 else 0
                for lit in sorted(model, key=abs)
                if 1 <= abs(lit) <= n
            ]

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=seconds)
    if thread.is_alive():
        try:
            solver.interrupt()
        except Exception:
            pass
        thread.join(timeout=2.0)
        return None
    return result["colors"]


def encode_tail(seed: list[int], target: int, free_tail: int) -> Cadical195:
    n = target
    solver = Cadical195()
    for ap in aps_in(n):
        solver.add_clause([-(p + 1) for p in ap])
        solver.add_clause([p + 1 for p in ap])
    freeze = max(0, n - free_tail)
    for i in range(min(freeze, len(seed))):
        lit = i + 1 if seed[i] else -(i + 1)
        solver.add_clause([lit])
    return solver


def encode_flips(seed: list[int], target: int, max_flips: int) -> Cadical195:
    n = target
    solver = Cadical195()
    for ap in aps_in(n):
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
    parser.add_argument("--mode", choices=("tail", "flips", "window"), default="tail")
    parser.add_argument("--target", type=int, default=3704)
    parser.add_argument("--tail", type=int, default=8)
    parser.add_argument("--flips", type=int, default=2)
    parser.add_argument("--seconds", type=float, default=30.0)
    args = parser.parse_args()
    seed = load_coloring(str(HERE / "coloring_3703.txt"))
    if args.mode == "tail":
        solver = encode_tail(seed, args.target, args.tail)
    elif args.mode == "window":
        solver = encode_tail(seed, args.target, args.tail)
    else:
        solver = encode_flips(seed, args.target, args.flips)
    colors = solve_with_timeout(solver, args.target, args.seconds)
    solver.delete()
    rec = {
        "mode": args.mode,
        "target": args.target,
        "tail": args.tail,
        "flips": args.flips,
        "sat": colors is not None,
    }
    if colors is not None:
        assert first_mono_ap(colors, k=7) is None
        path = HERE / f"coloring_{args.target}.txt"
        path.write_text(format_ab(colors) + "\n", encoding="ascii")
        rec["file"] = path.name
        rec["verified"] = True
    print(json.dumps(rec, sort_keys=True), flush=True)
    log = HERE / "extend_sat.jsonl"
    with log.open("a", encoding="ascii") as handle:
        handle.write(json.dumps(rec, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
