#!/usr/bin/env python3
"""Repair the turned 617-zip while keeping complementary halves.

If c[i] != c[i+617] for all i, a 7-AP of difference 617 in any unfolding
alternates colors. Then a cyclic 7-AP-free coloring of Z/1234Z would
repeat to length 7404.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

from pysat.solvers import Cadical195

from vdw import first_mono_ap, format_ab, max_monochrome_run, quadratic_residue_cycle

HERE = Path(__file__).resolve().parent
P = 617


def zip_turned() -> list[int]:
    cycle = quadratic_residue_cycle(P, 0)
    cycle_1 = [cycle[j % P] for j in range(1, P + 1)]
    p = P
    odds = [0] * (2 * p)
    for j in range(1, p + 1):
        odds[2 * j - 2] = cycle_1[j - 1]
    turned = [1 - c for c in odds]
    evens = [0] * (2 * p)
    for j in range(1, p + 1):
        src = 2 * j - 1
        dest = (src - p) % (2 * p)
        if dest == 0:
            dest = 2 * p
        evens[dest - 1] = turned[src - 1]
    merged = [0] * (2 * p)
    for i in range(2 * p):
        merged[i] = odds[i] if (i + 1) % 2 == 1 else evens[i]
    return merged


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


def main() -> None:
    zipped = zip_turned()
    n = len(zipped)
    complements = all(zipped[i] != zipped[i + P] for i in range(P))
    run = max_monochrome_run(zipped, True)
    lin = first_mono_ap(zipped, 7, False)
    cyc = first_mono_ap(zipped, 7, True)
    print(
        json.dumps(
            {
                "n": n,
                "complements": complements,
                "max_run": run,
                "linear_hit": None if lin is None else {"a": lin[0], "d": lin[1]},
                "cyclic_hit": None if cyc is None else {"a": cyc[0], "d": cyc[1]},
            },
            sort_keys=True,
        ),
        flush=True,
    )

    # SAT: 1234 vars, force complements, forbid mono 7-APs.
    # Second half is negation of first: x_{i+P} = ~x_i, so only 617 free vars.
    aps = cyclic_aps(n)
    solver = Cadical195()
    for i in range(P):
        # x_{i+P} XOR x_i  (exactly one true)
        solver.add_clause([i + 1, i + P + 1])
        solver.add_clause([-(i + 1), -(i + P + 1)])
    for ap in aps:
        solver.add_clause([-(p + 1) for p in ap])
        solver.add_clause([p + 1 for p in ap])
    # seed assumptions from turned zip on first half, optional
    box: dict = {"colors": None}

    def _run() -> None:
        if solver.solve():
            model = solver.get_model()
            box["colors"] = [
                1 if lit > 0 else 0
                for lit in sorted(model, key=abs)
                if 1 <= abs(lit) <= n
            ]

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=90.0)
    timed_out = thread.is_alive()
    if timed_out:
        try:
            solver.interrupt()
        except Exception:
            pass
        thread.join(timeout=3)
    colors = box["colors"]
    rec = {"sat": colors is not None, "timeout": timed_out and colors is None, "complements_seed": complements}
    if colors is not None:
        assert all(colors[i] != colors[i + P] for i in range(P))
        assert first_mono_ap(colors, 7, True) is None
        path = HERE / "cycle_1234_complement.txt"
        path.write_text(format_ab(colors) + "\n")
        linear = colors * 6
        (HERE / "coloring_7404.txt").write_text(format_ab(linear) + "\n")
        rec["file"] = "coloring_7404.txt"
        rec["verified_cycle"] = True
    print(json.dumps(rec, sort_keys=True), flush=True)
    (HERE / "zip_repair.json").write_text(json.dumps(rec, indent=2) + "\n")
    solver.delete()


if __name__ == "__main__":
    main()
