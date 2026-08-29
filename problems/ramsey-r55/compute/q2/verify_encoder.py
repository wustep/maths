#!/usr/bin/env python3
"""Independent small exhaustive checks for orbit_sat.py's reductions."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from pysat.solvers import Cadical195

from orbit_sat import Enc, OrbitEncoding

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from r55lib import is_ramsey


OUT = Path(__file__).resolve().parent / "certs" / "encoder_selftest.json"


def clause_value(clauses: list[list[int]], positive: set[int]) -> bool:
    return all(
        any((lit > 0 and lit in positive) or (lit < 0 and -lit not in positive)
            for lit in clause)
        for clause in clauses
    )


def graph_exhaustive(n: int, p: int) -> dict:
    obj = OrbitEncoding(n, p)
    obj.build(False, None)
    ids = sorted(obj.enc.names.values())
    checked = agree = 0
    for bits in itertools.product((False, True), repeat=len(ids)):
        positive = {v for v, bit in zip(ids, bits) if bit}
        cnf_ok = clause_value(obj.enc.clauses, positive)
        model = [v if v in positive else -v for v in ids]
        graph_ok = is_ramsey(obj.decode(model))
        checked += 1
        agree += cnf_ok == graph_ok
    return {
        "n": n,
        "p": p,
        "edge_orbit_vars": len(ids),
        "assignments": checked,
        "agree": agree == checked,
        "five_subset_orbits": obj.subset_orbits,
        "distinct_base_clause_keys": len(obj.base_clause_keys),
    }


def counter_exhaustive() -> dict:
    enc = Enc()
    a, b, c = enc.var("a"), enc.var("b"), enc.var("c")
    weighted = [a, a, b, c]
    enc.card_between(weighted, 2, 3)
    checked = agree = 0
    for bits in itertools.product((False, True), repeat=3):
        assumptions = [v if bit else -v for v, bit in zip((a, b, c), bits)]
        with Cadical195(bootstrap_with=enc.clauses) as solver:
            sat = solver.solve(assumptions=assumptions)
        total = 2 * bits[0] + bits[1] + bits[2]
        checked += 1
        agree += bool(sat) == (2 <= total <= 3)
    return {"assignments": checked, "agree": agree == checked}


def lex_exhaustive() -> dict:
    enc = Enc()
    left = [enc.var("left", i) for i in range(3)]
    right = [enc.var("right", i) for i in range(3)]
    enc.lex_leq(left, right)
    checked = agree = 0
    for x in itertools.product((False, True), repeat=3):
        for y in itertools.product((False, True), repeat=3):
            assumptions = [v if bit else -v for v, bit in zip(left, x)]
            assumptions += [v if bit else -v for v, bit in zip(right, y)]
            with Cadical195(bootstrap_with=enc.clauses) as solver:
                sat = solver.solve(assumptions=assumptions)
            checked += 1
            agree += bool(sat) == (x <= y)
    return {"assignments": checked, "agree": agree == checked}


def main() -> int:
    rec = {
        "graph_tests": [graph_exhaustive(6, 2), graph_exhaustive(7, 7)],
        "weighted_counter": counter_exhaustive(),
        "lex_constraint": lex_exhaustive(),
        "note": (
            "The n=6 order-2 and n=7 order-7 edge-orbit encodings were "
            "exhausted assignment by assignment against r55lib.is_ramsey. "
            "The repeated-literal weighted counter and lex constraint were "
            "also exhausted under all inputs."
        ),
    }
    rec["all_ok"] = all(row["agree"] for row in rec["graph_tests"]) and \
        rec["weighted_counter"]["agree"] and rec["lex_constraint"]["agree"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps(rec, indent=2, sort_keys=True))
    return 0 if rec["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
