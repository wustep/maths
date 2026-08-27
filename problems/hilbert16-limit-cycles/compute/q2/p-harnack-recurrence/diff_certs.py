#!/usr/bin/env python3
"""Diff the Python and Rust certificate cores."""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.join(HERE, "certs")


def load(name: str) -> dict:
    path = os.path.join(CERTS, name)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def fail(msg: str) -> None:
    print(f"diff_certs FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def as_int_map(d: dict) -> dict[int, int]:
    return {int(k): int(v) for k, v in d.items()}


def main() -> None:
    py = load("core.json")
    rs = load("rust_core.json")

    scalar_keys = [
        "N_max",
        "n_pairs",
        "n_beats_quoted_m_ge_2",
        "n_beats_closed_recorded",
        "n_beats_claimed",
        "H_K_5",
        "L_pub_4",
        "L_pub_5",
        "H_K_5_equals_L_pub_4",
        "H_K_5_equals_9",
        "H_K_5_beats_H_5",
        "Har_1",
        "weaker_than_increment",
        "do_not_claim_252_1080_1380_2012_as_ours",
        "do_not_claim_HK5_28_as_ours",
        "example_H6_from_H2",
        "L_pub_6",
        "L_closed_18",
    ]
    for key in scalar_keys:
        if py[key] != rs[key]:
            fail(f"{key}: python {py[key]!r} != rust {rs[key]!r}")

    if py["Har_1_to_6"] != rs["Har_1_to_6"]:
        fail(f"Har_1_to_6: {py['Har_1_to_6']} vs {rs['Har_1_to_6']}")

    if as_int_map(py["Har"]) != as_int_map(rs["Har"]):
        fail("Har map mismatch")
    if as_int_map(py["L_pub"]) != as_int_map(rs["L_pub"]):
        fail("L_pub mismatch")
    if as_int_map(py["four_chebyshev"]) != as_int_map(rs["four_chebyshev"]):
        fail("four_chebyshev mismatch")
    if as_int_map(py["harnack_vs_four"]) != as_int_map(rs["harnack_vs_four"]):
        fail("harnack_vs_four mismatch")

    if py["m1_quoted_exceedances"] != rs["m1_quoted_exceedances"]:
        fail(
            "m1_quoted_exceedances mismatch\n"
            f"  python {py['m1_quoted_exceedances']}\n"
            f"  rust {rs['m1_quoted_exceedances']}"
        )

    py_best = {int(k): v for k, v in py["best_harnack"].items()}
    rs_best = {int(k): v for k, v in rs["best_harnack"].items()}
    if py_best != rs_best:
        keys = sorted(set(py_best) | set(rs_best))
        diffs = [(n, py_best.get(n), rs_best.get(n)) for n in keys if py_best.get(n) != rs_best.get(n)]
        fail(f"best_harnack mismatch: {diffs}")

    table_py = load("table_replay.json")
    table_rs = load("rust_table.json")
    py_all = {
        int(row["N"]): row["harnack_best"]
        for row in table_py["recorded_N"]
    }
    # Rust table lists every N<=50; compare recorded degrees only.
    rs_all = {
        int(k): int(v["lift"])
        for k, v in table_rs["best_harnack_N_le_50"].items()
        if int(k) in py_all
    }
    if py_all != rs_all:
        keys = sorted(set(py_all) | set(rs_all))
        diffs = [(n, py_all.get(n), rs_all.get(n)) for n in keys if py_all.get(n) != rs_all.get(n)]
        fail(f"recorded best-lift mismatch: {diffs}")

    if int(table_rs["n_beats_claimed"]) != 0:
        fail("rust table claims a beat")
    if as_int_map(table_rs["L_pub"]) != as_int_map(py["L_pub"]):
        fail("rust_table L_pub mismatch")

    print("diff_certs: ok")
    print(f"  pairs = {py['n_pairs']}")
    print(f"  Har(1..6) = {py['Har_1_to_6']}")
    print(f"  claimed beats = {py['n_beats_claimed']}")
    print(f"  H_K(5) = {py['H_K_5']} == L_pub[4]; beats H(5)? {py['H_K_5_beats_H_5']}")
    print(f"  H(2)+Har(4) = {py['example_H6_from_H2']} vs L_pub[6] = {py['L_pub_6']}")


if __name__ == "__main__":
    main()
