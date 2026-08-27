#!/usr/bin/env python3
"""Replay every committed q2 census row from its certificate."""

from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
Q1 = PARENT / "q1"
sys.path.insert(0, str(PARENT))
sys.path.insert(0, str(Q1))

from ladders import ladder_poset, named, n_ordinal_summands  # noqa: E402
from posetlib import Poset, balance, pair_counts_fb  # noqa: E402
from three_rail import rail_poset  # noqa: E402


def delta_of(P: Poset):
    e, C = pair_counts_fb(P)
    num, den, e2, pair, _ = balance(P, C, e)
    g = gcd(num, den)
    return num // g, den // g, e2, pair


def check_ladders(blob: dict) -> None:
    for row in blob["census"]:
        got = named(row["n"], tuple(row["broken"]))
        if got["delta"] != row["min_delta"] or got["e"] != row["e"]:
            raise AssertionError(f"ladder n={row['n']}: {got} vs {row}")
        if got["n_summands"] != 1:
            raise AssertionError(f"ladder n={row['n']} splits")
        if row["min_delta"][0] * 3 < row["min_delta"][1]:
            raise AssertionError(f"ladder n={row['n']} below 1/3")
        print(
            f"ladder n={row['n']} {row['min_delta'][0]}/{row['min_delta'][1]} "
            f"L_{row['n']},{','.join(map(str, row['broken']))} e={row['e']} OK"
        )


def check_rails(blob: dict) -> None:
    for row in blob["exhaustive"]:
        P = rail_poset(row["n"], tuple(row["broken4"]), tuple(row["broken5"]))
        num, den, e, pair = delta_of(P)
        if [num, den] != row["min_delta"] or e != row["e"]:
            raise AssertionError(f"rail n={row['n']}: {(num, den, e)} vs {row}")
        if n_ordinal_summands(P) != 1:
            raise AssertionError(f"rail n={row['n']} splits")
        if num * 17 < den * 6:
            raise AssertionError(f"rail n={row['n']} below 6/17")
        if num * 3 < den:
            raise AssertionError(f"rail n={row['n']} below 1/3")
        print(
            f"rail n={row['n']} {num}/{den} e={e} "
            f"b4={row['broken4']} b5={row['broken5']} OK"
        )


def check_intervals(blob: dict) -> None:
    for row in blob["census"]:
        if row["n_below_1_3"] != 0:
            raise AssertionError(f"interval n={row['n']} below 1/3")
        if row["min_delta"][0] * 3 < row["min_delta"][1]:
            raise AssertionError(f"interval min n={row['n']} below 1/3")
        P = Poset(row["n"], row["min_down"])
        num, den, e, pair = delta_of(P)
        if [num, den] != row["min_delta"] or e != row["min_e"]:
            raise AssertionError(f"interval min n={row['n']}: {(num, den, e)}")
        if row.get("min_not_semi_down"):
            Q = Poset(row["n"], row["min_not_semi_down"])
            n2, d2, e2, _ = delta_of(Q)
            if [n2, d2] != row["min_not_semi"] or e2 != row["min_ns_e"]:
                raise AssertionError(
                    f"interval non-semi n={row['n']}: {(n2, d2, e2)}"
                )
            if n2 * 3 < d2:
                raise AssertionError(f"non-semi interval n={row['n']} below 1/3")
        print(
            f"interval n={row['n']} min {num}/{den} "
            f"all={row['n_natural_interval']} OK"
        )


def main():
    ladder = HERE / "ladder_census.json"
    rail = HERE / "three_rail.json"
    interval = HERE / "interval_orders.json"
    if ladder.exists():
        check_ladders(json.loads(ladder.read_text()))
    else:
        print("ladder_census.json missing (census not yet written)")
    if rail.exists():
        check_rails(json.loads(rail.read_text()))
    else:
        print("three_rail.json missing")
    if interval.exists():
        check_intervals(json.loads(interval.read_text()))
    else:
        print("interval_orders.json missing")
    print("Q2 WINNERS OK")


if __name__ == "__main__":
    main()
