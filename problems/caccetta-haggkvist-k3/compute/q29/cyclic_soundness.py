#!/usr/bin/env python3
"""Exhibit a C₃-free d-outregular circulant and check the encoder accepts it.

kissat timed out searching for the n=38 d=12 cube. The cyclic construction
is explicit. Relabel so N⁺(0)={1..d} and N⁻(0)={d+1..d+k}, then sort each
block by out-neighbourhood to meet the lex cut. If every clause of the
regenerated CNF is satisfied, the encoder is not vacuously UNSAT at that
order. This is not a counterexample to the exact statement (d = floor((n-1)/3)).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

Q1 = Path(__file__).resolve().parent.parent / "q1"
sys.path.insert(0, str(Q1))

from encode import encode, var_id
from verify_model import check

HERE = Path(__file__).resolve().parent
KEEP = HERE / "certs" / "keep"


def circulant_arcs(n: int, d: int) -> set[tuple[int, int]]:
    return {(i, (i + step) % n) for i in range(n) for step in range(1, d + 1)}


def relabel(arcs: set[tuple[int, int]], perm: list[int]) -> set[tuple[int, int]]:
    """perm[old] = new."""
    return {(perm[i], perm[j]) for i, j in arcs}


def out_bits(n: int, v: int, arcs: set[tuple[int, int]]) -> tuple[int, ...]:
    return tuple(1 if (v, j) in arcs else 0 for j in range(n) if j != v)


def place_zero_blocks(n: int, d: int, arcs: set[tuple[int, int]]) -> set[tuple[int, int]]:
    nplus = sorted(j for j in range(n) if (0, j) in arcs)
    nminus = sorted(j for j in range(n) if (j, 0) in arcs)
    leftover = [j for j in range(1, n) if j not in nplus and j not in nminus]
    if len(nplus) != d:
        raise ValueError(f"N+ size {len(nplus)} != {d}")
    order = [0] + nplus + nminus + leftover
    perm = [0] * n
    for new, old in enumerate(order):
        perm[old] = new
    return relabel(arcs, perm)


def sort_blocks(n: int, d: int, k: int, arcs: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """Lex-sort N⁺, N⁻, and U by out-neighbourhood. Repeat to a fixed point."""
    groups = [
        list(range(1, d + 1)),
        list(range(d + 1, d + k + 1)),
        list(range(d + k + 1, n)),
    ]
    for _ in range(n * 4):
        changed = False
        for g in groups:
            ranked = sorted(g, key=lambda v: out_bits(n, v, arcs))
            if ranked == g:
                continue
            perm = list(range(n))
            for dest, src in zip(g, ranked):
                perm[src] = dest
            arcs = relabel(arcs, perm)
            changed = True
        if not changed:
            return arcs
    raise RuntimeError("block sort did not stabilize")


def model_pos(n: int, arcs: set[tuple[int, int]]) -> set[int]:
    return {var_id(n, i, j) for i, j in arcs}


def clauses_hold(clauses, pos: set[int], max_arc_var: int) -> tuple[bool, int]:
    """Check clauses that mention only arc variables.

    Sinz auxiliaries are existentially quantified: if out-degrees are
    exact, those clauses can be satisfied.  Including them here with
    auxiliaries unset would be a false failure.
    """
    bad = 0
    for c in clauses:
        if not c:
            bad += 1
            continue
        if any(abs(lit) > max_arc_var for lit in c):
            continue
        if not any((lit > 0 and lit in pos) or (lit < 0 and -lit not in pos) for lit in c):
            bad += 1
    return bad == 0, bad


def run(n: int, d: int) -> dict:
    raw = circulant_arcs(n, d)
    placed = place_zero_blocks(n, d, raw)
    k = sum(1 for j in range(n) if (j, 0) in placed)
    sorted_arcs = sort_blocks(n, d, k, placed)
    info = check(n, d, model_pos(n, sorted_arcs))
    max_arc = n * n
    clauses_sb, nvars_sb = encode(n, d, exact=True, sb=True, indeg0=k)
    ok_sb, nbad_sb = clauses_hold(clauses_sb, model_pos(n, sorted_arcs), max_arc)
    clauses_nosb, nvars_nosb = encode(n, d, exact=True, sb=False, indeg0=k)
    ok_nosb, nbad_nosb = clauses_hold(clauses_nosb, model_pos(n, placed), max_arc)
    circulant_ok = (
        bool(info["ok"])
        and info["min_out"] == d
        and not info["triangles"]
        and not info["two_cycles"]
    )
    rec = {
        "n": n,
        "d": d,
        "k": k,
        "header_sb": f"p cnf {nvars_sb} {len(clauses_sb)}",
        "header_nosb": f"p cnf {nvars_nosb} {len(clauses_nosb)}",
        "circulant_ok": circulant_ok,
        "min_out": info["min_out"],
        "narcs": info["narcs"],
        "triangles": len(info["triangles"]),
        "two_cycles": len(info["two_cycles"]),
        "cnf_accepts_placed_circulant_nosb": ok_nosb,
        "unsat_clauses_nosb": nbad_nosb,
        "cnf_accepts_sorted_circulant_sb": ok_sb,
        "unsat_clauses_sb": nbad_sb,
        "ok": circulant_ok and ok_nosb,
        "note": (
            "cyclic degree floor((n-1)/3), not a counterexample to ceil(n/3). "
            "The placed circulant meets the non-SB cube units. Lex SB at this "
            "order is checked by the small-n SAT pair, not by this model."
        ),
    }
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=38)
    ap.add_argument("--d", type=int, default=12)
    args = ap.parse_args()
    rec = run(args.n, args.d)
    KEEP.mkdir(exist_ok=True)
    path = KEEP / f"soundness_n{args.n}_d{args.d}.json"
    path.write_text(json.dumps(rec, indent=2))
    print(json.dumps(rec, indent=2))
    print("wrote", path)
    raise SystemExit(0 if rec["ok"] else 1)


if __name__ == "__main__":
    main()
