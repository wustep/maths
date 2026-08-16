#!/usr/bin/env python3
"""SAT-search cyclic 2-colorings of Z/nZ with no monochromatic 7-AP.

A cycle of length n>=618 yields a linear coloring of length 6n >= 3708.
Also tries inserting one bit into the 617 residue cycle.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pysat.solvers import Cadical195

from vdw import first_mono_ap, format_ab, load_coloring, quadratic_residue_cycle

HERE = Path(__file__).resolve().parent


def cyclic_aps(n: int, k: int = 7) -> list[tuple[int, ...]]:
    aps = []
    seen: set[frozenset[int]] = set()
    for d in range(1, n):
        for a in range(n):
            pts = tuple((a + i * d) % n for i in range(k))
            key = frozenset(pts)
            if len(key) < k or key in seen:
                continue
            seen.add(key)
            aps.append(pts)
    return aps


def solve_cyclic(n: int, k: int, seconds: float, seed_cycle: list[int] | None) -> list[int] | None:
    import threading

    aps = cyclic_aps(n, k)
    solver = Cadical195()
    for ap in aps:
        solver.add_clause([-(p + 1) for p in ap])
        solver.add_clause([p + 1 for p in ap])
    solver.add_clause([-1])
    result: dict[str, list[int] | None] = {"colors": None}

    def _run() -> None:
        ok = solver.solve()
        if ok:
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
        solver.delete()
        return None
    solver.delete()
    return result["colors"]


def try_insert(cycle: list[int], k: int = 7) -> dict:
    """Insert one bit at each index / both colors; report first cyclic success."""
    n = len(cycle)
    trials = 0
    for pos in range(n + 1):
        for bit in (0, 1):
            trials += 1
            cand = cycle[:pos] + [bit] + cycle[pos:]
            if first_mono_ap(cand, k=k, cyclic=True) is None:
                return {"ok": True, "pos": pos, "bit": bit, "trials": trials, "n": n + 1}
    return {"ok": False, "trials": trials, "n": n + 1}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=618)
    parser.add_argument("--n-max", type=int, default=640)
    parser.add_argument("--seconds", type=float, default=20.0)
    args = parser.parse_args()

    cycle617 = quadratic_residue_cycle(617, zero_color=0)
    insert = try_insert(cycle617)
    print("insert", insert, flush=True)

    results = []
    for n in range(args.n_min, args.n_max + 1):
        colors = solve_cyclic(n, 7, args.seconds, None)
        rec = {"n": n, "sat": colors is not None}
        if colors is not None:
            assert first_mono_ap(colors, k=7, cyclic=True) is None
            path = HERE / f"cycle_{n}.txt"
            path.write_text(format_ab(colors) + "\n", encoding="ascii")
            rec["file"] = path.name
            rec["linear_len"] = 6 * n
            print("HIT", rec, flush=True)
        else:
            print("unsat-or-timeout", n, flush=True)
        results.append(rec)

    payload = {"insert_617": insert, "cyclic": results}
    (HERE / "cyclic_sat.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
